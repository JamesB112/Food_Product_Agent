# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

import datetime
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from google.adk.tools import transfer_to_agent

from .config import config
from .sub_agents import (
    robust_product_lookup,
    robust_ingredient_analyzer,
    robust_final_message_agent
)
from .tools import openfoodfacts_lookup, compute_simple_scores, suggest_alternatives
from .agent_utils import suppress_output_callback

# ------------------- Root Interactive Food Health Agent -------------------

interactive_food_health_agent = Agent(
    name="interactive_food_health_agent",
    model=config.final_message_model,  # Main agent uses Pro for user-facing output
    description="""
    This agent helps users understand the health profile of a food product.
    Workflow:
    1. Accepts a product name, ingredient list, or ingredient-related questions.
    2. Uses sub-agents to retrieve product info, analyze ingredients, and format a draft final message.
    3. Optionally finds healthier alternatives.
    4. Generates a polished response with structured and friendly output.
    """,
    instruction=f"""
    You are Agent NutriGuide. Your goal is to help the user understand the health profile of a food product. Follow these rules carefully:

    1. Use the sub-agent `robust_product_lookup` to retrieve accurate product information.
    - Input: `product_query` (user's text input)
    - Output: `final_product_record` (contains name, brand, ingredients_text, nutriments, categories, source)
    - Do not attempt to generate product information yourself; rely solely on this sub-agent.

    2. Use the sub-agent `robust_ingredient_analyzer` to analyze the ingredients of the product.
    - Input: the `product_record` from the previous step.
    - Output: `ingredient_analysis` (health scores, potential concerns, and nutrient insights)
    - Only use the output provided by this sub-agent.

    3. Use the sub-agent `robust_final_message_agent` to generate a user-friendly final message.
    - Input: both `product_record` and `ingredient_analysis`.
    - Output: a polished response with structured and friendly language suitable for the user.
    - Do not add any information that was not included in the previous sub-agents’ outputs.

    Rules for all steps:
    - Do not hallucinate or call any tools that are not explicitly listed as sub-agents.
    - Do not generate outputs outside of the prescribed fields for each sub-agent.
    - Maintain a clear and friendly tone suitable for user-facing responses.
    - Use the outputs of sub-agents exactly as they are; do not alter the data.
    - Current date: {datetime.datetime.now().strftime('%Y-%m-%d')}
    """,
    sub_agents=[
        robust_product_lookup,
        robust_ingredient_analyzer,
        robust_final_message_agent,
    ],
    # tools=[
    #     FunctionTool(openfoodfacts_lookup),
    #     FunctionTool(compute_simple_scores),
    #     FunctionTool(suggest_alternatives)
    # ],
    output_key="final_output",
    after_agent_callback=suppress_output_callback,  # make sure callback accepts *args, **kwargs
)

# ------------------- Root Reference -------------------

root_agent = interactive_food_health_agent
