# ============================================================
# app.py — AI Climate & Agricultural Intelligence Platform
# AcehRain Intelligence v3.1
# ============================================================

import streamlit as st
import warnings
import sys
from pathlib import Path

warnings.filterwarnings("ignore")
sys.path.insert(0, str(Path(__file__).parent))

st.set_page_config(
    page_title=" Prediksi Curah Hujan Aceh Besar",
    page_icon="🌧️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={"About": "Prediksi Curah Hujan Model Hybrid LSTM Xgboost v1.0"},
)

st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)
st.markdown("""
<style>
    [data-testid="stSidebarNav"] {
        display: none !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<meta http-equiv="refresh" content="300">', unsafe_allow_html=True)

from utils.helpers    import load_css, render_sidebar, render_footer
from utils.data_loader import load_data, reload_data, load_geojson, compute_stats
from utils.api         import try_update_api_data

# ── CSS ────────────────────────────────────────────────────────
load_css()

# ── Load Data ──────────────────────────────────────────────────
with st.spinner(""):
    df  = load_data()
    gdf = load_geojson()

# ── Update API (sekali per jam) ───────────────────────────────
import pandas as pd
now_hour = pd.Timestamp.now().floor("h")

if st.session_state.get("last_api_hour") != now_hour:
    updated = try_update_api_data()
    if updated is not None:
        # Reload data agar akumulasi hari ini langsung terlihat
        df = reload_data()
    st.session_state["last_api_hour"] = now_hour

# ── Session State ─────────────────────────────────────────────
st.session_state["df"]    = df
st.session_state["gdf"]   = gdf
st.session_state["stats"] = compute_stats(df)

# ── Navigation ─────────────────────────────────────────────────
page = render_sidebar()

if page == "🏠  Beranda":
    from pages import home
    home.render(df, gdf)
elif page == "📡  Live Monitoring":
    from pages import monitoring
    monitoring.render(df, gdf)
elif page == "🤖  AI Prediction":
    from pages import prediction
    prediction.render(df)
elif page == "🌾  Smart Agriculture":
    from pages import agriculture
    agriculture.render(df, gdf)
elif page == "🚨  Disaster Intelligence":
    from pages import disaster
    disaster.render(df, gdf)
elif page == "📊  Deep Analysis":
    from pages import analysis
    analysis.render(df)

render_footer()
