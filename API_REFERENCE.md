# API Reference Documentation

This document describes the public function signatures, parameters, classes, and service methods within the ACKO AI Native Insurance Platform.

---

## 🔒 1. Authentication Service (`src/services/authentication.py`)

### `class AuthenticationService`
Coordinates secure bcrypt password verification, session lock cycles, password resets, and user roles permissions.

#### `authenticate(email: str, password: str) -> Dict[str, Any]`
Validates user email and password.
* **Arguments**:
  * `email` (`str`): Target logging user email address.
  * `password` (`str`): Raw password character string.
* **Returns**: User details dictionary containing `id`, `name`, `email`, and `role`.
* **Raises**:
  * `ValidationError`: In case of invalid passwords or non-existent emails.
  * `LockoutError`: In case the account is locked due to excess login errors.

#### `register(name: str, email: str, password: str, role: str) -> None`
Creates and registers a new system user with hashed passwords.
* **Arguments**:
  * `name`, `email`, `password`, `role`.
* **Raises**: `ValidationError` if email is already taken or password fails complexity filters.

---

## 💰 2. Quotation Service (`src/services/quotation.py`)

### `class QuotationService`
Calculates premium quotes using machine learning estimators.

#### `predict_premium(input_features: Dict[str, Any], vehicle_type: str) -> Dict[str, Any]`
* **Arguments**:
  * `input_features` (`dict`): Vehicle attributes (e.g. engine capacity, value, age).
  * `vehicle_type` (`str`): `"car"` or `"bike"`.
* **Returns**: Dictionary containing:
  * `premium` (`float`): Calculated premium value.
  * `confidence` (`float`): Predictor confidence metric.
  * `shap_keys` (`list`): Explainer feature attribution rankings.

---

## 📄 3. Claims Service (`src/services/claim.py`)

### `class ClaimsService`
Audits claim details and processes uploaded vehicle photos using vision APIs.

#### `process_claims_vision(claim_id: uuid.UUID, image_bytes: bytes) -> Dict[str, Any]`
* **Arguments**:
  * `claim_id` (`uuid`): Claim primary key UUID.
  * `image_bytes` (`bytes`): Uploaded vehicle image file binary stream.
* **Returns**: Generative diagnostic dictionary detailing damage estimates, repair parts list, and confidence indices.

---

## 🤖 4. RAG Chatbot Service (`src/services/rag_chatbot.py`)

### `class RAGChatbotService`
Interfaces with vector stores and generates reference citations.

#### `query_policy_docs(session_id: uuid.UUID, user_query: str) -> Dict[str, Any]`
* **Returns**: Dictionary with `response` text block and a `citations` array.

---

## 🧠 5. Manager AI Service (`src/services/manager_ai.py`)

### `class ManagerAIService`
Translates natural text queries into execute-ready SQL commands.

#### `query_relational_agent(prompt: str) -> Dict[str, Any]`
* **Arguments**:
  * `prompt` (`str`): Natural text question (e.g. *"Show total quotes this month"*).
* **Returns**: Generative response string and executed SQL table.
