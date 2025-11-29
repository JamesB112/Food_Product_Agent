# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent, LoopAgent
from ..config import config
from ..tools import product_lookup_tool
from ..agent_util import suppress_output_callback
from ..validation_checkers import ProductDataValidationChecker


product_researcher = Agent(
    model=config.researcher_model,
    name="product_researcher",
    description="Researches food product information using Open Food Facts database.",
    instruction="""
    You are a food product research specialist. Your task is to look up comprehensive information about food products.
    
    When given a product name:
    1. Use the openfoodfacts_lookup tool to search for the product
    2. Extract all available information from the tool response
    3. IMPORTANT: Store the raw dictionary data directly in the `product_data` state key
    4. Do NOT format or present the information to the user yet - just store it
    
    The tool will return a dictionary with:
    - product_name, brand, ingredients, nutrients, nova_group, allergens, additives, categories
    
    Your output should be ONLY the dictionary returned by the tool, stored in product_data state key.
    Do not add any commentary or formatting - the main agent will handle presentation.
    
    If the product is not found or there's an error, store the error dictionary in product_data.
    """,
    tools=[product_lookup_tool],
    output_key="product_data",
    after_agent_callback=suppress_output_callback,
)


robust_product_researcher = LoopAgent(
    name="robust_product_researcher",
    description="A robust product researcher that retries if lookup fails.",
    sub_agents=[
        product_researcher,
        ProductDataValidationChecker(name="product_data_validation_checker"),
    ],
    max_iterations=3,
)