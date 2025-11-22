# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

from google.adk.agents import Agent, LoopAgent
from config import config
from agent_utils import suppress_output_callback
from tools import compute_scores_tool
from validation_checkers import AnalysisValidationChecker
from google.adk.tools import FunctionTool

# ------------------- Final Message Agent -------------------

final_message_agent = Agent(
    model=config.final_message_model,
    name="final_message_agent",
    description="""
    Generates a polished, user-friendly health report based on structured analysis.
    Takes extended_analysis from previous agents and produces:
    1. Friendly, conversational explanation
    2. Structured Markdown / JSON report for UI rendering
    """,
    instruction="""
    You are a nutrition assistant. Your job is to create a user-friendly explanation of the product's health profile.
    Input: `extended_analysis` dictionary with keys:
      - health_score
      - nova
      - breakdown
      - alternatives
      - tips
    Produce two outputs:
      1. friendly_message: clear, empathetic explanation for the user
      2. structured_report: Markdown or JSON version suitable for UI rendering
    Output both under the `final_output` state key.
    """,
    output_key="final_output",
    after_agent_callback=suppress_output_callback,
)

# ------------------- Robust Final Message Agent -------------------

final_message_validator_agent = Agent(
    name="final_message_validator_agent",
    model=config.worker_model,
    instruction="""
    Validate that the final message is complete and user-ready.
    Access state['final_message'].
    Set state['validation_passed'] = True if valid, else False.
    """,
    tools=[],
    output_key="validation_passed",
    after_agent_callback=lambda agent, state: AnalysisValidationChecker().validate(state)
)

robust_final_message_agent = LoopAgent(
    name="robust_final_message_agent",
    description="Ensures final message output is valid and user-ready.",
    sub_agents=[final_message_agent, final_message_validator_agent],
    max_iterations=config.max_search_iterations,
    after_agent_callback=suppress_output_callback,
)
