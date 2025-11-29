import pandas as pd
import streamlit as st

# -----------------------------------------------------
# GOOGLE SHEETS SOURCE (edit if needed)
# -----------------------------------------------------
CARDS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lTiPG_g1MFD6CHvbNCjXOlfYNnHo95QvXNwFK5aX_aw/export?format=csv&gid=0"
)

# -----------------------------------------------------
# LOAD CARDS DATA
# -----------------------------------------------------
@st.cache_data(ttl=300)
def load_cards():
    """Loads card data from Google Sheets and returns a DataFrame."""
    try:
        df = pd.read_csv(CARDS_SHEET_URL)
        # Normalize column names to lower for robustness (optional)
        # df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Failed to load Cards sheet: {e}")
        return pd.DataFrame()


# -----------------------------------------------------
# CLEAN PRICE FIELD
# -----------------------------------------------------
def clean_price(x):
    """Converts price strings like '$1,234.56' into floats; returns 0.0 on failure."""
    try:
        return float(str(x).replace("$", "").replace(",", "").strip())
    except:
        return 0.0


# -----------------------------------------------------
# BUILD LIST OF ALL CARD TYPES
# -----------------------------------------------------
def build_types(df: pd.DataFrame):
    """
    Generates an ordered list of types.
    Priority types (Pokemon, One Piece, Magic the Gathering) are placed first if present.
    """
    if df is None or df.empty or "type" not in df.columns:
        return []

    priority_display = ["Pokemon", "One Piece", "Magic the Gathering"]
    priority_lookup = [p.lower() for p in priority_display]

    raw_types = [
        t.strip()
        for t in df["type"].dropna().unique()
        if str(t).strip() != ""
    ]

    # preserve priority order only if present
    priority_types = [
        disp for disp, key in zip(priority_display, priority_lookup)
        if key in [r.lower() for r in raw_types]
    ]

    remaining_types = sorted([
        t.title() for t in raw_types
        if t.lower() not in priority_lookup
    ])

    return priority_types + remaining_types
