from google.adk.agents.callback_context import CallbackContext
from google.genai.types import Content


def suppress_output_callback(callback_context: CallbackContext) -> Content:
    """Suppresses the output of the agent by returning an empty Content object."""
    return Content()


def format_product_info(product_data: dict) -> str:
    """
    Format product information for display or agent consumption.
    
    Args:
        product_data: Product information dictionary
        
    Returns:
        Formatted string representation
    """
    if not product_data or product_data.get("error"):
        return f"Error: {product_data.get('error', 'Unknown error')}"
    
    lines = [
        f"Product: {product_data.get('product_name', 'Unknown')}",
        f"Brand: {product_data.get('brand', 'Unknown')}",
    ]
    
    if product_data.get('ingredients'):
        lines.append(f"Ingredients: {product_data.get('ingredients')}")
    
    if product_data.get('nova_group'):
        lines.append(f"NOVA Group: {product_data.get('nova_group')}")
    
    return "\n".join(lines)


def format_health_analysis(health_data: dict, nova_data: dict) -> str:
    """
    Format health score and NOVA classification for display.
    
    Args:
        health_data: Health score information
        nova_data: NOVA classification information
        
    Returns:
        Formatted analysis string
    """
    lines = [
        "\n" + "="*60,
        "HEALTH ANALYSIS",
        "="*60,
        f"\n{nova_data.get('nova_name', 'Unknown Classification')}",
        f"Reasoning: {nova_data.get('reasoning', 'N/A')}",
        f"\nHealth Score: {health_data.get('health_score', 'N/A')}/100",
        f"Assessment: {health_data.get('interpretation', 'N/A')}",
    ]
    
    if nova_data.get('key_indicators'):
        lines.append(f"\nKey Indicators: {', '.join(nova_data['key_indicators'])}")
    
    breakdown = health_data.get('breakdown', {})
    if breakdown:
        lines.extend([
            "\nNutritional Breakdown (per 100g):",
            f"  Sugar: {breakdown.get('sugar_g_per_100g', 'N/A')}g",
            f"  Saturated Fat: {breakdown.get('saturated_fat_g_per_100g', 'N/A')}g",
            f"  Salt: {breakdown.get('salt_g_per_100g', 'N/A')}g",
            f"  Fiber: {breakdown.get('fiber_g_per_100g', 'N/A')}g",
            f"  Protein: {breakdown.get('protein_g_per_100g', 'N/A')}g",
        ])
    
    return "\n".join(lines)


def format_alternatives(alternatives_data: dict) -> str:
    """
    Format alternative product suggestions for display.
    
    Args:
        alternatives_data: Alternative products information
        
    Returns:
        Formatted alternatives string
    """
    if alternatives_data.get('error'):
        return f"\nAlternatives: {alternatives_data['error']}"
    
    alternatives = alternatives_data.get('alternatives', [])
    if not alternatives:
        return "\nNo healthier alternatives found."
    
    lines = ["\n" + "="*60, "HEALTHIER ALTERNATIVES", "="*60]
    
    for i, alt in enumerate(alternatives, 1):
        lines.extend([
            f"\n{i}. {alt.get('name', 'Unknown')}",
            f"   Brand: {alt.get('brand', 'Unknown')}",
            f"   NOVA Group: {alt.get('nova_group', 'N/A')}",
            f"   Why it's better: {alt.get('reason', 'N/A')}",
        ])
    
    return "\n".join(lines)