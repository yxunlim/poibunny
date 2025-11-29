import streamlit as st
import pandas as pd

CARDS_URL = "https://docs.google.com/spreadsheets/d/1lTiPG_g1MFD6CHvbNCjXOlfYNnHo95QvXNwFK5aX_aw/export?format=csv&gid=533371784"
SLABS_URL = "https://docs.google.com/spreadsheets/d/1LSSAQdQerNWTci5ufYYBr_J3ZHUSlVRyW-rSHkvGqf4/export?format=csv&gid=44140124"


# ---------------------------------------------
# Loaders
# ---------------------------------------------
@st.cache_data
def load_cards():
    try:
        return pd.read_csv(CARDS_URL)
    except Exception as e:
        st.error(f"Failed loading CARDS sheet: {e}")
        return pd.DataFrame()


@st.cache_data
def load_slabs():
    try:
        df = pd.read_csv(SLABS_URL)

        # Normalise price column: slab_price → Price
        if "slab_price" in df.columns and "Price" not in df.columns:
            df.rename(columns={"slab_price": "Price"}, inplace=True)

        return df
    except Exception as e:
        st.error(f"Failed loading SLABS sheet: {e}")
        return pd.DataFrame()


# ---------------------------------------------
# Utility: clean price values safely
# ---------------------------------------------
def clean_price(x):
    if pd.isna(x):
        return 0.0
    try:
        s = str(x).replace(",", "").replace("$", "").strip()
        return float(s)
    except:
        return 0.0


# ---------------------------------------------
# UI FUNCTION FOR THE TAB
# ---------------------------------------------
def cards_tab():

    st.header("📇 Cards Inventory")

    df = load_cards().copy()
    slabs_df = load_slabs().copy()

    if df.empty:
        st.warning("Cards sheet is empty or failed to load.")
        return

    # ---------------------------------------------
    # Clean price columns
    # ---------------------------------------------
    for col in ["Price", "sell_price", "raw"]:
        df[col + "_clean"] = df[col].apply(clean_price) if col in df else 0

    # ---------------------------------------------
    # Filters
    # ---------------------------------------------
    c1, c2, c3 = st.columns(3)

    brand_filter = c1.selectbox(
        "Brand",
        options=["All"] + sorted(df["Brand"].dropna().unique().tolist())
    )

    subject_filter = c2.text_input("Search Subject / Name")

    show_only_profitable = c3.checkbox("Only show profitable ⚡")

    # ---------------------------------------------
    # Apply filters
    # ---------------------------------------------
    filtered = df.copy()

    if brand_filter != "All":
        filtered = filtered[filtered["Brand"] == brand_filter]

    if subject_filter.strip():
        q = subject_filter.lower()
        filtered = filtered[
            filtered["Subject"].str.lower().str.contains(q, na=False)
        ]

    if show_only_profitable:
        filtered = filtered[
            filtered["sell_price_clean"] > filtered["Price_clean"]
        ]

    st.subheader(f"Results ({len(filtered)} cards)")

    # ---------------------------------------------
    # Display each card block
    # ---------------------------------------------
    def card_row_display(row):
        cols = st.columns([1, 3])

        # Image
        if "image_link" in row and pd.notna(row["image_link"]):
            cols[0].image(row["image_link"], width=120)
        else:
            cols[0].write("No image")

        # Details
        with cols[1]:
            st.write(f"### {row.get('Subject', 'Unknown')}")
            st.write(f"**Brand:** {row.get('Brand', '')}")
            st.write(f"**Year:** {row.get('Year', '')}")
            st.write(f"**Card #** {row.get('CardNumber', '')}")
            st.write(f"**Grade:** {row.get('CardGrade', '')}")

            price = row.get("Price_clean", 0)
            sell = row.get("sell_price_clean", 0)

            st.write(f"**Market Price:** ${price:,.2f}")
            st.write(f"**Sell Price:** ${sell:,.2f}")

            profit = sell - price
            profit_color = "green" if profit > 0 else "red"
            st.markdown(
                f"**Profit:** <span style='color:{profit_color}'>${profit:,.2f}</span>",
                unsafe_allow_html=True
            )

    # Display items
    for _, row in filtered.iterrows():
        st.markdown("---")
        card_row_display(row)

    st.markdown("---")
    st.success("Cards loaded successfully ✔")


# END FILE
