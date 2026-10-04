from langgraph_state import AgentState


def supervisor(state: AgentState) -> AgentState:
    query = state["user_query"].lower()
    context = state.get("agent_context", {}).copy()

    # Create the execution plan only once.
    if "_plan" not in context:
        if (
            "outage" in query
            and any(word in query for word in ["sla", "eligible", "eligibility"])
        ):
            plan = [
                "network_analytics",
                "policy_rag",
                "customer_comms_crew",
            ]

        elif any(
            word in query
            for word in ["billing", "charge", "invoice", "credit", "balance"]
        ):
            plan = [
                "billing_resolution_adk",
                "customer_comms_crew",
            ]

        elif any(
            word in query
            for word in ["tower", "connectivity", "signal", "latency", "packet loss"]
        ):
            plan = [
                "network_diagnostics_adk",
                "customer_comms_crew",
            ]

        elif any(
            word in query
            for word in ["outage", "region", "traffic", "analytics"]
        ):
            plan = [
                "network_analytics",
                "customer_comms_crew",
            ]

        elif any(
            word in query
            for word in ["policy", "sla", "procedure", "eligible"]
        ):
            plan = [
                "policy_rag",
                "customer_comms_crew",
            ]

        else:
            plan = [
                "customer_comms_crew",
            ]

        context["_plan"] = plan
        context["_completed_workers"] = []

    plan = context["_plan"]
    completed = context["_completed_workers"]

    # Find the next worker that has not executed yet.
    for worker in plan:
        if worker not in completed:
            context["_completed_workers"] = completed

            return {
                **state,
                "agent_context": context,
                "next": worker,
            }

    # Everything in the plan has completed.
    return {
        **state,
        "agent_context": context,
        "next": "finish",
    }