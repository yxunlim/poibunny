import streamlit as st
from cards_tab import load_cards, clean_price, build_types

st.set_page_config(page_title="POiBUNNY", layout="wide")

# -----------------------------------------------------
# Load data once (stored in session_state)
# -----------------------------------------------------
if "cards_df" not in st.session_state:
    st.session_state.cards_df = load_cards()

cards_df = st.session_state.cards_df
all_types = build_types(cards_df)

# -----------------------------------------------------
# SIDEBAR
# -----------------------------------------------------
st.sidebar.title("Welcome to my Collection")
st.sidebar.write("Feel free to email me at lynx1186@hotmail.com to purchase my cards")

# -----------------------------------------------------
# MAIN TABS
# -----------------------------------------------------
tab_main, tab_cards, tab_admin = st.tabs(["Main", "Cards", "Admin"])

# =====================================================
# MAIN PAGE
# =====================================================
with tab_main:
    st.title("Hello World")
    st.write("Market Price follows PriceCharting at USD prices.")
    st.write("Listing price defaults to 1.1x — always happy to discuss!")


# =====================================================
# CARDS PAGE
# =====================================================
with tab_cards:
    st.title("My Cards")

    cards_df = st.session_state.cards_df

    # --------------------------------------------------
    # Build dynamic tabs from CSV
    # --------------------------------------------------
    priority_display = ["Pokemon", "One Piece", "Magic the Gathering"]
    priority_lookup = [p.lower() for p in priority_display]

    raw_types = [
        t.strip() for t in cards_df["type"].dropna().unique()
        if str(t).strip() != ""
    ]

    priority_types = []
    for disp, key in zip(priority_display, priority_lookup):
        if key in [r.lower() for r in raw_types]:
            priority_types.append(disp)

    remaining_types = sorted([
        t.title()
        for t in raw_types
        if t.lower() not in priority_lookup
    ])

    all_types = priority_types + remaining_types

    # --------------------------------------------------
    # Create dynamic tabs
    # --------------------------------------------------
    tabs = st.tabs(all_types)

    # --------------------------------------------------
    # For each type tab, show only those cards
    # --------------------------------------------------
    for index, t in enumerate(all_types):
        with tabs[index]:
            st.header(f"{t} Cards")

            type_df = cards_df[cards_df["type"].str.lower() == t.lower()]
            st.dataframe(type_df, use_container_width=True)

    # --------------------------------------------------
    # Extra static tabs
    # --------------------------------------------------
    with tabs[len(all_types)]:  # Slabs
        st.header("Slabs")
        st.write("Slab data coming soon...")

    with tabs[len(all_types) + 1]:  # Tracking
        st.header("Tracking")
        st.write("Tracking dashboard coming soon...")

    with tabs[len(all_types) + 2]:  # Admin Panel
        st.header("Admin Panel")
        st.write("Admin tools coming soon...")


# =====================================================
# ADMIN PAGE
# =====================================================
ADMIN_PASSWORD = "abc123"

with tab_admin:
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Access granted!")
        st.subheader("Existing Cards (Table View)")
        st.dataframe(cards_df, use_container_width=True)
    else:
        st.info("Enter password to access admin panel.")
