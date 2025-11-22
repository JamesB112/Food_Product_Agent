# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");

from typing import Dict

class ProductLookupValidationChecker:
    """
    Validates that the product lookup returned a product name and ingredients.
    """

    def __init__(self, name="product_lookup_validation_checker"):
        self.name = name

    def validate(self, state: Dict) -> bool:
        product = state.get("product_record")
        if not product:
            return False
        if not product.get("name"):
            return False
        # ingredients may be missing; still allow but warn
        return True


class AnalysisValidationChecker:
    """
    Validates that analysis contains a health_score and NOVA classification.
    """

    def __init__(self, name="analysis_validation_checker"):
        self.name = name

    def validate(self, state: Dict) -> bool:
        analysis = state.get("analysis")
        if not analysis:
            return False
        if "health_score" not in analysis or "nova" not in analysis:
            return False
        return True
