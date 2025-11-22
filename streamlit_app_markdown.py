import streamlit as st
from agent import root_agent

st.set_page_config(page_title="Food Health Advisor", layout="wide")
st.title("🍎 Food Health Advisor")

# User input
product_input = st.text_input(
    "Enter a product name, ingredient list, or ask about specific ingredients:",
    ""
)

def render_structured_report(report: dict):
    """Render structured report as Markdown table for Streamlit."""
    if not report:
        st.write("No structured report generated.")
        return

    st.write("**Overall Health Score:**", report.get("health_score", "N/A"))
    st.write("**NOVA Classification:**", report.get("nova", "N/A"))

    breakdown = report.get("breakdown", {})
    if breakdown:
        st.markdown("**Nutritional Breakdown (per 100g):**")
        md = "| Nutrient | Value |\n| --- | --- |\n"
        for k, v in breakdown.items():
            md += f"| {k.replace('_', ' ').title()} | {v} |\n"
        st.markdown(md)

    alternatives = report.get("alternatives", [])
    if alternatives:
        st.markdown("**Suggested Healthier Alternatives:**")
        md_alt = "| Product | Brand | Sugars (g) | Salt (g) |\n| --- | --- | --- | --- |\n"
        for alt in alternatives:
            md_alt += f"| {alt.get('name', '')} | {alt.get('brand', '')} | {alt.get('sugars_100g', 'N/A')} | {alt.get('salt_100g', 'N/A')} |\n"
        st.markdown(md_alt)

    tips = report.get("tips", [])
    if tips:
        st.markdown("**Tips:**")
        for tip in tips:
            st.markdown(f"- {tip}")

# Analyze button
if st.button("Analyze Product") and product_input.strip():
    with st.spinner("Analyzing product…"):
        result = root_agent.run({"user_message": product_input})

    final_output = result.get("final_output", {})

    # Friendly message
    friendly_message = final_output.get("friendly_message", "")
    st.subheader("👩‍⚕️ Friendly Health Advice")
    st.write(friendly_message or "No advice generated.")

    # Structured report (Markdown)
    st.subheader("📊 Structured Report")
    structured_report = final_output.get("structured_report", {})
    render_structured_report(structured_report)
