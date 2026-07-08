# ============================================================
# pages/disaster.py — Analisis Bencana
# Update: peta choropleth GIS dengan batas kecamatan lengkap
# ============================================================

import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import plotly.graph_objects as go
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.helpers import render_hero, section_header, render_alert
from data.disaster_data import get_disaster_df, get_yearly_df, generate_event_log
from services.recommendation import generate_recommendations
from components.insights import render_mitigation_cards
from components.map_view import build_disaster_map
from config import CHART_BG, LOCATION

_F = dict(family="DM Sans, sans-serif", color="#94a3b8", size=12)
_G = dict(gridcolor="rgba(59,130,246,0.07)", zeroline=False)
_M = dict(l=8, r=8, t=40, b=8)


def render(df: pd.DataFrame, gdf):
    render_hero(
        title="Analisis <span>Bencana</span>",
        subtitle="Frekuensi kejadian dan luas lingkungan terpapar bencana per kecamatan "
                 "di Kabupaten Aceh Besar. Sumber: BPBD Aceh Besar & Peta Rawan Bencana.",
        badge="🚨 DISASTER DATA",
        module_color="#ef4444",
    )

    df_dis    = get_disaster_df()
    df_yearly = get_yearly_df()
    df_events = generate_event_log(80)
    rain      = st.session_state.get("stats", {}).get("latest_rain", 0)
    forecast  = st.session_state.get("forecast_7d", [0]*7)
    avg_f7    = float(sum(forecast) / max(len(forecast), 1))

    if rain >= 50:
        render_alert("🆘 Curah hujan ekstrem aktif! Koordinasi dengan BPBD segera.", "critical")
    elif rain >= 20:
        render_alert("🚨 Hujan lebat — potensi banjir meningkat di kecamatan rawan.", "danger")
    else:
        render_alert("✅ Kondisi normal. Sistem monitoring aktif.", "normal")

    # ── KPIs ─────────────────────────────────────────────────
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.markdown(f"""<div class="metric-card fade-in">
            <span class="metric-icon">📊</span><div class="metric-label">Total Kejadian</div>
            <div class="metric-value" style="color:#ef4444">{df_dis['total_kejadian'].sum()}</div>
            <div class="metric-unit">2018–2025</div></div>""", unsafe_allow_html=True)
    with c2:
        st.markdown(f"""<div class="metric-card fade-in-1">
            <span class="metric-icon">🌊</span><div class="metric-label">Kejadian Banjir</div>
            <div class="metric-value" style="color:#f97316">{df_dis['kejadian_banjir'].sum()}</div>
            <div class="metric-unit">Kasus</div></div>""", unsafe_allow_html=True)
    with c3:
        st.markdown(f"""<div class="metric-card fade-in-2">
            <span class="metric-icon">⛰️</span><div class="metric-label">Kejadian Longsor</div>
            <div class="metric-value" style="color:#8b5cf6">{df_dis['kejadian_longsor'].sum()}</div>
            <div class="metric-unit">Kasus</div></div>""", unsafe_allow_html=True)
    with c4:
        st.markdown(f"""<div class="metric-card fade-in-3">
            <span class="metric-icon">🗺️</span><div class="metric-label">Terpapar Banjir</div>
            <div class="metric-value" style="color:#3b82f6">{df_dis['lingkungan_banjir_ha'].sum():,.0f}</div>
            <div class="metric-unit">Hektar</div></div>""", unsafe_allow_html=True)
    with c5:
        st.markdown(f"""<div class="metric-card fade-in-4">
            <span class="metric-icon">🗺️</span><div class="metric-label">Terpapar Longsor</div>
            <div class="metric-value" style="color:#8b5cf6">{df_dis['lingkungan_longsor_ha'].sum():,.0f}</div>
            <div class="metric-unit">Hektar</div></div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📍  Peta GIS",
        "📊  Frekuensi Kejadian",
        "🗺️  Lingkungan Terpapar",
        "📈  Tren Tahunan",
        "🤖  Rekomendasi Mitigasi",
    ])

    # ── Tab 1: Peta GIS Choropleth ─────────────────────────────
    with tab1:
        st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
        _shdr("📍", "Peta Bencana — Seluruh Kecamatan Aceh Besar",
              "Warna choropleth berdasarkan data yang dipilih · Klik kecamatan untuk detail")

        col_opt, _ = st.columns([2, 2])
        with col_opt:
            peta_type = st.radio(
                "Tampilkan berdasarkan:",
                options=[
                    ("total_kejadian", "Total Kejadian"),
                    ("lingkungan_banjir_ha", "Terpapar Banjir (Ha)"),
                    ("lingkungan_longsor_ha", "Terpapar Longsor (Ha)"),
                    ("total_terpapar_ha", "Total Terpapar (Ha)"),
                ],
                format_func=lambda x: x[1],
                horizontal=True,
                key="dis_peta_type",
            )

        color_by = peta_type[0] if isinstance(peta_type, tuple) else "total_kejadian"

        m = build_disaster_map(gdf, df_dis, color_by=color_by)
        st_folium(m, use_container_width=True, height=580, returned_objects=[])
        st.caption("Sumber: BPBD Kabupaten Aceh Besar (2025) & Peta Rawan Bencana BNPB.")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 2: Frekuensi ──────────────────────────────────────
    with tab2:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
            _shdr("🌊", "Frekuensi Banjir per Kecamatan")
            df_b  = df_dis.sort_values("kejadian_banjir")
            cmap  = ["#ef4444" if x>=20 else "#f97316" if x>=12 else "#eab308" if x>=6 else "#22c55e"
                     for x in df_b["kejadian_banjir"]]
            fig = go.Figure(go.Bar(
                x=df_b["kejadian_banjir"], y=df_b["kecamatan"], orientation="h",
                marker=dict(color=cmap, opacity=0.85),
                text=df_b["kejadian_banjir"].astype(str), textposition="outside",
                textfont=dict(color="#e2e8f0", size=10),
                hovertemplate="<b>%{y}</b><br>Banjir: %{x} kejadian<extra></extra>"))
            fig.update_layout(template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                height=520, font=_F, margin=_M, hovermode="y unified",
                xaxis=dict(**_G, title="Jumlah Kejadian"), yaxis=_G, showlegend=False,
                title=dict(text="Frekuensi Banjir (2018–2025)", font=dict(size=13,color="#e2e8f0"), x=0))
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
            _shdr("⛰️", "Frekuensi Longsor per Kecamatan")
            df_l  = df_dis.sort_values("kejadian_longsor")
            cmap2 = ["#8b5cf6" if x>=8 else "#a78bfa" if x>=4 else "#c4b5fd" if x>=2 else "#ede9fe"
                     for x in df_l["kejadian_longsor"]]
            fig2 = go.Figure(go.Bar(
                x=df_l["kejadian_longsor"], y=df_l["kecamatan"], orientation="h",
                marker=dict(color=cmap2, opacity=0.85),
                text=df_l["kejadian_longsor"].astype(str), textposition="outside",
                textfont=dict(color="#e2e8f0", size=10),
                hovertemplate="<b>%{y}</b><br>Longsor: %{x} kejadian<extra></extra>"))
            fig2.update_layout(template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                height=520, font=_F, margin=_M, hovermode="y unified",
                xaxis=dict(**_G, title="Jumlah Kejadian"), yaxis=_G, showlegend=False,
                title=dict(text="Frekuensi Longsor (2018–2025)", font=dict(size=13,color="#e2e8f0"), x=0))
            st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Stacked bar
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        _shdr("📊", "Total Kejadian per Kecamatan")
        df_s = df_dis.sort_values("total_kejadian", ascending=True)
        fig3 = go.Figure()
        for name, col, color in [
            ("Banjir","kejadian_banjir","rgba(59,130,246,.75)"),
            ("Longsor","kejadian_longsor","rgba(139,92,246,.75)"),
        ]:
            fig3.add_trace(go.Bar(y=df_s["kecamatan"], x=df_s[col], name=name,
                orientation="h", marker_color=color,
                hovertemplate=f"<b>%{{y}}</b><br>{name}: %{{x}}<extra></extra>"))
        fig3.update_layout(template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
            height=520, barmode="stack", font=_F, margin=_M, hovermode="y unified",
            legend=dict(bgcolor="rgba(7,20,40,.8)",bordercolor="rgba(59,130,246,.2)",borderwidth=1),
            xaxis=dict(**_G, title="Jumlah Kejadian"), yaxis=_G,
            title=dict(text="Total Kejadian Bencana per Kecamatan",font=dict(size=13,color="#e2e8f0"),x=0))
        st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar":False})
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 3: Lingkungan Terpapar ────────────────────────────
    with tab3:
        c1, c2 = st.columns(2, gap="medium")
        with c1:
            st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
            _shdr("🌊", "Lingkungan Terpapar Banjir (Ha)")
            df_tb = df_dis[df_dis["lingkungan_banjir_ha"]>0].sort_values("lingkungan_banjir_ha")
            cmap_b = ["#ef4444" if x>=3000 else "#f97316" if x>=2000 else "#eab308" if x>=1000 else "#22c55e"
                      for x in df_tb["lingkungan_banjir_ha"]]
            fig4 = go.Figure(go.Bar(
                x=df_tb["lingkungan_banjir_ha"], y=df_tb["kecamatan"], orientation="h",
                marker=dict(color=cmap_b, opacity=0.85),
                text=[f"{v:,.0f}" for v in df_tb["lingkungan_banjir_ha"]], textposition="outside",
                textfont=dict(color="#e2e8f0", size=10),
                hovertemplate="<b>%{y}</b><br>Terpapar Banjir: %{x:,.0f} ha<extra></extra>"))
            fig4.update_layout(template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                height=500, font=_F, margin=_M, hovermode="y unified",
                xaxis=dict(**_G, title="Luas (ha)"), yaxis=_G, showlegend=False,
                title=dict(text="Terpapar Banjir (Ha)",font=dict(size=13,color="#e2e8f0"),x=0))
            st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
            _shdr("⛰️", "Lingkungan Terpapar Longsor (Ha)")
            df_tl = df_dis[df_dis["lingkungan_longsor_ha"]>0].sort_values("lingkungan_longsor_ha")
            cmap_l = ["#8b5cf6" if x>=10000 else "#a78bfa" if x>=5000 else "#c4b5fd" if x>=1000 else "#ede9fe"
                      for x in df_tl["lingkungan_longsor_ha"]]
            fig5 = go.Figure(go.Bar(
                x=df_tl["lingkungan_longsor_ha"], y=df_tl["kecamatan"], orientation="h",
                marker=dict(color=cmap_l, opacity=0.85),
                text=[f"{v:,.0f}" for v in df_tl["lingkungan_longsor_ha"]], textposition="outside",
                textfont=dict(color="#e2e8f0", size=10),
                hovertemplate="<b>%{y}</b><br>Terpapar Longsor: %{x:,.0f} ha<extra></extra>"))
            fig5.update_layout(template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
                height=500, font=_F, margin=_M, hovermode="y unified",
                xaxis=dict(**_G, title="Luas (ha)"), yaxis=_G, showlegend=False,
                title=dict(text="Terpapar Longsor (Ha)",font=dict(size=13,color="#e2e8f0"),x=0))
            st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar":False})
            st.markdown("</div>", unsafe_allow_html=True)

        # Tabel lengkap
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        _shdr("📋", "Tabel Lengkap Kejadian & Lingkungan Terpapar")
        tbl = df_dis[["kecamatan","total_kejadian","kejadian_banjir","kejadian_longsor",
                      "lingkungan_banjir_ha","lingkungan_longsor_ha","total_terpapar_ha"]].copy()
        tbl.columns = ["Kecamatan","Total Kej.","Banjir","Longsor",
                       "Terpapar Banjir (Ha)","Terpapar Longsor (Ha)","Total Terpapar (Ha)"]
        for col in ["Terpapar Banjir (Ha)","Terpapar Longsor (Ha)","Total Terpapar (Ha)"]:
            tbl[col] = tbl[col].apply(lambda x: f"{x:,.0f}")
        tbl = tbl.reset_index(drop=True)
        st.dataframe(tbl, use_container_width=True, height=420)
        st.download_button("⬇️ Download CSV",
            data=df_dis[["kecamatan","total_kejadian","kejadian_banjir","kejadian_longsor",
                        "lingkungan_banjir_ha","lingkungan_longsor_ha",
                         "total_terpapar_ha"]].to_csv(index=False).encode(),
            file_name="data_bencana_aceh_besar.csv", mime="text/csv")
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Tab 4: Tren Tahunan ─────────────────────────────────────
    with tab4:

        st.markdown(
            '<div class="glass-card" style="margin-top:16px">',
            unsafe_allow_html=True
        )

        _shdr("📈", "Tren Kejadian Bencana per Tahun")

        # ===========================
        # FILTER KECAMATAN
        # ===========================

        daftar_kecamatan = sorted(df_yearly["kecamatan"].unique())

        selected = st.selectbox(
            "Pilih Kecamatan",
            ["Semua Kecamatan"] + daftar_kecamatan,
            key="trend_kecamatan"
        )

        # ===========================
        # FILTER JENIS BENCANA
        # ===========================

        jenis = st.radio(
            "Jenis Bencana",
            ["Semua", "Banjir", "Longsor"],
            horizontal=True
        )

        # ===========================
        # DATA
        # ===========================

        if selected == "Semua Kecamatan":

            plot_df = (
                df_yearly
                .groupby("tahun")[["banjir", "longsor"]]
                .sum()
                .reset_index()
            )

        else:

            plot_df = (
                df_yearly[df_yearly["kecamatan"] == selected]
                .sort_values("tahun")
            )

        # ===========================
        # GRAFIK BATANG
        # ===========================

        fig6 = go.Figure()

        if jenis == "Semua":

            fig6.add_trace(
                go.Bar(
                    x=plot_df["tahun"],
                    y=plot_df["banjir"],
                    name="Banjir",
                    marker_color="rgba(59,130,246,0.85)",
                    hovertemplate="<b>%{x}</b><br>Banjir : %{y}<extra></extra>"
                )
            )

            fig6.add_trace(
                go.Bar(
                    x=plot_df["tahun"],
                    y=plot_df["longsor"],
                    name="Longsor",
                    marker_color="rgba(139,92,246,0.85)",
                    hovertemplate="<b>%{x}</b><br>Longsor : %{y}<extra></extra>"
                )
            )

        elif jenis == "Banjir":

            fig6.add_trace(
                go.Bar(
                    x=plot_df["tahun"],
                    y=plot_df["banjir"],
                    marker_color="rgba(59,130,246,0.85)",
                    name="Banjir"
                )
            )

        else:

            fig6.add_trace(
                go.Bar(
                    x=plot_df["tahun"],
                    y=plot_df["longsor"],
                    marker_color="rgba(139,92,246,0.85)",
                    name="Longsor"
                )
            )

        fig6.update_layout(

            template="plotly_dark",

            paper_bgcolor=CHART_BG,
            plot_bgcolor=CHART_BG,

            barmode="group",

            height=420,

            margin=_M,

            font=_F,

            hovermode="x unified",

            title=dict(
                text=f"Tren Kejadian Bencana ({selected})",
                x=0,
                font=dict(size=14, color="#e2e8f0")
            ),

            xaxis=dict(
                **_G,
                title="Tahun",
                tickmode="linear",
                dtick=1
            ),

            yaxis=dict(
                **_G,
                title="Jumlah Desa/Kelurahan Terdampak"
            ),

            legend=dict(
                orientation="h",
                y=1.05,
                x=1,
                xanchor="right"
            )

        )

        st.plotly_chart(
            fig6,
            use_container_width=True,
            config={"displayModeBar": False}
        )

        st.markdown("</div>", unsafe_allow_html=True)
    # ── Tab 5: Rekomendasi ────────────────────────────────────
    with tab5:
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        section_header("🤖","Sistem Rekomendasi Mitigasi Bencana",
                       f"Berdasarkan curah hujan {rain:.1f} mm & prakiraan 7 hari")
        kec_list = sorted(df_dis["kecamatan"].tolist())
        col_s, col_r = st.columns([2,1])
        with col_s:
            sel_kec = st.selectbox("🏘️ Pilih Kecamatan", kec_list)
        with col_r:
            sim_rain = st.number_input("💧 Simulasi Curah Hujan (mm)",
                                       min_value=0.0, max_value=300.0, value=float(rain), step=5.0)
        plan = generate_recommendations(sel_kec, sim_rain, avg_f7)
        rc = {"NORMAL":"#22c55e","WASPADA":"#eab308","SIAGA":"#f97316",
              "BAHAYA":"#ef4444","BENCANA":"#7f1d1d"}.get(plan.risk_level,"#3b82f6")
        st.markdown(f"""
        <div style="background:{rc}15;border:1px solid {rc}44;border-radius:16px;
                    padding:18px 22px;margin:16px 0;position:relative;overflow:hidden">
            <div style="position:absolute;top:0;left:0;right:0;height:2px;background:{rc}"></div>
            <div style="display:flex;align-items:center;gap:12px">
                <div style="font-size:28px">🚨</div>
                <div>
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:4px">
                        <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;
                                     font-size:16px;color:#e2e8f0">{sel_kec}</span>
                        <span style="background:{rc}22;color:{rc};border:1px solid {rc}44;
                                     border-radius:6px;padding:2px 9px;font-size:11px;font-weight:700">{plan.risk_level}</span>
                    </div>
                    <p style="font-size:13px;color:#94a3b8;margin:0">{plan.alert_message}</p>
                </div>
            </div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="background:rgba(59,130,246,.08);border:1px solid rgba(59,130,246,.22);
                    border-radius:12px;padding:14px 18px;margin-bottom:16px">
            <div style="font-size:11px;text-transform:uppercase;letter-spacing:.08em;
                        color:#60a5fa;font-weight:600;margin-bottom:6px">🧠 Insight Cuaca</div>
            <p style="font-size:13px;color:#94a3b8;margin:0;line-height:1.7">{plan.smart_insight}</p>
        </div>""", unsafe_allow_html=True)
        section_header("📋","Rekomendasi Aksi Mitigasi","Urutan prioritas")
        render_mitigation_cards(plan)


def _shdr(icon, title, sub=""):
    sub_h = f'<p class="section-sub">{sub}</p>' if sub else ""
    st.markdown(f"""<div class="section-header">
        <div class="section-icon red">{icon}</div>
        <div><p class="section-title">{title}</p>{sub_h}</div>
    </div>""", unsafe_allow_html=True)