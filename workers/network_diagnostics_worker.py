from langgraph_state import AgentState
from adk_remote_client import run_network_diagnostics


def network_diagnostics_worker(state: AgentState) -> AgentState:
    print("\n>>> Network Diagnostics Worker CALLED")

    query = state["user_query"]

    result = run_network_diagnostics(query)

    context = state.get("agent_context", {}).copy()
    context["network_diagnostics"] = result

    completed = context.get("_completed_workers", []).copy()

    if "network_diagnostics" not in completed:
        completed.append("network_diagnostics")

    context["_completed_workers"] = completed

    trace = state.get("execution_trace", []).copy()
    trace.append({
        "step": str(len(trace) + 1),
        "worker": "NetworkDiagnosticsADK",
        "output": result[:500],
    })

    return {
        **state,
        "agent_context": context,
        "execution_trace": trace,
        "next": "supervisor",
    }