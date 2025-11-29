import streamlit as st
import pandas as pd
import random
from datetime import datetime

st.set_page_config(layout="wide")

@st.cache_data
def load_cards():
    return pd.read_csv("cards.csv")

cards_df = load_cards()

# -------------------- Helper for Featured Carousel --------------------
def get_random_cards(n=5):
    if len(cards_df) == 0:
        return []
    n = min(n, len(cards_df))
    return cards_df.sample(n).to_dict(orient="records")

# -------------------- Sidebar Dynamic Types for Cards Tab --------------------
def get_type_tabs():
    raw_types = [t.strip() for t in cards_df["type"].dropna().unique() if str(t).strip() != ""]

    priority_display = ["Base", "Insert", "Parallel", "Auto", "Patch"]
    priority_lookup = ["base", "insert", "parallel", "auto", "patch"]

    priority_types = []
    for disp, key in zip(priority_display, priority_lookup):
        if key in [r.lower() for r in raw_types]:
            priority_types.append(disp)

    remaining_types = sorted([
        t.title() for t in raw_types
        if t.lower() not in priority_lookup
    ])

    all_types = priority_types + remaining_types
    return all_types

# -------------------- Main Page --------------------
st.title("Featured Card")

featured_cards = get_random_cards(5)

# Carousel container with rotating JavaScript
carousel_imgs = []
for c in featured_cards:
    img_url = c.get("image", "")
    name = c.get("name", "Unknown Card")
    carousel_imgs.append(f"<div class='slide'><img src='{img_url}'><p>{name}</p></div>")

carousel_html = f"""
<div class='carousel'>
    {''.join(carousel_imgs)}
</div>

<style>
.carousel {{
    position: relative;
    width: 100%;
    max-width: 500px;
    height: 380px;
    overflow: hidden;
    margin: auto;
}}
.slide {{
    position: absolute;
    width: 100%;
    height: 100%;
    opacity: 0;
    transition: opacity 1s ease-in-out;
    text-align: center;
}}
.slide img {{
    max-height: 300px;
    margin: auto;
}}
.slide p {{
    font-size: 18px;
    color: white;
    background: rgba(0,0,0,0.5);
    padding: 5px;
    border-radius: 8px;
    width: fit-content;
    margin: 10px auto 0 auto;
}}
</style>

<script>
let slides = null;
let index = 0;

function showSlide(i) {{
    slides.forEach((s, idx) => {{
        s.style.opacity = idx === i ? 1 : 0;
    }});
}}

function startCarousel() {{
    slides = document.querySelectorAll('.slide');
    if (!slides.length) return;
    showSlide(index);
    setInterval(() => {{
        index = (index + 1) % slides.length;
        showSlide(index);
    }}, 5000);
}}

document.addEventListener('DOMContentLoaded', startCarousel);
</script>
"""

st.markdown(carousel_html, unsafe_allow_html=True)

# -------------------- Cards Tab --------------------
all_types = get_type_tabs()
extra_tabs = ["Slabs", "Tracking", "Admin Panel"]
all_tabs = all_types + extra_tabs

tabs = st.tabs(all_tabs)

for i, t in enumerate(all_tabs):
    with tabs[i]:
        if t in all_types:
            st.header(f"{t} Cards")
            subset = cards_df[cards_df["type"].str.lower() == t.lower()]
            for _, row in subset.iterrows():
                st.image(row.get("image", ""), width=200)
                st.write(row.get("name", "Unknown"))
        else:
            st.header(t)
            st.info(f"This is the {t} section.")
