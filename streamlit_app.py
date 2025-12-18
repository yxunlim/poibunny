import streamlit as st
import pandas as pd
from cards_tab import load_cards

# ====================================================
# PAGE CONFIG
# ====================================================
st.set_page_config(page_title="POiBUNNY", layout="wide")

# ====================================================
# LOAD DATA
# ====================================================
if "cards_df" not in st.session_state:
    df = load_cards()

    # ---- Normalize column names ----
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )

    st.session_state.cards_df = df

df = st.session_state.cards_df


# ====================================================
# REQUIRED COLUMN CHECKS
# ====================================================
# Handle "type" vs "card_type"
if "type" in df.columns:
    TYPE_COL = "type"
elif "card_type" in df.columns:
    TYPE_COL = "card_type"
else:
    st.error("❌ Missing required column: 'type' or 'card_type'")
    st.write("Available columns:", list(df.columns))
    st.stop()

REQUIRED_COLS = ["name", "set", "market_price", "sell_price"]

missing = [c for c in REQUIRED_COLS if c not in df.columns]
if missing:
    st.error(f"❌ Missing required columns: {missing}")
    st.write("Available columns:", list(df.columns))
    st.stop()


# ====================================================
# HELPERS
# ====================================================
def clean_price(x):
    try:
        return float(str(x).replace("$", "").strip())
    except Exception:
        return 0.0


# ====================================================
# SIDEBAR
# ====================================================
st.sidebar.title("Welcome to my Collection")
st.sidebar.markdown(
    "📧 **lynx1186@hotmail.com**  \n"
    "Feel free to email me to purchase cards"
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

    # ---- Types ----
    raw_types = sorted(
        str(t).strip()
        for t in df[TYPE_COL].dropna()
        if str(t).strip()
    )

    priority = ["Pokemon", "One Piece", "Magic the Gathering"]
    priority_lower = [p.lower() for p in priority]

    ordered_types = (
        [p for p in priority if p.lower() in [r.lower() for r in raw_types]]
        + sorted(t.title() for t in raw_types if t.lower() not in priority_lower)
    )

    type_tabs = st.tabs(ordered_types)

    # ====================================================
    # TYPE LOOP
    # ====================================================
    for idx, card_type in enumerate(ordered_types):
        with type_tabs[idx]:
            st.header(f"{card_type} Cards")

            type_df = df[
                df[TYPE_COL].str.lower() == card_type.lower()
            ].copy()

            type_df["market_price_clean"] = type_df["market_price"].apply(clean_price)

            # ----------------------------
            # FILTERS
            # ----------------------------
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
                grid = st.selectbox(
                    "Grid", [3, 4], key=f"grid_{card_type}"
                )

            # ----------------------------
            # PRICE FILTER
            # ----------------------------
            min_p = float(type_df["market_price_clean"].min())
            max_p = float(type_df["market_price_clean"].max())

            if min_p != max_p:
                min_price, max_price = st.slider(
                    "Market Price Range",
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
            per_page = st.selectbox(
                "Results per page", [9, 45, 99], key=f"per_{card_type}"
            )

            page_key = f"page_{card_type}"
            st.session_state.setdefault(page_key, 1)

            total_pages = max(1, (len(type_df) - 1) // per_page + 1)
            start = (st.session_state[page_key] - 1) * per_page
            page_df = type_df.iloc[start:start + per_page]

            # ----------------------------
            # CARD GRID
            # ----------------------------
            for i in range(0, len(page_df), grid):
                cols = st.columns(grid)
                for j, card in enumerate(page_df.iloc[i:i + grid].to_dict("records")):
                    with cols[j]:
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
                st.markdown(f"Page **{st.session_state[page_key]}** of **{total_pages}**")

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
