import pandas as pd
import streamlit as st

# -----------------------------------------------------
# GOOGLE SHEET URLS
# -----------------------------------------------------

# Cards sheet (GID = 533371784)
CARDS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lTiPG_g1MFD6CHvbNCjXOlfYNnHo95QvXNwFK5aX_aw/export?format=csv&gid=533371784"
)

# Slabs sheet (GID = 44140124)
SLABS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1LSSAQdQerNWTci5ufYYBr_J3ZHUSlVRyW-rSHkvGqf4/export?format=csv&gid=44140124"
)

# -----------------------------------------------------
# CLEAN PRICE FIELD
# -----------------------------------------------------
def clean_price(x):
    """
    Converts price strings like '$1,234.56', '100', 'N/A', etc.
    into floats.
    """
    try:
        return float(str(x).replace("$", "").replace(",", "").strip())
    except:
        return 0.0

# -----------------------------------------------------
# BUILD TYPE LIST (used by Cards UI)
# -----------------------------------------------------
def build_types(df: pd.DataFrame):
    """
    Generates an ordered list of card types.
    Priority order if present:
        - Pokemon
        - One Piece
        - Magic the Gathering
    """

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
# LOAD CARDS DATA
# -----------------------------------------------------
@st.cache_data(ttl=300)
def load_cards():
    """Loads raw cards from Google Sheets."""
    try:
        df = pd.read_csv(CARDS_SHEET_URL)
        return df
    except Exception as e:
        print("Error loading cards:", e)
        return pd.DataFrame()

# -----------------------------------------------------
# LOAD SLABS DATA
# -----------------------------------------------------
@st.cache_data(ttl=300)
def load_slabs():
    """Loads graded slabs from Google Sheets."""
    try:
        df = pd.read_csv(SLABS_SHEET_URL)
        return df
    except Exception as e:
        print("Error loading slabs:", e)
        return pd.DataFrame()
