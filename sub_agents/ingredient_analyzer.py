# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

from google.adk.agents import Agent, LoopAgent
from config import config
from agent_utils import suppress_output_callback
from validation_checkers import AnalysisValidationChecker
from tools import compute_scores_tool
from google.adk.tools import FunctionTool

# ------------------- Basic Ingredient Analyzer Agent -------------------

ingredient_analyzer = Agent(
    model=config.worker_model,
    name="ingredient_analyzer",
    description="Analyzes ingredients and computes a health score along with NOVA classification.",
    instruction="""
    You are an AI agent tasked with analyzing a product's ingredients and nutritional information.
    Compute a health_score (0–100), determine the NOVA classification (1–4), and provide a breakdown of sugar, saturated fat, salt, fiber, and protein per 100g.
    Output the result as a dictionary in the `analysis` state key.
    """,
    tools=[compute_scores_tool],
    output_key="analysis",
    after_agent_callback=suppress_output_callback,
)

# ------------------- Robust Ingredient Analyzer (Loop) -------------------

from sub_agents.ingredient_analyzer import ingredient_analyzer
from validation_checkers import AnalysisValidationChecker

ingredient_analysis_validator_agent = Agent(
    name="ingredient_analysis_validator_agent",
    model=config.worker_model,
    instruction="""
    Validate that ingredient analysis produced health_score and nova classification.
    Access state['analysis'].
    Set state['validation_passed'] = True if valid, else False.
    """,
    tools=[],
    output_key="validation_passed",
    after_agent_callback=lambda agent, state: AnalysisValidationChecker().validate(state)
)

robust_ingredient_analyzer = LoopAgent(
    name="robust_ingredient_analyzer",
    description="Retries ingredient analysis until valid results are produced or max iterations reached.",
    sub_agents=[ingredient_analyzer, ingredient_analysis_validator_agent],
    max_iterations=config.max_search_iterations,
    after_agent_callback=suppress_output_callback,
)
