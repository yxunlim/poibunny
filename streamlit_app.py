import streamlit as st
import pandas as pd

# Load Google Sheets CSV in environment
def load_google_sheet(csv_url):
    try:
        df = pd.read_csv(csv_url, on_bad_lines="skip", encoding="utf-8")
        df.columns = df.columns.str.strip().str.replace(" ", "_").str.lower()
        return df
    except Exception as e:
        st.error(f"Error loading sheet: {e}")
        return pd.DataFrame()

# Access secrets
cards_sheet_url = st.secrets["google_sheets"]["cards_sheet_url"]
slabs_sheet_url = st.secrets["google_sheets"]["slabs_sheet_url"]

# Load the sheets
cards_df = load_google_sheet(cards_sheet_url)
slabs_df = load_google_sheet(slabs_sheet_url)

# Display both DataFrames
st.subheader("Cards Sheet Data")
st.dataframe(cards_df)

st.subheader("Slabs Sheet Data")
st.dataframe(slabs_df)

import streamlit as st
import pandas as pd
import cards_tab  # your loader module
from cards_tab import load_cards

st.set_page_config(page_title="POiBUNNY", layout="wide")

# ----------------------------------------------------
# SESSION STATE
# ----------------------------------------------------
if "cards_df" not in st.session_state:
    st.session_state.cards_df = load_cards()

df = st.session_state.cards_df


# ----------------------------------------------------
# SIDEBAR
# ----------------------------------------------------
st.sidebar.title("Welcome to my Collection")
st.sidebar.write("Feel free to email me at lynx1186@hotmail.com to purchase my cards")


# ----------------------------------------------------
# MAIN TABS
# ----------------------------------------------------
tab_main, tab_cards, tab_admin = st.tabs(["Main", "Cards", "Admin"])


# ----------------------------------------------------
# MAIN TAB (Landing Page)
# ----------------------------------------------------
with tab_main:
    st.title("Hello World")
    st.write("Market Price follows PriceCharting at USD prices.")
    st.write("Listing price defaults to 1.1x — always happy to discuss!")


# ----------------------------------------------------
# CARDS TAB
# ----------------------------------------------------
with tab_cards:
    st.title("Browse by Type")

    # ---- Determine Types ----
    raw_types = sorted(set(
        t.strip() for t in df["type"].dropna()
        if str(t).strip() != ""
    ))

    priority_display = ["Pokemon", "One Piece", "Magic the Gathering"]
    priority_lookup = [p.lower() for p in priority_display]

    priority_types = [
        p for p in priority_display
        if p.lower() in [r.lower() for r in raw_types]
    ]

    remaining_types = sorted([
        t.title() for t in raw_types
        if t.lower() not in priority_lookup
    ])

    all_types = priority_types + remaining_types

    # ---- Build Type Tabs ----
    tabs = st.tabs(all_types)

    # ---- Clean price helper ----
    def clean_price(x):
        try:
            return float(str(x).replace("$", "").strip())
        except:
            return 0.0


    # ============================================================
    # TYPE TABS LOOP
    # ============================================================
    for index, t in enumerate(all_types):
        with tabs[index]:
            st.header(f"{t.title()} Cards")

            type_df = df[df["type"].str.lower() == t.lower()].dropna(subset=["name"])
            type_df["market_price_clean"] = type_df["market_price"].apply(clean_price)

            # ----------------------------------------------------
            # Filters
            # ----------------------------------------------------
            st.subheader("Filters")
            col1, col2, col3, col4 = st.columns([1, 1, 1, 1])

            with col1:
                sets_available = sorted(type_df["set"].dropna().unique())
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

            # ----------------------------------------------------
            # Price Filter
            # ----------------------------------------------------
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
                    key=f"price_{t}"
                )

            # ----------------------------------------------------
            # Apply Filters
            # ----------------------------------------------------
            if selected_set != "All":
                type_df = type_df[type_df["set"] == selected_set]

            if search_query.strip():
                type_df = type_df[type_df["name"].str.contains(search_query, case=False, na=False)]

            type_df = type_df[
                (type_df["market_price_clean"] >= min_price) &
                (type_df["market_price_clean"] <= max_price)
            ]

            # Sort
            if sort_option == "Name (A-Z)":
                type_df = type_df.sort_values("name")
            elif sort_option == "Name (Z-A)":
                type_df = type_df.sort_values("name", ascending=False)
            elif sort_option == "Price Low→High":
                type_df = type_df.sort_values("market_price_clean")
            elif sort_option == "Price High→Low":
                type_df = type_df.sort_values("market_price_clean", ascending=False)

            # ----------------------------------------------------
            # Pagination
            # ----------------------------------------------------
            st.subheader("Results")
            per_page = st.selectbox("Results per page", [9, 45, 99], index=0, key=f"per_page_{t}")

            if f"page_{t}" not in st.session_state:
                st.session_state[f"page_{t}"] = 1

            total_items = len(type_df)
            total_pages = max(1, (total_items - 1) // per_page + 1)

            start_idx = (st.session_state[f"page_{t}"] - 1) * per_page
            end_idx = start_idx + per_page

            page_df = type_df.iloc[start_idx:end_idx]

            # ----------------------------------------------------
            # Card Grid
            # ----------------------------------------------------
            for i in range(0, len(page_df), grid_size):
                cols = st.columns(grid_size)
                for j, card in enumerate(page_df.iloc[i:i + grid_size].to_dict(orient="records")):
                    with cols[j]:
                        img_link = card.get("image_link", "")
                        if img_link and img_link.lower() != "loading...":
                            st.image(img_link, use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/150", use_container_width=True)

                        st.markdown(f"**{card['name']}**")
                        st.markdown(
                            f"Set: {card.get('set','')}  \n"
                            f"Condition: {card.get('condition','')}  \n"
                            f"Sell: {card.get('sell_price','')} | "
                            f"Market: {card.get('market_price','')}"
                        )

            # ----------------------------------------------------
            # Pagination Controls
            # ----------------------------------------------------
            col_prev, col_page, col_next = st.columns([1, 2, 1])

            with col_prev:
                if st.button("⬅️ Previous", key=f"prev_{t}") and st.session_state[f"page_{t}"] > 1:
                    st.session_state[f"page_{t}"] -= 1

            with col_page:
                st.markdown(f"Page {st.session_state[f'page_{t}']} of {total_pages}")

            with col_next:
                if st.button("➡️ Next", key=f"next_{t}") and st.session_state[f"page_{t}"] < total_pages:
                    st.session_state[f"page_{t}"] += 1


# ----------------------------------------------------
# ADMIN TAB
# ----------------------------------------------------
ADMIN_PASSWORD = "abc123"
with tab_admin:
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Access granted!")
        st.subheader("Existing Cards (Table View)")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Enter password to access admin panel.")

# -----------------------------------------------------
# MAIN APP
# -----------------------------------------------------
st.title("📘 Card & Slab Inventory")

tabs = ["Raw Cards", "Graded Slabs"]
choice = st.radio("Select a category:", tabs)

if choice == "Raw Cards":
    cards_df = load_cards()
    display_cards(cards_df)

elif choice == "Graded Slabs":
    slabs_df = load_slabs()
    display_slabs(slabs_df)

# ---------------------------------------------------------
# Featured Cards Section
# ---------------------------------------------------------
st.markdown("## ⭐ Featured Cards")

if not cards_df.empty:
    temp_df = cards_df.copy()
    
    # Convert sell price to numeric (critical fix)
    temp_df["market_price_clean"] = pd.to_numeric(
        temp_df["card_sell_price"], errors="coerce"
    ).fillna(0)

    # Avoid divide-by-zero
    if temp_df["market_price_clean"].sum() == 0:
        weights = None
    else:
        weights = temp_df["market_price_clean"] + 1
        weights = weights / weights.sum()

    # Random selection
    featured_count = 3
    featured_cards = temp_df.sample(
        n=min(featured_count, len(temp_df)),
        weights=weights,
        replace=False
    )

    # Center the 3 cards using 5 columns: [spacer][card][card][card][spacer]
    left_spacer, col1, col2, col3, right_spacer = st.columns([1, 2, 2, 2, 1])
    cols = [col1, col2, col3]
    
    for idx, (_, row) in enumerate(featured_cards.iterrows()):
        with cols[idx]:
    
            # Half-size image
            st.image(row.get("card_image_link", ""), width=90)
    
            # Clean numeric prices
            market = pd.to_numeric(row.get("card_market_price", 0), errors="coerce") or 0
            sell = pd.to_numeric(row.get("card_sell_price", 0), errors="coerce") or 0
    
            # Compact text block
            st.markdown(
                f"""
    **{row.get('name', 'Unknown')}**  
    {row.get('set', 'Unknown')}  
    Market: ${market:,.2f} | Sell Price: ${sell:,.2f}
                """
            )

else:
    st.warning("No cards found in sheet.")

