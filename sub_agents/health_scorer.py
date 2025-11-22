# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

from google.adk.agents import Agent, LoopAgent
from ..config import config
from ..agent_utils import suppress_output_callback
from ..tools import suggest_alternatives_tool, compute_scores_tool
from ..validation_checkers import AnalysisValidationChecker

# ------------------- Health Scorer / Alternatives Agent -------------------

health_scorer = Agent(
    model=config.worker_model,
    name="health_scorer",
    description="""
    Computes a product health score and optionally suggests healthier alternatives.
    Input: product_record and analysis dictionaries from previous agents.
    Output: extended analysis with 'alternatives' list and health recommendations.
    """,
    instruction="""
    You are an AI agent that:
    1. Uses the ingredient analysis to confirm health score and NOVA classification.
    2. Optionally finds healthier alternatives in the same category with lower sugar and salt.
    3. Outputs everything as a dictionary in `extended_analysis` state key with:
       - health_score
       - nova
       - breakdown
       - alternatives
       - tips
    """,
    tools=[suggest_alternatives_tool, compute_scores_tool],
    output_key="extended_analysis",
    after_agent_callback=suppress_output_callback,
)

# ------------------- Robust Health Scorer (Loop) -------------------

robust_health_scorer = LoopAgent(
    name="robust_health_scorer",
    description="Retries scoring and alternative suggestions until valid or max iterations reached.",
    sub_agents=[
        health_scorer,
        AnalysisValidationChecker(name="extended_analysis_validator"),
    ],
    max_iterations=config.max_search_iterations,
    after_agent_callback=suppress_output_callback,
)
