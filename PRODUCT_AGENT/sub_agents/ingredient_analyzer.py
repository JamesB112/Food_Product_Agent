from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from ..config import config
from ..agent_utils import suppress_output_callback
from ..tools import compute_simple_scores

# ------------------- Ingredient Normalizer -------------------
ingredient_normalizer = Agent(
    model=config.worker_model,
    name="ingredient_normalizer",
    description="Normalizes ingredient text.",
    instruction="""
    Normalize the ingredient list:
    - Fix casing & spelling
    - Expand E-numbers
    - Translate to English
    - Split compound ingredients

    OUTPUT:
    {
        "normalized_ingredients": [...]
    }
    """,
    tools=[],
    output_key="normalized_ingredients",
    after_agent_callback=suppress_output_callback,
)

# ------------------- Additive & Processing Detector -------------------
processing_detector = Agent(
    model=config.worker_model,
    name="processing_detector",
    description="Detects additives and industrial processing indicators.",
    instruction="""
    OUTPUT:
    {
        "detected_additives": [...],
        "processing_indicators": [...],
        "all_signals": [...]
    }
    """,
    tools=[],
    output_key="processing_signals",
    after_agent_callback=suppress_output_callback,
)

# ------------------- NOVA Classifier -------------------
nova_classifier = Agent(
    model=config.worker_model,
    name="nova_classifier",
    description="Classifies food using NOVA 1–4.",
    instruction="""
    OUTPUT:
    {
        "nova": 1-4,
        "confidence": 0-1,
        "reasoning": "..."
    }
    """,
    tools=[],
    output_key="nova_result",
    after_agent_callback=suppress_output_callback,
)

# ------------------- Health Scorer -------------------
health_scorer = Agent(
    model=config.worker_model,
    name="health_scorer",
    description="Computes the final health score.",
    instruction="""
    Use compute_simple_scores to calculate:
    - health_score
    - macro breakdown per 100g
    - include NOVA class
    """,
    tools=[FunctionTool(compute_simple_scores)],
    output_key="analysis",
    after_agent_callback=suppress_output_callback,
) 
