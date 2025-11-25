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
    You are Agent NutriGuide. When analyzing a product:

    1. Call `robust_product_lookup` to fetch product info.
    2. Call `robust_ingredient_analyzer` to analyze ingredients and get health scores.
    3. Call `robust_final_message_agent` to generate a user-friendly final message.

    Use only the outputs of these agents. Do not hallucinate additional tools.
    Current date: {datetime.datetime.now().strftime('%Y-%m-%d')}
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
