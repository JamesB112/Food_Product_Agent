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

from typing import AsyncGenerator
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions


class ProductDataValidationChecker(BaseAgent):
    """Checks if product data has been successfully retrieved."""
    
    async def _run_async_impl(
        self, context: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        product_data = context.session.state.get("product_data")
        
        # Handle both string and dict responses
        has_valid_data = False
        if isinstance(product_data, dict):
            has_valid_data = product_data and not product_data.get("error")
        elif isinstance(product_data, str):
            # Agent returned string, try to parse it
            import json
            try:
                parsed = json.loads(product_data)
                has_valid_data = parsed and not parsed.get("error")
            except:
                # If not JSON, check if it's a non-empty string without "error"
                has_valid_data = product_data and "error" not in product_data.lower()
        
        if has_valid_data:
            yield Event(
                author=self.name,
                actions=EventActions(escalate=True),
            )
        else:
            yield Event(author=self.name)


class NovaClassificationValidationChecker(BaseAgent):
    """Checks if NOVA classification has been completed."""
    
    async def _run_async_impl(
        self, context: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        nova_classification = context.session.state.get("nova_classification")
        
        # Handle both string and dict responses
        has_valid_classification = False
        if isinstance(nova_classification, dict):
            has_valid_classification = nova_classification and nova_classification.get("nova_group")
        elif isinstance(nova_classification, str):
            # Agent returned string, accept it if non-empty
            has_valid_classification = bool(nova_classification and len(nova_classification) > 10)
        
        if has_valid_classification:
            yield Event(
                author=self.name,
                actions=EventActions(escalate=True),
            )
        else:
            yield Event(author=self.name)


class HealthScoreValidationChecker(BaseAgent):
    """Checks if health score has been calculated."""
    
    async def _run_async_impl(
        self, context: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        health_score = context.session.state.get("health_score")
        
        # Handle both string and dict responses
        has_valid_score = False
        if isinstance(health_score, dict):
            has_valid_score = health_score and "health_score" in health_score
        elif isinstance(health_score, str):
            # Agent returned string, accept it if non-empty
            has_valid_score = bool(health_score and len(health_score) > 10)
        
        if has_valid_score:
            yield Event(
                author=self.name,
                actions=EventActions(escalate=True),
            )
        else:
            yield Event(author=self.name)


class AlternativesValidationChecker(BaseAgent):
    """Checks if alternative products have been found."""
    
    async def _run_async_impl(
        self, context: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        alternatives = context.session.state.get("alternatives")
        
        # Escalate even if no alternatives found, as this completes the workflow
        if alternatives is not None:
            yield Event(
                author=self.name,
                actions=EventActions(escalate=True),
            )
        else:
            yield Event(author=self.name)