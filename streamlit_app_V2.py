# Streamlit Food Health AI Agent — Redesigned (Food Wellness style, bottom chat)
# Requirements:
#   pip install streamlit deep-translator langdetect (langdetect optional but recommended)
# This file replaces googletrans with deep-translator and implements a two-panel layout
# (product info + controls) with a bottom conversational chat panel that persists context.

import streamlit as st
import json
import time
from typing import Dict, Any

# External project tools (keep your original logic)
from PRODUCT_AGENT.tools import (
    openfoodfacts_lookup,
    classify_nova,
    compute_health_score,
    suggest_alternatives,
)

# deep-translator
from deep_translator import GoogleTranslator

# Optional language detection
try:
    from langdetect import detect
    LANGDETECT_AVAILABLE = True
except Exception:
    LANGDETECT_AVAILABLE = False

# Translator instances
INPUT_TRANSLATOR = GoogleTranslator(source="auto", target="en")
# We'll create output translators on the fly when we know the target language.

# ------------------------------
# App configuration & styling
# ------------------------------
st.set_page_config(
    page_title="Food Wellness — Health AI",
    page_icon="🍃",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Food Wellness CSS
st.markdown(
    """
    <style>
    /* Page background */
    .stApp {
        background: linear-gradient(180deg, #f7fbf7 0%, #ffffff 100%);
    }

    /* Header */
    .fw-header { text-align: left; padding: 18px; }
    .fw-title { font-size: 2.2rem; font-weight: 700; color: #2b5d34; margin: 0; }
    .fw-sub { color: #406a45; margin-top: 6px; }

    /* Cards */
    .fw-card { background: white; border-radius: 12px; box-shadow: 0 6px 18px rgba(67,90,57,0.08); padding: 16px; }

    /* Nova badge */
    .nova-badge { padding: 8px 12px; border-radius: 999px; color: white; font-weight: 600; }

    /* Chat input */
    .chat-input { margin-top: 10px; }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------
# Session state initialization
# ------------------------------
if "product_data" not in st.session_state:
    st.session_state.product_data = {}

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None

if "messages" not in st.session_state:
    # messages: list of dicts {role: 'user'|'assistant'|'system', content: str, lang: str}
    st.session_state.messages = []

if "user_lang" not in st.session_state:
    st.session_state.user_lang = "en"

# ------------------------------
# Translation helpers
# ------------------------------

def translate_to_english(text: str) -> str:
    """Translate arbitrary text to English using deep-translator.

    Falls back to returning the original text on failure. Skips trivial ASCII.
    """
    if not text or not isinstance(text, str):
        return text

    if text.strip() and text.isascii():
        return text

    try:
        translated = INPUT_TRANSLATOR.translate(text)
        return translated
    except Exception as e:
        st.warning(f"Translation failed: {e} — returning original text.")
        return text


def detect_language(text: str) -> str:
    """Detect language using langdetect if available, else return 'en'."""
    if not text or not isinstance(text, str):
        return "en"
    if LANGDETECT_AVAILABLE:
        try:
            lang = detect(text)
            return lang
        except Exception:
            return "en"
    return "en"


def translate_from_english(text: str, target_lang: str) -> str:
    """Translate English text into target_lang using deep-translator.
    If target_lang is 'en' or None, returns original text.
    """
    if not text or target_lang in (None, "en", "eng"):
        return text

    try:
        out_tr = GoogleTranslator(source="en", target=target_lang)
        return out_tr.translate(text)
    except Exception:
        # If translation fails, silently return English text
        return text


# ------------------------------
# Product translation
# ------------------------------

def translate_product_data(product_data: Dict[str, Any]) -> Dict[str, Any]:
    """Translate key textual fields in the product data to English for processing and display.
    We keep original fields untouched under _original_* keys for traceability.
    """
    if not product_data or product_data.get("error"):
        return product_data

    translated = dict(product_data)  # shallow copy

    text_fields = [
        ("product_name", "_original_product_name"),
        ("brand", "_original_brand"),
        ("ingredients", "_original_ingredients"),
        ("allergens", "_original_allergens"),
    ]

    for field, original_field in text_fields:
        if product_data.get(field):
            translated[original_field] = product_data.get(field)
            translated[field] = translate_to_english(product_data.get(field))

    if product_data.get("ingredients_list"):
        translated["_original_ingredients_list"] = product_data.get("ingredients_list")
        translated["ingredients_list"] = [
            translate_to_english(x) for x in product_data.get("ingredients_list", [])
        ]

    return translated


# ------------------------------
# Lightweight QA responder (uses structured data)
# ------------------------------

def simple_qa_response(product: Dict[str, Any], question: str) -> str:
    """Produce a helpful, context-aware answer about the product using simple heuristics.
    This is a placeholder assistant — for full natural answers connect this to an LLM.
    """
    q = question.lower()

    # Quick helpers
    nutrients = product.get("nutrients", {})
    nova_group = product.get("nova_group") or product.get("nova", {}).get("group")

    # If user asks to compare
    if "compare to" in q or q.startswith("compare") or "vs" in q:
        # Naive: suggest to search another product
        return (
            "I can compare this product to another. Type the other product name in the search box, "
            "or ask: 'Compare this to [product name]'."
        )

    # Sugar-related
    if "sugar" in q:
        sugar = nutrients.get("sugar_g_per_100g") or nutrients.get("sugars") or nutrients.get("sugar")
        if sugar is None:
            return "Sugar data isn't available for this product."
        try:
            val = float(sugar)
        except Exception:
            return f"Sugar: {sugar} (raw data)."

        if val >= 22:
            advice = "This is a very high sugar level for a per-100g serving — consider limiting intake."
        elif val >= 10:
            advice = "Moderately high sugar — could be ok in small portions."
        else:
            advice = "Relatively low sugar per 100g."

        return f"Sugar: {val} g per 100g. {advice}"

    # Salt / sodium
    if "salt" in q or "sodium" in q:
        salt = nutrients.get("salt_g_per_100g") or nutrients.get("salt") or nutrients.get("sodium")
        if salt is None:
            return "Salt data isn't available for this product."
        try:
            sval = float(salt)
        except Exception:
            return f"Salt: {salt} (raw data)."
        if sval >= 1.5:
            comment = "High salt — not suitable for low-sodium diets."
        elif sval >= 0.3:
            comment = "Moderate salt — be mindful if consuming frequently."
        else:
            comment = "Low salt."
        return f"Salt: {sval} g per 100g. {comment}"

    # NOVA
    if "nova" in q or "processed" in q or "ultra" in q:
        group = nova_group or "unknown"
        explanation = {
            1: "Group 1: Unprocessed or minimally processed foods — generally healthier.",
            2: "Group 2: Processed culinary ingredients — need moderation.",
            3: "Group 3: Processed foods — often contain added sugar/salt/fat.",
            4: "Group 4: Ultra-processed foods — typically less healthy for frequent consumption.",
        }.get(group, "NOVA group information not available.")
        return explanation

    # Allergens
    if "allerg" in q:
        allergens = product.get("allergens") or product.get("allergens_tags")
        if not allergens:
            return "No allergen information found in the product data."
        return f"Allergens listed: {allergens}"

    # Additives
    if "additive" in q or "e-number" in q or "e number" in q:
        additives = product.get("additives") or product.get("additives_tags")
        if not additives:
            return "No additive information found for this product."
        return f"Additives: {additives}\nIf you tell me which additive you are concerned about, I can explain it." 

    # Alternatives
    if "alternative" in q or "healthier" in q or "better" in q:
        alts = suggest_alternatives(product, limit=3)
        if alts.get("alternatives"):
            lines = []
            for a in alts["alternatives"]:
                lines.append(f"{a.get('name')} ({a.get('brand', 'Unknown')}) — NOVA {a.get('nova_group')} — {a.get('reason')}")
            return "Here are some healthier alternatives:\n" + "\n".join(lines)
        return "I couldn't find alternatives automatically. Try a different search or ask to compare with a specific product."

    # Diabetes / general safety
    if "diabet" in q or "diabetes" in q:
        sugar = nutrients.get("sugar_g_per_100g") or nutrients.get("sugars")
        if sugar:
            try:
                sval = float(sugar)
                if sval > 10:
                    return "This product is relatively high in sugar per 100g — people with diabetes should consult a healthcare provider and prefer smaller portions."
                else:
                    return "Sugar per 100g is moderate to low, but portion size matters for blood glucose management."
            except Exception:
                return "Sugar data present but not numeric — interpret with caution."
        return "Sugar information is unavailable — cannot assess diabetes suitability."

    # If not matched, provide a general summary
    # Use product name, nova, and a short health summary
    pname = product.get("product_name") or product.get("_original_product_name") or "This product"
    summary_parts = []
    if nova_group:
        summary_parts.append(f"NOVA group: {nova_group}.")
    if nutrients:
        su = nutrients.get("sugar_g_per_100g") or nutrients.get("sugars")
        if su:
            summary_parts.append(f"Sugar (per 100g): {su}.")
    if not summary_parts:
        return f"I don't have specific info for that question. You can ask about sugar, salt, NOVA, additives, allergens, or ask for alternatives."

    return f"{pname}: " + " ".join(summary_parts)


# ------------------------------
# UI Components
# ------------------------------

def render_header():
    st.markdown(
        "<div class='fw-header'><h1 class='fw-title'>🍃 Food Wellness — Health AI</h1>"
        "<div class='fw-sub'>Explore product healthiness, ask follow-up questions, and get friendly, actionable guidance.</div></div>",
        unsafe_allow_html=True,
    )


def render_left_panel(product_data: Dict[str, Any], analysis_results: Dict[str, Any]):
    """Render persistent left panel with product info and cards."""
    st.markdown("<div class='fw-card'>", unsafe_allow_html=True)

    # Top row: image + basic info
    col1, col2 = st.columns([1, 3])
    with col1:
        img_url = product_data.get("image_front_url") or product_data.get("image_url")
        if img_url:
            st.image(img_url, use_column_width=True, caption=product_data.get("product_name"))
        else:
            st.empty()

    with col2:
        st.markdown(f"### {product_data.get('product_name', 'Unknown product')}")
        st.markdown(f"**Brand:** {product_data.get('brand', 'Unknown')}")
        # Nova badge
        ng = analysis_results.get("nova_classification", {}).get("nova_group") if analysis_results else product_data.get("nova_group")
        if ng:
            color = {1: '#2b8a3e', 2: '#6fbf73', 3: '#f0a43a', 4: '#e03b3b'}.get(ng, '#999')
            st.markdown(f"<span class='nova-badge' style='background:{color}'>NOVA {ng}</span>", unsafe_allow_html=True)

    st.markdown("---")

    # Health summary
    st.markdown("#### Health Summary")
    if analysis_results:
        hs = analysis_results.get("health_score", {})
        score = hs.get("health_score", None)
        interp = hs.get("interpretation", "")
        if score is not None:
            st.metric(label="Health Score", value=f"{score}/100", delta=None)
            st.write(interp)
        else:
            st.write("No health score available.")
    else:
        st.write("Search for a product to see a health summary.")

    st.markdown("---")

    # Nutritional mini table
    st.markdown("#### Quick Nutrition (per 100g)")
    nutrients = analysis_results.get("health_score", {}).get("breakdown", {}) if analysis_results else product_data.get("nutrients", {})

    cols = st.columns(5)
    keys = [
        ("sugar_g_per_100g", "Sugar"),
        ("saturated_fat_g_per_100g", "Sat Fat"),
        ("salt_g_per_100g", "Salt"),
        ("fiber_g_per_100g", "Fiber"),
        ("protein_g_per_100g", "Protein"),
    ]
    for c, (k, label) in zip(cols, keys):
        with c:
            val = nutrients.get(k) if nutrients else None
            st.metric(label, f"{val or 0} g")

    st.markdown("---")

    # Ingredients & additives accordion
    with st.expander("Ingredients & Additives", expanded=False):
        if product_data.get("ingredients_list"):
            for ing in product_data.get("ingredients_list"):
                st.write(f"• {ing}")
        elif product_data.get("ingredients"):
            st.write(product_data.get("ingredients"))
        else:
            st.write("Ingredients not available.")

        if product_data.get("additives"):
            st.write("\n**Additives:**")
            st.write(product_data.get("additives"))

    st.markdown("</div>", unsafe_allow_html=True)


# Chat rendering at bottom
def render_chat_area():
    """Bottom chat panel where user can ask follow-up questions. Preserves conversation in session_state.
    The chat will reference the current product in session_state.product_data.
    """
    st.markdown("---")
    st.markdown("#### Ask the Food Wellness Assistant")

    # Display messages
    msg_box = st.container()
    with msg_box:
        for m in st.session_state.messages:
            role = m.get("role")
            content = m.get("content")
            if role == "user":
                st.markdown(f"<div style='text-align:right; background:#e9f7ef; padding:8px; border-radius:8px; margin:6px;'>{content}</div>", unsafe_allow_html=True)
            elif role == "assistant":
                st.markdown(f"<div style='text-align:left; background:#ffffff; padding:8px; border-radius:8px; margin:6px; box-shadow: 0 4px 10px rgba(67,90,57,0.04);'>{content}</div>", unsafe_allow_html=True)
            else:
                st.info(content)

    # Input area
    cols = st.columns([8, 1])
    with cols[0]:
        user_input = st.text_input("Ask a question about the product (e.g., 'Is this okay for diabetes?')", key="chat_input")
    with cols[1]:
        submit = st.button("Send")

    if submit and user_input:
        # Detect user language
        user_lang = detect_language(user_input)
        st.session_state.user_lang = user_lang

        # Translate input to English for processing
        english_query = translate_to_english(user_input)

        # Append user message
        st.session_state.messages.append({"role": "user", "content": user_input, "lang": user_lang})

        # Generate assistant reply (local heuristics) using product context
        product = st.session_state.product_data or {}
        reply_en = simple_qa_response(product, english_query)

        # If user's language is not English, translate reply back
        if user_lang != "en":
            reply = translate_from_english(reply_en, user_lang)
        else:
            reply = reply_en

        # Append assistant reply
        st.session_state.messages.append({"role": "assistant", "content": reply, "lang": "en"})

        # Clear input
        st.session_state.chat_input = ""

        # Scroll / small delay for UX
        time.sleep(0.1)
        st.experimental_rerun()


# ------------------------------
# Main analysis flow
# ------------------------------

def analyze_product_flow(name: str):
    """Run the analysis pipeline and store results in session_state.
    This mirrors your original analyze_product but simplified for integration.
    """
    # Local progress indicators
    placeholder = st.empty()

    try:
        placeholder.info("🔍 Looking up product — this may take a second...")
        product_data = openfoodfacts_lookup(name)

        if product_data.get("error"):
            placeholder.error(product_data.get("error"))
            return None

        # Translate product data to English for internal processing
        product_data_translated = translate_product_data(product_data)

        placeholder.info("🏷 Classifying NOVA and computing health score...")
        nova_classification = classify_nova(
            product_data_translated.get("ingredients", ""),
            product_data_translated.get("additives", []),
            product_data_translated.get("nova_group")
        )

        health_score = compute_health_score(
            product_data_translated.get("nutrients", {}),
            nova_classification.get("nova_group", 4)
        )

        alternatives = suggest_alternatives(product_data_translated, limit=3)

        results = {
            "product_data": product_data_translated,
            "nova_classification": nova_classification,
            "health_score": health_score,
            "alternatives": alternatives,
        }

        # Save to session
        st.session_state.product_data = product_data_translated
        st.session_state.analysis_results = results

        placeholder.success("✅ Analysis complete!")
        time.sleep(0.6)
        placeholder.empty()

        return results

    except Exception as e:
        placeholder.error(f"Error during analysis: {e}")
        return None


# ------------------------------
# App Layout: Top controls, left info, right controls, bottom chat
# ------------------------------

def main():
    render_header()

    top_cols = st.columns([3, 1])
    with top_cols[0]:
        product_name = st.text_input("Enter a food product or barcode:", placeholder="e.g., Nutella, Coca-Cola, 3017620422003", key="search_box")
    with top_cols[1]:
        search_btn = st.button("Analyze", type="primary")

    # Sidebar: tips & quick actions
    with st.sidebar:
        st.markdown("### ℹ️ About this app")
        st.write("This redesign focuses on conversational follow-ups and clearer wellness guidance.")
        st.markdown("---")
        st.markdown("### Quick actions")
        if st.button("Clear conversation"):
            st.session_state.messages = []
        if st.button("Clear product"):
            st.session_state.product_data = {}
            st.session_state.analysis_results = None
        st.markdown("---")
        st.markdown("### Tips")
        st.write("Ask the assistant contextual questions like:\n - 'Is this okay for kids?'\n - 'Compare sugar to peanut butter'\n - 'Explain the additives' ")

    # Two-column main area
    left_col, right_col = st.columns([1.6, 1])

    with left_col:
        # Product info card
        if st.session_state.analysis_results:
            render_left_panel(st.session_state.product_data, st.session_state.analysis_results)
        else:
            st.markdown("<div class='fw-card'><h3>Search for a product to begin</h3><p>Type a product name and click Analyze.</p></div>", unsafe_allow_html=True)

    with right_col:
        # Small action card: download / regenerate / examples
        st.markdown("<div class='fw-card'>", unsafe_allow_html=True)
        st.markdown("### Actions")
        if st.session_state.analysis_results:
            if st.button("🔄 Re-run analysis"):
                analyze_product_flow(st.session_state.product_data.get("product_name") or product_name)

            st.download_button(
                label="📥 Download Analysis (JSON)",
                data=json.dumps(st.session_state.analysis_results, indent=2),
                file_name=(st.session_state.product_data.get("product_name", "product") + "_analysis.json").replace(" ", "_"),
                mime="application/json",
            )

        st.markdown("---")
        st.markdown("### Examples")
        for ex in ["Nutella", "Coca-Cola", "Yogurt"]:
            if st.button(ex):
                st.session_state.search_box = ex
                st.experimental_rerun()

        st.markdown("</div>", unsafe_allow_html=True)

    # Run analysis if requested
    if search_btn and product_name:
        analyze_product_flow(product_name)

    # Render bottom chat
    render_chat_area()


if __name__ == "__main__":
    main()
