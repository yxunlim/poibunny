import streamlit as st
import pandas as pd
from cards_tab import display_cards_tab
from slabs_tab import display_slabs_tab

# Load Google Sheets CSV
def load_google_sheet(csv_url):
    try:
        df = pd.read_csv(csv_url, on_bad_lines="skip", encoding="utf-8")
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
        return df
    except Exception as e:
        st.error(f"Error loading sheet: {e}")
        return pd.DataFrame()

# URLs
cards_sheet_url = st.secrets["google_sheets"]["cards_sheet_url"]
slabs_sheet_url = st.secrets["google_sheets"]["slabs_sheet_url"]

# Load Data
cards_df = load_google_sheet(cards_sheet_url)
slabs_df = load_google_sheet(slabs_sheet_url)

# ---------------------------------------------------------
# FIX COLUMN MISMATCHES
# ---------------------------------------------------------
# cards_df columns expected:
# item_no, name, set, condition, card_sell, image_link, market_raw, link_on_tcg_player, type, quantity

# Normalize missing columns
cards_df["market_raw"] = pd.to_numeric(cards_df.get("market_raw", 0), errors="coerce").fillna(0)
cards_df["card_sell"] = pd.to_numeric(cards_df.get("card_sell", 0), errors="coerce").fillna(0)

# Slabs sheet fixes
slabs_df["raw"] = pd.to_numeric(slabs_df.get("raw", 0), errors="coerce").fillna(0)
slabs_df["price"] = pd.to_numeric(slabs_df.get("price", 0), errors="coerce").fillna(0)

# ---------------------------------------------------------
# Featured Cards Section
# ---------------------------------------------------------
st.markdown("## ⭐ Featured Cards")

if not cards_df.empty:
    temp_df = cards_df.copy()
    
    # Use market_raw as the weight
    temp_df["market_price_clean"] = temp_df["market_raw"].fillna(0)

    # Avoid divide-by-zero
    if temp_df["market_price_clean"].sum() == 0:
        weights = None
    else:
        weights = temp_df["market_price_clean"] + 1
        weights = weights / weights.sum()

    # Random selection
    featured_count = 6
    featured_cards = temp_df.sample(
        n=min(featured_count, len(temp_df)),
        weights=weights,
        replace=False
    )

    # Display featured cards
    for _, row in featured_cards.iterrows():
        st.image(row.get("image_link", ""), width=200)
        st.write(f"**{row.get('name','Unknown')}**")
        st.write(f"Set: {row.get('set','Unknown')}")
        st.write(f"Condition: {row.get('condition','N/A')}")
        st.write(f"Market Raw: ${row.get('market_raw', 0):,.2f}")
        st.write(f"My Sell Price: ${row.get('card_sell', 0):,.2f}")
        st.markdown("---")

else:
    st.warning("No cards found in sheet.")

# ---------------------------------------------------------
# Navigation Tabs
# ---------------------------------------------------------
st.markdown("## 📁 Inventory Sections")

tabs = [
    "🔹 Card Inventory",
    "📦 Slabs & Graded Cards"
]

selected_tab = st.radio("Select a section:", tabs)

if selected_tab == "🔹 Card Inventory":
    display_cards_tab(cards_df)

elif selected_tab == "📦 Slabs & Graded Cards":
    display_slabs_tab(slabs_df)
