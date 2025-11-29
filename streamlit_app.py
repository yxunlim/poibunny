import streamlit as st
import cards_tab   # ⬅️ your module that loads df

st.set_page_config(page_title="POiBUNNY", layout="wide")

# ------------------- SESSION STATE -------------------
if "cards_df" not in st.session_state:
    st.session_state.cards_df = load_cards()
if "track_df" not in st.session_state:
    st.session_state.track_df = load_tracking_sheet()

# ------------------- BUILD TABS -------------------
cards_df = st.session_state.cards_df

priority_display = ["Pokemon", "One Piece", "Magic the Gathering"]
priority_lookup = [p.lower() for p in priority_display]

raw_types = [t.strip() for t in cards_df["type"].dropna().unique() if str(t).strip() != ""]

priority_types = []
for disp, key in zip(priority_display, priority_lookup):
    if key in [r.lower() for r in raw_types]:
        priority_types.append(disp)

remaining_types = sorted([
    t.title() for t in raw_types
    if t.lower() not in priority_lookup
])

all_types = priority_types + remaining_types

tabs = st.tabs(all_types + ["Tracking", "Admin Panel"])

# ---- Sidebar ----
st.sidebar.title("Welcome to my Collection")
st.sidebar.write("Feel free to email me at lynx1186@hotmail.com to purchase my cards")

# ---- Main Tabs ----
tab1, tab2, tab3 = st.tabs(["Main", "Cards", "Admin"])

# ---- Landing Page ----
with tab1:
    st.title("Hello World")
    st.write("Market Price follows PriceCharting at USD prices. Listing price is default 1.1x, always happy to discuss")

# ---- Cards Page ----
with tab2:
    st.title("My Cards")

# ---- Admin Page ----
ADMIN_PASSWORD = "abc123"
with tab3:
    password = st.text_input("Enter Admin Password", type="password")
    if password == ADMIN_PASSWORD:
        st.success("Access granted!")
        st.subheader("Existing Cards (Table View)")
        st.dataframe(st.session_state.cards_df)
    st.title("My Cards")
    st.dataframe(cards_tab.df)
