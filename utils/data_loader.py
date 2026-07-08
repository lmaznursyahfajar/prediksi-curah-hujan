# ============================================================
# utils/data_loader.py — Data Loading & Session State
# ============================================================

import pandas as pd
import numpy as np
import geopandas as gpd
import streamlit as st
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import DATA_PATH, GEOJSON_PATH


@st.cache_data(ttl=600, show_spinner=False)
def load_data() -> pd.DataFrame:
    """Load dan bersihkan dataset historis dari Excel."""
    if not DATA_PATH.exists():
        st.error(f"❌ File tidak ditemukan: `{DATA_PATH.name}`. "
                 f"Letakkan `data_cuaca_aceh_besar.xlsx` di folder root project.")
        st.stop()

    df = pd.read_excel(DATA_PATH)
    df.columns = df.columns.str.lower().str.strip()

    # Hapus kolom bantu jika ada
    df = df[[c for c in df.columns if not c.startswith("_")]]

    required = {"tanggal", "curah_hujan", "kecepatan_angin", "kelembapan", "suhu"}
    missing  = required - set(df.columns)
    if missing:
        st.error(f"❌ Kolom tidak ditemukan: {missing}")
        st.stop()

    df = df[list(required)].copy()
    df["tanggal"] = pd.to_datetime(df["tanggal"], dayfirst=True, errors="coerce")
    df = df.dropna(subset=["tanggal"])

    for col in ["curah_hujan", "kecepatan_angin", "kelembapan", "suhu"]:
        df[col] = pd.to_numeric(
            df[col].astype(str).str.replace(",", ".", regex=False).str.strip(),
            errors="coerce"
        )

    df = df.dropna()
    df = df.sort_values("tanggal").drop_duplicates("tanggal")
    df["curah_hujan"] = df["curah_hujan"].clip(lower=0)
    df = df.set_index("tanggal")
    return df


def reload_data() -> pd.DataFrame:
    """
    Muat ulang data dari Excel tanpa cache.
    Dipanggil setelah update API agar data terbaru langsung terbaca.
    """
    load_data.clear()
    return load_data()


@st.cache_data(ttl=86400, show_spinner=False)
def load_geojson() -> gpd.GeoDataFrame:
    if not GEOJSON_PATH.exists():
        return None
    try:
        return gpd.read_file(GEOJSON_PATH)
    except Exception:
        return None


def compute_stats(df: pd.DataFrame) -> dict:
    now  = pd.Timestamp.now()
    w_df = df[df.index >= now - pd.Timedelta(days=7)]
    m_df = df[df.index >= now - pd.Timedelta(days=30)]
    latest = df.iloc[-1]
    prev   = df.iloc[-2] if len(df) >= 2 else df.iloc[-1]
    return {
        "latest_rain":     float(latest["curah_hujan"]),
        "latest_temp":     float(latest["suhu"]),
        "latest_humidity": float(latest["kelembapan"]),
        "latest_wind":     float(latest["kecepatan_angin"]),
        "prev_rain":       float(prev["curah_hujan"]),
        "week_sum":        float(w_df["curah_hujan"].sum()),
        "week_max":        float(w_df["curah_hujan"].max()) if len(w_df) > 0 else 0,
        "week_mean":       float(w_df["curah_hujan"].mean()) if len(w_df) > 0 else 0,
        "month_sum":       float(m_df["curah_hujan"].sum()),
        "month_max":       float(m_df["curah_hujan"].max()) if len(m_df) > 0 else 0,
        "extreme_days":    int((df["curah_hujan"] >= 50).sum()),
        "total_records":   len(df),
        "date_start":      str(df.index.min().date()),
        "date_end":        str(df.index.max().date()),
    }
