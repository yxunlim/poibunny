import streamlit as st
import nbformat
from nbconvert import HTMLExporter

st.set_page_config(page_title="POiBUNNY", layout="wide")

# ---- Sidebar ----
st.sidebar.title("Welcome to my Collection")
st.sidebar.write("Feel free to email me at lynx1186@hotmail.com to purchase my cards")

# ---- Main Tabs ----
tab1, tab2 = st.tabs(["Main", "Cards"])

# ---- Landing Page ----
with tab1:
    st.title("Hello World")
    st.write("Market Price follows PriceCharting at USD prices. Listing price is default 1.1x, always happy to discuss")

# ---- Notebook Reader ----
with tab2:
    st.header("base.ipynb Preview")

    try:
        with open("base.ipynb", "r", encoding="utf-8") as f:
            notebook = nbformat.read(f, as_version=4)

        html_exporter = HTMLExporter()
        html_exporter.template_name = "classic"

        (body, resources) = html_exporter.from_notebook_node(notebook)

        st.components.v1.html(body, height=800, scrolling=True)

    except FileNotFoundError:
        st.error("base.ipynb not found in the repository.")
    except Exception as e:
        st.error(f"Error reading notebook: {e}")
