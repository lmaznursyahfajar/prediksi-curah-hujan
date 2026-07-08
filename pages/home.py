# ============================================================
# pages/home.py — Hero Landing Dashboard
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.helpers import render_hero, section_header, render_kpi_cards, render_risk_banner, classify_rain
from components.charts import rainfall_area
from components.insights import render_insight_cards
from data.disaster_data import get_disaster_df


def render(df: pd.DataFrame, gdf):
    render_hero(
        title='Prediksi</span> Curah Hujan</span> Aceh Besar',
        subtitle="Platform terpadu untuk monitoring cuaca real-time, prediksi curah hujan ekstrem, "
                 "analisis risiko bencana, dan sistem cerdas mitigasi pertanian Kabupaten Aceh Besar.",
        badge="● PLATFORM PREDIKSI AKTIF",
        module_color="#3b82f6",
    )
    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    stats = st.session_state.get("stats", {})
    render_kpi_cards(stats)
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    render_risk_banner(stats.get("latest_rain", 0))
    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

    # ── Platform Modules ──────────────────────────────────────
    section_header("🚀", "Platform Modules", "6 modul terintegrasi dalam satu platform AI")
    modules = [
        ("📡","Live Monitoring",    "Real-time cuaca via OWM API + peta interaktif","#06b6d4"),
        ("🤖","Prediksi Curah Hujan",      "Hybrid LSTM-XGBoost inference + forecast 14 hari","#8b5cf6"),
        ("🌾","Analisis Pertanian",  "Kerentanan pertanian + radar risiko per kecamatan","#10b981"),
        ("🚨","Analisis Risiko Bencana",     "Risk scoring bencana + mitigasi AI per kecamatan","#ef4444"),
        ("📊","Statistik Curah Hujan",      "Tren, distribusi, korelasi, pola musiman mendalam","#f59e0b"),
        ("🗺️","GIS Dashboard",     "Peta choropleth, heatmap, layer kontrol enterprise","#3b82f6"),
    ]
    c1, c2, c3 = st.columns(3)
    for i, (icon, name, desc, color) in enumerate(modules):
        col = [c1, c2, c3][i % 3]
        with col:
            st.markdown(f"""
            <div class="glass-card" style="margin-bottom:14px;padding:18px">
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                    <div style="background:{color}22;border:1px solid {color}44;border-radius:9px;
                                width:34px;height:34px;display:flex;align-items:center;
                                justify-content:center;font-size:17px">{icon}</div>
                    <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;
                                 font-size:14px;color:#e2e8f0">{name}</span>
                </div>
                <p style="font-size:12px;color:#64748b;margin:0;line-height:1.6">{desc}</p>
                <div class="vuln-bar-wrap" style="margin-top:10px">
                    <div class="vuln-bar-fill" style="width:100%;background:{color}"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

    # ── Summary Stats ─────────────────────────────────────────
    c1, c2, c3 = st.columns(3)
    df_dis = get_disaster_df()
    with c1:
        st.markdown(f"""<div class="glass-card" style="text-align:center;padding:20px">
            <div style="font-size:32px;margin-bottom:8px">📅</div>
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#64748b;margin-bottom:6px">Total Data Historis</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:700;color:#3b82f6">{stats.get('total_records',0):,}</div>
            <div style="font-size:11px;color:#64748b;margin-top:4px">{stats.get('date_start','')} → {stats.get('date_end','')}</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="glass-card" style="text-align:center;padding:20px">
            <div style="font-size:32px;margin-bottom:8px">⛈️</div>
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#64748b;margin-bottom:6px">Hari Hujan Ekstrem</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:700;color:#ef4444">{stats.get('extreme_days',0)}</div>
            <div style="font-size:11px;color:#64748b;margin-top:4px">≥50 mm sejak {stats.get('date_start','')}</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        total_kejadian = df_dis["total_kejadian"].sum()
        st.markdown(f"""<div class="glass-card" style="text-align:center;padding:20px">
            <div style="font-size:32px;margin-bottom:8px">🚨</div>
            <div style="font-size:10px;text-transform:uppercase;letter-spacing:.1em;color:#64748b;margin-bottom:6px">Kejadian Bencana</div>
            <div style="font-family:'Space Grotesk',sans-serif;font-size:28px;font-weight:700;color:#f97316">{total_kejadian}</div>
            <div style="font-size:11px;color:#64748b;margin-top:4px">2018 – 2024 Aceh Besar</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

    # ── Main Trend Chart ──────────────────────────────────────
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_header("📈", "Tren Curah Hujan Historis", "1 Tahun terakhir + rolling average 7 hari")
    st.plotly_chart(rainfall_area(df.tail(365), height=400), use_container_width=True,
                    config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    # ── AI Insights ───────────────────────────────────────────
    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)
    forecast = st.session_state.get("forecast_7d", np.zeros(7))
    render_insight_cards(df, forecast, stats.get("latest_rain", 0))

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align:center;padding:12px 0">
        <p style="font-size:12px;color:#3d5570;font-family:'JetBrains Mono',monospace">
            🧠 Hybrid LSTM-XGBoost  •  ⚡ OpenWeatherMap API  •  🗺️ Folium GIS  •  📊 Plotly Enterprise  •  🌾 Agri Intelligence
        </p>
    </div>""", unsafe_allow_html=True)
