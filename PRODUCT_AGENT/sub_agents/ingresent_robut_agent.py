from google.adk.agents import LoopAgent
from ..agent_utils import suppress_output_callback
from .ingredient_master import Food_Ingredient_Analiser

robust_ingredient_analyzer = LoopAgent(
    name="robust_ingredient_analyzer",
    description="Retries ingredient analysis until results validate.",
    sub_agents=[Food_Ingredient_Analiser],   # ✔ use sub_agents list
    max_iterations=3,
    after_agent_callback=suppress_output_callback,
)
