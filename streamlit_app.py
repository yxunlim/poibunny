import streamlit as st
import cards_tab   # your module
from cards_tab import load_cards   # explicitly import loader

st.set_page_config(page_title="POiBUNNY", layout="wide")

# ------------------- SESSION STATE -------------------
if "cards_df" not in st.session_state:
    st.session_state.cards_df = load_cards()

cards_df = st.session_state.cards_df

# ---- Main Tabs ----
tab_main, tab_cards, tab_admin = st.tabs(["Main", "Cards", "Admin"])

# ---- Sidebar ----
st.sidebar.title("Welcome to my Collection")
st.sidebar.write("Feel free to email me at lynx1186@hotmail.com to purchase my cards")

# ---- Landing Page ----
with tab_main:
    st.title("Hello World")
    st.write("Market Price follows PriceCharting at USD prices.")
    st.write("Listing price defaults to 1.1x — always happy to discuss!")

# ---- Cards Page ----
with tab_cards:
    st.title("My Cards")
    selected_type = st.selectbox("Filter by Type", ["All"] + all_types)

    if selected_type == "All":
        filtered_df = cards_df
    else:
        filtered_df = cards_df[cards_df["type"].str.lower() == selected_type.lower()]

    st.dataframe(filtered_df, use_container_width=True)

# ---- Admin Page ----
ADMIN_PASSWORD = "abc123"
with tab_admin:
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Access granted!")
        st.subheader("Existing Cards (Table View)")
        st.dataframe(cards_df, use_container_width=True)
    else:
        st.info("Enter password to access admin panel.")
