# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

from google.adk.agents import LoopAgent, LlmAgent 
from google.adk.tools.tool_context import ToolContext

 
from ..config import config
from ..tools import openfoodfacts_lookup
from .google_search_agent import google_search_agent
from google.adk.tools import FunctionTool

# ------------------- Basic Product Lookup Agent -------------------

def exit_loop(tool_context: ToolContext):
    """Call this to stop the LoopAgent iteration."""
    # Store final product in state
    tool_context.state['final_product_record'] = tool_context.state['product_record']
    print(f"[Tool Call] exit_loop triggered by {tool_context.agent_name}")
    tool_context.actions.escalate = True
    return {}


product_lookup_agent = LlmAgent(
    name="ProductLookup",
    model=config.worker_model,
    include_contents="none",
    tools=[FunctionTool(openfoodfacts_lookup)],
    sub_agents=[google_search_agent],  # optional: extra fallback
    instruction="""
You are a product lookup agent. You must populate a `product_record`.

You have access to:
- openfoodfacts_lookup() tool
- google_search_agent (sub-agent)

State Variables:
- product_query: the user's text input
- lookup_attempt: integer count of the loop iteration (1,2,3...)

Behavior:
1. If lookup_attempt == 1:
   - Use openfoodfacts_lookup() first.
2. If lookup_attempt > 1:
   - Use google search (via google_search_agent).

Regardless of method, output ONLY JSON for `product_record`:

{
  "name": "...",
  "brand": "...",
  "ingredients_text": "...",
  "nutriments": {...},
  "categories": "...",
  "source": "openfoodfacts" or "google" or "none"
}

If no data found, return empty fields so the validator will retry.
""",
    description="Primary lookup agent that performs product API or Google-based search depending on loop iteration.",
    output_key="product_record"
)

# ------------------- Validation Agent -------------------
 
validation_agent = LlmAgent(
    name="ProductValidation",
    model=config.validator_model,
    include_contents="none",
    instruction="""
You validate a `product_record`.

A valid record must have:
- name (non-empty)
- ingredients_text (optional)
- nutriments (optional)

If valid:
- Output exactly: "VALID"

If invalid:
- Output a short error message explaining the problem.
""",
    description="Validates the product record.",
    output_key="validation_result"
)

# ------------------- Gatekeeper Agent (Stop or Retry) -------------------

validation_gate_agent = LlmAgent(
    name="ValidationGate",
    model=config.validator_model,
    include_contents="none",
    tools=[exit_loop],
    instruction="""
You examine the validation_result:

validation_result: {validation_result}
product_record: {product_record}

Rules:
1. If validation_result == "VALID":
    - Copy the current product_record to the output state so the parent agent can access it.
    - Call the 'exit_loop' tool. Do not output any text.
2. If validation_result != "VALID":
    - Output exactly the word "CONTINUE" to signal the LoopAgent to retry.
""",
    description="Exits the loop if the product is valid."
)

# ------------------- The LoopAgent -------------------

robust_product_lookup = LoopAgent(
    name="robust_product_lookup",
    sub_agents=[
        product_lookup_agent,
        validation_agent,
        validation_gate_agent
    ],
    max_iterations=3
)
