from langgraph_state import AgentState
from workers.customer_comms_crew import run_customer_comms


def customer_comms_worker(state: AgentState) -> AgentState:
    query = state["user_query"]
    context = state.get("agent_context", {})
    result = f"Customer communications placeholder for: {query}"
    result = run_customer_comms(query, context)
    
    trace = state.get("execution_trace", []).copy()
    trace.append({
        "step": str(len(trace) + 1),
        "worker": "CustomerCommsCrew",
        "output": result[:500],
    })

    return {
        **state,
        "final_response": result,
        "agent_context": context,
        "execution_trace": trace,
        "next": "finish",
    }