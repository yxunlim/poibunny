import streamlit as st
import pandas as pd
import time
import random

# Import card utilities
from card_tab import load_cards, clean_price, build_types

# -----------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------
st.set_page_config(page_title="Card Inventory", layout="wide")

# -----------------------------------------------------
# LOAD DATA
# -----------------------------------------------------
cards_df = load_cards()
if cards_df.empty:
    st.error("⚠️ Unable to load card data.")
    st.stop()

all_types = build_types(cards_df)

# Store dataframe in session
st.session_state["cards_df"] = cards_df

# -----------------------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------------------
menu = ["Home"] + all_types + ["Slabs", "Tracking", "Admin Panel"]
choice = st.sidebar.radio("Navigation", menu)

# -----------------------------------------------------
# FEATURED CARD CAROUSEL (HOME PAGE)
# -----------------------------------------------------
if choice == "Home":
    st.title("⭐ Featured Cards")

    # Pick 5 random cards
    def get_random_cards(n=5):
        df = st.session_state["cards_df"]
        df = df[df["image_link"].notna()]
        if df.empty:
            return []
        return df.sample(min(n, len(df))).to_dict(orient="records")

    featured_cards = get_random_cards()

    # Carousel state
    if "carousel_index" not in st.session_state:
        st.session_state.carousel_index = 0

    # Auto rotation every 5 seconds
    st_autorefresh = st.experimental_rerun

    placeholder = st.empty()

    with placeholder.container():
        card = featured_cards[st.session_state.carousel_index]

        left, mid, right = st.columns([1, 2, 1])
        with mid:
            st.image(card["image_link"], use_container_width=True)
            st.subheader(card["name"])
            st.write(f"Set: {card.get('set', '')}")
            st.write(f"Market Price: {card.get('market_price', '')}")

    time.sleep(5)

    st.session_state.carousel_index = (st.session_state.carousel_index + 1) % len(featured_cards)
    st.experimental_rerun()

# -----------------------------------------------------
# CARD TABS (DYNAMIC PAGES)
# -----------------------------------------------------
elif choice in all_types:
    t = choice  # selected type
    st.title(f"{t} Cards")

    df = st.session_state["cards_df"]
    type_df = df[df["type"].str.lower() == t.lower()].copy()
    type_df["market_price_clean"] = type_df["market_price"].apply(clean_price)

    # FILTERS
    st.subheader("Filters")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        sets_available = sorted(type_df["set"].dropna().unique())
        selected_set = st.selectbox("Set", ["All"] + sets_available)

    with col2:
        search_query = st.text_input("Search Name")

    with col3:
        sort_option = st.selectbox(
            "Sort By",
            ["Name (A-Z)", "Name (Z-A)", "Price Low→High", "Price High→Low"]
        )

    with col4:
        grid_size = st.selectbox("Grid", [3, 4])

    # PRICE SLIDER
    st.subheader("Price Filter")
    min_possible = float(type_df["market_price_clean"].min())
    max_possible = float(type_df["market_price_clean"].max())

    if min_possible == max_possible:
        min_price, max_price = min_possible, max_possible
    else:
        min_price, max_price = st.slider(
            "Market Price Range",
            min_value=min_possible,
            max_value=max_possible,
            value=(min_possible, max_possible),
        )

    # APPLY FILTERS
    if selected_set != "All":
        type_df = type_df[type_df["set"] == selected_set]

    if search_query.strip():
        type_df = type_df[type_df["name"].str.contains(search_query, case=False, na=False)]

    type_df = type_df[
        (type_df["market_price_clean"] >= min_price)
        & (type_df["market_price_clean"] <= max_price)
    ]

    match sort_option:
        case "Name (A-Z)":
            type_df = type_df.sort_values("name")
        case "Name (Z-A)":
            type_df = type_df.sort_values("name", ascending=False)
        case "Price Low→High":
            type_df = type_df.sort_values("market_price_clean")
        case "Price High→Low":
            type_df = type_df.sort_values("market_price_clean", ascending=False)

    # PAGINATION
    st.subheader("Results")
    per_page = st.selectbox("Results per page", [9, 45, 99], index=0)

    if f"page_{t}" not in st.session_state:
        st.session_state[f"page_{t}"] = 1

    total_items = len(type_df)
    total_pages = max(1, (total_items - 1) // per_page + 1)

    # Keep page in valid range
    st.session_state[f"page_{t}"] = min(st.session_state[f"page_{t}"], total_pages)

    start_idx = (st.session_state[f"page_{t}"] - 1) * per_page
    end_idx = start_idx + per_page
    page_df = type_df.iloc[start_idx:end_idx]

    # GRID
    for i in range(0, len(page_df), grid_size):
        cols = st.columns(grid_size)
        for j, card in enumerate(page_df.iloc[i:i+grid_size].to_dict(orient="records")):
            with cols[j]:
                img_link = card.get("image_link", "")
                if img_link:
                    st.image(img_link, use_container_width=True)
                st.markdown(f"**{card['name']}**")
                st.write(f"Set: {card.get('set','')}")
                st.write(f"Condition: {card.get('condition','')}")
                st.write(f"Sell: {card.get('sell_price','')} | Market: {card.get('market_price','')}")

    # PAGINATION BUTTONS
    col_prev, col_page, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("⬅️ Previous") and st.session_state[f"page_{t}"] > 1:
            st.session_state[f"page_{t}"] -= 1
            st.experimental_rerun()

    with col_page:
        st.write(f"Page {st.session_state[f'page_{t}']} of {total_pages}")

    with col_next:
        if st.button("➡️ Next") and st.session_state[f"page_{t}"] < total_pages:
            st.session_state[f"page_{t}"] += 1
            st.experimental_rerun()

# -----------------------------------------------------
# OTHER PAGES
# -----------------------------------------------------
elif choice == "Slabs":
    st.title("Slabs (Coming Soon)")
elif choice == "Tracking":
    st.title("Tracking (Coming Soon)")
elif choice == "Admin Panel":
    st.title("Admin Panel (Coming Soon)")
