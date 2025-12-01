import os
from dataclasses import dataclass

# ============================================================================
# IMPORTANT: ADD GOOGLE API KEY
# ============================================================================

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
os.environ["GOOGLE_API_KEY"] = ""  # Replace with your actual API key

# ============================================================================


@dataclass
class FoodHealthConfiguration:
    """Configuration for food health analysis models and parameters.
    
    Attributes:
        main_agent_model (str): Model for main orchestration tasks.
        researcher_model (str): Model for product research tasks.
        classifier_model (str): Model for NOVA classification tasks.
        alternative_model (str): Model for finding alternatives.
        max_search_results (int): Maximum search results to process.
        max_alternatives (int): Maximum number of alternatives to suggest.
        temperature (float): Generation temperature for responses.
    """
    main_agent_model: str = "gemini-2.5-pro"
    researcher_model: str = "gemini-2.5-flash"
    classifier_model: str = "gemini-2.5-flash"
    alternative_model: str = "gemini-2.5-flash"
    search_model: str = "gemini-2.5-flash"
    max_search_results: int = 5
    max_alternatives: int = 3
    temperature: float = 0.7


# NOVA Classification criteria
NOVA_CRITERIA = {
    "group_1": {
        "name": "Unprocessed or Minimally Processed Foods",
        "description": "Natural foods with no or minimal processing",
        "indicators": [
            "Fresh fruits and vegetables",
            "Grains, legumes, nuts, seeds",
            "Fresh or frozen meat, fish, eggs",
            "Milk with no additives",
            "Natural herbs and spices"
        ],
        "exclusions": ["Added sugar", "Added oils", "Added salt (beyond minimal)"]
    },
    "group_2": {
        "name": "Processed Culinary Ingredients",
        "description": "Substances extracted from Group 1 foods or from nature",
        "indicators": [
            "Oils, butter, lard",
            "Sugar, salt",
            "Vinegar",
            "Honey, maple syrup"
        ],
        "usage": "Used in combination with Group 1 foods for cooking"
    },
    "group_3": {
        "name": "Processed Foods",
        "description": "Foods made by adding Group 2 ingredients to Group 1 foods",
        "indicators": [
            "Canned vegetables with salt",
            "Canned fish in oil",
            "Cheeses",
            "Freshly made bread",
            "Salted or sugared nuts"
        ],
        "characteristics": "2-3 ingredients, recognizable as modified Group 1 foods"
    },
    "group_4": {
        "name": "Ultra-Processed Foods",
        "description": "Industrial formulations with 5+ ingredients",
        "indicators": [
            "Hydrogenated oils",
            "High-fructose corn syrup",
            "Flavor enhancers (MSG, etc.)",
            "Emulsifiers",
            "Colorants and dyes",
            "Sweeteners (aspartame, sucralose, etc.)",
            "Preservatives (sodium benzoate, etc.)"
        ],
        "examples": [
            "Soft drinks and energy drinks",
            "Sweet or savory packaged snacks",
            "Reconstituted meat products",
            "Pre-prepared frozen dishes",
            "Instant noodles and soups"
        ]
    }
}


config = FoodHealthConfiguration()