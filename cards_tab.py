import streamlit as st
import pandas as pd

# -----------------------------------------------------------------------------
# Google Sheets URL
# -----------------------------------------------------------------------------
CARDS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1lTiPG_g1MFD6CHvbNCjXOlfYNnHo95QvXNwFK5aX_aw/export?format=csv&gid=0"
)

# -----------------------------------------------------------------------------
# Load Cards Data from Google Sheets
# -----------------------------------------------------------------------------
@st.cache_data(ttl=300)
def load_cards():
    """Load card data from the Google Sheets 'Cards' tab."""
    try:
        df = pd.read_csv(CARDS_SHEET_URL)
        return df
    except Exception as e:
        st.error(f"Failed to load Cards sheet: {e}")
        return pd.DataFrame()

# -----------------------------------------------------------------------------
# Cards Tab UI
# -----------------------------------------------------------------------------
def tab_cards():
    st.title("📇 Cards")
    st.write("Browse and filter the Cards sheet.")

    # Load data
    df = load_cards()

    if df.empty:
        st.warning("No card data found.")
        return

    # --- Filters -------------------------------------------------------------
    st.subheader("Filters")

    col1, col2 = st.columns(2)
    with col1:
        name_filter = st.text_input("Search by name")
    with col2:
        type_filter = st.selectbox(
            "Filter by type",
            options=["All"] + sorted(df["type"].astype(str).unique())
        )

    filtered = df.copy()

    if name_filter:
        filtered = filtered[filtered["name"].str.contains(name_filter, case=False, na=False)]

    if type_filter != "All":
        filtered = filtered[filtered["type"] == type_filter]

    # --- Results Table -------------------------------------------------------
    st.subheader("Results")
    st.dataframe(filtered, use_container_width=True)

    # --- Card Details --------------------------------------------------------
    st.subheader("Card Details")

    if filtered.empty:
        st.info("No cards match your filters.")
        return

    card_ids = filtered["id"].tolist()
    selected_id = st.selectbox("Select a card", card_ids)

    card = filtered[filtered["id"] == selected_id].iloc[0]

    st.write("### Card Info")
    st.json({
        "Name": card["name"],
        "Type": card["type"],
        "Attack": card["attack"],
        "Defense": card["defense"]
    })
