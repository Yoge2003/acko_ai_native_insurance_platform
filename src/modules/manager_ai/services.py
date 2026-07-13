"""
Service layer for the Manager AI module.
Production-ready Agent SQL analytics compiler utilizing LangGraph and Google Gemini.
"""

import logging
import uuid
import json
import re
import time
from typing import Dict, Any, List, Optional, Tuple, TypedDict
from datetime import datetime

import google.generativeai as genai
import google.api_core.exceptions
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log
from sqlalchemy import text, inspect
from langgraph.graph import StateGraph, END

from src.database.session import SessionLocal
from src.database.base import Base
from src.config.settings import settings
from src.modules.manager_ai.validators import SQLAgentQueryValidator
from src.models.manager_query_log import ManagerSession, ManagerQueryLog
from src.models.user import User

logger = logging.getLogger(__name__)


class ManagerState(TypedDict):
    user_query: str
    session_id: str
    intent: Optional[str]
    schema_info: Optional[str]
    generated_sql: Optional[str]
    is_valid: Optional[bool]
    validation_error: Optional[str]
    sql_execution_status: Optional[str]  # 'success', 'warning', 'error', 'rejected'
    query_result: Optional[List[Dict[str, Any]]]
    row_count: Optional[int]
    execution_time_ms: Optional[float]
    explanation: Optional[str]
    warnings: Optional[List[str]]
    error: Optional[str]


def get_db_schema() -> str:
    """
    Introspects the live database schema (columns, types, refs) dynamically.
    Fails gracefully to fallback mock schema under unit test or isolated DBs.
    """
    session = SessionLocal()
    try:
        engine = session.bind
        inspector = inspect(engine)
        schema_desc = []
        for table_name in inspector.get_table_names():
            columns = inspector.get_columns(table_name)
            col_desc = []
            for col in columns:
                col_type = str(col.get("type", "UNKNOWN"))
                nullable = "NULL" if col.get("nullable", True) else "NOT NULL"
                default = f" DEFAULT {col.get('default')}" if col.get("default") is not None else ""
                col_desc.append(f"  {col['name']} {col_type} {nullable}{default}")
            
            # Primary key
            pk = inspector.get_pk_constraint(table_name)
            pk_cols = ", ".join(pk.get("constrained_columns", []))
            if pk_cols:
                col_desc.append(f"  PRIMARY KEY ({pk_cols})")
                
            # Foreign keys
            fks = inspector.get_foreign_keys(table_name)
            for fk in fks:
                ref_table = fk.get("referred_table")
                ref_cols = ", ".join(fk.get("referred_columns", []))
                constrained_cols = ", ".join(fk.get("constrained_columns", []))
                col_desc.append(f"  FOREIGN KEY ({constrained_cols}) REFERENCES {ref_table}({ref_cols})")
                
            schema_desc.append(f"CREATE TABLE {table_name} (\n" + ",\n".join(col_desc) + "\n);")
        
        if schema_desc:
            return "\n\n".join(schema_desc)
    except Exception as e:
        logger.error(f"Error introspecting database schema: {e}")
    finally:
        session.close()

    # Fallback Schema
    return """
    CREATE TABLE users (
      id UUID PRIMARY KEY,
      email VARCHAR NOT NULL UNIQUE,
      full_name VARCHAR,
      role VARCHAR
    );
    CREATE TABLE policies (
      id UUID PRIMARY KEY,
      policy_number VARCHAR NOT NULL UNIQUE,
      user_id UUID REFERENCES users(id),
      vehicle_type VARCHAR,
      premium NUMERIC,
      status VARCHAR
    );
    CREATE TABLE claims (
      id UUID PRIMARY KEY,
      policy_id UUID REFERENCES policies(id),
      user_id UUID REFERENCES users(id),
      claim_amount NUMERIC,
      damage_summary VARCHAR,
      gemini_analysis_json JSONB,
      predicted_decision VARCHAR,
      approval_probability NUMERIC
    );
    CREATE TABLE quotations (
      id UUID PRIMARY KEY,
      user_id UUID REFERENCES users(id),
      quote_amount NUMERIC,
      risk_score NUMERIC
    );
    """


def validate_sql_safety(sql: str) -> Tuple[bool, Optional[str]]:
    """
    Verifies query safety constraints:
    - Prevents multiple statements to safeguard against injection.
    - Blacklists modifying operations (INSERT, UPDATE, DELETE, DROP, etc.).
    - Enforces read-only statements starting with WITH or SELECT.
    """
    cleaned = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
    cleaned = re.sub(r'/\*.*?\*/', '', cleaned, flags=re.DOTALL)
    cleaned_upper = cleaned.upper().strip()
    
    if ";" in cleaned:
        statements = [s.strip() for s in cleaned.split(";") if s.strip()]
        if len(statements) > 1:
            return False, "Multiple SQL statements are not authorized."
            
    forbidden_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "TRUNCATE", "CREATE", 
        "COPY", "EXECUTE", "GRANT", "REVOKE", "MERGE"
    ]
    for word in forbidden_keywords:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, cleaned_upper):
            return False, f"Unauthorized SQL keyword found: {word}."

    if not (cleaned_upper.startswith("SELECT") or cleaned_upper.startswith("WITH")):
        return False, "SQL statement must be a SELECT or WITH read-only query statement."
            
    return True, None


def execute_query(sql: str) -> Tuple[List[Dict[str, Any]], int, float]:
    """
    Executes the validated SQL query in a read-only session context.
    Strictly rolls back transaction upon completion of reads to enforce safety.
    """
    start = time.perf_counter()
    session = SessionLocal()
    try:
        result = session.execute(text(sql))
        if result.returns_rows:
            rows = [dict(row) for row in result.mappings()]
        else:
            rows = []
        row_count = len(rows)
        execution_time_ms = (time.perf_counter() - start) * 1000.0
        session.rollback()  # Safety safeguard rollback
        return rows, row_count, execution_time_ms
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


# --- LangGraph Nodes ---

def analyze_intent(state: ManagerState) -> Dict[str, Any]:
    user_query = state["user_query"]
    prompt = f"""
    Evaluate if this natural language prompt is requesting statistics, reports, aggregation queries, or lists from an insurance database.
    Respond in single-line JSON format:
    {{
      "intent": "db_query" or "unrelated",
      "reason": "short explanation"
    }}
    User Query: "{user_query}"
    """
    try:
        # Check safe configuration
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            # Direct database query fallback
            return {"intent": "db_query"}

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        @retry(
            reraise=True,
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=4),
            retry=retry_if_exception_type((
                google.api_core.exceptions.ResourceExhausted,
                google.api_core.exceptions.ServiceUnavailable,
                google.api_core.exceptions.DeadlineExceeded
            )),
            before_sleep=before_sleep_log(logger, logging.WARNING)
        )
        def _intent_call():
            return model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})

        response = _intent_call()
        data = json.loads(response.text)
        intent = data.get("intent", "db_query")
        if intent == "unrelated":
            return {
                "intent": "unrelated",
                "sql_execution_status": "rejected",
                "error": "Query is not database related."
            }
        return {"intent": intent}
    except Exception as e:
        logger.error(f"Intent analysis error: {e}")
        return {"intent": "db_query"}


def retrieve_schema(state: ManagerState) -> Dict[str, Any]:
    schema = get_db_schema()
    return {"schema_info": schema}


def generate_sql(state: ManagerState) -> Dict[str, Any]:
    if state.get("intent") == "unrelated":
        return {"generated_sql": None, "sql_execution_status": "rejected", "error": "Query is not database related."}
        
    schema = state["schema_info"]
    user_query = state["user_query"]
    
    prompt = f"""
    You are an expert PostgreSQL developer. Convert this natural language question into a safe, valid read-only SELECT or WITH statement.
    Database Schema:
    {schema}
    
    Question: "{user_query}"
    
    Rules:
    1. Respond ONLY with a JSON object. No Markdown highlights.
    2. Format: {{"sql": "SELECT ... FROM ... COLLATE ..."}}
    3. The query must compile under standard SQL and reference actual table/columns in the schema.
    """
    try:
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            # Heuristic SQL generator for offline testing
            query_lower = user_query.lower()
            sql = "SELECT COUNT(*) as count FROM policies;"
            if "claim" in query_lower:
                sql = "SELECT COUNT(*) as count, predicted_decision FROM claims GROUP BY predicted_decision;"
            elif "user" in query_lower:
                sql = "SELECT COUNT(*) as count FROM users;"
            elif "quotation" in query_lower:
                sql = "SELECT AVG(quote_amount) as average_quote FROM quotations;"
            return {"generated_sql": sql}

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        @retry(
            reraise=True,
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=4),
            retry=retry_if_exception_type((
                google.api_core.exceptions.ResourceExhausted,
                google.api_core.exceptions.ServiceUnavailable,
                google.api_core.exceptions.DeadlineExceeded
            )),
            before_sleep=before_sleep_log(logger, logging.WARNING)
        )
        def _sql_gen_call():
            return model.generate_content(prompt, generation_config={"response_mime_type": "application/json"})

        response = _sql_gen_call()
        data = json.loads(response.text)
        sql = data.get("sql", "").strip()
        return {"generated_sql": sql}
    except Exception as e:
        logger.error(f"SQL Generation error: {e}")
        return {"generated_sql": "SELECT COUNT(*) as count FROM policies;", "warnings": ["Offline generator mode fallback applied."]}


def validate_sql(state: ManagerState) -> Dict[str, Any]:
    sql = state.get("generated_sql")
    if not sql:
        return {"is_valid": False, "validation_error": "No SQL code compiled.", "sql_execution_status": "rejected"}
        
    # Validation checks
    is_valid, err = validate_sql_safety(sql)
    if not is_valid:
        return {
            "is_valid": False,
            "validation_error": err,
            "sql_execution_status": "rejected",
            "error": err
        }
    return {"is_valid": True, "sql_execution_status": "success"}


def execute_sql(state: ManagerState) -> Dict[str, Any]:
    if not state.get("is_valid"):
        return {"query_result": [], "row_count": 0, "execution_time_ms": 0.0}

    sql = state["generated_sql"]
    try:
        rows, row_count, execution_time = execute_query(sql)
        return {
            "query_result": rows,
            "row_count": row_count,
            "execution_time_ms": execution_time,
            "sql_execution_status": "success"
        }
    except Exception as e:
        logger.error(f"SQL Execution failure: {e}")
        return {
            "query_result": [],
            "row_count": 0,
            "execution_time_ms": 0.0,
            "sql_execution_status": "error",
            "error": f"Database execution failure: {e}"
        }


def generate_summary(state: ManagerState) -> Dict[str, Any]:
    user_query = state["user_query"]
    sql = state.get("generated_sql")
    results = state.get("query_result", [])
    row_count = state.get("row_count", 0)
    status = state.get("sql_execution_status", "success")
    err = state.get("error") or state.get("validation_error")

    if status == "rejected":
        return {"explanation": f"Query execution rejected: {err}"}
    elif status == "error":
        return {"explanation": f"Execution failed: {err}"}

    prompt = f"""
    Summarize these database inquiry results. Answer the question in a friendly analytics tone.
    Question: "{user_query}"
    Executed SQL: "{sql}"
    Query Rows Count: {row_count}
    Sample Data: {results[:10]}
    """
    try:
        if not settings.GEMINI_API_KEY or settings.GEMINI_API_KEY == "your_gemini_api_key_here":
            return {"explanation": f"Successfully retrieved {row_count} rows from the database. [Offline Summary View]"}

        genai.configure(api_key=settings.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.0-flash")

        @retry(
            reraise=True,
            stop=stop_after_attempt(3),
            wait=wait_exponential(multiplier=1, min=1, max=4),
            retry=retry_if_exception_type((
                google.api_core.exceptions.ResourceExhausted,
                google.api_core.exceptions.ServiceUnavailable,
                google.api_core.exceptions.DeadlineExceeded
            )),
            before_sleep=before_sleep_log(logger, logging.WARNING)
        )
        def _summary_call():
            return model.generate_content(prompt)

        response = _summary_call()
        return {"explanation": response.text.strip()}
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return {"explanation": f"Query executed successfully returning {row_count} rows."}


# --- Construct State Graph Workflow ---

workflow = StateGraph(ManagerState)

workflow.add_node("analyze_intent", analyze_intent)
workflow.add_node("retrieve_schema", retrieve_schema)
workflow.add_node("generate_sql", generate_sql)
workflow.add_node("validate_sql", validate_sql)
workflow.add_node("execute_sql", execute_sql)
workflow.add_node("generate_summary", generate_summary)

workflow.set_entry_point("analyze_intent")

def route_intent(state: ManagerState) -> str:
    if state.get("intent") == "unrelated":
        return "generate_summary"
    return "retrieve_schema"

workflow.add_conditional_edges(
    "analyze_intent",
    route_intent,
    {
        "generate_summary": "generate_summary",
        "retrieve_schema": "retrieve_schema"
    }
)

workflow.add_edge("retrieve_schema", "generate_sql")
workflow.add_edge("generate_sql", "validate_sql")

def route_validation(state: ManagerState) -> str:
    if not state.get("is_valid"):
        return "generate_summary"
    return "execute_sql"

workflow.add_conditional_edges(
    "validate_sql",
    route_validation,
    {
        "generate_summary": "generate_summary",
        "execute_sql": "execute_sql"
    }
)

workflow.add_edge("execute_sql", "generate_summary")
workflow.add_edge("generate_summary", END)

app = workflow.compile()


# --- Service Interface ---

class ManagerAIService:
    """
    Business service layer orchestrating the LangGraph SQL reasoning agents.
    """

    def run_agent_query(self, user_query: str, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs language-to-SQL compiler checks.
        Validates structures and saves execution records to PostgreSQL logs.
        """
        # Form validation
        validator = SQLAgentQueryValidator(user_prompt=user_query)
        logger.info(f"ManagerAIService executing query: {validator.user_prompt}")

        session = SessionLocal()
        try:
            # Table Auto-Creation
            Base.metadata.create_all(bind=session.bind)

            if not session_id:
                # Find default user context
                user = session.query(User).first()
                if not user:
                    user = User(full_name="System Manager", email="manager@acko.com", role="manager")
                    session.add(user)
                    session.commit()
                # Create session tracker
                mgr_session = ManagerSession(user_id=user.id, title=f"Q&A Session {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                session.add(mgr_session)
                session.commit()
                session_id = str(mgr_session.id)

            initial_state = {
                "user_query": user_query,
                "session_id": session_id,
                "intent": None,
                "schema_info": None,
                "generated_sql": None,
                "is_valid": None,
                "validation_error": None,
                "sql_execution_status": "success",
                "query_result": [],
                "row_count": 0,
                "execution_time_ms": 0.0,
                "explanation": None,
                "warnings": [],
                "error": None
            }

            res = app.invoke(initial_state)

            # Persist query log to DB
            log = ManagerQueryLog(
                session_id=uuid.UUID(session_id),
                question=user_query,
                generated_sql=res.get("generated_sql"),
                execution_time_ms=res.get("execution_time_ms", 0.0),
                row_count=res.get("row_count", 0),
                status=res.get("sql_execution_status", "success"),
                error_message=res.get("error") or res.get("validation_error")
            )
            session.add(log)
            session.commit()

            return {
                "status": res.get("sql_execution_status", "success"),
                "compiled_sql": res.get("generated_sql") or "",
                "answer": res.get("explanation") or "",
                "data": res.get("query_result", []),
                "execution_time_ms": res.get("execution_time_ms", 0.0),
                "row_count": res.get("row_count", 0),
                "session_id": session_id,
                "error": res.get("error") or res.get("validation_error") or ""
            }
        except Exception as e:
            session.rollback()
            logger.error(f"Manager Agent query pipeline failed: {e}")
            raise e
        finally:
            session.close()

    def get_session_history(self, session_id: str) -> List[Dict[str, Any]]:
        session = SessionLocal()
        try:
            logs = session.query(ManagerQueryLog).filter(
                ManagerQueryLog.session_id == uuid.UUID(session_id)
            ).order_by(ManagerQueryLog.created_at.asc()).all()
            return [
                {
                    "question": log.question,
                    "compiled_sql": log.generated_sql or "",
                    "execution_time_ms": log.execution_time_ms or 0.0,
                    "row_count": log.row_count or 0,
                    "status": log.status,
                    "error": log.error_message or "",
                    "created_at": log.created_at.isoformat()
                } for log in logs
            ]
        finally:
            session.close()

    def get_user_sessions(self, email: str = "manager@acko.com") -> List[Dict[str, Any]]:
        session = SessionLocal()
        try:
            user = session.query(User).filter(User.email == email).first()
            if not user:
                return []
            sessions = session.query(ManagerSession).filter(
                ManagerSession.user_id == user.id
            ).order_by(ManagerSession.created_at.desc()).all()
            return [
                {
                    "id": str(s.id),
                    "title": s.title,
                    "created_at": s.created_at.isoformat()
                } for s in sessions
            ]
        finally:
            session.close()
