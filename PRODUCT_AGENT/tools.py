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
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
from typing import Dict, Any, List
from google.adk.tools import FunctionTool


# ------------------- Product Lookup -------------------

def openfoodfacts_lookup(product_name: str) -> dict:
    """
    Fetch nutrition, ingredients, and processing info for a product using Open Food Facts API.
    
    Args:
        product_name: Name of the product to search for
        
    Returns:
        Dictionary containing product information including ingredients, nutrients, and NOVA group
    """
    print(f'🔍 Searching Product: {product_name}')
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": product_name,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": 1
    }

    # Try multiple times with increasing timeout
    for attempt in range(3):
        try:
            timeout = 15 + (attempt * 5)  # 15s, 20s, 25s
            print(f'  Attempt {attempt + 1}/3 (timeout: {timeout}s)...')
            
            response = requests.get(url, params=params, timeout=timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("products"):
                    product = data["products"][0]
                    print(f'  ✓ Found: {product.get("product_name")}')
                    return {
                        "product_name": product.get("product_name"),
                        "brand": product.get("brands"),
                        "ingredients": product.get("ingredients_text"),
                        "ingredients_list": [ing.get("text") for ing in product.get("ingredients", []) if ing.get("text")],
                        "nutrients": product.get("nutriments", {}),
                        "nova_group": product.get("nova_group"),  # 1–4 scale (4 = ultra-processed)
                        "allergens": product.get("allergens"),
                        "additives": product.get("additives_tags", []),
                        "categories": product.get("categories_tags", [])
                    }
                else:
                    print(f'  ✗ No products found in response')
            else:
                print(f'  ✗ HTTP {response.status_code}')
                
        except requests.exceptions.Timeout:
            print(f'  ✗ Timeout on attempt {attempt + 1}')
            if attempt == 2:  # Last attempt
                return {"error": f"API request timed out after 3 attempts. The Open Food Facts API may be slow or unavailable."}
        except Exception as e:
            print(f'  ✗ Error: {str(e)}')
            return {"error": f"API request failed: {str(e)}"}
    
    return {"error": "No product found in Open Food Facts database. Try searching with a more specific product name or brand."}


# ------------------- NOVA Classification -------------------

def classify_nova(ingredients_text: str, additives: List[str], nova_group_api: int = None) -> Dict[str, Any]:
    """
    Classify product according to NOVA system based on official criteria from 
    'NOVA. The star shines bright' (World Nutrition, Jan-Mar 2016).
    
    NOVA classifies foods by extent and purpose of processing:
    - Group 1: Unprocessed or minimally processed foods
    - Group 2: Processed culinary ingredients
    - Group 3: Processed foods (Group 1 + Group 2 ingredients, 2-3 ingredients typically)
    - Group 4: Ultra-processed foods (industrial formulations, 5+ ingredients typically)
    
    Args:
        ingredients_text: Full ingredients text
        additives: List of additive tags
        nova_group_api: NOVA group from API (if available, used as reference)
        
    Returns:
        Dictionary with NOVA classification and reasoning
    """
    ing = (ingredients_text or "").lower()
    
    # Group 4 indicators: Substances only found in ultra-processed products
    group_4_substances = [
        # Extracted food constituents
        "casein", "lactose", "whey", "gluten",
        # Derived from further processing
        "hydrogenated oil", "interesterified oil", "hydrolysed protein", 
        "soy protein isolate", "maltodextrin", "invert sugar", 
        "high fructose corn syrup", "high-fructose corn syrup",
        # Additives only in ultra-processed
        "dye", "colour stabiliser", "color stabilizer", "flavour enhancer", 
        "flavor enhancer", "non-sugar sweetener", "aspartame", "sucralose",
        "acesulfame", "carbonating agent", "firming agent", "bulking agent",
        "anti-caking agent", "glazing agent", "emulsifier", "sequestrant",
        "humectant", "modified starch", "monosodium glutamate", "msg"
    ]
    
    # Group 3 indicators: Preservation/cooking additives
    group_3_additives = [
        "anti-oxidant", "antioxidant", "preservative", "stabiliser", "stabilizer"
    ]
    
    # Group 2 indicators: Culinary ingredients
    group_2_ingredients = [
        "oil", "butter", "lard", "sugar", "salt", "honey", "syrup", "molasses",
        "vinegar", "starch"
    ]
    
    # Count ingredients (rough estimate by comma count + 1)
    ingredient_count = ing.count(",") + 1 if ing else 0
    
    # Check for Group 4 indicators
    group_4_matches = [term for term in group_4_substances if term in ing]
    has_group_4_substances = len(group_4_matches) > 0
    
    # Check for cosmetic/sensory additives in otherwise simple products
    has_cosmetic_additives = any(term in ing for term in [
        "artificial sweetener", "emulsifier", "flavour enhancer", "flavor enhancer",
        "colour", "color", "dye"
    ])
    
    # Check additive count
    additive_count = len(additives) if additives else 0
    
    # Determine NOVA group based on official criteria
    if nova_group_api == 4 or has_group_4_substances or ingredient_count >= 5:
        # Group 4: Ultra-processed
        # Industrial formulations with 5+ ingredients and/or substances only in ultra-processed
        nova_group = 4
        reasoning = "Industrial formulation. "
        if group_4_matches:
            reasoning += f"Contains ultra-processed substances: {', '.join(group_4_matches[:3])}. "
        if ingredient_count >= 5:
            reasoning += f"Has {ingredient_count} ingredients (typical of ultra-processed). "
        if additive_count > 0:
            reasoning += f"Contains {additive_count} additives."
            
    elif has_cosmetic_additives and ingredient_count <= 3:
        # Group 4: Simple product with cosmetic additives
        # e.g., plain yoghurt with artificial sweeteners, bread with emulsifiers
        nova_group = 4
        reasoning = "Simple product with cosmetic or sensory-intensifying additives, classified as ultra-processed per NOVA criteria."
        
    elif ingredient_count >= 2 and any(term in ing for term in group_2_ingredients):
        # Group 3: Processed foods
        # Group 1 foods + Group 2 ingredients (2-3 ingredients typically)
        # Purpose: increase durability or enhance sensory qualities
        nova_group = 3
        reasoning = "Processed food. "
        group_2_found = [term for term in group_2_ingredients if term in ing]
        reasoning += f"Contains Group 2 culinary ingredients ({', '.join(group_2_found[:2])}) added to whole foods. "
        if ingredient_count <= 3:
            reasoning += f"Has {ingredient_count} ingredients (typical of processed foods). "
        if any(term in ing for term in group_3_additives):
            reasoning += "Contains preservation additives."
            
    elif ingredient_count <= 2 and all(term in ing for term in group_2_ingredients[:1]):
        # Group 2: Processed culinary ingredients
        # Substances from Group 1 or nature (oil, sugar, salt, butter, etc.)
        # Rarely consumed alone
        nova_group = 2
        reasoning = "Processed culinary ingredient. "
        reasoning += "Substance extracted from Group 1 foods or nature, used in cooking and preparation."
        
    else:
        # Group 1: Unprocessed or minimally processed
        # Natural foods or minimally processed without added substances
        nova_group = 1
        reasoning = "Unprocessed or minimally processed food. "
        reasoning += "Natural food with no added salt, sugar, oils, or fats. "
        if ingredient_count <= 2:
            reasoning += "Minimal ingredients, no ultra-processing indicators."
    
    # Use API group as validation if available
    if nova_group_api and nova_group_api != nova_group:
        reasoning += f" (Note: Open Food Facts classifies as Group {nova_group_api})"
    
    # Classification names per official NOVA system
    nova_names = {
        1: "Group 1: Unprocessed or Minimally Processed Foods",
        2: "Group 2: Processed Culinary Ingredients",
        3: "Group 3: Processed Foods",
        4: "Group 4: Ultra-Processed Food and Drink Products"
    }
    
    return {
        "nova_group": nova_group,
        "nova_name": nova_names.get(nova_group, "Unknown"),
        "reasoning": reasoning.strip(),
        "key_indicators": group_4_matches[:5] if group_4_matches else [],
        "ingredient_count": ingredient_count,
        "additive_count": additive_count
    }


# ------------------- Health Score Calculation -------------------

def compute_health_score(nutrients: Dict[str, Any], nova_group: int) -> Dict[str, Any]:
    """
    Compute a health score (0-100) based on nutrients and NOVA classification.
    
    Args:
        nutrients: Nutrient information per 100g
        nova_group: NOVA classification group (1-4)
        
    Returns:
        Dictionary with health score and breakdown
    """
    sugar = float(nutrients.get("sugars_100g") or 0)
    sat_fat = float(nutrients.get("saturated-fat_100g") or 0)
    salt = float(nutrients.get("salt_100g") or 0)
    fiber = float(nutrients.get("fiber_100g") or 0)
    protein = float(nutrients.get("proteins_100g") or 0)
    
    # Base score from NOVA classification
    base_scores = {1: 90, 2: 75, 3: 60, 4: 30}
    score = float(base_scores.get(nova_group, 50))
    
    # Adjust for negative factors
    score -= min(sugar * 1.5, 30)      # High sugar penalty
    score -= min(sat_fat * 2.0, 25)    # Saturated fat penalty
    score -= min(salt * 10.0, 20)      # High salt penalty
    
    # Adjust for positive factors
    score += min(fiber * 2.0, 15)      # Fiber bonus
    score += min(protein * 0.5, 10)    # Protein bonus
    
    # Clamp to 0-100 range
    score = max(0.0, min(100.0, score))
    
    # Interpretation
    if score >= 80:
        interpretation = "Excellent - Whole food, minimal processing"
    elif score >= 65:
        interpretation = "Good - Moderately processed"
    elif score >= 50:
        interpretation = "Fair - Processed food, consume in moderation"
    else:
        interpretation = "Poor - Ultra-processed, limit consumption"
    
    return {
        "health_score": round(score, 1),
        "interpretation": interpretation,
        "breakdown": {
            "sugar_g_per_100g": round(sugar, 1),
            "saturated_fat_g_per_100g": round(sat_fat, 1),
            "salt_g_per_100g": round(salt, 2),
            "fiber_g_per_100g": round(fiber, 1),
            "protein_g_per_100g": round(protein, 1),
        }
    }


# ------------------- Suggest Alternatives -------------------

def suggest_alternatives(product_data: Dict[str, Any], limit: int = 3) -> Dict[str, Any]:
    """
    Suggest healthier alternatives based on category and nutritional profile.
    
    Args:
        product_data: Product information including categories and nutrients
        limit: Maximum number of alternatives to return
        
    Returns:
        Dictionary containing list of alternative products
    """
    categories = product_data.get("categories", [])
    if not categories:
        return {"alternatives": [], "message": "No category information available for alternatives"}
    
    # Use first category for search
    category = categories[0].replace("en:", "").replace("_", " ")
    print(f"🔎 Searching alternatives in category: {category}")
    
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
        "search_terms": category,
        "search_simple": 1,
        "action": "process",
        "json": 1,
        "page_size": limit * 3  # Get more to filter
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        data = response.json()
        
        candidates = []
        for product in data.get("products", []):
            name = product.get("product_name")
            if not name:
                continue
            
            nutrients = product.get("nutriments", {})
            nova = product.get("nova_group", 4)
            sugar = float(nutrients.get("sugars_100g") or 0)
            salt = float(nutrients.get("salt_100g") or 0)
            
            candidates.append({
                "name": name,
                "brand": product.get("brands", "Unknown"),
                "nova_group": nova,
                "sugars_100g": sugar,
                "salt_100g": salt,
                "score": sugar + salt + (nova * 10)  # Combined score for sorting
            })
        
        # Sort by health (lower is better)
        candidates = sorted(candidates, key=lambda c: c["score"])
        
        # Remove score from output and take top results
        alternatives = []
        for candidate in candidates[:limit]:
            reason = []
            if candidate["nova_group"] <= 2:
                reason.append("minimally processed")
            if candidate["sugars_100g"] < 5:
                reason.append("low sugar")
            if candidate["salt_100g"] < 0.5:
                reason.append("low salt")
            
            alternatives.append({
                "name": candidate["name"],
                "brand": candidate["brand"],
                "nova_group": candidate["nova_group"],
                "reason": ", ".join(reason) if reason else "healthier nutritional profile"
            })
        
        return {"alternatives": alternatives}
        
    except Exception as e:
        return {"alternatives": [], "error": f"Failed to find alternatives: {str(e)}"}


# ------------------- Tool Registration -------------------

# Create FunctionTool instances for use with agents
product_lookup_tool = FunctionTool(
    openfoodfacts_lookup,
)

alternative_finder_tool = FunctionTool(
    suggest_alternatives,
)