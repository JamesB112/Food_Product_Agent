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

from typing import Any

def suppress_output_callback(agent_result: Any):
    """
    Simple after-agent callback that suppresses verbose tool output
    for a cleaner interactive UX. 
    Can be extended to log outputs if needed.
    """
    return None
