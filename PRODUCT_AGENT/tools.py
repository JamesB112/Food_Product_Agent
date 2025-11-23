# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

import requests
from typing import Dict, Any
from google.adk.tools import FunctionTool

# ------------------- Product Lookup -------------------
import time


def openfoodfacts_lookup(product_name: str) -> dict:
    """
    Fetch nutrition, ingredients, and processing info for a product using Open Food Facts API.
    """
    url = f"https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": product_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1
    }

    response = requests.get(url, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data.get("products"):
            product = data["products"][0]
            return {
                "product_name": product.get("product_name"),
                "brand": product.get("brands"),
                "ingredients": product.get("ingredients_text"),
                "nutrients": product.get("nutriments"),
                "nova_group": product.get("nova_group"),  # 1–4 scale (4 = ultra-processed)
                "allergens": product.get("allergens"),
                "additives": product.get("additives_tags")
            }
    return {"error": "No product found or API request failed"}

# ------------------- Ingredient Scoring -------------------
def compute_simple_scores(ingredients_text: str, nutriments: Dict[str, Any]) -> Dict[str, Any]:
    """
    Computes a simple health score (0-100) and NOVA classification.
    """
    sugar = float(nutriments.get("sugars_100g") or 0)
    sat = float(nutriments.get("saturated-fat_100g") or 0)
    salt = float(nutriments.get("salt_100g") or 0)
    fiber = float(nutriments.get("fiber_100g") or 0)
    protein = float(nutriments.get("proteins_100g") or 0)

    score = 100.0
    score -= min(sugar * 1.5, 40)
    score -= min(sat * 2.0, 30)
    score -= min(salt * 10.0, 20)
    score += min(fiber * 2.0, 20)
    score += min(protein * 0.5, 5)
    score = max(0.0, min(100.0, score))

    ing = (ingredients_text or "").lower()
    ultra_terms = ["emulsifier", "maltodextrin", "colour", "artificial", "preservative", "sweetener", "stabilizer"]
    if any(t in ing for t in ultra_terms):
        nova = "NOVA 4 (Ultra-processed)"
    elif "sugar" in ing and "," in ing:
        nova = "NOVA 3 (Processed)"
    else:
        nova = "NOVA 1–2 (Unprocessed/minimally processed)"

    return {
        "health_score": round(score, 1),
        "nova": nova,
        "breakdown": {
            "sugar_g_per_100g": sugar,
            "saturated_fat_g_per_100g": sat,
            "salt_g_per_100g": salt,
            "fiber_g_per_100g": fiber,
            "protein_g_per_100g": protein,
        }
    }

# ------------------- Suggest Alternatives -------------------
def suggest_alternatives(product_record: Dict[str, Any], limit: int = 3) -> Dict[str, Any]:
    """
    Suggest healthier alternatives based on category and sugar/salt content.
    """
    categories = product_record.get("categories") or []
    if not categories:
        return {"alternatives": []}

    q = categories[0].replace("en:", "").replace("_", " ")
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": q,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit * 3
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        data = r.json()
        candidates = []
        for p in data.get("products", []):
            name = p.get("product_name")
            if not name:
                continue
            nutr = p.get("nutriments", {})
            sugar = float(nutr.get("sugars_100g") or 0)
            salt = float(nutr.get("salt_100g") or 0)
            candidates.append({
                "name": name,
                "brand": p.get("brands"),
                "sugars_100g": sugar,
                "salt_100g": salt,
                "nutriments": nutr
            })
        candidates = sorted(candidates, key=lambda c: (c["sugars_100g"], c["salt_100g"]))
        return {"alternatives": candidates[:limit]}
    except Exception:
        return {"alternatives": []}
