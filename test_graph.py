from graph import graph


initial_state = {
    "user_query": (
        "Which region had the most critical network outages recently, "
        "and are the affected customers eligible for SLA compensation?"
    ),
    "messages": [],
    "agent_context": {},
    "execution_trace": [],
}


result = graph.invoke(initial_state)

print("\n===== FINAL RESPONSE =====")
print(result.get("final_response"))

print("\n===== EXECUTION TRACE =====")
for step in result.get("execution_trace", []):
    print(
        f"{step['step']}. "
        f"{step['worker']}: "
        f"{step['output']}"
    )

print("\n===== AGENT CONTEXT =====")
for key, value in result.get("agent_context", {}).items():
    if not key.startswith("_"):
        print(f"\n--- {key} ---")
        print(value)