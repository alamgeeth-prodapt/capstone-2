from langgraph_state import AgentState
from semantic_sql import query_network_analytics


def run_network_analytics(query: str) -> str:
    return query_network_analytics(query)


def network_analytics_worker(state: AgentState) -> AgentState:
    query = state["user_query"]

    result = run_network_analytics(query)

    context = state.get("agent_context", {}).copy()
    context["network_analytics"] = result

    completed = context.get("_completed_workers", []).copy()

    if "network_analytics" not in completed:
        completed.append("network_analytics")

    context["_completed_workers"] = completed

    trace = state.get("execution_trace", []).copy()
    trace.append({
        "step": str(len(trace) + 1),
        "worker": "NetworkAnalytics",
        "output": result[:500],
    })

    return {
        **state,
        "agent_context": context,
        "execution_trace": trace,
        "next": "supervisor",
    }