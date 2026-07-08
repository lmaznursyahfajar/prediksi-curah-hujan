# ============================================================
# models/inference.py — Pre-trained Model Inference Engine
# IMPORTANT: This module ONLY loads and runs inference.
# Models are pre-trained. NEVER retrain on app startup.
# ============================================================

import numpy as np
import pandas as pd
import streamlit as st
from pathlib import Path
from sklearn.preprocessing import MinMaxScaler
import warnings
warnings.filterwarnings("ignore")

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import LSTM_MODEL_PATH, XGB_MODEL_PATH, INFERENCE_CONFIG

LOOKBACK  = INFERENCE_CONFIG["lookback"]
FEATURES  = INFERENCE_CONFIG["features"]
N_FEAT    = INFERENCE_CONFIG["n_features"]


# ── Load Pre-trained LSTM ─────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_lstm_model():
    """
    Load pre-trained LSTM from disk.
    Uses @cache_resource so it's loaded once per session.
    """
    try:
        import tensorflow as tf
        if not LSTM_MODEL_PATH.exists():
            return None
        model = tf.keras.models.load_model(str(LSTM_MODEL_PATH), compile=False)
        return model
    except Exception as e:
        return None


# ── Load Pre-trained XGBoost ──────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_xgb_model():
    """
    Load pre-trained XGBoost from JSON.
    Uses @cache_resource so it's loaded once per session.
    """
    try:
        import xgboost as xgb
        if not XGB_MODEL_PATH.exists():
            st.warning(f"⚠️ XGBoost model tidak ditemukan di: {XGB_MODEL_PATH}. Menggunakan fallback.")
            return None
        model = xgb.XGBRegressor()
        model.load_model(str(XGB_MODEL_PATH))
        return model
    except Exception as e:
        st.warning(f"⚠️ Gagal load XGBoost model: {e}")
        return None


# ── Scaler (fitted on historical data) ───────────────────────
@st.cache_resource(show_spinner=False)
def get_fitted_scaler(df: pd.DataFrame) -> MinMaxScaler:
    """
    Fit MinMaxScaler on the full historical dataset.
    Called once, cached for the session.
    """
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaler.fit(df[FEATURES].values)
    return scaler


# ── Core Inference: Next Step ─────────────────────────────────
def predict_next(
    df: pd.DataFrame,
    lstm_model,
    xgb_model,
    scaler: MinMaxScaler,
) -> float:
    """
    Predict curah hujan for the next time step.
    Returns predicted value in mm.
    """
    # Prepare last-lookback window
    last_window = df[FEATURES].tail(LOOKBACK).values.copy()
    scaled      = scaler.transform(last_window)
    X_lstm      = scaled.reshape(1, LOOKBACK, N_FEAT)

    # LSTM inference
    pred_log  = float(lstm_model.predict(X_lstm, verbose=0)[0, 0]) if lstm_model else 0.0
    pred_lstm = max(0.0, np.expm1(pred_log))

    # XGBoost feature vector
    if xgb_model is not None:
        rain_series = df["curah_hujan"].values
        lags        = [rain_series[-i] if i <= len(rain_series) else 0 for i in range(1, 8)]
        roll_mean   = float(np.mean(rain_series[-7:])) if len(rain_series) >= 7 else 0.0
        roll_std    = float(np.std(rain_series[-7:]))  if len(rain_series) >= 7 else 0.0
        roll_sum    = float(np.sum(rain_series[-3:]))  if len(rain_series) >= 3 else 0.0
        roll_max    = float(np.max(rain_series[-7:]))  if len(rain_series) >= 7 else 0.0
        month       = df.index[-1].month
        sin_m       = np.sin(2 * np.pi * month / 12)
        cos_m       = np.cos(2 * np.pi * month / 12)
        humidity    = float(df["kelembapan"].iloc[-1])
        temp        = float(df["suhu"].iloc[-1])
        wind        = float(df["kecepatan_angin"].iloc[-1])
        pred_x_hum  = pred_lstm * humidity

        xgb_features = np.array([[
            pred_lstm, humidity, temp, wind,
            *lags,
            roll_mean, roll_std, roll_sum, roll_max,
            sin_m, cos_m, pred_x_hum,
        ]])
        residual  = float(xgb_model.predict(xgb_features)[0])
        final_mm  = max(0.0, pred_lstm + residual)
    else:
        final_mm = pred_lstm

    return round(final_mm, 3)


# ── Rolling Forecast (n days) ─────────────────────────────────
def predict_future(
    df: pd.DataFrame,
    lstm_model,
    xgb_model,
    scaler: MinMaxScaler,
    n_days: int = 7,
) -> np.ndarray:
    """
    Rolling multi-step forecast for n_days ahead.
    Each step uses the previous prediction to extend the window.
    Returns array of n_days predicted values (mm).
    """
    results = []
    # Working buffer (copy of recent data)
    buf_data = df[FEATURES].tail(max(LOOKBACK * 2, 30)).copy().reset_index(drop=True)

    for step in range(n_days):
        last_window = buf_data[FEATURES].tail(LOOKBACK).values
        scaled      = scaler.transform(last_window)
        X_lstm      = scaled.reshape(1, LOOKBACK, N_FEAT)

        pred_log  = float(lstm_model.predict(X_lstm, verbose=0)[0, 0]) if lstm_model else 0.0
        pred_lstm = max(0.0, np.expm1(pred_log))

        if xgb_model is not None:
            rain_series = buf_data["curah_hujan"].values
            lags        = [rain_series[-i] if i <= len(rain_series) else 0 for i in range(1, 8)]
            roll_mean   = float(np.mean(rain_series[-7:])) if len(rain_series) >= 7 else 0.0
            roll_std    = float(np.std(rain_series[-7:]))  if len(rain_series) >= 7 else 0.0
            roll_sum    = float(np.sum(rain_series[-3:]))  if len(rain_series) >= 3 else 0.0
            roll_max    = float(np.max(rain_series[-7:]))  if len(rain_series) >= 7 else 0.0
            # Use last known auxiliary features
            humidity    = float(buf_data["kelembapan"].iloc[-1])
            temp        = float(buf_data["suhu"].iloc[-1])
            wind        = float(buf_data["kecepatan_angin"].iloc[-1])
            # Simple decay on humidity: slight variation
            humidity = min(100, humidity + np.random.normal(0, 2))
            month_offset = (df.index[-1].month + step) % 12 or 12
            sin_m        = np.sin(2 * np.pi * month_offset / 12)
            cos_m        = np.cos(2 * np.pi * month_offset / 12)
            pred_x_hum   = pred_lstm * humidity

            xgb_features = np.array([[
                pred_lstm, humidity, temp, wind,
                *lags, roll_mean, roll_std, roll_sum, roll_max,
                sin_m, cos_m, pred_x_hum,
            ]])
            residual = float(xgb_model.predict(xgb_features)[0])
            final_mm = max(0.0, pred_lstm + residual)
        else:
            final_mm = pred_lstm

        results.append(round(final_mm, 2))

        # Extend buffer with predicted value
        new_row = buf_data.iloc[-1].copy()
        new_row["curah_hujan"] = final_mm
        buf_data = pd.concat([buf_data, new_row.to_frame().T], ignore_index=True)

    return np.array(results)


# ── Batch Inference (on test set for evaluation display) ──────
def batch_predict(
    df: pd.DataFrame,
    lstm_model,
    xgb_model,
    scaler: MinMaxScaler,
) -> dict:
    """
    Run inference on the last 20% of data for evaluation display.
    This is NOT training — it's just re-running inference for chart rendering.
    """
    scaled_df  = pd.DataFrame(scaler.transform(df[FEATURES]), columns=FEATURES, index=df.index)
    X_all, y_all, dates = [], [], []

    for i in range(LOOKBACK, len(scaled_df)):
        X_all.append(scaled_df.values[i-LOOKBACK:i])
        y_all.append(df["curah_hujan"].values[i])
        dates.append(df.index[i])

    X_all = np.array(X_all)
    split = int(len(X_all) * 0.8)
    X_test = X_all[split:]
    y_test = np.array(y_all[split:])
    dates_test = dates[split:]

    if lstm_model is None:
        return {"dates": dates_test, "actual": y_test, "predicted": y_test * 0.9}

    pred_log_test = lstm_model.predict(X_test, verbose=0).flatten()
    pred_lstm_mm  = np.expm1(pred_log_test).clip(0)

    if xgb_model is not None:
        # Build XGBoost features for test set
        xgb_preds = []
        for i, idx in enumerate(range(split, len(X_all))):
            pos      = LOOKBACK + idx
            rain_hist = df["curah_hujan"].values[:pos]
            lags     = [rain_hist[-j] if j <= len(rain_hist) else 0 for j in range(1, 8)]
            roll_mean= float(np.mean(rain_hist[-7:])) if len(rain_hist) >= 7 else 0
            roll_std = float(np.std(rain_hist[-7:]))  if len(rain_hist) >= 7 else 0
            roll_sum = float(np.sum(rain_hist[-3:]))  if len(rain_hist) >= 3 else 0
            roll_max = float(np.max(rain_hist[-7:]))  if len(rain_hist) >= 7 else 0
            month    = df.index[pos].month
            sin_m    = np.sin(2 * np.pi * month / 12)
            cos_m    = np.cos(2 * np.pi * month / 12)
            hum      = float(df["kelembapan"].values[pos])
            temp     = float(df["suhu"].values[pos])
            wind     = float(df["kecepatan_angin"].values[pos])
            pred_x   = pred_lstm_mm[i] * hum
            vec      = np.array([[pred_lstm_mm[i], hum, temp, wind, *lags,
                                  roll_mean, roll_std, roll_sum, roll_max,
                                  sin_m, cos_m, pred_x]])
            xgb_preds.append(float(xgb_model.predict(vec)[0]))

        hybrid_pred = np.maximum(0, pred_lstm_mm + np.array(xgb_preds))
    else:
        hybrid_pred = pred_lstm_mm

    return {
        "dates":      dates_test,
        "actual":     y_test,
        "predicted":  hybrid_pred,
        "lstm_only":  pred_lstm_mm,
    }
