from langgraph_state import AgentState
from llamaindex_rag.search import test_vector_search


def run_policy_rag(query: str) -> str:
    return test_vector_search(query)


def policy_rag_worker(state: AgentState) -> AgentState:
    query = state["user_query"]

    result = run_policy_rag(query)

    context = state.get("agent_context", {}).copy()
    context["policy_rag"] = result

    completed = context.get("_completed_workers", []).copy()

    if "policy_rag" not in completed:
        completed.append("policy_rag")

    context["_completed_workers"] = completed

    trace = state.get("execution_trace", []).copy()
    trace.append({
        "step": str(len(trace) + 1),
        "worker": "PolicyRAG",
        "output": result[:500],
    })

    return {
        **state,
        "agent_context": context,
        "execution_trace": trace,
        "next": "supervisor",
    }