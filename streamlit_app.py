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

import streamlit as st
import asyncio
import json
from PRODUCT_AGENT.tools import (
    openfoodfacts_lookup,
    classify_nova,
    compute_health_score,
    suggest_alternatives
)

# Page configuration
st.set_page_config(
    page_title="Food Health AI Agent",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .section-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 0.5rem;
        border-bottom: 2px solid #4CAF50;
        padding-bottom: 0.3rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    .nova-group-1 { color: #4CAF50; font-weight: bold; }
    .nova-group-2 { color: #8BC34A; font-weight: bold; }
    .nova-group-3 { color: #FF9800; font-weight: bold; }
    .nova-group-4 { color: #F44336; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


def display_header():
    """Display the app header."""
    st.markdown('<div class="main-header">🍎 Food Health AI Agent</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Analyze the healthiness of any food product using NOVA classification</div>', unsafe_allow_html=True)


def display_nova_badge(nova_group):
    """Display colored NOVA group badge."""
    colors = {1: "green", 2: "lightgreen", 3: "orange", 4: "red"}
    labels = {
        1: "Group 1: Unprocessed/Minimally Processed",
        2: "Group 2: Processed Culinary Ingredients",
        3: "Group 3: Processed Foods",
        4: "Group 4: Ultra-Processed Foods"
    }
    
    color = colors.get(nova_group, "gray")
    label = labels.get(nova_group, "Unknown")
    
    st.markdown(f"""
    <div style='background-color: {color}; color: white; padding: 10px; 
                border-radius: 5px; text-align: center; font-weight: bold;'>
        {label}
    </div>
    """, unsafe_allow_html=True)


def display_health_score(score, interpretation):
    """Display health score with color coding."""
    if score >= 80:
        color = "#4CAF50"
    elif score >= 65:
        color = "#8BC34A"
    elif score >= 50:
        color = "#FF9800"
    else:
        color = "#F44336"
    
    st.markdown(f"""
    <div style='text-align: center; margin: 1rem 0;'>
        <div style='font-size: 4rem; font-weight: bold; color: {color};'>{score}/100</div>
        <div style='font-size: 1.2rem; color: #666;'>{interpretation}</div>
    </div>
    """, unsafe_allow_html=True)


def analyze_product(product_name):
    """
    Main analysis function that runs all steps sequentially.
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Step 1: Product Lookup
        status_text.text("🔍 Step 1/4: Searching product database...")
        progress_bar.progress(25)
        
        product_data = openfoodfacts_lookup(product_name)
        
        if product_data.get("error"):
            st.error(f"❌ {product_data['error']}")
            st.info("💡 Try searching with a more specific product name or include the brand name.")
            return None
        
        # Step 2: NOVA Classification
        status_text.text("🏷️ Step 2/4: Classifying processing level...")
        progress_bar.progress(50)
        
        nova_classification = classify_nova(
            product_data.get("ingredients", ""),
            product_data.get("additives", []),
            product_data.get("nova_group")
        )
        
        # Step 3: Health Score
        status_text.text("💯 Step 3/4: Calculating health score...")
        progress_bar.progress(75)
        
        health_score = compute_health_score(
            product_data.get("nutrients", {}),
            nova_classification.get("nova_group", 4)
        )
        
        # Step 4: Find Alternatives
        status_text.text("🌱 Step 4/4: Finding healthier alternatives...")
        progress_bar.progress(90)
        
        alternatives = suggest_alternatives(product_data, limit=3)
        
        progress_bar.progress(100)
        status_text.text("✅ Analysis complete!")
        
        return {
            "product_data": product_data,
            "nova_classification": nova_classification,
            "health_score": health_score,
            "alternatives": alternatives
        }
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        return None


def display_results(results):
    """Display the analysis results."""
    
    product_data = results["product_data"]
    nova_classification = results["nova_classification"]
    health_score = results["health_score"]
    alternatives = results["alternatives"]
    
    # Product Information
    st.markdown('<div class="section-header">📦 Product Information</div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**Product:** {product_data.get('product_name', 'Unknown')}")
        st.write(f"**Brand:** {product_data.get('brand', 'Unknown')}")
    
    with col2:
        if product_data.get('allergens'):
            st.write(f"**⚠️ Allergens:** {product_data.get('allergens')}")
    
    if product_data.get('ingredients'):
        with st.expander("📝 Full Ingredients List"):
            st.write(product_data['ingredients'])
    
    # NOVA Classification
    st.markdown('<div class="section-header">🏷️ NOVA Classification</div>', unsafe_allow_html=True)
    
    display_nova_badge(nova_classification.get("nova_group", 4))
    
    st.write(f"**Reasoning:** {nova_classification.get('reasoning', 'N/A')}")
    
    if nova_classification.get('key_indicators'):
        st.write("**Key Indicators:**")
        for indicator in nova_classification['key_indicators']:
            st.write(f"  • {indicator}")
    
    # Health Score
    st.markdown('<div class="section-header">💯 Health Score</div>', unsafe_allow_html=True)
    
    display_health_score(
        health_score.get("health_score", 0),
        health_score.get("interpretation", "N/A")
    )
    
    # Nutritional Breakdown
    st.markdown("**Nutritional Breakdown (per 100g):**")
    
    breakdown = health_score.get("breakdown", {})
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Sugar", f"{breakdown.get('sugar_g_per_100g', 0)}g")
    with col2:
        st.metric("Sat. Fat", f"{breakdown.get('saturated_fat_g_per_100g', 0)}g")
    with col3:
        st.metric("Salt", f"{breakdown.get('salt_g_per_100g', 0)}g")
    with col4:
        st.metric("Fiber", f"{breakdown.get('fiber_g_per_100g', 0)}g")
    with col5:
        st.metric("Protein", f"{breakdown.get('protein_g_per_100g', 0)}g")
    
    # Healthier Alternatives
    if alternatives.get("alternatives"):
        st.markdown('<div class="section-header">🌱 Healthier Alternatives</div>', unsafe_allow_html=True)
        
        for i, alt in enumerate(alternatives["alternatives"], 1):
            with st.expander(f"{i}. {alt.get('name', 'Unknown')} - {alt.get('brand', 'Unknown')}"):
                st.write(f"**NOVA Group:** {alt.get('nova_group', 'N/A')}")
                st.write(f"**Why it's better:** {alt.get('reason', 'N/A')}")
    
    elif alternatives.get("message"):
        st.info(f"ℹ️ {alternatives['message']}")


def main():
    """Main Streamlit app."""
    
    display_header()
    
    # Sidebar
    with st.sidebar:
        st.header("ℹ️ About")
        st.write("""
        This app analyzes food products using the **NOVA classification system**, 
        which categorizes foods by their level of processing.
        
        **NOVA Groups:**
        - **Group 1:** Unprocessed/Minimally Processed
        - **Group 2:** Processed Culinary Ingredients  
        - **Group 3:** Processed Foods
        - **Group 4:** Ultra-Processed Foods
        
        Data is sourced from **Open Food Facts**, a collaborative database 
        of food products from around the world.
        """)
        
        st.header("🔍 How to Use")
        st.write("""
        1. Enter a product name (e.g., "Nutella", "Coca-Cola")
        2. Click "Analyze Product"
        3. View the comprehensive health analysis
        4. Check out healthier alternatives
        """)
        
        st.header("💡 Tips")
        st.write("""
        - Include brand names for better results
        - Be specific (e.g., "Kellogg's Corn Flakes" vs "cereal")
        - Try different variations if not found
        """)
    
    # Main content
    st.markdown("---")
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        product_name = st.text_input(
            "Enter a food product name:",
            placeholder="e.g., Nutella, Coca-Cola, Doritos...",
            help="Enter the name of any food product you want to analyze"
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        analyze_button = st.button("🔍 Analyze Product", type="primary", use_container_width=True)
    
    # Example products
    st.write("**Quick examples:**")
    example_cols = st.columns(5)
    examples = ["Nutella", "Coca-Cola", "Cheerios", "Doritos", "Yogurt"]
    
    for i, example in enumerate(examples):
        with example_cols[i]:
            if st.button(example, use_container_width=True):
                product_name = example
                analyze_button = True
    
    st.markdown("---")
    
    # Analysis section
    if analyze_button and product_name:
        with st.spinner(f"Analyzing {product_name}..."):
            results = analyze_product(product_name)
        
        if results:
            st.success(f"✅ Analysis complete for **{product_name}**!")
            display_results(results)
            
            # Download results as JSON
            st.download_button(
                label="📥 Download Full Analysis (JSON)",
                data=json.dumps(results, indent=2),
                file_name=f"{product_name.replace(' ', '_')}_analysis.json",
                mime="application/json"
            )
    
    elif analyze_button:
        st.warning("⚠️ Please enter a product name first.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9rem;'>
        <p>Data provided by <a href='https://world.openfoodfacts.org' target='_blank'>Open Food Facts</a> | 
        NOVA Classification by <a href='http://www.fao.org/nutrition/education/food-dietary-guidelines/background/nova-classification/en/' target='_blank'>FAO</a></p>
        <p>⚠️ This tool is for informational purposes only. Consult a healthcare professional for personalized dietary advice.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()