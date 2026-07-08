# ============================================================
# components/charts.py — Plotly Enterprise Visualizations v3
# ============================================================

import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import (CHART_BG, CHART_PAPER_BG, ACCENT_BLUE, ACCENT_CYAN,
                    ACCENT_EMERALD, ACCENT_AMBER, ACCENT_ROSE, ACCENT_VIOLET)

_F = dict(family="DM Sans, sans-serif", color="#94a3b8", size=12)
_G = dict(gridcolor="rgba(59,130,246,0.07)", zeroline=False, showline=False)
_M = dict(l=8, r=8, t=40, b=8)

def _base(height=400, title="", hovermode="x unified", **kw) -> dict:
    return dict(
        template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        font=_F, margin=_M, height=height, hovermode=hovermode,
        legend=dict(bgcolor="rgba(7,20,40,.8)", bordercolor="rgba(59,130,246,.2)",
                    borderwidth=1, font=dict(size=11)),
        xaxis=_G, yaxis=_G,
        title=dict(text=title, font=dict(size=14,color="#e2e8f0"), x=0) if title else {},
        **kw,
    )


# ── Rainfall Area ─────────────────────────────────────────────
def rainfall_area(df: pd.DataFrame, height=400) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df.index, y=df["curah_hujan"], name="Curah Hujan",
        mode="lines", fill="tozeroy", fillcolor="rgba(59,130,246,.10)",
        line=dict(color=ACCENT_BLUE,width=2.5,shape="spline"),
        hovertemplate="<b>%{x|%d %b %Y}</b><br>%{y:.1f} mm<extra></extra>"))
    roll = df["curah_hujan"].rolling(7,center=True).mean()
    fig.add_trace(go.Scatter(x=df.index, y=roll, name="Rolling 7d",
        mode="lines", line=dict(color=ACCENT_CYAN,width=2,dash="dot"),
        hovertemplate="Avg 7d: %{y:.1f} mm<extra></extra>"))
    fig.add_hline(y=50, line_dash="dash", line_color=ACCENT_ROSE, line_width=1.5,
        annotation_text="Ekstrem 50mm", annotation_font_color=ACCENT_ROSE,
        annotation_position="bottom right")
    fig.update_layout(**_base(height=height, title="Tren Curah Hujan"))
    return fig


# ── Actual vs Predicted ───────────────────────────────────────
def actual_vs_predicted(dates, actual: np.ndarray, predicted: np.ndarray,
                        lstm_only: np.ndarray = None, height=460) -> go.Figure:
    fig = go.Figure()
    mae = float(np.mean(np.abs(actual - predicted)))
    fig.add_trace(go.Scatter(
        x=list(dates)+list(dates)[::-1],
        y=list(predicted+mae)+list(predicted-mae)[::-1],
        fill="toself", fillcolor="rgba(59,130,246,.07)",
        line=dict(color="rgba(0,0,0,0)"), name="Confidence Band", showlegend=True, hoverinfo="skip"))
    if lstm_only is not None:
        fig.add_trace(go.Scatter(x=dates, y=lstm_only, name="LSTM Only",
            mode="lines", line=dict(color=ACCENT_AMBER,width=1.5,dash="dot"),
            hovertemplate="LSTM: <b>%{y:.2f} mm</b><extra></extra>"))
    fig.add_trace(go.Scatter(x=dates, y=actual, name="Aktual",
        mode="lines", line=dict(color=ACCENT_EMERALD,width=2.5),
        hovertemplate="Aktual: <b>%{y:.2f} mm</b><extra></extra>"))
    fig.add_trace(go.Scatter(x=dates, y=predicted, name="Hybrid Prediksi",
        mode="lines", line=dict(color=ACCENT_BLUE,width=2.5),
        hovertemplate="Hybrid: <b>%{y:.2f} mm</b><extra></extra>"))
    fig.update_layout(**_base(height=height, title="Aktual vs Prediksi Hybrid LSTM-XGBoost"))
    return fig


# ── Forecast Bar ──────────────────────────────────────────────
def forecast_bar(dates, values: np.ndarray, height=340) -> go.Figure:
    colors = [("#22c55e" if v<5 else "#eab308" if v<20 else "#f97316" if v<50 else "#ef4444") for v in values]
    fig = go.Figure(go.Bar(
        x=[str(d) for d in dates], y=values,
        marker=dict(color=colors, opacity=.85),
        text=[f"{v:.1f}" for v in values], textposition="outside",
        textfont=dict(color="#e2e8f0",size=11),
        hovertemplate="<b>%{x}</b><br>%{y:.1f} mm<extra></extra>"))
    fig.add_hline(y=20, line_dash="dash", line_color=ACCENT_AMBER, line_width=1,
        annotation_text="Lebat (20mm)", annotation_font_color=ACCENT_AMBER)
    fig.add_hline(y=50, line_dash="dash", line_color=ACCENT_ROSE, line_width=1,
        annotation_text="Ekstrem (50mm)", annotation_font_color=ACCENT_ROSE)
    fig.update_layout(**_base(height=height, title="Prakiraan Curah Hujan",
        hovermode="x", yaxis_title="mm"))
    return fig


# ── Forecast with Confidence Band ────────────────────────────
def forecast_confidence(dates, values: np.ndarray, height=380) -> go.Figure:
    noise = np.array(values) * 0.18
    upper = values + noise
    lower = np.maximum(0, values - noise)
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(dates)+list(dates)[::-1],
        y=list(upper)+list(lower)[::-1],
        fill="toself", fillcolor="rgba(59,130,246,.09)",
        line=dict(color="rgba(0,0,0,0)"), name="Confidence Interval", hoverinfo="skip"))
    fig.add_trace(go.Scatter(x=dates, y=values, name="Prediksi",
        mode="lines+markers", line=dict(color=ACCENT_BLUE,width=2.5),
        marker=dict(size=7,color=ACCENT_BLUE,line=dict(color="#fff",width=1.5)),
        hovertemplate="<b>%{x}</b><br>Prediksi: <b>%{y:.1f} mm</b><extra></extra>"))
    fig.add_trace(go.Scatter(x=dates, y=upper, name="Batas Atas", mode="lines",
        line=dict(color=ACCENT_CYAN,width=1,dash="dot")))
    fig.add_trace(go.Scatter(x=dates, y=lower, name="Batas Bawah", mode="lines",
        line=dict(color=ACCENT_CYAN,width=1,dash="dot")))
    fig.update_layout(**_base(height=height, title="Forecast dengan Confidence Interval", yaxis_title="mm"))
    return fig


# ── Feature Importance ────────────────────────────────────────
def feature_importance(importance: dict, top_n=15, height=360) -> go.Figure:
    items  = list(importance.items())[:top_n]
    labels = [i[0] for i in items][::-1]
    vals   = [i[1] for i in items][::-1]
    n      = len(vals)
    colors = [f"rgba(59,{int(130+80*(i/max(n-1,1)))},{int(246-100*(i/max(n-1,1)))},0.85)" for i in range(n)]
    fig = go.Figure(go.Bar(x=vals, y=labels, orientation="h",
        marker=dict(color=colors), hovertemplate="<b>%{y}</b>: %{x:.4f}<extra></extra>"))
    fig.update_layout(**_base(height=height, title="Feature Importance (XGBoost)", hovermode="y unified"))
    return fig


# ── Correlation Heatmap ───────────────────────────────────────
def correlation_heatmap(df: pd.DataFrame, height=360) -> go.Figure:
    cols  = [c for c in ["curah_hujan","kecepatan_angin","kelembapan","suhu"] if c in df.columns]
    corr  = df[cols].corr()
    alias = {"curah_hujan":"Curah Hujan","kecepatan_angin":"Angin","kelembapan":"Kelembapan","suhu":"Suhu"}
    axes  = [alias.get(c,c) for c in cols]
    fig = go.Figure(go.Heatmap(z=corr.values, x=axes, y=axes,
        colorscale=[[0,"#ef4444"],[.5,"#1e293b"],[1,"#3b82f6"]], zmid=0,
        text=[[f"{v:.2f}" for v in row] for row in corr.values],
        texttemplate="%{text}", textfont=dict(size=13,color="#e2e8f0"),
        hovertemplate="<b>%{y} × %{x}</b><br>r = %{z:.3f}<extra></extra>"))
    fig.update_layout(**_base(height=height, title="Matriks Korelasi Cuaca", hovermode=False))
    return fig


# ── Monthly Box ───────────────────────────────────────────────
def monthly_box(df: pd.DataFrame, height=360) -> go.Figure:
    months = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"]
    fig = go.Figure()
    for m in range(1,13):
        vals = df.loc[df.index.month==m,"curah_hujan"]
        fig.add_trace(go.Box(y=vals, name=months[m-1], boxpoints="outliers",
            marker_color=ACCENT_BLUE, line_color=ACCENT_CYAN,
            fillcolor="rgba(59,130,246,.10)"))
    fig.update_layout(**_base(height=height, title="Distribusi Bulanan Curah Hujan",
        hovermode="closest", showlegend=False))
    return fig


# ── Agriculture Vulnerability Radar ───────────────────────────
def agri_radar(kecamatan: str, banjir: float, longsor: float,
               gagal_panen: float, irigasi: float, height=360) -> go.Figure:
    cats = ["Risiko Banjir","Risiko Longsor","Gagal Panen","Kekurangan Irigasi","Risiko Banjir"]
    vals = [banjir, longsor, gagal_panen, 100-irigasi, banjir]
    fig = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill="toself",
        fillcolor="rgba(16,185,129,.12)", line=dict(color=ACCENT_EMERALD,width=2.5),
        marker=dict(size=7,color=ACCENT_EMERALD),
        name=kecamatan, hovertemplate="<b>%{theta}</b><br>%{r:.0f}<extra></extra>"))
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=CHART_BG, height=height,
        font=_F, margin=dict(l=50,r=50,t=40,b=50),
        polar=dict(
            bgcolor="rgba(0,0,0,0)",
            radialaxis=dict(visible=True, range=[0,100], gridcolor="rgba(255,255,255,.08)",
                            tickfont=dict(size=9,color="#64748b")),
            angularaxis=dict(gridcolor="rgba(255,255,255,.08)", tickfont=dict(size=11,color="#94a3b8")),
        ),
        title=dict(text=f"Profil Risiko — {kecamatan}", font=dict(size=13,color="#e2e8f0"), x=0),
    )
    return fig


# ── Agriculture Bar (production) ─────────────────────────────
def agri_production_bar(df_agri: pd.DataFrame, height=380) -> go.Figure:
    df_s = df_agri.sort_values("produksi_padi", ascending=True)
    fig = go.Figure()
    fig.add_trace(go.Bar(x=df_s["produksi_padi"], y=df_s["kecamatan"], orientation="h",
        marker=dict(color=df_s["produksi_padi"],
                    colorscale=[[0,"#064e3b"],[.5,"#10b981"],[1,"#6ee7b7"]]),
        hovertemplate="<b>%{y}</b><br>Produksi: %{x:,.0f} ton<extra></extra>"))
    fig.update_layout(**_base(height=height, title="Produksi Padi per Kecamatan (ton)",
        hovermode="y unified", xaxis_title="Produksi (ton)"))
    return fig


# ── Vulnerability Index Bar ───────────────────────────────────
def vulnerability_index_bar(df_agri: pd.DataFrame, height=380) -> go.Figure:
    df_s = df_agri.sort_values("vulnerability_index", ascending=True)
    colors = df_s["vulnerability_index"].apply(
        lambda x: "#ef4444" if x>=.75 else "#f97316" if x>=.55 else "#eab308" if x>=.35 else "#22c55e"
    ).tolist()
    fig = go.Figure(go.Bar(x=df_s["vulnerability_index"], y=df_s["kecamatan"], orientation="h",
        marker=dict(color=colors, opacity=.88),
        text=[f"{v:.2f}" for v in df_s["vulnerability_index"]], textposition="outside",
        hovertemplate="<b>%{y}</b><br>VI: %{x:.3f}<extra></extra>"))
    fig.update_layout(
    **_base(
        height=height,
        title="Agricultural Vulnerability Index",
        hovermode="y unified"
    ),
    )

    fig.update_xaxes(range=[0, 1.1])


# ── Disaster Timeline ─────────────────────────────────────────
def disaster_timeline(df_yearly: pd.DataFrame, height=360) -> go.Figure:
    fig = make_subplots(specs=[[{"secondary_y":True}]])
    fig.add_trace(go.Bar(x=df_yearly["tahun"], y=df_yearly["banjir"],
        name="Banjir", marker_color="rgba(59,130,246,.75)"), secondary_y=False)
    fig.add_trace(go.Bar(x=df_yearly["tahun"], y=df_yearly["longsor"],
        name="Longsor", marker_color="rgba(139,92,246,.75)"), secondary_y=False)
    fig.add_trace(go.Scatter(x=df_yearly["tahun"], y=df_yearly["curah_hujan"],
        name="Curah Hujan (mm)", mode="lines+markers",
        line=dict(color=ACCENT_CYAN,width=2.5),
        marker=dict(size=7,color=ACCENT_CYAN)), secondary_y=True)
    fig.update_layout(
        template="plotly_dark", paper_bgcolor=CHART_BG, plot_bgcolor=CHART_BG,
        height=height, barmode="stack", font=_F, margin=_M, hovermode="x unified",
        legend=dict(bgcolor="rgba(7,20,40,.8)",bordercolor="rgba(59,130,246,.2)",borderwidth=1),
        title=dict(text="Kejadian Bencana & Curah Hujan Tahunan", font=dict(size=14,color="#e2e8f0"),x=0),
        xaxis=_G, yaxis=dict(**_G, title="Jumlah Kejadian"),
        yaxis2=dict(**_G, title="Curah Hujan (mm)"),
    )
    return fig


# ── Disaster Risk Heatmap (kecamatan × type) ─────────────────
def disaster_risk_matrix(df_disaster: pd.DataFrame, height=380) -> go.Figure:
    kec  = df_disaster["kecamatan"].tolist()
    z    = np.column_stack([
        df_disaster["banjir_score"].values,
        df_disaster["longsor_score"].values,
        df_disaster["kekeringan_score"].values,
    ])
    fig = go.Figure(go.Heatmap(
        z=z, x=["Banjir","Longsor","Kekeringan"], y=kec,
        colorscale=[[0,"#1e3a5f"],[.4,"#f59e0b"],[.7,"#ef4444"],[1,"#7f1d1d"]],
        text=[[f"{v:.0f}" for v in row] for row in z],
        texttemplate="%{text}", textfont=dict(size=11,color="#fff"),
        hovertemplate="<b>%{y}</b><br>%{x}: <b>%{z:.0f}</b><extra></extra>",
        zmin=0, zmax=100,
    ))
    fig.update_layout(**_base(height=height, title="Risk Matrix: Kecamatan vs Jenis Bencana", hovermode=False))
    return fig


# ── Error Distribution ────────────────────────────────────────
def error_dist(actual: np.ndarray, predicted: np.ndarray, height=320) -> go.Figure:
    errors = actual - predicted
    fig = go.Figure(go.Histogram(x=errors, nbinsx=40,
        marker=dict(color=ACCENT_BLUE,opacity=.82,line=dict(color="rgba(59,130,246,.3)",width=.5))))
    fig.add_vline(x=0, line_color=ACCENT_ROSE, line_dash="dash", line_width=2,
        annotation_text="Zero Error", annotation_font_color=ACCENT_ROSE)
    fig.update_layout(**_base(height=height, title="Distribusi Error Prediksi",
        hovermode=False, xaxis_title="Error (mm)", yaxis_title="Frekuensi"))
    return fig


# ── Scatter Actual vs Pred ────────────────────────────────────
def scatter_pred(actual: np.ndarray, predicted: np.ndarray, height=360) -> go.Figure:
    mx = max(actual.max(), predicted.max()) * 1.05
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[0,mx], y=[0,mx], mode="lines",
        line=dict(color=ACCENT_ROSE,dash="dash",width=1.5), name="Perfect"))
    fig.add_trace(go.Scatter(x=actual, y=predicted, mode="markers",
        marker=dict(color=predicted,colorscale="Blues",size=5,opacity=.7),
        name="Data", hovertemplate="Aktual:%{x:.1f}<br>Pred:%{y:.1f}<extra></extra>"))
    fig.update_layout(**_base(height=height, title="Scatter: Aktual vs Prediksi",
        hovermode="closest", xaxis_title="Aktual (mm)", yaxis_title="Prediksi (mm)"))
    return fig


# ── Loss History ─────────────────────────────────────────────
def training_loss(history: dict, height=300) -> go.Figure:
    if not history: return go.Figure()
    e = list(range(1,len(history.get("loss",[]))+1))
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=e,y=history.get("loss",[]),name="Train Loss",
        mode="lines",line=dict(color=ACCENT_BLUE,width=2)))
    if "val_loss" in history:
        fig.add_trace(go.Scatter(x=e,y=history["val_loss"],name="Val Loss",
            mode="lines",line=dict(color=ACCENT_CYAN,width=2,dash="dot")))
    fig.update_layout(**_base(height=height,title="LSTM Training Loss",
        xaxis_title="Epoch",yaxis_title="MSE Loss"))
    return fig


# ── Multi-variable Subplot ────────────────────────────────────
def weather_multi(df: pd.DataFrame, height=580) -> go.Figure:
    fig = make_subplots(rows=4,cols=1,shared_xaxes=True,vertical_spacing=0.04,
        subplot_titles=["Curah Hujan (mm)","Suhu (°C)","Kelembapan (%)","Angin (m/s)"])
    pairs = [("curah_hujan",ACCENT_BLUE),("suhu",ACCENT_AMBER),
             ("kelembapan",ACCENT_CYAN),("kecepatan_angin",ACCENT_VIOLET)]
    for row,(col,color) in enumerate(pairs,1):
        fig.add_trace(go.Scatter(x=df.index,y=df[col],fill="tozeroy",
            fillcolor=color.replace("rgb", "rgba").replace(")", ",0.08)") if "rgb" in color else "rgba(59,130,246,0.08)",line=dict(color=color,width=1.8),
            name=col.replace("_"," ").title(),showlegend=False),row=row,col=1)
    fig.update_layout(height=height,template="plotly_dark",paper_bgcolor=CHART_BG,
        plot_bgcolor=CHART_BG,font=_F,margin=dict(l=8,r=8,t=30,b=8),hovermode="x unified")
    for i in range(1,5):
        fig.update_xaxes(gridcolor="rgba(59,130,246,.07)",row=i,col=1)
        fig.update_yaxes(gridcolor="rgba(59,130,246,.07)",row=i,col=1)
    return fig
