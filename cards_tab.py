import pandas as pd
import streamlit as st

# -----------------------------------------------------
# GOOGLE SHEET BASE URL (same for both sheets)
# -----------------------------------------------------
GOOGLE_SHEET_BASE = (
    "https://docs.google.com/spreadsheets/d/"
    "1lTiPG_g1MFD6CHvbNCjXOlfYNnHo95QvXNwFK5aX_aw/export?format=csv&gid="
)

CARDS_GID = "0"              # Sheet 1 = Cards
SLABS_GID = "1192341408"     # Sheet 2 = Slabs  ← update if needed

CARDS_SHEET_URL = GOOGLE_SHEET_BASE + CARDS_GID
SLABS_SHEET_URL = GOOGLE_SHEET_BASE + SLABS_GID

# -----------------------------------------------------
# LOADERS
# -----------------------------------------------------
@st.cache_data(ttl=300)
def load_cards():
    """Load Sheet 1 (Cards)."""
    try:
        return pd.read_csv(CARDS_SHEET_URL)
    except Exception:
        return pd.DataFrame()


@st.cache_data(ttl=300)
def load_slabs():
    """Load Sheet 2 (Slabs) from the same Google Sheet URL."""
    try:
        return pd.read_csv(SLABS_SHEET_URL)
    except Exception:
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
# BUILD LIST OF CARD TYPES
# -----------------------------------------------------
def build_types(df: pd.DataFrame):
    """
    Generates an ordered list of types.
    Priority types (Pokemon, One Piece, Magic the Gathering) appear first.
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

    priority_types = [
        disp for disp, key in zip(priority_display, priority_lookup)
        if key in [r.lower() for r in raw_types]
    ]

    remaining_types = sorted([
        t.title() for t in raw_types
        if t.lower() not in priority_lookup
    ])

    return priority_types + remaining_types

# -----------------------------------------------------
# RENDERING FUNCTIONS (used by main app)
# -----------------------------------------------------
def render_cards_tab():
    st.header("Cards")

    df = load_cards()
    if df.empty:
        st.warning("No card data found.")
        return

    types = build_types(df)
    selected_type = st.selectbox("Select Type", ["All"] + types)

    if selected_type != "All":
        df = df[df["type"].str.lower() == selected_type.lower()]

    st.dataframe(df)


def render_slabs_tab():
    st.header("Slabs")

    df = load_slabs()
    if df.empty:
        st.warning("No slab data found.")
        return

    st.dataframe(df)
