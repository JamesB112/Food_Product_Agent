from google.adk.agents import Agent
from ..tools import google_search_tool

from ..config import config
from ..agent_util import suppress_output_callback


# -------------------------------------------------------------
# Google Search Agent (Wikipedia-filtered)
# -------------------------------------------------------------

google_search_agent = Agent(
    name="google_search_agent",
    description=(
        "Uses the Google Search tool to retrieve public information about "
        "food products, brands, ingredients, or general facts. "
        "This agent MUST contain only the google_search tool due to Gemini 1.x constraints."
    ),
    instruction="""
    You are a search agent that retrieves factual information through the `google_search` tool only.

    YOUR RULES:
    1. ALWAYS perform a google_search tool call using the user query.
    2. NEVER generate your own knowledge — rely solely on tool results.
    3. ALWAYS filter out Wikipedia results completely.
       - Exclude any result whose URL contains "wikipedia.org".
       - Do NOT quote, summarize, reference, or rely on Wikipedia content.
    4. Produce output ONLY as a structured JSON dictionary of the filtered results:
       {
         "query": "...",
         "results": [...],   # after wikipedia filtering
         "source_count": N
       }
    5. Do NOT add commentary or prose.
    6. Do NOT fabricate missing data.

    If all results are filtered out (e.g., all were Wikipedia),
    return:
       {"query": "<user query>", "results": [], "error": "no_non_wikipedia_results"}
    """,

    tools=[google_search_tool],         # REQUIRED: only one tool allowed
    model=config.researcher_model,     # small worker or function-call model
    output_key="google_search_results",
    after_agent_callback=suppress_output_callback,
)
