import streamlit as st
import nbformat
from nbconvert import HTMLExporter

st.set_page_config(page_title="Notebook Reader", layout="wide")

# ---- Sidebar ----
st.sidebar.title("Notebook Reader")
st.sidebar.write("Reads local .ipynb files in the repository")

# ---- Main Tabs ----
tab1, tab2 = st.tabs(["Landing Page", "Read Notebook"])

# ---- Landing Page ----
with tab1:
    st.title("Hello World")
    st.write("This landing page is ready to load additional notebooks in the future.")

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
