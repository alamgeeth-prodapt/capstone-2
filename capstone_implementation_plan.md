# Implementation Plan: Prodapt Agentic AI Operations Center

## Goal Description
Build the complete **Prodapt Agentic AI Operations Center Capstone Project** adhering to the specifications in `data/prodapt-project/Agentic AI Project .html`. The system unites five key frameworks:
1. **LlamaIndex**: Unstructured document RAG over 6 policy TXT files + Structured Semantic SQL over SQLite `telecom_ops.db`.
2. **Google ADK (Agent Development Kit)**: Two independent Agent-to-Agent (A2A) microservices running on HTTP ports 8001 (Network Diagnostics) and 8002 (Billing Resolution) executing SQLite-backed tools.
3. **CrewAI**: Sequential two-agent crew (Communications Specialist + Quality Reviewer) to synthesize and polish the final customer response.
4. **LangGraph**: Supervisor state machine coordinating routing across specialists, accumulating execution context, and tracking the execution trace.
5. **Streamlit**: Unified operations center UI displaying live system health, inquiry input, final response, and the mandatory **Agent Execution Trace** panel.

---

## Current Project Status & Audit

| Component | Current State | Required Action |
| :--- | :--- | :--- |
| **Starter Data & SQL** | Present in `data/prodapt-project/projectfiles/` | Move/standardize to root `data/documents/` and ensure `data/telecom_ops.db` is populated. |
| **LlamaIndex Semantic SQL** | Implemented as [semantic_sql.py](file:///D:/Project_2/semantic_sql.py) in root | Move & standardize to `llamaindex_rag/sql_semantic_search.py` with full table schemas and persistent query interface. |
| **LlamaIndex Document RAG** | Preliminary ChromaDB scripts in `llamaindex_rag/` | Implement spec-compliant [document_rag.py](file:///D:/Project_2/llamaindex_rag/document_rag.py) with `VectorStoreIndex` persisting to `data/vector_index/`. |
| **Network Diagnostics ADK** | **Not yet created** | Build `adk-services/network_diagnostics/agent.py` on port 8001 with 3 SQLite tools (`check_tower_status`, `run_connectivity_diagnostics`, `get_regional_network_summary`). |
| **Billing Resolution ADK** | **Not yet created** | Build `adk-services/billing_resolution/agent.py` on port 8002 with 3 SQLite tools (`lookup_billing_account`, `check_duplicate_charges`, `apply_billing_credit` with $50 policy rule). |
| **Remote ADK Client** | **Not yet created** | Build `orchestration/adk_remote_client.py` wrapping `RemoteA2aAgent` and ADK `Runner` with health check and graceful fallbacks. |
| **CrewAI Customer Comms** | **Not yet created** | Build `orchestration/crew_nodes.py` with sequential Communications Specialist and Quality Reviewer agents. |
| **LangGraph Orchestration** | **Not yet created** | Build `orchestration/state.py` and `orchestration/graph.py` with Supervisor routing across 5 scenarios and execution trace tracking. |
| **Streamlit UI** | **Not yet created** | Build `ui/app.py` with live sidebar health checks (DB, vector index, ports 8001 & 8002) and Agent Execution Trace expander. |
| **PII Privacy Guardrail** | Implemented in [pii/](file:///D:/Project_2/pii) | Retain and provide seamless integration/toggle for anonymizing customer inquiries before LLM processing. |

---

## User Review Required

> [!IMPORTANT]
> **Python Virtual Environment (`.venv`) for CrewAI & Dependencies**:
> - The system currently runs Python 3.14 as the default interpreter. Certain upstream dependencies for `crewai` require Python `<= 3.13` (Python 3.11 is installed on your system at `C:\Users\geeth.madhu\AppData\Local\Programs\Python\Python311`).
> - We recommend creating a dedicated Python 3.11 virtual environment (`py -3.11 -m venv .venv`) where all project packages (`langgraph`, `google-adk[a2a]`, `llama-index`, `crewai`, `streamlit`, `sentence-transformers`) can run cohesively without version conflicts.

> [!NOTE]
> **Environment Variables**:
> - We will strictly avoid reading, displaying, or exposing any `.env` keys.
> - The modules will load configuration using standard `dotenv.load_dotenv()` directly from `.env`.

---

## Proposed Changes & Leftover Modules

### 1. Starter Assets & Database Standardization
- Copy documents from `data/prodapt-project/projectfiles/data/documents/` into `data/documents/`.
- Ensure `data/telecom_ops.db` is populated directly from `01_schema.sql` and `02_seed_data.sql`.

---

### 2. LlamaIndex Retrieval Layer (`llamaindex_rag/`)

#### [NEW] `llamaindex_rag/document_rag.py`
- Uses HuggingFace `sentence-transformers/all-MiniLM-L6-v2` embeddings.
- Loads TXT files from `data/documents/` using `SimpleDirectoryReader`.
- Builds and persists `VectorStoreIndex` to `data/vector_index/`.
- Exposes:
  ```python
  def query_policy_faq(question: str) -> str:
      ...
  ```
- Uses `as_query_engine()` (retrieval-only, no LlamaIndex agents).

#### [NEW] `llamaindex_rag/sql_semantic_search.py`
- Migrates and standardizes the logic from [semantic_sql.py](file:///D:/Project_2/semantic_sql.py).
- Connects to `data/telecom_ops.db` via `SQLDatabase`.
- Maps schemas for `network_outages`, `network_towers`, `tower_performance`, and `customer_subscriptions`.
- Uses `ObjectIndex` over `SQLTableSchema` with `similarity_top_k=2`.
- Exposes:
  ```python
  def query_network_analytics(question: str) -> str:
      ...
  ```

---

### 3. Google ADK A2A Microservices (`adk-services/`)

#### [NEW] `adk-services/network_diagnostics/agent.py`
- Runs as an A2A service on port `8001` via `to_a2a` and `uvicorn`.
- Agent instruction: NOC Diagnostics Specialist.
- Implements 3 SQLite-backed async tools:
  - `check_tower_status(tower_id: str)`: Joins `network_towers` with latest `tower_performance` sample (`MAX(recorded_at)`) and active `open_incidents`.
  - `run_connectivity_diagnostics(tower_id: str, symptom: str)`: Inspects metrics (latency, packet loss, signal strength) and returns remediation recommendations.
  - `get_regional_network_summary(region: str)`: Aggregates operational, degraded, and offline towers in the region.
- Serves agent card at `http://localhost:8001/.well-known/agent-card.json`.

#### [NEW] `adk-services/billing_resolution/agent.py`
- Runs as an A2A service on port `8002` via `to_a2a` and `uvicorn`.
- Agent instruction: Billing Dispute Resolution Specialist.
- Implements 3 SQLite-backed async tools:
  - `lookup_billing_account(customer_id: str)`: Reads balance and line items from `billing_accounts` and `billing_charges` (open vs paid).
  - `check_duplicate_charges(customer_id: str)`: Identifies same charge in same period or `is_duplicate_flag = 1`, skipping already applied credits.
  - `apply_billing_credit(customer_id: str, amount: float, reason: str)`:
    - If `amount <= 50.00`: Inserts credit with status `APPLIED` and updates `current_balance` in `billing_accounts`.
    - If `amount > 50.00`: Inserts credit with status `PENDING_APPROVAL` and leaves `current_balance` unchanged.
- Serves agent card at `http://localhost:8002/.well-known/agent-card.json`.

---

### 4. Orchestration Layer (`orchestration/`)

#### [NEW] `orchestration/adk_remote_client.py`
- Instantiates `RemoteA2aAgent` pointing to `http://localhost:8001` and `http://localhost:8002`.
- Implements helper functions using ADK `Runner.run_async`:
  - `call_network_diagnostics(query: str) -> str`
  - `call_billing_resolution(query: str) -> str`
- Checks whether the services are reachable and returns descriptive status if ports 8001/8002 are offline.

#### [NEW] `orchestration/crew_nodes.py`
- Defines sequential CrewAI crew:
  - **Communications Specialist**: Drafts the response using `user_query` and accumulated `agent_context`.
  - **Quality Reviewer**: Reviews for tone, customer empathy, policy consistency, and clarity.
- Exposes:
  ```python
  def polish_customer_response(user_query: str, agent_context: str) -> str:
      ...
  ```

#### [NEW] `orchestration/state.py`
- Defines `AgentState` TypedDict:
  ```python
  class AgentState(TypedDict):
      messages: Annotated[list[BaseMessage], operator.add]
      next: str
      user_query: str
      agent_context: str
      execution_trace: list[dict[str, str]]
  ```

#### [NEW] `orchestration/graph.py`
- Compiles the LangGraph StateGraph with nodes:
  - `supervisor`: Structured routing decision based on query and accumulated context.
  - `policy_rag`: Invokes `document_rag.py`.
  - `network_analytics`: Invokes `sql_semantic_search.py`.
  - `network_diagnostics_adk`: Invokes `adk_remote_client.py` (Port 8001).
  - `billing_resolution_adk`: Invokes `adk_remote_client.py` (Port 8002).
  - `customer_comms_crew`: Invokes `crew_nodes.py`.
- Routing rules:
  - Specialist nodes append output to `agent_context` and record entry in `execution_trace`.
  - Every specialist loops back to `supervisor`.
  - `supervisor` routes to `customer_comms_crew` before terminating at `END`.
- Exposes primary entry function:
  ```python
  def run_telecom_assistant(user_query: str) -> dict:
      ...
      # returns {"final_response": ..., "execution_trace": [...], "agent_context": ...}
  ```

---

### 5. Streamlit User Interface (`ui/`)

#### [NEW] `ui/app.py`
- **Sidebar**:
  - Database status (`data/telecom_ops.db` exists and has rows).
  - Vector Index status (`data/vector_index/`).
  - Live HTTP status for ADK services (ports 8001 and 8002) with start commands if down.
  - Framework mapping table.
- **Main Area**:
  - Title and framework caption (LangGraph, LlamaIndex, Google ADK, CrewAI).
  - Customer inquiry text input.
  - "Submit" button with interactive `st.spinner`.
  - Prominent final customer response card.
  - **Agent Execution Trace** expander displaying:
    - Step number (1, 2, 3...)
    - Exact worker name (`PolicyRAG`, `NetworkAnalytics`, `NetworkDiagnosticsADK`, `BillingResolutionADK`, `CustomerCommsCrew`)
    - Truncated worker output (first 500 characters).

---

## Verification Plan

### Automated Tests
1. **LlamaIndex Unit Test**:
   - Query `query_policy_faq("What is the roaming policy for Western Europe?")` -> Check for Zone B pricing.
   - Query `query_network_analytics("Which region had the most CRITICAL network outages recently?")` -> Verify SQL query matches `network_outages` table.
2. **ADK Service Test**:
   - Query `check_tower_status("TX-512")` -> Verify OPERATIONAL and INC-8841.
   - Query `apply_billing_credit("CUST-10002", 65.99, "duplicate")` -> Verify status `PENDING_APPROVAL` and balance remains 131.98.
3. **End-to-End Scenarios via LangGraph**:
   - **Scenario 1 (Policy)**: `PolicyRAG` -> `CustomerCommsCrew` -> `FINISH`.
   - **Scenario 2 (Analytics)**: `NetworkAnalytics` -> `CustomerCommsCrew` -> `FINISH`.
   - **Scenario 3 (Diagnostics)**: `NetworkDiagnosticsADK` -> `CustomerCommsCrew` -> `FINISH`.
   - **Scenario 4 (Billing Dispute)**: `BillingResolutionADK` -> `CustomerCommsCrew` -> `FINISH`.
   - **Scenario 5 (Multi-worker)**: `NetworkAnalytics` -> `PolicyRAG` -> `CustomerCommsCrew` -> `FINISH`.

### Manual UI Verification
- Launch ADK services on ports 8001 and 8002.
- Launch `streamlit run ui/app.py`.
- Verify sidebar indicators turn green/Ready.
- Input queries for each scenario and check that the **Agent Execution Trace** panel reflects the exact step sequence and worker contributions.
