# ============================================================
# utils/helpers.py — UI Helpers, CSS Loader, Shared Components
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import io, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import (
    RAIN_LEVELS, STYLES_PATH, APP_NAME, APP_VERSION,
    APP_TAGLINE, AUTHOR, INSTITUTION,
)


# ── CSS ───────────────────────────────────────────────────────
def load_css():
    if STYLES_PATH.exists():
        st.markdown(f"<style>{STYLES_PATH.read_text('utf-8')}</style>", unsafe_allow_html=True)
    else:
        st.markdown("<style>.stApp{background:#030c1a;color:#e2e8f0}</style>", unsafe_allow_html=True)


# ── Rain Classification ───────────────────────────────────────
def classify_rain(mm: float) -> dict:
    for lvl in RAIN_LEVELS:
        if lvl["min"] <= mm < lvl["max"]:
            return lvl
    return RAIN_LEVELS[-1]


def risk_css(risk_label: str) -> str:
    return {
        "Rendah":  "low",
        "Sedang":  "medium",
        "Tinggi":  "high",
        "Kritis":  "critical",
        "Bencana": "critical",
    }.get(risk_label, "low")


# ── Sidebar ───────────────────────────────────────────────────
def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(f"""
        <div class="sidebar-brand">
            <span class="sidebar-logo">🌧️</span>
            <p class="sidebar-title">{APP_NAME}</p>
            <p class="sidebar-tagline">AI Climate Intelligence</p>
            <span class="sidebar-badge">
                <span class="live-dot"></span>LIVE · v{APP_VERSION}
            </span>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<div style='padding:0 6px'>", unsafe_allow_html=True)

        page = st.radio(
            "navigasi",
            options=[
                "🏠  Beranda",
                "📡  Live Monitoring",
                "🤖  Prediksi Curah Hujan Ekstrem",
                "🌾  Analisis Pertanian",
                "🚨  Analisis Bencana",
                "📊  Statistik Curah Hujan",
            ],
            label_visibility="collapsed",
        )

        st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

        now = datetime.now()
        st.markdown(f"""
        <div style="font-size:11px;color:#3d5570;padding:6px 4px;
                    font-family:'JetBrains Mono',monospace">
            <div style="margin-bottom:3px">📅 {now.strftime('%d %b %Y')}</div>
            <div style="margin-bottom:3px">🕐 {now.strftime('%H:%M:%S')} WIB</div>
            <div>📍 Kab. Aceh Besar, Aceh</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

    return page


# ── Hero ──────────────────────────────────────────────────────
def render_hero(
    title: str,
    subtitle: str,
    badge: str = "● LIVE",
    module_color: str = "#3b82f6",
):
    now_str = datetime.now().strftime("%d %B %Y  •  %H:%M WIB")
    st.markdown(f"""
    <div class="hero-section fade-in">
        <div class="hero-badge" style="border-color:rgba(59,130,246,.3)">
            <span style="width:6px;height:6px;background:{module_color};border-radius:50%;
                         animation:pulse-dot 1.5s infinite;display:inline-block"></span>
            {badge}
        </div>
        <h1 class="hero-title">{title}</h1>
        <p class="hero-subtitle">{subtitle}</p>
        <div class="status-bar">
            <span class="live-status">ONLINE</span>
            <span style="color:#3d5570">|</span>
            {now_str}
            <span style="color:#3d5570">|</span>
            📍 Aceh Besar
        </div>
    </div>
    """, unsafe_allow_html=True)


# ── Section Header ────────────────────────────────────────────
def section_header(
    icon: str,
    title: str,
    sub: str = "",
    color: str = "default",
):
    css_class = {"green": "green", "red": "red", "amber": "amber"}.get(color, "")
    sub_h = f'<p class="section-sub">{sub}</p>' if sub else ""
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon {css_class}">{icon}</div>
        <div><p class="section-title">{title}</p>{sub_h}</div>
    </div>
    """, unsafe_allow_html=True)


# ── KPI Cards ─────────────────────────────────────────────────
def render_kpi_cards(stats: dict):
    rain  = stats.get("latest_rain", 0)
    lvl   = classify_rain(rain)
    cards = [
        ("🌧️", "Curah Hujan",    f"{rain:.1f}",                         "mm",  lvl["color"]),
        ("🌡️", "Suhu Udara",     f"{stats.get('latest_temp',0):.1f}",    "°C",  "#f59e0b"),
        ("💧", "Kelembapan",     f"{stats.get('latest_humidity',0):.0f}", "%",   "#06b6d4"),
        ("💨", "Kec. Angin",     f"{stats.get('latest_wind',0):.1f}",     "m/s", "#8b5cf6"),
    ]
    cols = st.columns(4)
    for col, (icon, label, val, unit, color) in zip(cols, cards):
        with col:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <span class="metric-icon">{icon}</span>
                <div class="metric-label">{label}</div>
                <div class="metric-value" style="color:{color}">{val}</div>
                <div class="metric-unit">{unit}</div>
            </div>""", unsafe_allow_html=True)


# ── Risk Banner ───────────────────────────────────────────────
def render_risk_banner(rain_mm: float):
    lvl = classify_rain(rain_mm)
    css = risk_css(lvl["risk"])
    st.markdown(f"""
    <div class="risk-card {css}">
        <div class="risk-label-sm">Status Curah Hujan Terkini</div>
        <div class="risk-value">{lvl['icon']}  {lvl['label']}</div>
        <div class="risk-desc">
            {rain_mm:.2f} mm  •  Risiko: <strong>{lvl['risk']}</strong>
        </div>
    </div>""", unsafe_allow_html=True)


# ── Alert Banner ──────────────────────────────────────────────
def render_alert(msg: str, level: str = "info"):
    icons = {
        "normal":   "✅",
        "warning":  "⚠️",
        "danger":   "🚨",
        "info":     "ℹ️",
        "critical": "🆘",
    }
    st.markdown(f"""
    <div class="alert-banner alert-{level}">
        <span style="font-size:18px">{icons.get(level,'ℹ️')}</span>
        <span>{msg}</span>
    </div>""", unsafe_allow_html=True)


# ── Footer ────────────────────────────────────────────────────
def render_footer():
    st.markdown(f"""
    <div class="app-footer">
        <div style="font-size:26px;margin-bottom:6px">🌧️</div>
        <div class="footer-name">{APP_NAME} — {APP_TAGLINE}</div>
        <div class="footer-meta">
            © {datetime.now().year} {AUTHOR} · {INSTITUTION} · v{APP_VERSION}<br>
            Hybrid LSTM-XGBoost · OpenWeatherMap API · Streamlit
        </div>
    </div>""", unsafe_allow_html=True)


# ── Export ────────────────────────────────────────────────────
def to_csv(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=True).encode("utf-8")


def to_excel(df: pd.DataFrame, sheet: str = "Data") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.to_excel(w, sheet_name=sheet)
    return buf.getvalue()


def forecast_to_csv(dates, values, labels) -> bytes:
    df_out = pd.DataFrame({
        "Tanggal":  [str(d) for d in dates],
        "Prediksi_mm": [round(v, 2) for v in values],
        "Kategori": labels,
    })
    return df_out.to_csv(index=False).encode("utf-8")
