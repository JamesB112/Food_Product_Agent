from google.adk.agents import Agent, LoopAgent
from ..config import config
from ..agent_util import suppress_output_callback
from ..validation_checkers import ProductDataValidationChecker
from ..tools import openfoodfacts_lookup



product_researcher = Agent(
    model=config.researcher_model,
    name="product_researcher",
    description="Researches food product information using Open Food Facts API.",
    instruction="""
    You are a food product research specialist.

    When given a product name:
    1. Use the `openfoodfacts_lookup` tool Python function to fetch product info.
    2. Store the dictionary returned by the function in the `product_data` state key.
    3. Do NOT format, summarize, or add commentary.
    """,
    tools=[openfoodfacts_lookup],   # <-- NEW TOOL
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
