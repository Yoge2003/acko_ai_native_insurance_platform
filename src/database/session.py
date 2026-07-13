"""
Database Session Management for the ACKO AI Native Insurance Platform.
Defines SessionLocal factory and the get_db context generator for routing transactions.
"""

import logging
from typing import Generator
from sqlalchemy.orm import sessionmaker, Session
import src.database.database as db_module


logger = logging.getLogger(__name__)

# Configure transaction session maker
# Binding is deferred to connection check out or run time to facilitate dynamic configuration/mocking
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    bind=db_module.engine
)


def get_db() -> Generator[Session, None, None]:
    """
    Context generator for obtaining thread-safe Database Sessions.
    Opens a database transaction session, yields it, and guarantees cleanup hook close calls.

    Yields:
        Active SQLAlchemy Session transaction container.
    """
    if db_module.engine is None:
        logger.error("Attempting to get DB session but engine is uninitialized/None.")
        raise RuntimeError("SQLAlchemy Engine is not initialized. Verify PostgreSQL credentials in settings.")
        
    # Dynamically bind the current engine instance
    SessionLocal.configure(bind=db_module.engine)
    
    db: Session = SessionLocal()
    try:
        yield db
    except Exception as err:
        logger.error(f"Exception raised during database session transactional block: {err}", exc_info=True)
        raise err
    finally:
        db.close()
        logger.debug("Database session closed successfully.")

