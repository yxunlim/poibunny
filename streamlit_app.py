import streamlit as st
import pandas as pd
import plotly.express as px
import subprocess
import re

# ------------------- CONFIG -------------------
ADMIN_PASSWORD = st.secrets["ADMIN_PASSWORD"]

CARDS_SHEET_URL = st.secrets["CARDS_SHEET_URL"]
SLABS_SHEET_URL = st.secrets["SLABS_SHEET_URL"]
PSA_API_TOKEN = st.secrets["PSA_API_TOKEN"]

# ------------------- UTIL FUNCTIONS -------------------
def clean_price(value):
    if pd.isna(value):
        return 0.0
    value = str(value).replace("$", "").replace(",", "").strip()
    try:
        return float(value)
    except:
        return 0.0

def normalize_columns(df, column_map):
    df.columns = df.columns.str.strip().str.lower()
    df = df.rename(columns={k.lower(): v for k, v in column_map.items() if k.lower() in df.columns})
    return df

def make_safe_key(name):
    return re.sub(r"[^a-z0-9_]+", "_", name.lower())

# ------------------- LOAD DATA -------------------
@st.cache_data
def load_cards():
    df = pd.read_csv(CARDS_SHEET_URL)
    column_map = {
        "item no": "item_no",
        "name": "name",
        "set": "set",
        "type": "type",
        "category": "type",
        "card type": "type",
        "game": "type",
        "condition": "condition",
        "sell price": "sell_price",
        "image link": "image_link",
        "market price": "market_price",
        "quantity": "quantity"
    }
    df = normalize_columns(df, column_map)

    if "type" not in df.columns:
        df["type"] = "Other"
    if "quantity" not in df.columns:
        df["quantity"] = 0

    return df

@st.cache_data
def load_slabs():
    df = pd.read_csv(SLABS_SHEET_URL)
    column_map = {
        "item no": "item_no",
        "name": "name",
        "set": "set",
        "psa grade": "psa_grade",
        "sell price": "sell_price",
        "image link": "image_link",
        "market price": "market_price"
    }
    return normalize_columns(df, column_map)

# ------------------- SESSION STATE -------------------
if "cards_df" not in st.session_state:
    st.session_state.cards_df = load_cards()

if "slabs_df" not in st.session_state:
    st.session_state.slabs_df = load_slabs()

# ------------------- BUILD TABS -------------------
cards_df = st.session_state.cards_df

priority_display = ["Pokemon", "One Piece", "Magic the Gathering"]
priority_lookup = [p.lower() for p in priority_display]
raw_types = [t.strip() for t in cards_df["type"].dropna().unique() if str(t).strip()]

priority_types = [disp for disp in priority_display if disp.lower() in [r.lower() for r in raw_types]]
remaining_types = sorted([t.title() for t in raw_types if t.lower() not in priority_lookup])

all_types = priority_types + remaining_types

tabs = st.tabs(all_types + ["Slabs", "Admin Panel"])

# =================== TYPE TABS ===================
for index, t in enumerate(all_types):
    with tabs[index]:
        st.header(f"{t.title()} Cards")

        df = cards_df
        type_df = df[df["type"].str.lower() == t.lower()].dropna(subset=["name"])
        type_df = type_df[type_df["quantity"].astype(int) > 0]
        type_df["market_price_clean"] = type_df["market_price"].apply(clean_price)

        st.subheader("Filters")
        col1, col2, col3 = st.columns(3)
        safe_t = make_safe_key(t)

        with col1:
            selected_set = st.selectbox(
                "Set",
                ["All"] + sorted(type_df["set"].dropna().unique()),
                key=f"set_{safe_t}_{index}"
            )

        with col2:
            search_query = st.text_input("Search Name", key=f"search_{safe_t}_{index}")

        with col3:
            sort_option = st.selectbox(
                "Sort By",
                ["Name (A-Z)", "Name (Z-A)", "Price Low→High", "Price High→Low"],
                key=f"sort_{safe_t}_{index}"
            )

        min_price = float(type_df["market_price_clean"].min())
        max_price = float(type_df["market_price_clean"].max())

        min_p, max_p = st.slider(
            "Market Price Range",
            min_price,
            max_price,
            (min_price, max_price),
            key=f"price_{safe_t}_{index}"
        )

        if selected_set != "All":
            type_df = type_df[type_df["set"] == selected_set]

        if search_query:
            type_df = type_df[type_df["name"].str.contains(search_query, case=False, na=False)]

        type_df = type_df[
            (type_df["market_price_clean"] >= min_p) &
            (type_df["market_price_clean"] <= max_p)
        ]

        if sort_option == "Name (A-Z)":
            type_df = type_df.sort_values("name")
        elif sort_option == "Name (Z-A)":
            type_df = type_df.sort_values("name", ascending=False)
        elif sort_option == "Price Low→High":
            type_df = type_df.sort_values("market_price_clean")
        elif sort_option == "Price High→Low":
            type_df = type_df.sort_values("market_price_clean", ascending=False)

        st.subheader("Results")

        for i in range(0, len(type_df), 3):
            cols = st.columns(3)
            for j, card in enumerate(type_df.iloc[i:i+3].to_dict("records")):
                with cols[j]:
                    st.image(card.get("image_link") or "https://via.placeholder.com/150", use_container_width=True)
                    st.markdown(f"**{card['name']}**")
                    st.markdown(
                        f"Set: {card.get('set','')}  \n"
                        f"Condition: {card.get('condition','')}  \n"
                        f"Qty: {card.get('quantity','')}  \n"
                        f"Sell: {card.get('sell_price','')} | Market: {card.get('market_price','')}"
                    )

# =================== SLABS TAB ===================
with tabs[len(all_types)]:
    st.header("Slabs")

    for i in range(0, len(st.session_state.slabs_df), 3):
        cols = st.columns(3)
        for j, slab in enumerate(st.session_state.slabs_df.iloc[i:i+3].to_dict("records")):
            with cols[j]:
                st.image(slab.get("image_link") or "https://via.placeholder.com/150", use_container_width=True)
                st.markdown(f"**{slab['name']}**")
                st.markdown(
                    f"Set: {slab.get('set','')}  \n"
                    f"PSA: {slab.get('psa_grade','')}  \n"
                    f"Sell: {slab.get('sell_price','')} | Market: {slab.get('market_price','')}"
                )

# =================== ADMIN PANEL ===================
with tabs[len(all_types)+1]:
    st.header("Admin Panel")

    password = st.text_input("Admin Password", type="password")
    if password == ADMIN_PASSWORD:
        st.success("Access granted")

        st.dataframe(st.session_state.cards_df)

        st.subheader("PSA Certificate Check")
        cert = st.text_input("Certificate Number", type="password")

        if st.button("Check PSA"):
            curl_cmd = f'''curl -X GET "https://api.psacard.com/publicapi/cert/GetByCertNumber/{cert}" \
-H "Authorization: bearer {PSA_API_TOKEN}"'''
            result = subprocess.run(curl_cmd, shell=True, capture_output=True, text=True)
            st.code(result.stdout or result.stderr)
