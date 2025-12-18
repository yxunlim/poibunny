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

    # Clean quantity
    df["quantity"] = pd.to_numeric(df.get("quantity", 0), errors="coerce").fillna(0)

    # Clean prices
    df["market_price_clean"] = df.get("market_price", 0).apply(clean_price)
    df["sell_price_clean"] = df.get("sell_price", 0).apply(clean_price)

    # Clean type column
    df["type"] = df.get("type", "Other").astype(str).str.strip().str.title()
    df["type"] = df["type"].replace({
        "Pokemon-English": "Pokemon-English",
        "Pokemon-Japanese": "Pokemon-Japanese"
    }).fillna("Others")

    # Ensure name column is string
    df["name"] = df["name"].astype(str).fillna("Unknown")

    return df

cards_df = load_cards()

# ------------------- FEATURED CARDS -------------------
st.markdown("## ⭐ Featured Cards")

if not cards_df.empty:
    temp_df = cards_df.copy()

    temp_df["market_price_clean"] = pd.to_numeric(temp_df.get("sell_price", 0), errors="coerce").fillna(0)

    if temp_df["market_price_clean"].sum() == 0:
        weights = None
    else:
        weights = temp_df["market_price_clean"] + 1
        weights = weights / weights.sum()

    featured_count = 3
    featured_cards = temp_df.sample(n=min(featured_count, len(temp_df)), weights=weights, replace=False)

    left_spacer, col1, col2, col3, right_spacer = st.columns([1,2,2,2,1])
    cols = [col1, col2, col3]

    for idx, (_, row) in enumerate(featured_cards.iterrows()):
        with cols[idx]:
            # Safe image URL
            image_url = row.get("image_link")
            if pd.isna(image_url) or not image_url:
                image_url = "https://via.placeholder.com/150"
            st.image(image_url, width=90)

            market = pd.to_numeric(row.get("market_price", 0), errors="coerce") or 0
            sell = pd.to_numeric(row.get("sell_price", 0), errors="coerce") or 0

            st.markdown(
                f"**{row.get('name', 'Unknown')}**  \n"
                f"{row.get('set', 'Unknown')}  \n"
                f"Market: ${market:,.2f} | Sell Price: ${sell:,.2f}"
            )
else:
    st.warning("No cards found in sheet.")

# ------------------- TABS -------------------
tabs_labels = ["Pokemon-English", "Pokemon-Japanese", "Others", "Admin Panel"]
tabs = st.tabs(tabs_labels)

for idx, t in enumerate(tabs_labels[:-1]):  # skip Admin Panel
    with tabs[idx]:
        st.header(f"{t} Cards")

        # Filter cards based on type and quantity
        if t == "Others":
            df = cards_df[~cards_df["type"].isin(["Pokemon-English", "Pokemon-Japanese"]) & (cards_df["quantity"] > 0)]
        else:
            df = cards_df[(cards_df["type"] == t) & (cards_df["quantity"] > 0)]

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

        # Display cards in grid
        for i in range(0, len(df), 3):
            cols = st.columns(3)
            for j, card in enumerate(df.iloc[i:i+3].to_dict("records")):
                with cols[j]:
                    image_url = card.get("image_link")
                    if pd.isna(image_url) or not image_url:
                        image_url = "https://via.placeholder.com/150"
                    st.image(image_url, use_container_width=True)

                    quantity = int(card.get("quantity", 0) or 0)
                    sell_price = clean_price(card.get("sell_price"))
                    market_price = clean_price(card.get("market_price"))

                    st.markdown(
                        f"**{card.get('name', 'Unknown')}**  \n"
                        f"{card.get('set','')}  \n"
                        f"Qty: {quantity}  \n"
                        f"Sell: ${sell_price:,.2f} | Market: ${market_price:,.2f}"
                    )

# ------------------- ADMIN PANEL -------------------
with tabs[-1]:
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
