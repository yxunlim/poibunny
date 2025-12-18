import streamlit as st
import pandas as pd
from cards_tab import load_cards, load_slabs

# ====================================================
# PAGE CONFIG
# ====================================================
st.set_page_config(page_title="POiBUNNY", layout="wide")

# ====================================================
# HELPERS
# ====================================================
def clean_price(x):
    try:
        return float(str(x).replace("$", "").strip())
    except Exception:
        return 0.0


# ====================================================
# SESSION STATE
# ====================================================
if "cards_df" not in st.session_state:
    st.session_state.cards_df = load_cards()

df = st.session_state.cards_df


# ====================================================
# SIDEBAR
# ====================================================
st.sidebar.title("Welcome to my Collection")
st.sidebar.write(
    "📧 Feel free to email me at **lynx1186@hotmail.com** to purchase my cards"
)


# ====================================================
# MAIN TABS
# ====================================================
tab_main, tab_cards, tab_admin = st.tabs(["Main", "Cards", "Admin"])


# ====================================================
# MAIN TAB
# ====================================================
with tab_main:
    st.title("POiBUNNY Card Collection")
    st.write("Market Price follows **PriceCharting (USD)**.")
    st.write("Listing price defaults to **1.1×** — always happy to discuss!")


# ====================================================
# CARDS TAB
# ====================================================
with tab_cards:
    st.title("Browse by Type")

    # ---- Card Types ----
    raw_types = sorted(
        t.strip()
        for t in df["type"].dropna()
        if str(t).strip()
    )

    priority_types = ["Pokemon", "One Piece", "Magic the Gathering"]
    remaining_types = sorted(
        t.title()
        for t in raw_types
        if t.lower() not in [p.lower() for p in priority_types]
    )

    all_types = [
        p for p in priority_types if p.lower() in [r.lower() for r in raw_types]
    ] + remaining_types

    type_tabs = st.tabs(all_types)

    # ====================================================
    # TYPE LOOP
    # ====================================================
    for idx, card_type in enumerate(all_types):
        with type_tabs[idx]:
            st.header(f"{card_type} Cards")

            type_df = df[
                df["type"].str.lower() == card_type.lower()
            ].dropna(subset=["name"]).copy()

            type_df["market_price_clean"] = type_df["market_price"].apply(clean_price)

            # ----------------------------
            # FILTERS
            # ----------------------------
            st.subheader("Filters")
            c1, c2, c3, c4 = st.columns(4)

            with c1:
                sets = sorted(type_df["set"].dropna().unique())
                selected_set = st.selectbox(
                    "Set", ["All"] + sets, key=f"set_{card_type}"
                )

            with c2:
                search = st.text_input(
                    "Search Name", key=f"search_{card_type}"
                )

            with c3:
                sort_by = st.selectbox(
                    "Sort By",
                    [
                        "Name (A-Z)",
                        "Name (Z-A)",
                        "Price Low→High",
                        "Price High→Low",
                    ],
                    key=f"sort_{card_type}",
                )

            with c4:
                grid_size = st.selectbox(
                    "Grid", [3, 4], key=f"grid_{card_type}"
                )

            # ----------------------------
            # PRICE FILTER
            # ----------------------------
            st.subheader("Price Range")
            min_p, max_p = (
                float(type_df["market_price_clean"].min()),
                float(type_df["market_price_clean"].max()),
            )

            if min_p != max_p:
                min_price, max_price = st.slider(
                    "Market Price",
                    min_value=min_p,
                    max_value=max_p,
                    value=(min_p, max_p),
                    key=f"price_{card_type}",
                )
            else:
                min_price = max_price = min_p

            # ----------------------------
            # APPLY FILTERS
            # ----------------------------
            if selected_set != "All":
                type_df = type_df[type_df["set"] == selected_set]

            if search:
                type_df = type_df[
                    type_df["name"].str.contains(search, case=False, na=False)
                ]

            type_df = type_df[
                (type_df["market_price_clean"] >= min_price)
                & (type_df["market_price_clean"] <= max_price)
            ]

            # Sorting
            sort_map = {
                "Name (A-Z)": ("name", True),
                "Name (Z-A)": ("name", False),
                "Price Low→High": ("market_price_clean", True),
                "Price High→Low": ("market_price_clean", False),
            }
            col, asc = sort_map[sort_by]
            type_df = type_df.sort_values(col, ascending=asc)

            # ----------------------------
            # PAGINATION
            # ----------------------------
            st.subheader("Results")
            per_page = st.selectbox(
                "Results per page", [9, 45, 99], key=f"per_{card_type}"
            )

            page_key = f"page_{card_type}"
            st.session_state.setdefault(page_key, 1)

            total_pages = max(1, (len(type_df) - 1) // per_page + 1)
            start = (st.session_state[page_key] - 1) * per_page
            page_df = type_df.iloc[start : start + per_page]

            # ----------------------------
            # CARD GRID
            # ----------------------------
            for i in range(0, len(page_df), grid_size):
                cols = st.columns(grid_size)
                for col_idx, card in enumerate(
                    page_df.iloc[i : i + grid_size].to_dict("records")
                ):
                    with cols[col_idx]:
                        img = card.get("image_link")
                        st.image(
                            img if img else "https://via.placeholder.com/150",
                            use_container_width=True,
                        )

                        st.markdown(f"**{card['name']}**")
                        st.markdown(
                            f"{card.get('set','')}  \n"
                            f"Market: {card.get('market_price','')} | "
                            f"Sell: {card.get('sell_price','')}"
                        )

            # ----------------------------
            # PAGE CONTROLS
            # ----------------------------
            p1, p2, p3 = st.columns([1, 2, 1])

            with p1:
                if st.button("⬅ Previous", key=f"prev_{card_type}") and st.session_state[page_key] > 1:
                    st.session_state[page_key] -= 1

            with p2:
                st.markdown(
                    f"Page **{st.session_state[page_key]}** of **{total_pages}**"
                )

            with p3:
                if st.button("Next ➡", key=f"next_{card_type}") and st.session_state[page_key] < total_pages:
                    st.session_state[page_key] += 1


# ====================================================
# ADMIN TAB
# ====================================================
ADMIN_PASSWORD = "abc123"

with tab_admin:
    password = st.text_input("Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Access granted")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Enter password to access admin panel")
