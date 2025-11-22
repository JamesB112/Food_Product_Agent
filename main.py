# main.py

import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agent import root_agent  # your root agent

async def main():
    """Runs the Food Product Health Advisor agent interactively."""

    # Set up an in-memory session service
    session_service = InMemorySessionService()
    await session_service.create_session(
        app_name="food_health_app",
        user_id="user_1",
        session_id="session_1"
    )

    # Create the runner
    runner = Runner(
        agent=root_agent,
        app_name="food_health_app",
        session_service=session_service
    )

    print("Welcome to the Food Product Health Advisor!")
    print("Enter a product name or ingredients list, or 'exit' to quit.\n")

    while True:
        user_input = input("Your query: ")
        if user_input.lower() == "exit":
            print("Goodbye!")
            break

        print("\nProcessing...\n")

        # Run the agent asynchronously and stream events
        async for event in runner.run_async(
            user_id="user_1",
            session_id="session_1",
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part.from_text(text=user_input)]
            )
        ):
            if event.is_final_response() and event.content and event.content.parts:
                print(event.content.parts[0].text)

if __name__ == "__main__":
    asyncio.run(main())
