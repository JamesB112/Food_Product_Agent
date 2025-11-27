# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

from google.adk.agents import Agent

from .config import config


# ---------------------------------------------------------------------
# Ingredient / Health Analysis Validation Checker
# ---------------------------------------------------------------------

class AnalysisValidationChecker(Agent):
    """
    ADK-compatible validation agent for analysis results.
    Ensures health_score and nova classification exist.
    """

    def __init__(self, name: str = "analysis_validation_checker"):
        super().__init__(
            name=name,
            model=config.validator_model,
            description="Validates the health and ingredient analysis output.",
            instruction="""
You are a validation agent.

Inspect the `analysis` object in state and determine whether analysis contains:
- health_score
- nova   (NOVA classification)

Rules:

1. If analysis is missing → output: "No analysis found."
2. If health_score is missing → output: "Missing health_score."
3. If nova is missing → output: "Missing NOVA classification."
4. If all required fields exist → output exactly: "valid"

Your output must be:
- "valid"
- or a one-sentence error message.
""",
            output_key="validation_result",
        )
