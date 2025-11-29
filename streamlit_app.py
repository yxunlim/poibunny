import streamlit as st
import time
import random
import pandas as pd

from cards_tab import load_cards, clean_price, build_types

st.set_page_config(page_title="POiBUNNY", layout="wide")

# ---------------- LOAD DATA (defensive) ----------------
if "cards_df" not in st.session_state:
    st.session_state.cards_df = load_cards()

cards_df = st.session_state.cards_df

# If loader returned empty, show diagnostics and allow upload fallback.
def show_loader_diagnostics(df):
    st.error("⚠️ Unable to load Google Sheet or sheet returned no rows.")
    st.markdown("**Diagnostics**")
    st.write(f"- DataFrame is empty: `{df.empty}`")
    st.write("- Expected columns (if present): `name, type, image_link, set, condition, sell_price, market_price`")
    st.write("Raw dataframe preview (first 10 rows):")
    st.dataframe(df.head(10))

    uploaded = st.file_uploader("Upload a CSV of card data (optional)", type=["csv"])
    if uploaded is not None:
        try:
            df2 = pd.read_csv(uploaded)
            st.session_state.cards_df = df2
            st.success("Uploaded CSV loaded — rerunning app.")
            st.experimental_rerun()
        except Exception as e:
            st.error(f"Failed to read uploaded CSV: {e}")
    else:
        st.info("You can upload a CSV to populate the app, or check your Google Sheet URL/network.")

# If empty, show diagnostics but still continue with a minimal fallback so UI is not blank
if cards_df is None or cards_df.empty:
    show_loader_diagnostics(cards_df if cards_df is not None else pd.DataFrame())
    # Create a tiny fallback dataset so UI renders (user can upload to replace)
    fallback = pd.DataFrame([
        {"name": "Sample Card A", "type": "Pokemon", "image_link": "", "set": "SampleSet", "condition": "NM", "sell_price": "10", "market_price": "$8.00"},
        {"name": "Sample Card B", "type": "One Piece", "image_link": "", "set": "SampleSet2", "condition": "LP", "sell_price": "20", "market_price": "$18.00"},
        {"name": "Sample Card C", "type": "Magic the Gathering", "image_link": "", "set": "SampleSet3", "condition": "MP", "sell_price": "30", "market_price": "$25.00"},
    ])
    cards_df = fallback
    st.session_state.cards_df = cards_df  # store fallback so rest of UI shows something

# Ensure required columns exist
for col in ["name", "type", "image_link", "set", "condition", "sell_price", "market_price"]:
    if col not in cards_df.columns:
        cards_df[col] = ""

# Build list of types
all_types = build_types(cards_df)

# ---------------- SIDEBAR & TABS ----------------
st.sidebar.title("Welcome to my Collection")
st.sidebar.write("Feel free to email me at lynx1186@hotmail.com to purchase my cards")

tab_main, tab_cards, tab_admin = st.tabs(["Main", "Cards", "Admin"])

# ---------------- MAIN PAGE (Featured Carousel - Option A
