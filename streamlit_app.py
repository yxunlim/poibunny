import streamlit as st
import pandas as pd
import re
import requests

# ------------------- SAFETY CHECK -------------------

required_keys = ["google_sheets", "admin", "psa"]
for key in required_keys:
    if key not in st.secrets:
        st.error(f"Missing secrets section: [{key}]")
        st.stop()

# ------------------- CONFIG -------------------

ADMIN_PASSWORD = st.secrets["admin"]["password"]
PSA_API_TOKEN = st.secrets["psa"]["api_token"]

CARDS_SHEET_URL = st.secrets["google_sheets"]["cards_sheet_url"]
SLABS_SHEET_URL = st.secrets["google_sheets"]["slabs_sheet_url"]

# ------------------- HELPERS -------------------

def load_google_sheet(csv_url):
    df = pd.read_csv(csv_url, on_bad_lines="skip", encoding="utf-8")
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df

def clean_price(value):
    if pd.isna(value):
        return 0.0
    try:
        return float(str(value).replace("$", "").replace(",", ""))
    except:
        return 0.0

def make_safe_key(name):
    return re.sub(r"[^a-z0-9_]+", "_", name.lower())

# ------------------- LOAD DATA -------------------

@st.cache_data
def load_cards():
    df = load_google_sheet(CARDS_SHEET_URL)
    df["quantity"] = pd.to_numeric(df.get("quantity", 0), errors="coerce").fillna(0)
    df["market_price_clean"] = df.get("market_price", 0).apply(clean_price)
    df["type"] = df.get("type", "Other").fillna("Other")
    return df

@st.cache_data
def load_slabs():
    return load_google_sheet(SLABS_SHEET_URL)

cards_df = load_cards()
slabs_df = load_slabs()

# ------------------- BUILD TABS -------------------

card_types = sorted(cards_df["type"].dropna().unique())
tabs = st.tabs(card_types + ["Slabs", "Admin Panel"])

# =================== CARD TABS ===================

for idx, t in enumerate(card_types):
    with tabs[idx]:
        st.header(f"{t} Cards")

        df = cards_df[(cards_df["type"].str.lower() == t.lower()) & (cards_df["quantity"] > 0)]

        if df.empty:
            st.info("No cards available")
            continue

        safe_t = make_safe_key(t)
        col1, col2, col3 = st.columns(3)

        with col1:
            selected_set = st.selectbox(
                "Set",
                ["All"] + sorted(df["set"].dropna().unique()),
                key=f"set_{safe_t}"
            )

        with col2:
            search = st.text_input("Search Name", key=f"search_{safe_t}")

        with col3:
            sort = st.selectbox(
                "Sort",
                ["Name (A-Z)", "Price Low→High", "Price High→Low"],
                key=f"sort_{safe_t}"
            )

        if selected_set != "All":
            df = df[df["set"] == selected_set]

        if search:
            df = df[df["name"].str.contains(search, case=False, na=False)]

        if sort == "Name (A-Z)":
            df = df.sort_values("name")
        elif sort == "Price Low→High":
            df = df.sort_values("market_price_clean")
        else:
            df = df.sort_values("market_price_clean", ascending=False)

        for i in range(0, len(df), 3):
            cols = st.columns(3)
            for j, card in enumerate(df.iloc[i:i+3].to_dict("records")):
                with cols[j]:
                    st.image(card.get("image_link") or "https://via.placeholder.com/150", use_container_width=True)
                    st.markdown(f"**{card['name']}**")
                    st.markdown(
                        f"{card.get('set','')}  \n"
                        f"Qty: {int(card.get('quantity',0))}  \n"
                        f"Sell: {card.get('sell_price','')} | Market: {card.get('market_price','')}"
                    )

# =================== SLABS ===================

with tabs[len(card_types)]:
    st.header("Slabs")

    for i in range(0, len(slabs_df), 3):
        cols = st.columns(3)
        for j, slab in enumerate(slabs_df.iloc[i:i+3].to_dict("records")):
            with cols[j]:
                st.image(slab.get("image_link") or "https://via.placeholder.com/150", use_container_width=True)
                st.markdown(f"**{slab['name']}**")
                st.markdown(
                    f"{slab.get('set','')}  \n"
                    f"PSA: {slab.get('psa_grade','')}  \n"
                    f"Sell: {slab.get('sell_price','')} | Market: {slab.get('market_price','')}"
                )

# =================== ADMIN PANEL ===================

with tabs[len(card_types) + 1]:
    st.header("Admin Panel")

    password = st.text_input("Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Access granted")
        st.dataframe(cards_df)

        cert = st.text_input("PSA Certificate Number")

        if st.button("Check PSA") and cert:
            url = f"https://api.psacard.com/publicapi/cert/GetByCertNumber/{cert}"
            headers = {"Authorization": f"Bearer {PSA_API_TOKEN}"}
            response = requests.get(url, headers=headers)

            if response.ok:
                st.json(response.json())
            else:
                st.error("Failed to fetch PSA data")
    elif password:
        st.error("Incorrect password")
