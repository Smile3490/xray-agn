import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="pPXF Results Viewer", layout="wide")

# ---- Load Data ----
@st.cache_data
def load_results():
    df = pd.read_csv("data/ppxf_results.csv")
    return df

df = load_results()

st.title("🌟 pPXF Interactive Results Dashboard")

st.markdown("""
This app lets you explore pPXF fitting results:

- Interactive scatter plots (e.g. BPT)
- Click/select a source to view cutouts and spectra
- Quick access to line fluxes, errors, EWs, χ²
""")

# ---- Sidebar Controls ----
st.sidebar.header("Plot Controls")

xcol = st.sidebar.selectbox("X-axis", df.columns)
ycol = st.sidebar.selectbox("Y-axis", df.columns)

color_by = st.sidebar.selectbox("Color by", ["None"] + list(df.columns))

# Filter by signal-to-noise or EW if needed
id_col = "id"

# ---- Scatter Plot ----
fig, ax = plt.subplots(figsize=(6, 5))

if color_by != "None":
    sc = ax.scatter(df[xcol], df[ycol], c=df[color_by], cmap="viridis")
    plt.colorbar(sc, ax=ax, label=color_by)
else:
    ax.scatter(df[xcol], df[ycol])

ax.set_xlabel(xcol)
ax.set_ylabel(ycol)
ax.grid(alpha=0.3)

st.pyplot(fig)

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