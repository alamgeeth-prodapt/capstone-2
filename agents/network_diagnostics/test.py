import asyncio

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agent import root_agent


async def main():
    session_service = InMemorySessionService()

    app_name = "network_diagnostics_test"
    user_id = "test_user"
    session_id = "test_session"

    await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
    )

    runner = Runner(
        agent=root_agent,
        app_name=app_name,
        session_service=session_service,
    )

    message = types.Content(
        role="user",
        parts=[
            types.Part(
                text="Check the current status and health of tower TX-512."
            )
        ],
    )

    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    ):
        print(
            f"Event: author={event.author}, "
            f"final={event.is_final_response()}"
        )

        if event.is_final_response():
            if event.content and event.content.parts:
                print("\n=== FINAL RESPONSE ===")
                print(event.content.parts[0].text)
            else:
                print("\n=== FINAL RESPONSE ===")
                print("Final event contained no text content.")


if __name__ == "__main__":
    asyncio.run(main())