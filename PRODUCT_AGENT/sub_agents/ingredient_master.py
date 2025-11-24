from google.adk.agents import SequentialAgent

from .ingredient_analyzer import (
    ingredient_normalizer,
    processing_detector,
    nova_classifier,
    health_scorer,
)

# ingredient_master.py

from google.adk.agents import SequentialAgent
from .ingredient_analyzer import (
    ingredient_normalizer,
    processing_detector,
    nova_classifier,
    health_scorer,
)

Food_Ingredient_Analiser = SequentialAgent(
    name="food_ingredient_analyser",
    description="Orchestrates ingredient normalization, processing detection, NOVA classification, and health scoring.",
    sub_agents=[
        ingredient_normalizer,
        processing_detector,
        nova_classifier,
        health_scorer,
    ],
)
