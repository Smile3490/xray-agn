# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

st.set_page_config(page_title="pPXF Interactive Viewer", layout="wide")

# ========================
# Load results table
# ========================
@st.cache_data
def load_results():
    return pd.read_csv("tables/ppxf_results.csv")

df = load_results()
id_col = "id"

st.title("🌟 pPXF Interactive Results Dashboard")

st.markdown("""
Explore pPXF results:

- Interactive scatter plots (Plotly)
- Hover to show ID, redshift
- Column calculator for custom derived quantities
- Built-in BPT diagram mode
""")


# BPT boundaries
def add_bpt_boundaries(fig):
    import numpy as np

    # Kauffmann 2003
    x = np.linspace(-2.0, 0., 200)
    y = 0.61 / (x - 0.05) + 1.3
    fig.add_scatter(x=x, y=y, mode="lines",
                    line=dict(color="blue", dash="dash"),
                    name="Kauffmann 2003")

    # Kewley 2001
    x = np.linspace(-2.0, 0.4, 200)
    y = 0.61 / (x - 0.47) + 1.19
    fig.add_scatter(x=x, y=y, mode="lines",
                    line=dict(color="red", dash="solid"),
                    name="Kewley 2001")

    # Seyfert/LINER division (Kewley 2006)
    x = np.linspace(-0.18, 1.5, 200)
    y = 1.05 * x + 0.45
    fig.add_scatter(x=x, y=y, mode="lines",
                    line=dict(color="black", dash="dot"),
                    name="Seyfert/LINER (Kewley 2006)")

# ========================
# Sidebar Controls
# ========================

st.sidebar.header("Plot Controls")

mode = st.sidebar.radio(
    "Plot mode:",
    ["Custom scatter", "BPT diagram"],
)

# Custom scatter: select columns manually
if mode == "Custom scatter":
    xcol = st.sidebar.selectbox("X-axis", df.columns)
    ycol = st.sidebar.selectbox("Y-axis", df.columns)
    color_by = st.sidebar.selectbox("Color by", ["None"] + list(df.columns))

# BPT mode: columns are fixed
if mode == "BPT diagram":
    # Compute BPT axes
    df["NII_Ha"] = df["[NII]6583_d_flux"] / (df["Halpha_flux"])
    df["OIII_Hb"] = df["[OIII]5007_d_flux"] / (df["Hbeta_flux"])

    df["log_NII_Ha"] = np.log10(df["NII_Ha"])
    df["log_OIII_Hb"] = np.log10(df["OIII_Hb"])

    xcol = "log_NII_Ha"
    ycol = "log_OIII_Hb"
    color_by = st.sidebar.selectbox("Color by", ["None"] + list(df.columns))

    st.sidebar.success("BPT axes generated automatically.")


# ========================
# Column calculator
# ========================

st.sidebar.header("Column Calculator")

calc_expr = st.sidebar.text_input(
    "Enter expression using df[...] syntax:\n"
    'Example:\n'
    'df["[OIII]5007_d_flux"] / df["Hbeta_flux"]'
)

new_col_name = st.sidebar.text_input("Name the new column")

if calc_expr and new_col_name:
    try:
        df[new_col_name] = eval(calc_expr, {"df": df, "np": np})
        st.sidebar.success(f"Column '{new_col_name}' created.")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")


# ========================
# Interactive Plot
# ========================

st.header("Interactive Scatter Plot")

hover_columns = [
    id_col, "redshift"
]

fig = px.scatter(
    df,
    x=xcol,
    y=ycol,
    color=color_by if color_by != "None" else None,
    hover_data=hover_columns,
    height=650,
)

if mode == "BPT diagram":
    add_bpt_boundaries(fig)
    
fig.update_traces(marker=dict(size=8, opacity=0.8))
selected_points = st.plotly_chart(fig, use_container_width=True)


# ========================
# Select a source (manual & click)
# ========================

st.header("Selected Source Details")

# CLICK HANDLING
# Note: Streamlit currently exposes Plotly click events via st.session_state
clicked_id = None

if "selectedpoints" in st.session_state:
    pts = st.session_state["selectedpoints"]
    if pts and len(pts) > 0:
        idx = pts[0]   # index in the dataframe
        clicked_id = df.iloc[idx][id_col]

# Manual fallback selector
selected_id = clicked_id or st.selectbox("Choose source:", df[id_col].unique())

row = df[df[id_col] == selected_id].iloc[0]


# ========================
# Show images for this source
# ========================

col1, col2 = st.columns(2)

with col1:
    st.subheader("All Info")
    info_path = f"info/{selected_id}.png"
    if os.path.exists(info_path):
        st.image(info_path)
    else:
        st.write("No info image found.")

with col2:
    st.subheader("pPXF Fitting Results")
    fit_path = f"fitting_results/{selected_id}.png"
    if os.path.exists(fit_path):
        st.image(fit_path)
    else:
        st.write("No fitting result found.")

st.subheader(f"Metadata for {selected_id}")
st.json(row.to_dict())

