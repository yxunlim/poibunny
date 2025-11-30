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

import streamlit as st
import pandas as pd

# -----------------------------------------------------
# GOOGLE SHEET URLS
# -----------------------------------------------------

CARDS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lTiPG_g1MFD6CHvbNCjXOlfYNnHo95QvXNwFK5aX_aw/export?format=csv&gid=533371784"
)

SLABS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1LSSAQdQerNWTci5ufYYBr_J3ZHUSlVRyW-rSHkvGqf4/export?format=csv&gid=44140124"
)

# -----------------------------------------------------
# CLEAN PRICE
# -----------------------------------------------------
def clean_price(x):
    try:
        return float(str(x).replace("$", "").replace(",", "").strip())
    except:
        return 0.0

# -----------------------------------------------------
# TYPE LIST (for filtering)
# -----------------------------------------------------
def build_types(df: pd.DataFrame):
    if df is None or df.empty or "type" not in df.columns:
        return []

    priority = ["Pokemon", "One Piece", "Magic the Gathering"]
    priority_lower = [p.lower() for p in priority]

    raw_types = [
        str(t).strip()
        for t in df["type"].dropna().unique()
        if str(t).strip() != ""
    ]

    priority_found = [
        name for name in priority
        if name.lower() in [t.lower() for t in raw_types]
    ]

    rest = sorted([
        t.title()
        for t in raw_types
        if t.lower() not in priority_lower
    ])

    return priority_found + rest

# -----------------------------------------------------
# LOAD CARDS
# -----------------------------------------------------
@st.cache_data(ttl=300)
def load_cards():
    try:
        df = pd.read_csv(CARDS_SHEET_URL)

        # Normalize column names
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        # Rename to match the app logic
        df = df.rename(columns={
            "card_sell": "sell_price",
            "market_raw": "price"     # Market Raw → price
        })

        df["price"] = df["price"].apply(clean_price)
        df["sell_price"] = df["sell_price"].apply(clean_price)

        return df
    except Exception as e:
        st.error(f"Error loading cards: {e}")
        return pd.DataFrame()

# -----------------------------------------------------
# LOAD SLABS
# -----------------------------------------------------
@st.cache_data(ttl=300)
def load_slabs():
    try:
        df = pd.read_csv(SLABS_SHEET_URL)

        # Normalize names
        df.columns = df.columns.str.lower().str.replace(" ", "_")

        df = df.rename(columns={
            "price": "price",
            "sell_price": "sell_price"
        })

        df["price"] = df["price"].apply(clean_price)
        df["sell_price"] = df["sell_price"].apply(clean_price)

        return df
    except Exception as e:
        st.error(f"Error loading slabs: {e}")
        return pd.DataFrame()

# -----------------------------------------------------
# DISPLAY CARDS (GRID VIEW)
# -----------------------------------------------------
def display_cards(cards_df):
    st.markdown("## 🃏 Raw Card Inventory")

    if cards_df.empty:
        st.warning("No card data available.")
        return

    # Filters
    st.markdown("### 🔍 Filters")
    unique_sets = sorted(cards_df["set"].dropna().unique())
    unique_conditions = sorted(cards_df["condition"].dropna().unique())
    unique_types = sorted(cards_df["type"].dropna().unique())

    selected_set = st.selectbox("Set", ["All"] + unique_sets)
    selected_condition = st.selectbox("Condition", ["All"] + unique_conditions)
    selected_type = st.selectbox("Type", ["All"] + unique_types)

    filtered = cards_df.copy()
    if selected_set != "All":
        filtered = filtered[filtered["set"] == selected_set]
    if selected_condition != "All":
        filtered = filtered[filtered["condition"] == selected_condition]
    if selected_type != "All":
        filtered = filtered[filtered["type"] == selected_type]

    st.markdown(f"### 📦 Showing {len(filtered)} cards")

    # GRID DISPLAY
    cols_per_row = 3
    rows = (len(filtered) + cols_per_row - 1) // cols_per_row

    for i in range(rows):
        row_cards = filtered.iloc[i * cols_per_row: (i+1) * cols_per_row]
        cols = st.columns(cols_per_row)

        for col, (_, card) in zip(cols, row_cards.iterrows()):
            with col:
                st.image(card.get("image_link", ""), width=180)
                st.markdown(f"**{card.get('name', 'Unknown')}**")
                st.write(f"Set: {card.get('set', 'Unknown')}")
                st.write(f"Condition: {card.get('condition', 'N/A')}")
                st.write(f"Type: {card.get('type','Unknown')}")
                st.write(f"Quantity: {int(card.get('quantity', 0))}")
                st.markdown(f"**Market Raw:** ${card.get('price', 0):,.2f}")
                st.markdown(f"**My Price:** ${card.get('sell_price', 0):,.2f}")

                tcg = card.get("link_on_tcg_player", "")
                if isinstance(tcg, str) and tcg.startswith("http"):
                    st.link_button("🔗 TCGPlayer", tcg)

# -----------------------------------------------------
# DISPLAY SLABS (GRID VIEW)
# -----------------------------------------------------
def display_slabs(slabs_df):
    st.markdown("## 🏅 Graded Slabs")

    if slabs_df.empty:
        st.warning("No slab data available.")
        return

    # Filters
    st.markdown("### 🔍 Filters")
    unique_grades = sorted(slabs_df["cardgrade"].dropna().unique())
    unique_brands = sorted(slabs_df["brand"].dropna().unique())

    selected_brand = st.selectbox("Brand", ["All"] + unique_brands)
    selected_grade = st.selectbox("Grade", ["All"] + unique_grades)

    filtered = slabs_df.copy()
    if selected_brand != "All":
        filtered = filtered[filtered["brand"] == selected_brand]
    if selected_grade != "All":
        filtered = filtered[filtered["cardgrade"] == selected_grade]

    st.markdown(f"### 📦 Showing {len(filtered)} slabs")

    # GRID DISPLAY
    cols_per_row = 3
    rows = (len(filtered) + cols_per_row - 1) // cols_per_row

    for i in range(rows):
        row_slabs = filtered.iloc[i * cols_per_row: (i+1) * cols_per_row]
        cols = st.columns(cols_per_row)

        for col, (_, slab) in zip(cols, row_slabs.iterrows()):
            with col:
                st.image(slab.get("image_link", ""), width=180)
                st.markdown(f"**{slab.get('subject', 'Unknown')}**")
                st.write(f"Brand: {slab.get('brand', 'Unknown')}")
                st.write(f"Grade: {slab.get('cardgrade','N/A')}")

                st.markdown(f"**Market Raw:** ${slab.get('raw', 0):,.2f}")
                st.markdown(f"**My Price:** ${slab.get('sell_price', 0):,.2f}")

                link = slab.get("link", "")
                if isinstance(link, str) and link.startswith("http"):
                    st.link_button("🔗 Listing", link)

# -----------------------------------------------------
# MAIN APP
# -----------------------------------------------------
st.title("📘 Card & Slab Inventory")

tabs = ["Raw Cards", "Graded Slabs"]
choice = st.radio("Select a category:", tabs)

if choice == "Raw Cards":
    cards_df = load_cards()
    display_cards(cards_df)

elif choice == "Graded Slabs":
    slabs_df = load_slabs()
    display_slabs(slabs_df)
