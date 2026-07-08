# ============================================================
# pages/analysis.py — Deep Statistical Analysis
# ============================================================
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.helpers import render_hero, section_header, classify_rain, to_csv
from components.charts import correlation_heatmap, monthly_box, rainfall_area
from config import CHART_BG, ACCENT_BLUE, ACCENT_CYAN, ACCENT_AMBER, ACCENT_ROSE
_F = dict(family="DM Sans, sans-serif", color="#94a3b8", size=12)
_G = dict(gridcolor="rgba(59,130,246,0.07)", zeroline=False)
_M = dict(l=8, r=8, t=40, b=8)


def render(df: pd.DataFrame):
    render_hero(title="Statistik <span>Curah Hujan</span>",
        subtitle="Analisis statistik mendalam: tren, distribusi, korelasi, pola musiman, dan deteksi anomali.",
        badge="📊 STATISTICAL ENGINE", module_color="#8b5cf6")

    # Filters
    with st.expander("🔧 Filter Data", expanded=False):
        c1, c2 = st.columns(2)
        years = sorted(df.index.year.unique(), reverse=True)
        sel_y = c1.multiselect("Tahun", years, default=years[:3], key="an_y")
        m_n   = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
        sel_m = c2.multiselect("Bulan", list(range(1,13)), default=list(range(1,13)),
                               format_func=lambda x: m_n[x-1], key="an_m")
    df_f = df[df.index.year.isin(sel_y) & df.index.month.isin(sel_m)] if (sel_y and sel_m) else df
    if len(df_f) == 0:
        st.warning("Tidak ada data untuk filter ini."); return

    tab1, tab2, tab3, tab4 = st.tabs(["📈 Tren","📦 Distribusi","🔗 Korelasi","🌙 Musiman"])

    with tab1:
        st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
        st.plotly_chart(rainfall_area(df_f, height=400), use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        # Annual cumulative
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        section_header("📊","Curah Hujan Kumulatif Tahunan")
        colors = ["#3b82f6","#06b6d4","#f59e0b","#ef4444","#8b5cf6"]
        fig = go.Figure()
        for i, yr in enumerate(sorted(sel_y or years)):
            d = df[df.index.year==yr]["curah_hujan"]
            if len(d):
                cs = d.groupby(d.index.dayofyear).sum().cumsum()
                fig.add_trace(go.Scatter(x=cs.index, y=cs.values, name=str(yr),
                    mode="lines", line=dict(color=colors[i%len(colors)],width=2)))
        fig.update_layout(template="plotly_dark",paper_bgcolor=CHART_BG,plot_bgcolor=CHART_BG,
            height=340,font=_F,margin=_M,hovermode="x unified",xaxis=_G,yaxis=_G,
            title=dict(text="Curah Hujan Kumulatif per Tahun",font=dict(size=14,color="#e2e8f0"),x=0))
        st.plotly_chart(fig, use_container_width=True); st.markdown("</div>", unsafe_allow_html=True)

    with tab2:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
            fig = go.Figure(go.Histogram(x=df_f["curah_hujan"],nbinsx=50,
                marker=dict(color=ACCENT_BLUE,opacity=.82)))
            fig.add_vline(x=df_f["curah_hujan"].mean(),line_dash="dash",line_color=ACCENT_AMBER,
                annotation_text="Mean",annotation_font_color=ACCENT_AMBER)
            fig.update_layout(template="plotly_dark",paper_bgcolor=CHART_BG,plot_bgcolor=CHART_BG,
                height=320,font=_F,margin=_M,xaxis=_G,yaxis=_G,
                title=dict(text="Histogram Curah Hujan",font=dict(size=14,color="#e2e8f0"),x=0))
            st.plotly_chart(fig, use_container_width=True); st.markdown("</div>", unsafe_allow_html=True)
        with c2:
            st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
            cats = {}
            for v in df_f["curah_hujan"]:
                lbl = classify_rain(v)["label"]
                cats[lbl] = cats.get(lbl, 0) + 1
            colors_p = ["#22c55e","#84cc16","#eab308","#f97316","#ef4444"]
            fig2 = go.Figure(go.Pie(labels=list(cats.keys()), values=list(cats.values()),
                marker=dict(colors=colors_p[:len(cats)],line=dict(color="#030c1a",width=2)),
                hole=0.52))
            fig2.update_layout(template="plotly_dark",paper_bgcolor=CHART_BG,height=320,
                margin=_M,title=dict(text="Proporsi Kategori Hujan",font=dict(size=14,color="#e2e8f0"),x=0))
            st.plotly_chart(fig2, use_container_width=True); st.markdown("</div>", unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
        st.plotly_chart(correlation_heatmap(df_f,height=400),use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with tab4:
        st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
        st.plotly_chart(monthly_box(df_f,height=380),use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)
        # Monthly avg
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        mn = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
        avg = df_f.groupby(df_f.index.month)["curah_hujan"].mean()
        std = df_f.groupby(df_f.index.month)["curah_hujan"].std().fillna(0)
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=mn,y=(avg+std).values,fill=None,mode="lines",
            line_color="rgba(0,0,0,0)",showlegend=False))
        fig.add_trace(go.Scatter(x=mn,y=(avg-std).values,fill="tonexty",
            fillcolor="rgba(59,130,246,.08)",mode="lines",line_color="rgba(0,0,0,0)",name="±1 Std"))
        fig.add_trace(go.Scatter(x=mn,y=avg.values,name="Rata-rata",mode="lines+markers",
            line=dict(color=ACCENT_BLUE,width=2.5),marker=dict(size=8,color=ACCENT_BLUE)))
        fig.update_layout(template="plotly_dark",paper_bgcolor=CHART_BG,plot_bgcolor=CHART_BG,
            height=340,font=_F,margin=_M,xaxis=_G,yaxis=_G,hovermode="x unified",
            title=dict(text="Pola Musiman Rata-rata Bulanan",font=dict(size=14,color="#e2e8f0"),x=0))
        st.plotly_chart(fig,use_container_width=True); st.markdown("</div>", unsafe_allow_html=True)

    with st.expander("⬇️ Export Data"):
        st.download_button("CSV", data=to_csv(df_f), file_name="analysis_data.csv", mime="text/csv")
