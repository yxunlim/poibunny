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
    featured_count = 6
    featured_cards = temp_df.sample(
        n=min(featured_count, len(temp_df)),
        weights=weights,
        replace=False
    )

    # Display featured cards
    for _, row in featured_cards.iterrows():
        st.image(row.get("card_image_link", ""), width=200)

        st.write(f"**{row.get('name','Unknown')}**")
        st.write(f"Set: {row.get('set','Unknown')}")
        st.write(f"Condition: {row.get('card_condition','N/A')}")

        # Clean display prices safely
        market = pd.to_numeric(row.get("card_market_price", 0), errors="coerce") or 0
        sell = pd.to_numeric(row.get("card_sell_price", 0), errors="coerce") or 0

        st.write(f"Market Raw: ${market:,.2f}")
        st.write(f"My Sell Price: ${sell:,.2f}")

        st.markdown("---")

else:
    st.warning("No cards found in sheet.")
