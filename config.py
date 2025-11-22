# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

import os
from dataclasses import dataclass
import google.auth

# Resolve project and ensure Vertex AI is used
_, project_id = google.auth.default()
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", project_id)
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "global")
os.environ.setdefault("GOOGLE_GENAI_USE_VERTEXAI", "True")

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
