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
from ..tools import alternative_finder_tool
from ..agent_util import suppress_output_callback
from ..validation_checkers import AlternativesValidationChecker


alternative_finder = Agent(
    model=config.alternative_model,
    name="alternative_finder",
    description="Finds healthier alternative products in the same food category.",
    instruction="""
    You are a nutrition expert finding healthier food alternatives.
    
    Your task:
    1. Read product_data, nova_classification, and health_score from state
    2. If NOVA Group 3 or 4, use suggest_alternatives tool to find healthier options
    3. If NOVA Group 1 or 2, note that it's already minimally processed
    4. IMPORTANT: Output ONLY a JSON dictionary with these exact keys:
       - alternatives: list of objects with name, brand, nova_group, reason
       - message: optional string if no alternatives needed
    
    Do NOT add additional text. Output only the JSON dictionary.
    Store this in the `alternatives` state key.
    """,
    tools=[alternative_finder_tool],
    output_key="alternatives",
    after_agent_callback=suppress_output_callback,
)


robust_alternative_finder = LoopAgent(
    name="robust_alternative_finder",
    description="A robust alternative finder that retries if search fails.",
    sub_agents=[
        alternative_finder,
        AlternativesValidationChecker(name="alternatives_validation_checker"),
    ],
    max_iterations=2,
)