import uvicorn

from .agent import root_agent
from a2a.types import AgentCard, AgentInterface
from google.adk.a2a.utils.agent_to_a2a import to_a2a


agent_card = AgentCard(
    name="billing_resolution_agent",
    description=(
        "A billing resolution specialist that investigates customer "
        "billing accounts, duplicate charges, and billing credit requests."
    ),
    supported_interfaces=[
        AgentInterface(
            url="http://127.0.0.1:8002",
            protocol_binding="JSONRPC",
            protocol_version="1.0",
        )
    ],
    version="0.0.1",
    default_input_modes=["text/plain"],
    default_output_modes=["text/plain"],
)

app = to_a2a(
    root_agent,
    agent_card=agent_card,
)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8002,
    )