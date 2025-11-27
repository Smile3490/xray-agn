import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import os

st.set_page_config(page_title="pPXF Results Viewer", layout="wide")

# ---- Load Data ----
@st.cache_data
def load_results():
    df = pd.read_csv("tables/ppxf_results.csv")
    return df

df = load_results()

st.title("🌟 pPXF Interactive Results Dashboard")

st.markdown("""
This app lets you explore pPXF fitting results:

- Interactive scatter plots (e.g. BPT)
- Click/select a source to view cutouts and spectra
- Quick access to line fluxes, errors, EWs, χ²
""")


st.sidebar.header("Column Calculator")
expr = st.sidebar.text_input(
    "Enter a column expression (e.g. ppxf_[OIII]5007_d_flux / ppxf_Hbeta_flux)",
    ""
)
colname = st.sidebar.text_input(
    "Name the column",
    ""
)

if expr:
    try:
        df[colname] = eval(expr, {"__builtins__": None}, df.to_dict("series"))
        st.sidebar.success("Column "+colname+" created!")
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
        
# ---- Sidebar Controls ----
st.sidebar.header("Plot Controls")

xcol = st.sidebar.selectbox("X-axis", df.columns)
ycol = st.sidebar.selectbox("Y-axis", df.columns)

color_by = st.sidebar.selectbox("Color by", ["None"] + list(df.columns))

# Filter by signal-to-noise or EW if needed
id_col = "id"

# ---- Scatter Plot ----

fig = px.scatter(
    df,
    x=xcol,
    y=ycol,
    color=color_by if color_by != "None" else 'k',
    hover_data=[id_col, "redshift"],
    width=650,
    height=550,
)


st.plotly_chart(fig, use_container_width=True)

selected = st.plotly_chart(fig, use_container_width=True).selection["points"]

# ---- Select a Source ----
st.header("Selected Source Details")

selected_id = st.selectbox("Choose a source ID:", df[id_col].unique())
row = df[df[id_col] == selected_id].iloc[0]

st.subheader(f"📄 Metadata for {selected_id}")
st.json(row.to_dict())

# ---- Display Cutout + Spectrum ----
col1, col2 = st.columns(2)

with col1:
    st.subheader("All Info")
    info_path = f"info/{selected_id}.png"
    if os.path.exists(info_path):
        st.image(info_path)
    else:
        st.write("No info found.")

with col2:
    st.subheader("Fitting Results")
    fit_path = f"fitting_results/{selected_id}.png"
    if os.path.exists(fit_path):
        st.image(fit_path)
    else:
        st.write("No fitting result found.")