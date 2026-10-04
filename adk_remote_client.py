import asyncio

from google.adk.agents.remote_a2a_agent import RemoteA2aAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types


NETWORK_AGENT_CARD = (
    "http://127.0.0.1:8001/.well-known/agent-card.json"
)

BILLING_AGENT_CARD = (
    "http://127.0.0.1:8002/.well-known/agent-card.json"
)


# ---------------------------------------------------------
# Remote A2A agents
# ---------------------------------------------------------

network_diagnostics_agent = RemoteA2aAgent(
    name="network_diagnostics_remote",
    agent_card=NETWORK_AGENT_CARD,
    description="Remote Network Diagnostics ADK agent.",
)

billing_resolution_agent = RemoteA2aAgent(
    name="billing_resolution_remote",
    agent_card=BILLING_AGENT_CARD,
    description="Remote Billing Resolution ADK agent.",
)


# ---------------------------------------------------------
# Run a remote ADK agent
# ---------------------------------------------------------

async def _run_remote_agent(agent, query: str) -> str:

    session_service = InMemorySessionService()

    runner = Runner(
        app_name="telecom_ops_remote_client",
        agent=agent,
        session_service=session_service,
    )

    user_id = "langgraph_user"
    session_id = f"session_{id(query)}"

    await session_service.create_session(
        app_name="telecom_ops_remote_client",
        user_id=user_id,
        session_id=session_id,
    )

    content = types.Content(
        role="user",
        parts=[
            types.Part(text=query)
        ],
    )

    response_text = ""

    try:

        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=content,
        ):

            if event.is_final_response():

                if event.content and event.content.parts:

                    response_text = "".join(
                        part.text
                        for part in event.content.parts
                        if part.text
                    )

        return response_text

    except Exception as exc:

        return (
            f"Remote ADK service unavailable or failed: "
            f"{type(exc).__name__}: {exc}"
        )


# ---------------------------------------------------------
# Synchronous wrappers
# ---------------------------------------------------------

def run_network_diagnostics(query: str) -> str:

    return asyncio.run(
        _run_remote_agent(
            network_diagnostics_agent,
            query,
        )
    )


def run_billing_resolution(query: str) -> str:

    return asyncio.run(
        _run_remote_agent(
            billing_resolution_agent,
            query,
        )
    )


# ---------------------------------------------------------
# Local test
# ---------------------------------------------------------

if __name__ == "__main__":

    print("\n--- NETWORK DIAGNOSTICS ---")

    result = run_network_diagnostics(
        "Check the current status and health of tower TX-512."
    )

    print(result)

    print("\n--- BILLING RESOLUTION ---")

    result = run_billing_resolution(
        "Investigate the billing account for CUST-10002 "
        "and check whether there are any duplicate charges."
    )

    print(result)