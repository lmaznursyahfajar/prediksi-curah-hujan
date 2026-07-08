# ============================================================
# pages/agriculture.py — Smart Agriculture
# Fix: peta menggunakan use_container_width=True + OSM tiles
# ============================================================

import streamlit as st
import pandas as pd
import folium
from folium.plugins import Fullscreen
from streamlit_folium import st_folium
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.helpers import render_hero, section_header, render_alert
from data.agriculture_data import get_agriculture_df, get_monthly_df
from config import CHART_BG, LOCATION
from components.map_view import build_agriculture_map

_F = dict(family="DM Sans, sans-serif", color="#94a3b8", size=12)
_G = dict(gridcolor="rgba(59,130,246,0.07)", zeroline=False)
_M = dict(l=8, r=8, t=40, b=8)


def render(df: pd.DataFrame, gdf):
    render_hero(
        title="Analisis <span>Pertanian</span>",
        subtitle="Data produksi padi dan luas sawah per kecamatan di Kabupaten Aceh Besar. "
                 "Sumber: BPS Kabupaten Aceh Besar 2022.",
        badge="🌾 AGRICULTURAL DATA",
        module_color="#10b981",
    )

    df_agri    = get_agriculture_df()
    df_monthly = get_monthly_df()
    rain       = st.session_state.get("stats", {}).get("latest_rain", 0)

    # ── Alert ─────────────────────────────────────────────────
    if rain >= 50:
        render_alert(f"🚨 Curah hujan ekstrem ({rain:.1f} mm)! Potensi gagal panen pada sawah dataran rendah.", "danger")
    elif rain >= 20:
        render_alert(f"⚠️ Hujan lebat ({rain:.1f} mm). Pantau kondisi drainase sawah di kecamatan rawan.", "warning")
    else:
        render_alert("✅ Kondisi cuaca mendukung pertanian. Monitoring rutin direkomendasikan.", "normal")

    # ── KPIs ─────────────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f"""<div class="metric-card fade-in">
            <span class="metric-icon">🌾</span>
            <div class="metric-label">Total Luas Sawah</div>
            <div class="metric-value" style="color:#10b981">{df_agri['luas_sawah'].sum():,.0f}</div>
            <div class="metric-unit">Hektar</div>
        </div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card fade-in-1">
            <span class="metric-icon">📦</span>
            <div class="metric-label">Total Produksi</div>
            <div class="metric-value" style="color:#f59e0b">{df_agri['produksi_padi'].sum()/1000:.1f}K</div>
            <div class="metric-unit">Ton Padi</div>
        </div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card fade-in-2">
            <span class="metric-icon">⚡</span>
            <div class="metric-label">Rata-rata Produktivitas</div>
            <div class="metric-value" style="color:#06b6d4">{df_agri['produktivitas'].mean():.2f}</div>
            <div class="metric-unit">Ton / Hektar</div>
        </div>""", unsafe_allow_html=True)
    with c4:
        top = df_agri.iloc[0]
        st.markdown(f"""<div class="metric-card fade-in-3">
            <span class="metric-icon">🏆</span>
            <div class="metric-label">Luas Sawah Terbesar</div>
            <div class="metric-value" style="color:#8b5cf6;font-size:20px">{top['kecamatan']}</div>
            <div class="metric-unit">{top['luas_sawah']:,} ha</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)


    # ── Tab 1: Charts + Tabel ─────────────────────────────────
  
    c1, c2 = st.columns(2, gap="medium")
    with c1:
            st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
            _shdr("🌾", "Luas Sawah per Kecamatan (Ha)")
            df_s = df_agri.sort_values("luas_sawah")
            fig = go.Figure(go.Bar(
                x=df_s["luas_sawah"], y=df_s["kecamatan"], orientation="h",
                marker=dict(color=df_s["luas_sawah"],
                            colorscale=[[0,"#064e3b"],[.5,"#10b981"],[1,"#6ee7b7"]],
                            showscale=False),
                text=[f"{v:,.0f}" for v in df_s["luas_sawah"]],
                textposition="outside", textfont=dict(color="#e2e8f0", size=10),
                hovertemplate="<b>%{y}</b><br>Luas: %{x:,.0f} ha<extra></extra>",
            ))
            fig.update_layout(template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                height=480, font=_F, margin=_M, hovermode="y unified",
                xaxis=dict(**_G, title="Luas (ha)"), yaxis=_G,
                title=dict(text="Luas Sawah (ha)", font=dict(size=13, color="#e2e8f0"), x=0))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

    with c2:
            st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
            _shdr("📦", "Produksi Padi per Kecamatan (Ton)")
            df_p = df_agri.sort_values("produksi_padi")
            fig2 = go.Figure(go.Bar(
                x=df_p["produksi_padi"], y=df_p["kecamatan"], orientation="h",
                marker=dict(color=df_p["produksi_padi"],
                            colorscale=[[0,"#1e3a5f"],[.5,"#3b82f6"],[1,"#93c5fd"]],
                            showscale=False),
                text=[f"{v:,.0f}" for v in df_p["produksi_padi"]],
                textposition="outside", textfont=dict(color="#e2e8f0", size=10),
                hovertemplate="<b>%{y}</b><br>Produksi: %{x:,.0f} ton<extra></extra>",
            ))
            fig2.update_layout(template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                height=480, font=_F, margin=_M, hovermode="y unified",
                xaxis=dict(**_G, title="Produksi (ton)"), yaxis=_G,
                title=dict(text="Produksi Padi (ton)", font=dict(size=13, color="#e2e8f0"), x=0))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Produktivitas
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    _shdr("⚡", "Produktivitas per Kecamatan (Ton/Ha)")
    df_k = df_agri.sort_values("produktivitas", ascending=True)
    colors_k = ["#22c55e" if x>=5.0 else "#eab308" if x>=4.5 else "#f97316" for x in df_k["produktivitas"]]
    fig3 = go.Figure(go.Bar(
            x=df_k["produktivitas"], y=df_k["kecamatan"], orientation="h",
            marker=dict(color=colors_k, opacity=0.85),
            text=[f"{v:.2f}" for v in df_k["produktivitas"]],
            textposition="outside", textfont=dict(color="#e2e8f0", size=10),
            hovertemplate="<b>%{y}</b><br>Produktivitas: %{x:.2f} ton/ha<extra></extra>",
        ))
    avg_k = df_agri["produktivitas"].mean()
    fig3.add_vline(x=avg_k, line_dash="dash", line_color="#06b6d4", line_width=1.5,
                       annotation_text=f"Rata-rata {avg_k:.2f}", annotation_font_color="#06b6d4")
    fig3.update_layout(template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            height=480, font=_F, margin=_M, hovermode="y unified",
            xaxis=dict(**_G, title="Produktivitas (ton/ha)", range=[3.5, 5.8]),
            yaxis=_G, showlegend=False,
            title=dict(text="Produktivitas per Kecamatan", font=dict(size=13, color="#e2e8f0"), x=0))
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

        # Tabel
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    _shdr("📋", "Tabel Data Pertanian", "Sumber: BPS Kabupaten Aceh Besar 2022")
    tbl = df_agri[["kecamatan","luas_sawah","produksi_padi","produktivitas"]].copy()
    tbl.columns = ["Kecamatan","Luas Sawah (ha)","Produksi Padi (ton)","Produktivitas (ton/ha)"]
    tbl["Luas Sawah (ha)"]     = tbl["Luas Sawah (ha)"].apply(lambda x: f"{x:,}")
    tbl["Produksi Padi (ton)"] = tbl["Produksi Padi (ton)"].apply(lambda x: f"{x:,}")
    tbl["Produktivitas (ton/ha)"] = tbl["Produktivitas (ton/ha)"].apply(lambda x: f"{x:.2f}")
    tbl = tbl.reset_index(drop=True)
    st.dataframe(tbl, use_container_width=True, height=340)
    st.download_button("⬇️ Download CSV",
            data=df_agri[["kecamatan","luas_sawah","produksi_padi","produktivitas"]].to_csv(index=False).encode(),
            file_name="data_pertanian_aceh_besar.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)


    st.markdown(
        '<div class="glass-card" style="margin-top:16px">',
        unsafe_allow_html=True,
    )

    _shdr(
        "🗺️",
        "Peta Sebaran Sawah per Kecamatan",
        "Klik pada kecamatan untuk melihat informasi luas sawah, produksi padi, dan produktivitas."
    )

    # Pastikan GeoJSON berhasil dimuat
    if gdf is None:
        st.error("❌ File GeoJSON batas kecamatan tidak berhasil dimuat.")
    else:
        # Bangun peta choropleth menggunakan komponen map_view.py
        m = build_agriculture_map(
            gdf=gdf,
            df_agri=df_agri,
        )

        st_folium(
            m,
            use_container_width=True,
            height=600,
            returned_objects=[],
        )

        st.caption(
            "Sumber: BPS Kabupaten Aceh Besar (2022). "
            "Warna menunjukkan luas sawah pada setiap kecamatan. "
            "Klik label atau wilayah kecamatan untuk melihat informasi lengkap."
        )

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
    _shdr("📅", "Produksi vs Curah Hujan Bulanan")

    months = df_monthly["Bulan"].tolist()
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
            x=months, y=df_monthly["Produksi_Ton"], name="Produksi (ton)",
            marker_color="rgba(16,185,129,.75)",
            hovertemplate="<b>%{x}</b><br>Produksi: %{y:,.0f} ton<extra></extra>",
        ))
    fig4.add_trace(go.Scatter(
            x=months, y=df_monthly["Curah_Hujan_Avg"], name="Curah Hujan (mm)",
            mode="lines+markers", yaxis="y2",
            line=dict(color="#3b82f6", width=2.5),
            marker=dict(size=7, color="#3b82f6"),
            hovertemplate="<b>%{x}</b><br>Hujan: %{y:.0f} mm<extra></extra>",
        ))
    fig4.update_layout(
            template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            height=380, hovermode="x unified", font=_F, margin=_M,
            legend=dict(bgcolor="rgba(7,20,40,.8)", bordercolor="rgba(59,130,246,.2)", borderwidth=1),
            yaxis=dict(**_G, title="Produksi (ton)"),
            yaxis2=dict(**_G, title="Curah Hujan (mm)", overlaying="y", side="right"),
            title=dict(text="Pola Musiman Produksi vs Curah Hujan",
                       font=dict(size=13, color="#e2e8f0"), x=0),
        )
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

        # Pie chart
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    _shdr("📊", "Proporsi Luas Sawah per Kecamatan")
    df_pie = df_agri.nlargest(8, "luas_sawah").copy()
    others_luas = df_agri.nsmallest(len(df_agri)-8, "luas_sawah")["luas_sawah"].sum()
    pie_labels  = df_pie["kecamatan"].tolist() + ["Lainnya"]
    pie_values  = df_pie["luas_sawah"].tolist() + [others_luas]
    colors_pie  = ["#10b981","#06b6d4","#3b82f6","#8b5cf6","#f59e0b",
                       "#f97316","#ef4444","#ec4899","#94a3b8"]
    fig5 = go.Figure(go.Pie(
            labels=pie_labels, values=pie_values,
            marker=dict(colors=colors_pie, line=dict(color="#030c1a", width=2)),
            hole=0.50,
            hovertemplate="<b>%{label}</b><br>%{value:,.0f} ha<br>%{percent}<extra></extra>",
        ))
    fig5.update_layout(
            template="plotly_dark", paper_bgcolor=CHART_BG, height=360,
            margin=dict(l=8, r=8, t=40, b=8),
            title=dict(text="Proporsi Luas Sawah (8 Terbesar)", font=dict(size=13, color="#e2e8f0"), x=0),
        )
    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)


def _shdr(icon, title, sub=""):
    sub_h = f'<p class="section-sub">{sub}</p>' if sub else ""
    st.markdown(f"""
    <div class="section-header">
        <div class="section-icon green">{icon}</div>
        <div><p class="section-title">{title}</p>{sub_h}</div>
    </div>""", unsafe_allow_html=True)
