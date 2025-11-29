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
from ..agent_util import suppress_output_callback
from ..validation_checkers import HealthScoreValidationChecker


health_assessor = Agent(
    model=config.classifier_model,
    name="health_assessor",
    description="Calculates a health score based on NOVA classification and nutritional information.",
    instruction="""
    You are a nutrition expert who assesses the healthiness of food products.
    
    Your task:
    1. Read the product data from `product_data` state key
    2. Read the NOVA classification from `nova_classification` state key
    3. Calculate a health score (0-100) based on:
       - NOVA classification group (primary factor)
       - Nutritional content per 100g (sugar, saturated fat, salt, fiber, protein)
    
    Health Score Calculation Guidelines:
    - Start with base score from NOVA group:
      * Group 1: 90 points (unprocessed/minimally processed - excellent)
      * Group 2: 75 points (culinary ingredients - good)
      * Group 3: 60 points (processed - moderate)
      * Group 4: 30 points (ultra-processed - poor)
    
    - Adjust based on nutrients:
      * High sugar (>15g/100g): reduce 10-20 points
      * High saturated fat (>5g/100g): reduce 10-15 points
      * High salt (>500mg/100g): reduce 10-15 points
      * Good fiber (>3g/100g): add up to 15 points
      * Good protein (>5g/100g): add up to 10 points
    
    - Clamp final score to 0-100 range
    
    Provide an interpretation:
    - 80-100: "Excellent - Whole food, minimal processing"
    - 65-79: "Good - Moderately processed"
    - 50-64: "Fair - Processed food, consume in moderation"
    - 0-49: "Poor - Ultra-processed, limit consumption"
    
    Store your assessment in the `health_score` state key as a dictionary with:
    - health_score: number (0-100)
    - interpretation: string
    - breakdown: object with nutritional values per 100g
    
    Be objective and base your assessment on established nutritional guidelines.
    """,
    tools=[],
    output_key="health_score",
    after_agent_callback=suppress_output_callback,
)


robust_health_assessor = LoopAgent(
    name="robust_health_assessor",
    description="A robust health assessor that retries if assessment fails.",
    sub_agents=[
        health_assessor,
        HealthScoreValidationChecker(name="health_score_validation_checker"),
    ],
    max_iterations=2,
)