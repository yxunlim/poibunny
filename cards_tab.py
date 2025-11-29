import streamlit as st
import pandas as pd

CARDS_SHEET_URL = (
    "https://docs.google.com/spreadsheets/d/"
    "1_VbZQuf86KRU062VfyLzPU6KP8C3XhZ7MPAvqjfjf0o/export"
    "?format=csv&gid=0"
)

def normalize_columns(df, column_map):
    df.columns = df.columns.str.strip().str.lower()

    # rename columns dynamically
    rename_dict = {src.lower(): dst for src, dst in column_map.items() if src.lower() in df.columns}
    df = df.rename(columns=rename_dict)
    return df

@st.cache_data
def load_cards():
    df = pd.read_csv(CARDS_SHEET_URL)

    column_map = {
        "item no": "item_no",
        "name": "name",
        "set": "set",
        "type": "type",
        "category": "type",
        "card type": "type",
        "game": "type",
        "condition": "condition",
        "sell price": "sell_price",
        "image link": "image_link",
        "market price": "market_price",
    }

    df = normalize_columns(df, column_map)

    if "type" not in df.columns:
        df["type"] = "Other"

    return df

# expose df for debugging only
df = load_cards()
