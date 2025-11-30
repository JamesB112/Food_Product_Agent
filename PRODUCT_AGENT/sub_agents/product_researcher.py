from google.adk.agents import Agent, LoopAgent
from ..config import config
from ..agent_util import suppress_output_callback
from ..validation_checkers import ProductDataValidationChecker
from ..sub_agents.google_search_agent import google_search_agent



product_researcher = Agent(
    model=config.researcher_model,
    name="product_researcher",
    description="Researches food product information using Google Search.",
    instruction="""
    You are a food product research specialist.

    When given a food product name:
    1. Use the google_search_agent sub agent to search for information about the product.
    2. Extract ALL returned fields exactly as the tool provides them.
    3. Store the raw dictionary returned by the google_search_agent sub agent in the `product_data` state key.
    4. Do NOT format, summarize, or explain the results.

    Output must be ONLY the dictionary returned by the tool.
    If the search fails or no results exist, store the error dictionary instead.
    """,
    sub_agents=[google_search_agent],   # <-- NEW TOOL
    output_key="product_data",
    after_agent_callback=suppress_output_callback,
)


robust_product_researcher = LoopAgent(
    name="robust_product_researcher",
    description="A robust product researcher that retries if lookup fails.",
    sub_agents=[
        product_researcher,
        ProductDataValidationChecker(name="product_data_validation_checker"),
    ],
    max_iterations=3,
)
