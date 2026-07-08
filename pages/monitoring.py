# ============================================================
# pages/monitoring.py — Live Monitoring Dashboard
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import timedelta
from streamlit_folium import st_folium
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.helpers import render_hero, section_header, render_kpi_cards, render_risk_banner, render_alert, classify_rain, to_csv, to_excel
from components.charts import rainfall_area, weather_multi
from components.map_view import build_monitoring_map


def render(df: pd.DataFrame, gdf):
    render_hero(
        title="Live <span>Monitoring</span>",
        subtitle="Data cuaca real-time Aceh Besar — curah hujan, suhu, kelembapan, angin "
                 "dengan pembaruan otomatis via OpenWeatherMap API.",
        badge="📡 REAL-TIME DATA",
        module_color="#06b6d4",
    )

    stats = st.session_state.get("stats", {})
    rain  = stats.get("latest_rain", 0)
    lvl   = classify_rain(rain)

    # ── Alert ────────────────────────────────────────────────
    if lvl["risk"] == "Bencana":
        render_alert("🆘 CURAH HUJAN KATASTROFIK! Evakuasi segera. Hubungi BPBD Aceh Besar.", "critical")
    elif lvl["risk"] == "Kritis":
        render_alert(f"🚨 Curah hujan ekstrem {rain:.1f} mm! Risiko banjir & longsor sangat tinggi.", "danger")
    elif lvl["risk"] == "Tinggi":
        render_alert(f"⚠️ Hujan lebat {rain:.1f} mm. Waspada genangan dan banjir.", "warning")
    else:
        render_alert(f"✅ Kondisi cuaca normal. Curah hujan: {rain:.1f} mm.", "normal")

    # ── KPIs ─────────────────────────────────────────────────
    render_kpi_cards(stats)
    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    render_risk_banner(rain)
    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

    # ── Stats tabs ────────────────────────────────────────────
    t1, t2, t3 = st.tabs(["📅 Harian", "📆 Mingguan", "🗓️ Bulanan"])
    with t1:
        c1, c2 = st.columns(2)
        c1.metric("Curah Hujan Hari Ini", f"{rain:.1f} mm")
        c2.metric("Suhu Hari Ini", f"{stats.get('latest_temp',0):.1f} °C")
    with t2:
        c1, c2, c3 = st.columns(3)
        c1.metric("Total Hujan 7 Hari", f"{stats.get('week_sum',0):.1f} mm")
        c2.metric("Maks 7 Hari", f"{stats.get('week_max',0):.1f} mm")
        c3.metric("Rata-rata 7 Hari", f"{stats.get('week_mean',0):.1f} mm")
    with t3:
        c1, c2 = st.columns(2)
        c1.metric("Total Hujan 30 Hari", f"{stats.get('month_sum',0):.1f} mm")
        c2.metric("Maks 30 Hari", f"{stats.get('month_max',0):.1f} mm")

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

    # ── Chart + Map ───────────────────────────────────────────
    col_c, col_m = st.columns([1.3, 1], gap="medium")
    with col_c:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("📈", "Grafik Curah Hujan", "Tren historis dengan rolling average 7 hari")
        min_d, max_d = df.index.min().date(), df.index.max().date()
        dr = st.date_input("Rentang", value=(max_d - timedelta(days=180), max_d),
                           min_value=min_d, max_value=max_d, key="mon_dr")
        if len(dr) == 2:
            mask = (df.index.date >= dr[0]) & (df.index.date <= dr[1])
            df_f = df[mask]
        else:
            df_f = df.tail(180)
        st.plotly_chart(rainfall_area(df_f), use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

    with col_m:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("🗺️", "Peta Monitoring", "Heatmap curah hujan real-time")
        m = build_monitoring_map(gdf, rain, df.tail(30))
        st_folium(m, width=None, height=460, returned_objects=[])
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Multi-variable ────────────────────────────────────────
    with st.expander("🔬 Lihat Semua Variabel Cuaca", expanded=False):
        st.plotly_chart(weather_multi(df_f), use_container_width=True)

    # ── Data Table ────────────────────────────────────────────
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    section_header("📋", "Tabel Data Monitoring", "30 data terbaru")
    c1, c2 = st.columns([1, 1])
    with c1:
        st.download_button("⬇️ CSV", data=to_csv(df.tail(30)), file_name="monitoring.csv", mime="text/csv")
    with c2:
        st.download_button("⬇️ Excel", data=to_excel(df.tail(100)), file_name="monitoring.xlsx",
                           mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.dataframe(
        df.tail(30).reset_index().sort_values("tanggal", ascending=False).rename(columns={
            "tanggal":"Tanggal","curah_hujan":"Hujan (mm)","kecepatan_angin":"Angin (m/s)",
            "kelembapan":"Kelembapan (%)","suhu":"Suhu (°C)",
        }),
        use_container_width=True, height=320,
    )
    st.markdown("</div>", unsafe_allow_html=True)
