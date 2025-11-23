# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

from google.adk.agents import Agent, LoopAgent

from ..config import config
from ..agent_utils import suppress_output_callback
from ..validation_checkers import AnalysisValidationChecker
from ..tools import compute_simple_scores
 
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
    tools=[compute_simple_scores],
    output_key="analysis",
    after_agent_callback=suppress_output_callback,
)

# ------------------- Robust Ingredient Analyzer (Loop) -------------------
 
robust_ingredient_analyzer = LoopAgent(
    name="robust_ingredient_analyzer",
    description="Retries ingredient analysis until valid results are produced or max iterations reached.",
    sub_agents=[
        ingredient_analyzer,
        AnalysisValidationChecker(name="analysis_validation_checker"),
    ],
    max_iterations=3,
    after_agent_callback=suppress_output_callback,
)