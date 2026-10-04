from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    messages: list[dict[str, str]]
    user_query: str
    next: str
    agent_context: dict[str, Any]
    final_response: str
    execution_trace: list[dict[str, str]]