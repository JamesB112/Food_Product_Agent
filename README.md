# Food Product Health Agent

This project implements a multi-agent system for analyzing food products using the Google Agent Development Kit (ADK). The system automatically retrieves product information, classifies products according to NOVA processing levels, computes a health score, and suggests healthier alternatives.

---

## Project Overview

Consumers often struggle to understand the nutritional quality and health implications of food products. Manual research is time-consuming, inconsistent, and difficult to scale when comparing multiple products or exploring ingredients in depth.

In Australia, a health star rating system does exists to provide a high level ranking of a products "healthiness", however is not widely adopted, and experts say is based on a flawed formula, which manufactors can easlially explit to make their products seem healthy, where in reality they are not (https://www.sbs.com.au/news/article/health-star-rating-system-changes-criticism/g2el9r52i).

To address this issue, I have developed a draft AI Agent, which despite having a lot more work to get it production ready, addesses this issue, by giving propoer advice to consumers.

The Food Product Health Agent automates this workflow. It combines a Wikipedia-filtered Google Search tool with specialized sub-agents to provide structured, actionable insights on food products.

![Architecture](./flowchart.png "Optional Title")

---

## Agent Architecture

The **interactive_food_health_agent** orchestrates all sub-agents and tools. Its workflow is fully automated, requiring user input only at the beginning (product name) and at the end (presenting results).

### Sub-Agents

**1. Product Researcher: `robust_product_researcher`**

* Looks up detailed product information via the Wikipedia-filtered Google Search tool.
* Stores the raw structured data in `product_data`.
* Retries automatically if data is incomplete.

**2. NOVA Classifier: `robust_nova_classifier`**

* Assigns a NOVA processing group and provides reasoning.
* Stores results in `nova_classification`.

**3. Health Assessor: `robust_health_assessor`**

* Computes health score and nutrient breakdown.
* Stores results in `health_score`.

**4. Alternative Finder: `robust_alternative_finder`**

* Suggests healthier alternatives with explanations.
* Stores results in `alternatives`.

### Tools

**Google Search Tool (`google_search_tool`)**

* Callable function returning structured search results.
* Filters out Wikipedia results automatically.
* Used by `robust_product_researcher` to retrieve product information.

---

## Workflow

1. **User Input:** Enter a product name.
2. **Product Lookup:** `robust_product_researcher` retrieves product data.
3. **NOVA Classification:** `robust_nova_classifier` assigns processing group.
4. **Health Assessment:** `robust_health_assessor` calculates health score and nutrient details.
5. **Alternative Suggestions:** `robust_alternative_finder` provides healthier substitutes.
6. **Presentation:** All results are aggregated and presented in structured format.

The agent runs each sub-agent automatically and stores results in the agent state; formatting and display happen at the end.

---

## Installation

1. Clone the repository:

```bash
git clone https://github.com/JamesB112/Food_Product_Agent.git
cd Food_Product_Agent
```

2. Create a virtual environment and activate it:

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

---


4. Update API Key:

Within the `config.py`, please save your Google API KEY in the file (see below)

Please refer to the following website to generate a key: [https://ai.google.dev/gemini-api/docs/api-key]

```python
import os
from dataclasses import dataclass

# ============================================================================
# IMPORTANT: ADD GOOGLE API KEY
# ============================================================================

os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "FALSE"
os.environ["GOOGLE_API_KEY"] = ""  # Replace with your actual API key
```

---


## Usage

### Running the Agent in Python

```python
from PRODUCT_AGENT.agent import interactive_food_health_agent

result_state = interactive_food_health_agent.run({"user_input": "Nutella"})
print(result_state)
```

## Repository Structure

```
Food_Product_Agent/
├─ PRODUCT_AGENT/
│   ├─ __init__.py
│   ├─ agent.py                      # Main agent orchestration
│   ├─ sub_agents                    # Sub-agent definitions
├       |─ alternative_finder.py     # Finds alternative products
├       |─ google_search_agent.py    # Custom Google Search Agent
├       |─ health_assessor.py        # Assesses the healthiness of a product
├       |─ nova_classifier.py        # Determines the level of food processing for a product
├       └─ product_researcher.py     # Finds the ingredients of a given product

├─ tools/
│   └─ google_search_tool.py         # Wikipedia-filtered Google Search tool
├─ streamlit_app.py                  # Interactive testing interface
├─ config.py                         # Model configuration and parameters
├─ agent_util.py                     # Utility functions for agents
├─ validation_checkers.py            # Custom validation checkers for agent outputs
├─ requirements.txt                  # Dependencies
├─ flowchart.png                     # Agent Architecture diagram
```

---

## Special Mention

I would like to recognise the great work being done by Open Food Facts (https://world.openfoodfacts.org/).

Am curring using one of the API's as a product recommender.

They have an awesome app you should try.
 


## Room for Improvement

There is a lot of room for improving this Agent, including but not limited to:

- Redesign the food product recommender to use grocery websites, so pricing data can be used as a ranking metric as well (i.e., Health‑to‑Price ratio). It's clear that not everyone can afford the healthiest options, but incorporating cost‑sensitive ranking would increase accessibility.

- Add debugging, logging, and persistent chat/history storage to improve user experience and help identify weak points in the architecture. Caching previously retrieved product data would also speed up future queries.

- Improve robustness through stricter agent rules and instruction design to ensure the correct tools are used at the right times. Additional tools for multi‑language processing or for accessing specialised ingredient dictionaries would reduce hallucinations.

- Replace static, hard‑coded NOVA classification rules with a dynamically updated nutrition science knowledge base or public dataset to ensure classifications remain current and evidence‑based.

- Add user profiling support (budget, dietary restrictions, health goals, allergens) to produce personalised nutrition insights and recommendations.

- Strengthen error‑handling for cases where search tools fail, rate‑limit, or return incomplete product data. This could include fallback searches or ingredient‑based inference.

- Create a Streamlit app as a front-end to the Agent.

- Support batch comparison mode, allowing users to compare several products simultaneously.

- Introduce automated monitoring that refreshes product data when updated nutrition facts become available.
