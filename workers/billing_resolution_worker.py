from langgraph_state import AgentState
from adk_remote_client import run_billing_resolution


def billing_resolution_worker(state: AgentState) -> AgentState:
    query = state["user_query"]

    result = run_billing_resolution(query)

    context = state.get("agent_context", {}).copy()
    context["billing_resolution"] = result

    completed = context.get("_completed_workers", []).copy()

    if "billing_resolution" not in completed:
        completed.append("billing_resolution")

    context["_completed_workers"] = completed

    trace = state.get("execution_trace", []).copy()
    trace.append({
        "step": str(len(trace) + 1),
        "worker": "BillingResolutionADK",
        "output": result[:500],
    })

    return {
        **state,
        "agent_context": context,
        "next": "supervisor",
    }