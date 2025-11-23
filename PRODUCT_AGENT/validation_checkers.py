# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

from google.adk.agents import Agent

from .config import config


# ---------------------------------------------------------------------
# Product Lookup Validation Checker
# ---------------------------------------------------------------------

class ProductLookupValidationChecker(Agent):
    """
    ADK-compatible validation agent for product lookup.
    Ensures product_record contains required fields.
    """

    def __init__(self, name: str = "product_lookup_validation_checker"):
        super().__init__(
            name=name,
            model=config.validator_model,    # or config.worker_model if you prefer
            description="Validates the product_record returned by product_lookup.",
            instruction="""
You are a validation agent.

Your task is to inspect the `product_record` in state and determine if it is valid.

A valid product_record MUST include:
- name (non-empty)
- ingredients_text (optional, but warn if missing)
- nutriments (optional, but warn if missing)

Rules:

1. If product_record is missing entirely → output: "No product_record provided."
2. If name is missing or empty → output: "Missing product name."
3. If all required fields are present → output exactly: "valid"

Your output MUST be either:
- "valid"
- or a short error message string

Do NOT output JSON. Do not wrap in code blocks.
""",
            output_key="validation_result",
        )


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
