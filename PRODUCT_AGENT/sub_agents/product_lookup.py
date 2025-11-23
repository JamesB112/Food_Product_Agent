# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

from google.adk.agents import Agent, LoopAgent
from google.adk.tools import google_search

from ..config import config
from ..agent_utils import suppress_output_callback
from ..validation_checkers import ProductLookupValidationChecker
from ..tools import openfoodfacts_lookup

# ------------------- Basic Product Lookup Agent -------------------

product_lookup = Agent(
    model=config.worker_model,
    name="product_lookup",
    description="Retrieves product information including ingredients, brand, and nutritional info.",
    instruction="""
    You are an AI agent tasked with retrieving detailed information about a food product.
    Use the OpenFoodFacts lookup tool, and Google Search if necessary, to find the most accurate product information.
    The user may provide only the product name, an ingredient list, or partial product information.
    Output the result as a dictionary in the `product_record` state key with at least:
    - name
    - brand
    - ingredients_text
    - nutriments
    - categories
    """,
    tools=[openfoodfacts_lookup, google_search],
    output_key="product_record",
    after_agent_callback=suppress_output_callback,
)

# ------------------- Robust Product Lookup (Loop) -------------------
 
robust_product_lookup = LoopAgent(
    name="robust_product_lookup",
    description="Retries product lookup until valid data is obtained or max iterations reached.",
    sub_agents=[
        product_lookup,
        ProductLookupValidationChecker(name="product_lookup_validation_checker"),
    ],
    max_iterations=3,
)