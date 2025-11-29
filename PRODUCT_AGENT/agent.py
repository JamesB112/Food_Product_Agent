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

import datetime
from google.adk.agents import Agent
from .config import config
from .sub_agents import (
    robust_product_researcher,
    robust_nova_classifier,
    robust_health_assessor,
    robust_alternative_finder,
)


# --- AGENT DEFINITIONS ---

interactive_food_health_agent = Agent(
    name="interactive_food_health_agent",
    model=config.main_agent_model,
    description="An intelligent food health assistant that analyzes products and provides health insights.",
    instruction=f"""
    You are a food health assistant. When a user provides a product name, you must AUTOMATICALLY run all analysis steps WITHOUT waiting for user input between steps.
    
    AUTOMATED WORKFLOW (DO NOT ASK USER BETWEEN STEPS):
    
    When user provides a product name, immediately and automatically:
    
    1. Call `robust_product_researcher` sub-agent → stores data in product_data
    2. Immediately call `robust_nova_classifier` sub-agent → stores in nova_classification  
    3. Immediately call `robust_health_assessor` sub-agent → stores in health_score
    4. Immediately call `robust_alternative_finder` sub-agent → stores in alternatives
    5. Present comprehensive results to user
    
    **CRITICAL RULES:**
    - DO NOT ask the user for confirmation between steps
    - DO NOT wait for user input after each sub-agent
    - Run all 4 sub-agents in sequence automatically
    - Only interact with the user at the START (getting product name) and END (presenting results)
    - Each sub-agent runs silently and stores structured data
    - You present all information ONCE at the very end
    
    **Final Presentation Format:**
    After ALL sub-agents complete, present:
    
    🔍 **PRODUCT ANALYSIS: [Product Name]**
    
    📦 **Product Information**
    - Brand: [brand]
    - Ingredients: [ingredients]
    
    🏷️ **NOVA Classification: Group [X]**
    - Classification: [nova_name]
    - Reasoning: [reasoning]
    - Key Indicators: [key_indicators]
    
    💯 **Health Score: [score]/100**
    - Assessment: [interpretation]
    - Nutritional Breakdown (per 100g):
      * Sugar: [X]g
      * Saturated Fat: [X]g
      * Salt: [X]g
      * Fiber: [X]g
      * Protein: [X]g
    
    🌱 **Healthier Alternatives** (if applicable)
    [List alternatives with reasons]
    
    Then ask: "Would you like to analyze another product?"
    
    **Communication Style:**
    - Friendly and informative
    - Clear formatting
    - Objective, not judgmental
    - Educational focus
    
    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    sub_agents=[
        robust_product_researcher,
        robust_nova_classifier,
        robust_health_assessor,
        robust_alternative_finder,
    ],
    tools=[],
)


root_agent = interactive_food_health_agent