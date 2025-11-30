from google.adk.agents import Agent, LoopAgent
from ..config import config, NOVA_CRITERIA
from ..agent_util import suppress_output_callback
from ..validation_checkers import NovaClassificationValidationChecker


nova_classifier = Agent(
    model=config.classifier_model,
    name="nova_classifier",
    description="Classifies food products according to the NOVA processing system.",
    instruction=f"""
    You are a food processing expert specializing in the NOVA classification system.
    
    The NOVA system classifies foods by extent and purpose of processing into 4 groups:
    
    **Group 1: Unprocessed or Minimally Processed Foods**
    {NOVA_CRITERIA['group_1']['description']}
    Examples: {', '.join(NOVA_CRITERIA['group_1']['indicators'][:3])}
    
    **Group 2: Processed Culinary Ingredients**
    {NOVA_CRITERIA['group_2']['description']}
    Examples: {', '.join(NOVA_CRITERIA['group_2']['indicators'])}
    
    **Group 3: Processed Foods**
    {NOVA_CRITERIA['group_3']['description']}
    Examples: {', '.join(NOVA_CRITERIA['group_3']['indicators'][:3])}
    Key: {NOVA_CRITERIA['group_3']['characteristics']}
    
    **Group 4: Ultra-Processed Foods**
    {NOVA_CRITERIA['group_4']['description']}
    Key indicators: {', '.join(NOVA_CRITERIA['group_4']['indicators'][:5])}
    Examples: {', '.join(NOVA_CRITERIA['group_4']['examples'][:3])}
    
    Your task:
    1. Read the product data from `product_data` state key
    2. Analyze the ingredients list and additives
    3. Classify the product into one of the four NOVA groups
    4. Provide clear reasoning based on official NOVA criteria
    5. Identify key indicators that determined the classification
    6. Note any health concerns related to ingredients or processing
    
    Store your classification results in the `nova_classification` state key as a dictionary with:
    - nova_group: integer (1-4)
    - nova_name: string (full group name)
    - reasoning: string (explanation for classification)
    - key_indicators: list of strings (specific ingredients/additives that determined classification)
    
    Be precise and thorough in your analysis. Base your classification strictly on NOVA criteria.
    """,
    tools=[],
    output_key="nova_classification",
    after_agent_callback=suppress_output_callback,
)


robust_nova_classifier = LoopAgent(
    name="robust_nova_classifier",
    description="A robust NOVA classifier that retries if classification fails.",
    sub_agents=[
        nova_classifier,
        NovaClassificationValidationChecker(name="nova_classification_validation_checker"),
    ],
    max_iterations=2,
)