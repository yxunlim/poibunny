import streamlit as st
from cards_tab import load_cards, clean_price, build_types, load_slabs
import numpy as np

st.set_page_config(page_title="POiBUNNY", layout="wide")

# -----------------------------------------------------
# Load once
# -----------------------------------------------------
if "cards_df" not in st.session_state:
    st.session_state.cards_df = load_cards()

if "slabs_df" not in st.session_state:
    st.session_state.slabs_df = load_slabs()

cards_df = st.session_state.cards_df
slabs_df = st.session_state.slabs_df
all_types = build_types(cards_df)

# -----------------------------------------------------
# Sidebar
# -----------------------------------------------------
st.sidebar.title("Welcome to my Collection")
st.sidebar.write("Feel free to email me at lynx1186@hotmail.com to purchase my cards")

# -----------------------------------------------------
# Tabs
# -----------------------------------------------------
tab_main, tab_cards, tab_slabs, tab_admin = st.tabs(["Main", "Cards", "Slabs", "Admin"])


# =====================================================
# MAIN PAGE — Featured Cards
# =====================================================
with tab_main:
    st.title("Hello World")
    st.write("Market Price follows PriceCharting at USD prices.")
    st.write("Listing price defaults to 1.1x — always happy to discuss!")

    st.markdown("## ⭐ Featured Cards")

    temp_df = cards_df.copy()
    temp_df["market_price_clean"] = temp_df["price"].fillna(0)

    weights = temp_df["market_price_clean"] + 1
    weights = weights / weights.sum()

    if "featured_cards" not in st.session_state:
        st.session_state.featured_cards = temp_df.sample(3, weights=weights)

    if st.button("➡️ Show Next"):
        st.session_state.featured_cards = temp_df.sample(3, weights=weights)
        st.rerun()

    featured_cards = st.session_state.featured_cards

    st.markdown("""
        <style>
        .fade-card { animation: fadein 0.9s ease-in-out; }
        @keyframes fadein {
            from { opacity: 0; transform: translateY(6px); }
            to   { opacity: 1; transform: translateY(0); }
        }
        </style>
    """, unsafe_allow_html=True)

    cols = st.columns(3)

    for col, (_, card) in zip(cols, featured_cards.iterrows()):
        with col:
            col.markdown('<div class="fade-card">', unsafe_allow_html=True)

            img = card.get("image_link", "")
            st.image(img if img else "https://via.placeholder.com/200", use_container_width=True)

            st.markdown(f"**{card['name']}**")
            st.markdown(
                f"Set: {card.get('set','')}  \n"
                f"Condition: {card.get('condition','')}  \n"
                f"Sell: {card.get('sell_price','')} | Market: {card.get('price','')}"
            )

            col.markdown("</div>", unsafe_allow_html=True)


# =====================================================
# CARDS PAGE
# =====================================================
with tab_cards:
    st.title("My Cards")

    cards_df = st.session_state.cards_df

    tabs = st.tabs(all_types)

    for index, t in enumerate(all_types):
        with tabs[index]:
            st.header(f"{t.title()} Cards")

            df = cards_df[cards_df["type"].str.lower() == t.lower()].dropna(subset=["name"])
            df["market_price_clean"] = df["price"].fillna(0)

            # Filters
            st.subheader("Filters")
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

            with col1:
                sets_available = sorted(df["set"].dropna().unique())
                selected_set = st.selectbox("Set", ["All"] + sets_available, key=f"set_{t}")

            with col2:
                search_query = st.text_input("Search Name", "", key=f"search_{t}")

            with col3:
                sort_option = st.selectbox(
                    "Sort By",
                    ["Name (A-Z)", "Name (Z-A)", "Price Low→High", "Price High→Low"],
                    key=f"sort_{t}"
                )

            with col4:
                grid_size = st.selectbox("Grid", [3, 4], key=f"grid_{t}")

            st.subheader("Price Filter")
            min_possible = float(df["market_price_clean"].min())
            max_possible = float(df["market_price_clean"].max())

            if min_possible == max_possible:
                min_price, max_price = min_possible, max_possible
            else:
                min_price, max_price = st.slider(
                    "Market Price Range",
                    min_value=min_possible,
                    max_value=max_possible,
                    value=(min_possible, max_possible),
                    key=f"price_{t}"
                )

            if selected_set != "All":
                df = df[df["set"] == selected_set]

            if search_query.strip():
                df = df[df["name"].str.contains(search_query, case=False, na=False)]

            df = df[
                (df["market_price_clean"] >= min_price) &
                (df["market_price_clean"] <= max_price)
            ]

            if sort_option == "Name (A-Z)":
                df = df.sort_values("name")
            elif sort_option == "Name (Z-A)":
                df = df.sort_values("name", ascending=False)
            elif sort_option == "Price Low→High":
                df = df.sort_values("market_price_clean")
            elif sort_option == "Price High→Low":
                df = df.sort_values("market_price_clean", ascending=False)

            # Pagination
            st.subheader("Results")
            per_page = st.selectbox("Results per page", [9, 45, 99], index=0, key=f"per_page_{t}")

            if f"page_{t}" not in st.session_state:
                st.session_state[f"page_{t}"] = 1

            total_items = len(df)
            total_pages = (total_items - 1) // per_page + 1

            start_idx = (st.session_state[f"page_{t}"] - 1) * per_page
            end_idx = start_idx + per_page

            page_df = df.iloc[start_idx:end_idx]

            # Grid
            for i in range(0, len(page_df), grid_size):
                cols = st.columns(grid_size)
                for j, card in enumerate(page_df.iloc[i:i + grid_size].to_dict(orient="records")):
                    with cols[j]:
                        img_link = card.get("image_link", "")
                        st.image(img_link if img_link else "https://via.placeholder.com/150",
                                 use_container_width=True)

                        st.markdown(f"**{card['name']}**")
                        st.markdown(
                            f"Set: {card.get('set','')}  \n"
                            f"Condition: {card.get('condition','')}  \n"
                            f"Sell: {card.get('sell_price','')} | Market: {card.get('price','')}"
                        )

            col_prev, col_page, col_next = st.columns([1, 2, 1])

            with col_prev:
                if st.button("⬅️ Previous", key=f"prev_{t}") and st.session_state[f"page_{t}"] > 1:
                    st.session_state[f"page_{t}"] -= 1

            with col_page:
                st.markdown(f"Page {st.session_state[f'page_{t}']} of {total_pages}")

            with col_next:
                if st.button("➡️ Next", key=f"next_{t}") and st.session_state[f"page_{t}"] < total_pages:
                    st.session_state[f"page_{t}"] += 1


# =====================================================
# SLABS PAGE
# =====================================================
with tab_slabs:
    st.title
