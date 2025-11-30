import streamlit as st
import json
import os
from PRODUCT_AGENT.tools import (
    openfoodfacts_lookup,
    classify_nova,
    compute_health_score,
    suggest_alternatives
)

# Try to import Gemini for chat
try:
    import google.generativeai as genai
    
    # Get API key from environment (same as config.py uses)
    api_key = os.environ.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY")
    
    if api_key:
        genai.configure(api_key=api_key)
        GEMINI_AVAILABLE = True
    else:
        GEMINI_AVAILABLE = False
except ImportError:
    GEMINI_AVAILABLE = False
    # Only show warning once in sidebar, not at top
except Exception as e:
    GEMINI_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="Food Health AI Chat",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1rem;
        text-align: center;
        color: #666;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #e3f2fd;
        margin-left: 2rem;
    }
    .assistant-message {
        background-color: #f5f5f5;
        margin-right: 2rem;
    }
    .product-card {
        background-color: #fff;
        border: 2px solid #4CAF50;
        border-radius: 0.5rem;
        padding: 1rem;
        margin: 1rem 0;
    }
    .nova-badge {
        display: inline-block;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-weight: bold;
        color: white;
    }
    .nova-1 { background-color: #4CAF50; }
    .nova-2 { background-color: #8BC34A; }
    .nova-3 { background-color: #FF9800; }
    .nova-4 { background-color: #F44336; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "analyzed_products" not in st.session_state:
    st.session_state.analyzed_products = {}
if "should_process" not in st.session_state:
    st.session_state.should_process = False
if "last_processed_message" not in st.session_state:
    st.session_state.last_processed_message = None


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

def analyze_with_custom_ingredients(product_name, ingredients_text):
    """Analyze a product with user-provided ingredients."""
    try:
        # Create minimal product data structure
        product_data = {
            "product_name": product_name,
            "brand": "User-provided",
            "ingredients": ingredients_text,
            "ingredients_list": [ing.strip() for ing in ingredients_text.split(',')],
            "nutrients": {},
            "nova_group": None,
            "allergens": None,
            "additives": [],
            "categories": []
        }
        
        # NOVA Classification
        nova_classification = classify_nova(
            ingredients_text,
            [],  # No additive tags from user input
            None
        )
        
        # Health Score (with default nutrients since we don't have them)
        health_score = compute_health_score(
            {},  # Empty nutrients
            nova_classification.get("nova_group", 4)
        )
        
        return {
            "product_data": product_data,
            "nova_classification": nova_classification,
            "health_score": health_score,
            "alternatives": {"alternatives": [], "message": "Custom ingredient analysis - alternatives not available"}
        }
    except Exception as e:
        return {"error": str(e)}
    """Analyze a product and return structured data."""
    try:
        # Product Lookup
        product_data = openfoodfacts_lookup(product_name)
        if product_data.get("error"):
            return {"error": product_data["error"]}
        
        # NOVA Classification
        nova_classification = classify_nova(
            product_data.get("ingredients", ""),
            product_data.get("additives", []),
            product_data.get("nova_group")
        )
        
        # Health Score
        health_score = compute_health_score(
            product_data.get("nutrients", {}),
            nova_classification.get("nova_group", 4)
        )
        
        # Find Alternatives
        alternatives = suggest_alternatives(product_data, limit=3)
        
        return {
            "product_data": product_data,
            "nova_classification": nova_classification,
            "health_score": health_score,
            "alternatives": alternatives
        }
    except Exception as e:
        return {"error": str(e)}


def format_product_analysis(analysis, product_name):
    """Format product analysis for display."""
    if analysis.get("error"):
        return f"❌ Sorry, I couldn't find information about {product_name}. {analysis['error']}"
    
    product = analysis["product_data"]
    nova = analysis["nova_classification"]
    health = analysis["health_score"]
    
    # Build response
    response = f"## 🍎 Analysis: {product.get('product_name', product_name)}\n\n"
    
    # Product Info
    response += f"**Brand:** {product.get('brand', 'Unknown')}\n\n"
    
    # NOVA Classification
    nova_group = nova.get('nova_group', 4)
    nova_colors = {1: "🟢", 2: "🟡", 3: "🟠", 4: "🔴"}
    response += f"### {nova_colors.get(nova_group, '⚪')} NOVA Classification: Group {nova_group}\n"
    response += f"{nova.get('nova_name', 'Unknown')}\n\n"
    response += f"**Why?** {nova.get('reasoning', 'N/A')}\n\n"
    
    # Health Score
    score = health.get('health_score', 0)
    response += f"### 💯 Health Score: **{score}/100**\n"
    response += f"_{health.get('interpretation', 'N/A')}_\n\n"
    
    # Nutritional breakdown
    breakdown = health.get('breakdown', {})
    response += "**Nutritional Info (per 100g):**\n"
    response += f"- Sugar: {breakdown.get('sugar_g_per_100g', 0)}g\n"
    response += f"- Saturated Fat: {breakdown.get('saturated_fat_g_per_100g', 0)}g\n"
    response += f"- Salt: {breakdown.get('salt_g_per_100g', 0)}g\n"
    response += f"- Fiber: {breakdown.get('fiber_g_per_100g', 0)}g\n"
    response += f"- Protein: {breakdown.get('protein_g_per_100g', 0)}g\n\n"
    
    # Ingredients
    if product.get('ingredients'):
        response += f"**Ingredients:** {product['ingredients'][:200]}{'...' if len(product.get('ingredients', '')) > 200 else ''}\n\n"
    
    # Alternatives
    alts = analysis.get("alternatives", {}).get("alternatives", [])
    if alts:
        response += "### 🌱 Healthier Alternatives:\n"
        for i, alt in enumerate(alts[:3], 1):
            response += f"{i}. **{alt.get('name')}** ({alt.get('brand', 'Unknown')})\n"
            response += f"   - NOVA Group {alt.get('nova_group')}: {alt.get('reason')}\n"
    
    return response


def compare_products(product_names):
    """Compare multiple products without AI."""
    analyzed = st.session_state.analyzed_products
    
    # Filter to only products that have been analyzed
    products_to_compare = {name: data for name, data in analyzed.items() 
                          if name in product_names and not data.get("error")}
    
    if len(products_to_compare) < 2:
        return "I need at least 2 products to compare. Please analyze the products first!"
    
    response = f"## 📊 Comparison: {' vs '.join(products_to_compare.keys())}\n\n"
    
    # Create comparison table
    response += "| Metric | " + " | ".join(products_to_compare.keys()) + " |\n"
    response += "|--------|" + "|".join(["--------"] * len(products_to_compare)) + "|\n"
    
    # NOVA Group comparison
    nova_row = "| **NOVA Group** |"
    for name, data in products_to_compare.items():
        nova = data['nova_classification']['nova_group']
        nova_row += f" Group {nova} |"
    response += nova_row + "\n"
    
    # Health Score comparison
    score_row = "| **Health Score** |"
    winner_score = 0
    winner = None
    for name, data in products_to_compare.items():
        score = data['health_score']['health_score']
        score_row += f" {score}/100 |"
        if score > winner_score:
            winner_score = score
            winner = name
    response += score_row + "\n"
    
    # Sugar comparison
    sugar_row = "| **Sugar (per 100g)** |"
    for name, data in products_to_compare.items():
        sugar = data['health_score']['breakdown']['sugar_g_per_100g']
        sugar_row += f" {sugar}g |"
    response += sugar_row + "\n"
    
    # Salt comparison
    salt_row = "| **Salt (per 100g)** |"
    for name, data in products_to_compare.items():
        salt = data['health_score']['breakdown']['salt_g_per_100g']
        salt_row += f" {salt}g |"
    response += salt_row + "\n"
    
    # Sat Fat comparison
    fat_row = "| **Saturated Fat (per 100g)** |"
    for name, data in products_to_compare.items():
        fat = data['health_score']['breakdown']['saturated_fat_g_per_100g']
        fat_row += f" {fat}g |"
    response += fat_row + "\n"
    
    response += f"\n### 🏆 Winner: **{winner}**\n"
    response += f"With a health score of {winner_score}/100, {winner} is the healthier choice among these options.\n"
    
    return response


def get_ai_response(user_message, context):
    """Get AI response using Gemini with context about analyzed products and conversation history."""
    if not GEMINI_AVAILABLE:
        # Fallback response without AI
        return """I don't have AI chat capabilities enabled right now, but I can still help! 
        
Try asking me to:
- **Analyze a product** (e.g., "Analyze Doritos")
- **Compare products** (e.g., "Compare Coca-Cola and Pepsi")
- **Show alternatives** for products I've analyzed

For ingredient questions, you can install AI chat with:
```
pip install google-generativeai
```"""
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Build context from analyzed products
        context_str = "You are a friendly food health assistant. Here's what we've analyzed:\n\n"
        for name, data in context.items():
            if not data.get("error"):
                context_str += f"**{name}:**\n"
                context_str += f"- NOVA Group: {data['nova_classification']['nova_group']}\n"
                context_str += f"- Health Score: {data['health_score']['health_score']}/100\n"
                context_str += f"- Ingredients: {data['product_data'].get('ingredients', 'N/A')}\n\n"
        
        # Add recent conversation history (last 6 messages for context)
        recent_messages = st.session_state.messages[-6:] if len(st.session_state.messages) > 6 else st.session_state.messages
        context_str += "\n**Recent conversation:**\n"
        for msg in recent_messages:
            role = "User" if msg["role"] == "user" else "Assistant"
            content_preview = msg["content"][:150] + ("..." if len(msg["content"]) > 150 else "")
            context_str += f"{role}: {content_preview}\n"
        
        context_str += f"\n**Current user question:** {user_message}\n\n"
        context_str += """Guidelines:
- If user provides new ingredient information, acknowledge it and explain the health implications
- If they ask to re-analyze based on new info, suggest: "Would you like me to re-analyze [product] with these ingredients?"
- For specific ingredients: explain what they are and health impacts
- For comparisons: use the analyzed data above
- Be concise but informative
- Use emojis sparingly

IMPORTANT: The analyzed data above is from Open Food Facts database. If the user provides different/additional ingredient information, acknowledge that the database info may be incomplete and provide insights based on what they've shared."""
        
        response = model.generate_content(context_str)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error: {str(e)}\n\nTry asking me to analyze or compare specific products!"
    """Get AI response using Gemini with context about analyzed products."""
    if not GEMINI_AVAILABLE:
        # Fallback response without AI
        return """I don't have AI chat capabilities enabled right now, but I can still help! 
        
Try asking me to:
- **Analyze a product** (e.g., "Analyze Doritos")
- **Compare products** you've already analyzed
- **Show alternatives** for products I've analyzed

Or you can ask specific questions about the analyzed products in the sidebar."""
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash-exp')
        
        # Build context from analyzed products
        context_str = "You are a friendly food health assistant. Here's what we've analyzed so far:\n\n"
        for name, data in context.items():
            if not data.get("error"):
                context_str += f"**{name}:**\n"
                context_str += f"- NOVA Group: {data['nova_classification']['nova_group']}\n"
                context_str += f"- Health Score: {data['health_score']['health_score']}/100\n"
                context_str += f"- Ingredients: {data['product_data'].get('ingredients', 'N/A')[:150]}...\n\n"
        
        context_str += f"\nUser's question: {user_message}\n\n"
        context_str += """Please provide a helpful, friendly response. If they ask about:
- Specific ingredients: explain what they are and health impacts
- Comparisons: compare the analyzed products
- Recommendations: suggest based on NOVA groups and health scores
- General questions: provide educational information about nutrition and food processing

Keep responses concise but informative. Use emojis sparingly."""
        
        response = model.generate_content(context_str)
        return response.text
    except Exception as e:
        return f"Sorry, I encountered an error with AI chat: {str(e)}\n\nTry asking me to analyze a specific product instead!"


def display_chat_message(role, content):
    """Display a chat message."""
    if role == "user":
        st.markdown(f'<div class="chat-message user-message">👤 **You:** {content}</div>', 
                   unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-message assistant-message">🤖 **Assistant:** \n\n{content}</div>', 
                   unsafe_allow_html=True)


def main():
    """Main Streamlit app."""
    
    # Header
    st.markdown('<div class="main-header">🍎 Food Health AI Chat</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ask me anything about food products, ingredients, or nutrition!</div>', 
               unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("📊 Analyzed Products")
        
        if st.session_state.analyzed_products:
            for name, data in st.session_state.analyzed_products.items():
                if not data.get("error"):
                    nova_group = data['nova_classification']['nova_group']
                    score = data['health_score']['health_score']
                    
                    with st.expander(f"🍴 {name}"):
                        st.write(f"**NOVA Group:** {nova_group}")
                        st.write(f"**Health Score:** {score}/100")
                        if st.button(f"View details", key=f"view_{name.replace(' ', '_')}"):
                            msg = format_product_analysis(data, name)
                            st.session_state.messages.append({"role": "user", "content": f"Tell me about {name}"})
                            st.session_state.messages.append({"role": "assistant", "content": msg})
                            st.rerun()
        else:
            st.info("No products analyzed yet. Try asking to analyze a product!")
        
        st.markdown("---")
        
        st.header("💡 Try asking:")
        suggestions = [
            "Analyze Nutella",
            "Compare Coca-Cola and Pepsi",
            "What is maltodextrin?",
            "Is palm oil bad for you?",
            "Show me healthier alternatives",
            "What does NOVA Group 4 mean?"
        ]
        
        for idx, suggestion in enumerate(suggestions):
            if st.button(suggestion, key=f"suggest_btn_{idx}", use_container_width=True):
                # Add message to trigger processing
                st.session_state.messages.append({"role": "user", "content": suggestion})
                # Set a flag to process this message
                st.session_state.should_process = True
                st.rerun()
        
        st.markdown("---")
        
        # AI Status
        if not GEMINI_AVAILABLE:
            st.info("ℹ️ **AI Chat (Optional)**\n\nFor ingredient questions, install:\n```\npip install google-generativeai\n```\nComparisons work without AI!")
        
        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.analyzed_products = {}
            st.session_state.should_process = False
            st.rerun()
    
    # Main chat area
    st.markdown("---")
    
    # Display chat history
    for message in st.session_state.messages:
        with st.container():
            if message["role"] == "user":
                st.markdown(f"**👤 You:** {message['content']}")
            else:
                st.markdown(f"**🤖 Assistant:**")
                st.markdown(message["content"])
    
    # Chat input
    st.markdown("---")
    
    user_input = st.chat_input("Ask about a product, ingredient, or nutrition topic...")
    
    # Process messages - either from chat input or button clicks
    should_process_now = False
    message_to_process = None
    
    if user_input:
        # New message from chat input
        st.session_state.messages.append({"role": "user", "content": user_input})
        message_to_process = user_input
        should_process_now = True
    elif st.session_state.should_process and st.session_state.messages:
        # Message from button click
        last_msg = st.session_state.messages[-1]
        if last_msg["role"] == "user" and last_msg["content"] != st.session_state.last_processed_message:
            message_to_process = last_msg["content"]
            should_process_now = True
        st.session_state.should_process = False
    
    if should_process_now and message_to_process:
        # Mark this message as processed
        st.session_state.last_processed_message = message_to_process
        
        # Check if user is providing custom ingredients
        has_ingredient_keywords = any(word in message_to_process.lower() for word in 
                                     ["ingredients are", "ingredients:", "here are the ingredients", "contains"])
        
        # Check if they're asking to re-analyze with new info
        is_reanalyze = "re-analyze" in message_to_process.lower() or "reanalyze" in message_to_process.lower()
        
        # Check for comparison request
        is_comparison = "compare" in message_to_process.lower() and " and " in message_to_process.lower()
        
        # Determine if this is a product analysis request
        is_analysis = any(word in message_to_process.lower() for word in 
                         ["analyze", "check", "look up", "search", "tell me about"])
        
        response = ""
        
        if has_ingredient_keywords and len(st.session_state.messages) > 1:
            # User is providing custom ingredients - try to determine which product
            # Look at recent messages to find product name
            product_name = None
            for msg in reversed(st.session_state.messages[:-1]):
                if msg["role"] == "user":
                    # Check if message mentions a product
                    for analyzed_product in st.session_state.analyzed_products.keys():
                        if analyzed_product.lower() in msg["content"].lower():
                            product_name = analyzed_product
                            break
                if product_name:
                    break
            
            if product_name:
                # Extract ingredients from message
                ingredients = message_to_process
                for phrase in ["ingredients are", "ingredients:", "here are the ingredients", "contains"]:
                    if phrase in ingredients.lower():
                        ingredients = ingredients[ingredients.lower().index(phrase) + len(phrase):].strip()
                        break
                
                with st.spinner(f"Re-analyzing {product_name} with provided ingredients..."):
                    analysis = analyze_with_custom_ingredients(product_name, ingredients)
                    
                    # Update stored analysis
                    st.session_state.analyzed_products[f"{product_name} (Updated)"] = analysis
                    
                    response = f"### ✅ Re-analyzed {product_name} with your ingredients!\n\n"
                    response += format_product_analysis(analysis, product_name)
            else:
                response = get_ai_response(message_to_process, st.session_state.analyzed_products)
        
        elif is_comparison:
            # Extract product names from comparison request
            parts = message_to_process.lower().split("compare")[-1].split(" and ")
            product_names = [p.strip().title() for p in parts if len(p.strip()) > 2]
            
            # Check if products need to be analyzed first
            products_to_analyze = []
            for name in product_names:
                found = False
                for analyzed_name in st.session_state.analyzed_products.keys():
                    if name.lower() in analyzed_name.lower() or analyzed_name.lower() in name.lower():
                        found = True
                        break
                if not found:
                    products_to_analyze.append(name)
            
            # Analyze missing products
            if products_to_analyze:
                response = f"Let me analyze these products first:\n\n"
                for product in products_to_analyze:
                    with st.spinner(f"Analyzing {product}..."):
                        analysis = analyze_product(product)
                        st.session_state.analyzed_products[product] = analysis
                        if not analysis.get("error"):
                            response += f"✅ {product} analyzed\n"
                        else:
                            response += f"❌ Could not find {product}\n"
                response += "\n"
            
            # Now compare
            response += compare_products(product_names)
        
        elif is_analysis:
            # Try to extract product name
            product_name = None
            
            # Remove common phrases to isolate product name
            clean_msg = message_to_process.lower()
            for phrase in ["analyze ", "check ", "look up ", "tell me about ", "search for ", "what is ", "what's "]:
                if phrase in clean_msg:
                    start = clean_msg.index(phrase) + len(phrase)
                    product_name = message_to_process[start:].strip()
                    product_name = product_name.rstrip('?.!')
                    break
            
            if product_name:
                with st.spinner(f"Analyzing {product_name}..."):
                    analysis = analyze_product(product_name)
                    st.session_state.analyzed_products[product_name] = analysis
                    response = format_product_analysis(analysis, product_name)
            else:
                response = "I'm not sure which product you want me to analyze. Could you please specify the product name?"
        else:
            # General question - use AI if available
            response = get_ai_response(message_to_process, st.session_state.analyzed_products)
        
        # Add assistant response
        st.session_state.messages.append({"role": "assistant", "content": response})
        
        st.rerun()
    
    # Quick action buttons
    if not st.session_state.messages:
        st.markdown("### 🚀 Get Started")
        st.write("Try analyzing a product or ask a nutrition question!")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🍫 Analyze Nutella", use_container_width=True, key="quick_nutella"):
                st.session_state.messages.append({"role": "user", "content": "Analyze Nutella"})
                st.session_state.should_process = True
                st.rerun()
        
        with col2:
            if st.button("🥤 Analyze Coca-Cola", use_container_width=True, key="quick_coke"):
                st.session_state.messages.append({"role": "user", "content": "Analyze Coca-Cola"})
                st.session_state.should_process = True
                st.rerun()
        
        with col3:
            if st.button("❓ What is NOVA?", use_container_width=True, key="quick_nova"):
                st.session_state.messages.append({"role": "user", "content": "What is the NOVA classification system?"})
                st.session_state.should_process = True
                st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.85rem;'>
        <p>Powered by Open Food Facts | NOVA Classification System | Google Gemini AI</p>
        <p>⚠️ For informational purposes only. Consult healthcare professionals for personalized advice.</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()