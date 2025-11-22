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

import os
from dataclasses import dataclass
from dotenv import load_dotenv

# ===============================
# Load environment variables
# ===============================
load_dotenv()  # Loads variables from .env file if present

# ===============================
# Google AI Studio API Key
# ===============================
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not GOOGLE_API_KEY:
    raise RuntimeError(
        "❌ Missing GOOGLE_API_KEY environment variable.\n"
        "Set it before running your agent, for example:\n"
        "   export GOOGLE_API_KEY='your-key-here'   (macOS/Linux)\n"
        "   setx GOOGLE_API_KEY \"your-key-here\"    (Windows)\n"
        "Or create a .env file in your project root with:\n"
        "   GOOGLE_API_KEY=your-key-here"
    )

# ===============================
# Agent configuration
# ===============================
@dataclass
class ResearchConfiguration:
    """
    Configuration for Food Health Advisor Agent.
    - worker_model: fast/light model for background processing
    - final_message_model: high-quality model for user-facing messages
    - critic_model: optional model for validation / scoring
    """
    worker_model: str = "gemini-2.5-flash-lite"
    final_message_model: str = "gemini-2.5-pro"
    critic_model: str = "gemini-2.5-pro"
    max_search_iterations: int = 5

config = ResearchConfiguration()

