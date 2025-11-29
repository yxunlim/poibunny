import streamlit as st
from cards_tab import load_cards, clean_price, build_types
import streamlit.components.v1 as components

def card_carousel(cards):
    """
    cards = list of dicts with keys:
    name, image_link, set, condition, sell_price, market_price
    """

    # Build HTML slides
    slides_html = ""
    for card in cards:
        img = card.get("image_link", "")
        if not img or img.lower() == "loading...":
            img = "https://via.placeholder.com/300"

        slides_html += f"""
        <div class="slide">
            <img src="{img}" class="carousel-img" />
            <div class="carousel-text">
                <h3>{card['name']}</h3>
                <p><strong>Set:</strong> {card.get('set','')}</p>
                <p><strong>Condition:</strong> {card.get('condition','')}</p>
                <p><strong>Sell:</strong> {card.get('sell_price','')}</p>
                <p><strong>Market:</strong> {card.get('market_price','')}</p>
            </div>
        </div>
        """

    html = f"""
    <style>
        .carousel-container {{
            width: 100%;
            max-width: 400px;
            margin: auto;
            position: relative;
        }}
        .slide {{
            display: none;
            text-align: center;
        }}
        .carousel-img {{
            width: 100%;
            border-radius: 10px;
            box-shadow: 0 0 8px rgba(0,0,0,0.2);
        }}
        .carousel-text {{
            margin-top: 10px;
        }}
    </style>

    <div class="carousel-container">
        {slides_html}
    </div>

    <script>
        let slideIndex = 0;
        const slides = window.parent.document.querySelectorAll('.carousel-container .slide');

        function showSlides() {{
            for (let i = 0; i < slides.length; i++) {{
                slides[i].style.display = "none";
            }}
            slideIndex++;
            if (slideIndex > slides.length) {{ slideIndex = 1; }}
            slides[slideIndex - 1].style.display = "block";
        }}

        showSlides();
        setInterval(showSlides, 5000);  // 5 seconds rotation
    </script>
    """

    components.html(html, height=550)


st.set_page_config(page_title="POiBUNNY", layout="wide")

# -----------------------------------------------------
# Load data once (stored in session_state)
# -----------------------------------------------------
if "cards_df" not in st.session_state:
    st.session_state.cards_df = load_cards()

cards_df = st.session_state.cards_df
all_types = build_types(cards_df)

# -----------------------------------------------------
# SIDEBAR
# -----------------------------------------------------
st.sidebar.title("Welcome to my Collection")
st.sidebar.write("Feel free to email me at lynx1186@hotmail.com to purchase my cards")

# -----------------------------------------------------
# MAIN TABS
# -----------------------------------------------------
tab_main, tab_cards, tab_admin = st.tabs(["Main", "Cards", "Admin"])

# =====================================================
# MAIN PAGE
# =====================================================
with tab_main:
    st.title("Hello World")
    st.write("Market Price follows PriceCharting at USD prices.")
    st.write("Listing price defaults to 1.1x — always happy to discuss!")
    st.title("Featured Cards")

    df = st.session_state.cards_df.dropna(subset=["name"]).copy()

    # Pick 3–5 random featured cards
    num = min(5, max(3, len(df)))
    featured_df = df.sample(num)

    # Convert card rows → dicts
    cards_list = featured_df.to_dict(orient="records")

    # Carousel display
    card_carousel(cards_list)

# =====================================================
# CARDS PAGE
# =====================================================
with tab_cards:
    st.title("My Cards")

    cards_df = st.session_state.cards_df

    # --------------------------------------------------
    # Build dynamic type tabs from the CSV
    # --------------------------------------------------
    priority_display = ["Pokemon", "One Piece", "Magic the Gathering"]
    priority_lookup = [p.lower() for p in priority_display]

    raw_types = [
        t.strip()
        for t in cards_df["type"].dropna().unique()
        if str(t).strip() != ""
    ]

    priority_types = []
    for disp, key in zip(priority_display, priority_lookup):
        if key in [r.lower() for r in raw_types]:
            priority_types.append(disp)

    remaining_types = sorted([
        t.title() for t in raw_types
        if t.lower() not in priority_lookup
    ])

    all_types = priority_types + remaining_types

    # --------------------------------------------------
    # Create the tabs dynamically
    # --------------------------------------------------
    tabs = st.tabs(all_types)

    # --------------------------------------------------
    # FULL ADVANCED UI INSIDE EACH TAB
    # --------------------------------------------------
    for index, t in enumerate(all_types):
        with tabs[index]:
            st.header(f"{t.title()} Cards")

            df = cards_df
            type_df = df[df["type"].str.lower() == t.lower()].dropna(subset=["name"])
            type_df["market_price_clean"] = type_df["market_price"].apply(clean_price)

            # Filters
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

            # Price slider
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

            # Apply filters
            if selected_set != "All":
                type_df = type_df[type_df["set"] == selected_set]

            if search_query.strip():
                type_df = type_df[type_df["name"].str.contains(search_query, case=False, na=False)]

            type_df = type_df[
                (type_df["market_price_clean"] >= min_price) &
                (type_df["market_price_clean"] <= max_price)
            ]

            if selected_set == "All":
                type_df = type_df.sort_values("set", ascending=False)

            if sort_option == "Name (A-Z)":
                type_df = type_df.sort_values("name")
            elif sort_option == "Name (Z-A)":
                type_df = type_df.sort_values("name", ascending=False)
            elif sort_option == "Price Low→High":
                type_df = type_df.sort_values("market_price_clean")
            elif sort_option == "Price High→Low":
                type_df = type_df.sort_values("market_price_clean", ascending=False)

            # Pagination
            st.subheader("Results")
            per_page = st.selectbox("Results per page", [9, 45, 99], index=0, key=f"per_page_{t}")

            if f"page_{t}" not in st.session_state:
                st.session_state[f"page_{t}"] = 1

            total_items = len(type_df)
            total_pages = (total_items - 1) // per_page + 1

            start_idx = (st.session_state[f"page_{t}"] - 1) * per_page
            end_idx = start_idx + per_page

            page_df = type_df.iloc[start_idx:end_idx]

            # Card Grid
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
                            f"Sell: {card.get('sell_price','')} | Market: {card.get('market_price','')}"
                        )

            # Pagination buttons
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
# ADMIN PAGE
# =====================================================
ADMIN_PASSWORD = "abc123"

with tab_admin:
    password = st.text_input("Enter Admin Password", type="password")

    if password == ADMIN_PASSWORD:
        st.success("Access granted!")
        st.subheader("Existing Cards (Table View)")
        st.dataframe(cards_df, use_container_width=True)
    else:
        st.info("Enter password to access admin panel.")
