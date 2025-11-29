import pandas as pd
import streamlit as st

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
# TYPE LIST
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

        # ----- FIX COLUMNS to match the app -----
        df = df.rename(columns={
            "card_sell": "sell_price",
            "market_raw": "price"
        })

        df["price"] = df["price"].apply(clean_price)
        df["sell_price"] = df["sell_price"].apply(clean_price)

        return df
    except Exception as e:
        print("Error loading cards:", e)
        return pd.DataFrame()

# -----------------------------------------------------
# LOAD SLABS
# -----------------------------------------------------
@st.cache_data(ttl=300)
def load_slabs():
    try:
        df = pd.read_csv(SLABS_SHEET_URL)

        df = df.rename(columns={
            "Price": "price",
            "sell_price": "sell_price"
        })

        df["price"] = df["price"].apply(clean_price)
        df["sell_price"] = df["sell_price"].apply(clean_price)

        return df
    except Exception as e:
        print("Error loading slabs:", e)
        return pd.DataFrame()
