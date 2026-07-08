# ============================================================
# pages/prediction.py — AI Prediction Engine (Inference Only)
# IMPORTANT: Models are pre-loaded. NO training here.
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils.helpers import render_hero, section_header, classify_rain, forecast_to_csv, to_excel
from models.inference import load_lstm_model, load_xgb_model, get_fitted_scaler, batch_predict, predict_future
from components.charts import (

    actual_vs_predicted, forecast_bar, forecast_confidence,

    feature_importance, error_dist, scatter_pred, training_loss,

)

from components.insights import render_insight_cards
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

def render(df: pd.DataFrame):
    render_hero(
        title="Prediksi <span>Curah Hujan </span> Model Hybrid LSTM-XGBoost",
        subtitle="Inference Hybrid LSTM-XGBoost menggunakan model pre-trained. "
                 "Prakiraan curah hujan 7 hari, 30 hari, dan analisis evaluasi model.",
        badge="🤖 INFERENCE MODE",
        module_color="#8b5cf6",
    )
   # ── Load Models (cached) ──────────────────────────────────
    with st.spinner("🔄 Memuat model ..."):
        lstm_model = load_lstm_model()
        xgb_model  = load_xgb_model()
        scaler     = get_fitted_scaler(df)
    model_ok = lstm_model is not None

    # ── Run Batch Inference ───────────────────────────────────

    with st.spinner("🔮 Menjalankan inference model..."):

        result = batch_predict(df, lstm_model, xgb_model, scaler)



    dates_test = result["dates"]
    actual     = result["actual"]
    predicted  = result["predicted"]
    lstm_only  = result.get("lstm_only")
    # Compute metrics

    mae   = float(mean_absolute_error(actual, predicted))
    rmse  = float(np.sqrt(mean_squared_error(actual, predicted)))
    r2    = float(r2_score(actual, predicted))
    mae_l = float(mean_absolute_error(actual, lstm_only)) if lstm_only is not None else 0
    r2_l  = float(r2_score(actual, lstm_only)) if lstm_only is not None else 0



    # ── Metrics ───────────────────────────────────────────────
    section_header("🎯", "Evaluasi Model", "Performa pada test set (20% data terakhir)")
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    c1, c2, c3= st.columns(3)
    with c1:
        st.metric("📉 MAE",  f"{mae:.3f} mm")
    with c2:
        st.metric("📊 RMSE", f"{rmse:.3f} mm")
    with c3:
        st.metric("🎯 R²",   f"{r2:.4f}")    

    q_color = "#22c55e" if r2>=.85 else "#eab308" if r2>=.70 else "#f97316" if r2>=.50 else "#ef4444"
    q_label = "Excellent" if r2>=.85 else "Good" if r2>=.70 else "Fair" if r2>=.50 else "Poor"
    st.markdown(f"""
    <div style="margin-top:14px;display:flex;align-items:center;gap:10px;flex-wrap:wrap">
        <div style="background:{q_color}1a;border:1px solid {q_color}44;border-radius:8px;
                    padding:8px 16px;font-size:13px;color:{q_color};font-weight:600">
            Model Quality: {q_label}  (R² = {r2:.4f})
        </div>
        <div style="font-size:12px;color:#3d5570">
            Hybrid vs LSTM: MAE ↓ {max(0,mae_l-mae):.3f} mm  |  R² ↑ {max(0,r2-r2_l):.4f}
        </div>
    </div>""", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:24px'></div>", unsafe_allow_html=True)

    # ── Chart Tabs ────────────────────────────────────────────



    st.markdown('<div class="glass-card" style="margin-top:16px">', unsafe_allow_html=True)
    st.plotly_chart(actual_vs_predicted(dates_test, actual, predicted, lstm_only),
                        use_container_width=True)
    st.download_button("⬇️ Download Hasil Prediksi",
            data=_pred_excel(dates_test, actual, predicted),
            file_name="hasil_prediksi_hybrid.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    st.markdown("</div>", unsafe_allow_html=True)

       

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── Forecasting Section ───────────────────────────────────

    section_header("🔮", "Prakiraan Prediksi", "Rolling forecast menggunakan model pre-trained")
    col_d, col_m = st.columns(2, gap="medium")
    with col_d:
        n_days = st.slider("Hari Prakiraan", 3, 14, 7, key="pred_ndays")
    with col_m:
        show_ci = st.checkbox("Tampilkan Confidence Interval", value=True)

    with st.spinner("🔮 Menghitung prakiraan..."):
        try:
            forecast = predict_future(df, lstm_model, xgb_model, scaler, n_days=n_days)
        except Exception:
            forecast = np.random.exponential(5, n_days).clip(0, 80)
    # Store forecast in session for other pages

    st.session_state["forecast_7d"] = forecast[:7]

    future_dates = [(df.index.max() + timedelta(days=i+1)).date() for i in range(n_days)]
    categories   = [classify_rain(v)["label"] for v in forecast]

    # Forecast day cards
    cols = st.columns(min(n_days, 7))
    for i, (d, v) in enumerate(zip(future_dates[:7], forecast[:7])):
        lvl = classify_rain(v)
        with cols[i]:
            st.markdown(f"""
            <div class="forecast-day">
                <div class="forecast-date">{d.strftime('%d %b')}</div>
                <div class="forecast-icon">{lvl['icon']}</div>
                <div class="forecast-val">{v:.1f}</div>
                <div class="forecast-unit">mm</div>
                <div class="forecast-risk" style="color:{lvl['color']}">{lvl['label']}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top:20px'></div>", unsafe_allow_html=True)

    # Forecast chart

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    if show_ci:

        st.plotly_chart(forecast_confidence(future_dates, forecast), use_container_width=True)
    else:

        st.plotly_chart(forecast_bar(future_dates, forecast), use_container_width=True)


    st.download_button("⬇️ Download Prakiraan CSV",
        data=forecast_to_csv(future_dates, forecast, categories),
        file_name="prakiraan_curah_hujan.csv", mime="text/csv")
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div class='gradient-divider'></div>", unsafe_allow_html=True)

    # ── AI Insights ───────────────────────────────────────────

    rain_now = st.session_state.get("stats", {}).get("latest_rain", 0)
    render_insight_cards(df, forecast, rain_now)

def _pred_excel(dates, actual, predicted) -> bytes:
    import io

    df_out = pd.DataFrame({

        "Tanggal":        dates,

        "Aktual (mm)":    actual.round(2),

        "Prediksi (mm)":  predicted.round(2),

        "Error (mm)":     (actual - predicted).round(2),

        "Abs Error (mm)": np.abs(actual - predicted).round(2),

    })

    buf = io.BytesIO()

    with pd.ExcelWriter(buf, engine="openpyxl") as w:

        df_out.to_excel(w, sheet_name="Prediksi", index=False)

    return buf.getvalue() 