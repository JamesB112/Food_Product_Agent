# google_search_agent.py
#
# A dedicated ADK agent that wraps Google Search as a standalone tool.
# This bypasses the ADK restriction that Google Search cannot be mixed
# with other tools in Gemini 1.x agents.

from google.adk.agents import Agent
from google.adk.tools import google_search

from ..config import config
from ..agent_utils import suppress_output_callback


# -------------------------------------------------------------
# Google Search Agent
# -------------------------------------------------------------

google_search_agent = Agent(
    name="google_search_agent",
    description=(
        "Uses the Google Search tool to retrieve public information about "
        "food products, brands, ingredients, or general facts. "
        "This agent MUST contain only the google_search tool due to Gemini 1.x constraints."
    ),
    instruction="""
    You are an AI agent that performs Google Search queries.
    Use the `google_search` tool to look up factual information.
    Always return structured results containing the search findings.
    """,
    
    # IMPORTANT: google_search must be the ONLY tool
    tools=[google_search],

    # Use whichever worker model you're using for functional agents
    model=config.worker_model,

    # Optional: where the agent stores its output in the state graph
    output_key="google_search_results",

    # Prevent messy LLM chatter leaking into your main pipeline
    after_agent_callback=suppress_output_callback,
)
