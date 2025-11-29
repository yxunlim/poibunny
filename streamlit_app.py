import streamlit as st
import cards_tab   # ⬅️ your module that loads df

st.set_page_config(page_title="POiBUNNY", layout="wide")

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
with tab3:
    st.dataframe(cards_tab.df)
