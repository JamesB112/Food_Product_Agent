# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

import datetime
from google.adk.agents import Agent
from google.adk.tools import FunctionTool

from .config import config
from .sub_agents import (
    robust_product_lookup,
    robust_ingredient_analyzer,
    robust_health_scorer,
    robust_final_message_agent,
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
    2. Uses sub-agents to retrieve product info, analyze ingredients, and compute health scores.
    3. Optionally finds healthier alternatives.
    4. Generates a polished response with structured and friendly output.
    """,
    instruction=f"""
    You are a friendly nutrition assistant named Agent NutriGuide.
    Use only the tools explicitly listed below. Do NOT invent new tools.
    Current date: {datetime.datetime.now().strftime('%Y-%m-%d')}
    
    Available tools:
    - openfoodfacts_lookup
    - compute_simple_scores
    - suggest_alternatives
    
    Guidelines:
    - Only call these tools exactly as named.
    - Always provide user-friendly explanations.
    - Do not hallucinate additional functions.
    """,
    sub_agents=[
        robust_product_lookup,
        robust_ingredient_analyzer,
        robust_health_scorer,
        robust_final_message_agent,
    ],
    tools=[
        FunctionTool(openfoodfacts_lookup),
        FunctionTool(compute_simple_scores),
        FunctionTool(suggest_alternatives)
    ],
    output_key="final_output",
    after_agent_callback=suppress_output_callback,  # make sure callback accepts *args, **kwargs
)

# ------------------- Root Reference -------------------

root_agent = interactive_food_health_agent
