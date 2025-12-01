from google.adk.agents import Agent, LoopAgent
from ..config import config
from ..agent_util import suppress_output_callback
from ..validation_checkers import ProductDataValidationChecker
from ..tools import google_search_product



product_researcher = Agent(
    model=config.researcher_model,
    name="product_researcher",
    description="Researches food product ingredients, nutrition (per 100g), and allergen information using Google Search.",
    instruction="""
    You are a food product research specialist.

    When given a product name:
    1. Use the `google_search_product` tool to search for detailed product information on Google.
    2. Extract and structure the following information:
       - Product name and brand
       - Complete ingredients list
       - Nutritional information per 100g (energy, protein, carbohydrates, sugars, fat, saturated fat, fiber, sodium/salt)
       - Allergen information (specifically "Gluten free" status and "Traces of nuts" or similar warnings)
    3. Store the extracted data as a structured dictionary in the `product_data` state key.
    4. Prioritize official product pages, manufacturer websites, and verified retailer sites.
    5. If information is missing, clearly indicate which fields could not be found.
    6. Do NOT add commentary outside the structured data.
    """,
    tools=[google_search_product],
    output_key="product_data",
    after_agent_callback=suppress_output_callback,
)


robust_product_researcher = LoopAgent(
    name="robust_product_researcher",
    description="A robust product researcher that retries if ingredient, nutrition, or allergen lookup fails.",
    sub_agents=[
        product_researcher,
        ProductDataValidationChecker(name="product_data_validation_checker"),
    ],
    max_iterations=3,
)