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
