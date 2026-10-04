import os

from crewai import Agent, Task, Crew, Process, LLM
from dotenv import load_dotenv

load_dotenv()


llm = LLM(
    model="anthropic/claude-haiku-4-5-20251001",
    api_key=os.environ.get("ANTHROPIC_API_KEY"),
)


def run_customer_comms(query: str, agent_context: dict) -> str:

    context_text = "\n\n".join(
        f"{key}:\n{value}"
        for key, value in agent_context.items()
        if not key.startswith("_")
    )

    communications_specialist = Agent(
        role="Customer Communications Specialist",
        goal="Create a clear, accurate, professional response for the telecom customer.",
        backstory=(
            "You communicate technical telecom and billing information "
            "clearly without inventing facts."
        ),
        llm=llm,
        verbose=False,
    )

    quality_reviewer = Agent(
        role="Quality Reviewer",
        goal=(
            "Review the drafted response for accuracy, tone, "
            "and policy compliance, then produce the final response."
        ),
        backstory=(
            "You are a strict quality reviewer. You ensure the final "
            "answer is supported by the specialist findings."
        ),
        llm=llm,
        verbose=False,
    )

    draft_task = Task(
        description=f"""
Original customer query:
{query}

Specialist findings:
{context_text}

Create a customer-facing response based only on the information
provided by the specialist findings.
Do not invent facts.
""",
        expected_output="A clear customer-facing response.",
        agent=communications_specialist,
    )

    review_task = Task(
        description="""
Review the Communications Specialist's draft.

Check:
- factual accuracy
- clarity
- professional tone
- policy compliance
- whether unsupported claims were introduced

Return ONLY the final customer-facing response.
""",
        expected_output="The final reviewed customer-facing response.",
        agent=quality_reviewer,
        context=[draft_task],
    )

    crew = Crew(
        agents=[
            communications_specialist,
            quality_reviewer,
        ],
        tasks=[
            draft_task,
            review_task,
        ],
        process=Process.sequential,
        verbose=False,
    )

    result = crew.kickoff()

    return str(result.raw)