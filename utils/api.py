# ============================================================
# utils/api.py — OpenWeatherMap API Handler
# Fix: hapus st.toast (tidak tersedia di Streamlit < 1.28)
# ============================================================

import requests
import pandas as pd
import streamlit as st
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import OWM_API_KEY, OWM_BASE_URL, LOCATION, DATA_PATH


def get_current_weather() -> dict | None:
    """
    Ambil data cuaca saat ini dari OpenWeatherMap.
    Mengembalikan dict raw untuk diproses akumulasi harian.
    """
    try:
        r = requests.get(OWM_BASE_URL, params={
            "lat":   LOCATION["lat"],
            "lon":   LOCATION["lon"],
            "appid": OWM_API_KEY,
            "units": "metric",
        }, timeout=10)
        r.raise_for_status()
        d = r.json()
        return {
            "timestamp":       datetime.now(),
            "curah_hujan":     d.get("rain", {}).get("1h", 0.0),
            "suhu":            d.get("main", {}).get("temp", 0.0),
            "kelembapan":      d.get("main", {}).get("humidity", 0.0),
            "kecepatan_angin": d.get("wind", {}).get("speed", 0.0),
        }
    except requests.exceptions.ConnectionError:
        return None
    except requests.exceptions.Timeout:
        return None
    except Exception:
        return None


def update_daily_excel(raw: dict) -> pd.DataFrame | None:
    """
    Baca Excel, akumulasi data harian, simpan kembali.
    - curah_hujan    : SUM  (akumulasi sepanjang hari)
    - suhu           : rata-rata (running average)
    - kelembapan     : rata-rata (running average)
    - kecepatan_angin: maksimum harian
    """
    if raw is None:
        return None

    if not DATA_PATH.exists():
        return None

    try:
        df = pd.read_excel(DATA_PATH)
        df.columns = df.columns.str.lower().str.strip()

        # Hapus kolom bantu jika ada
        df = df[[c for c in df.columns if not c.startswith("_")]]

        df["tanggal"] = pd.to_datetime(df["tanggal"], dayfirst=True, errors="coerce")
        df = df.dropna(subset=["tanggal"]).sort_values("tanggal").reset_index(drop=True)

        today     = pd.Timestamp(raw["timestamp"]).normalize()
        today_str = today.date()
        existing  = df["tanggal"].dt.date == today_str

        if existing.any():
            idx = df[existing].index[-1]

            # Hitung jumlah update sebelumnya dari kolom _n (tidak disimpan ke Excel)
            n = int(df.at[idx, "_n"]) if "_n" in df.columns else 1

            # Akumulasi curah hujan
            df.at[idx, "curah_hujan"] = round(
                float(df.at[idx, "curah_hujan"]) + float(raw["curah_hujan"]), 2
            )
            # Running average suhu
            df.at[idx, "suhu"] = round(
                (float(df.at[idx, "suhu"]) * n + float(raw["suhu"])) / (n + 1), 1
            )
            # Running average kelembapan
            df.at[idx, "kelembapan"] = round(
                (float(df.at[idx, "kelembapan"]) * n + float(raw["kelembapan"])) / (n + 1), 1
            )
            # Maksimum kecepatan angin
            df.at[idx, "kecepatan_angin"] = round(
                max(float(df.at[idx, "kecepatan_angin"]), float(raw["kecepatan_angin"])), 1
            )

        else:
            new_row = {
                "tanggal":         today,
                "curah_hujan":     round(float(raw["curah_hujan"]), 2),
                "suhu":            round(float(raw["suhu"]), 1),
                "kelembapan":      round(float(raw["kelembapan"]), 1),
                "kecepatan_angin": round(float(raw["kecepatan_angin"]), 1),
            }
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)

        # Simpan — hanya 5 kolom standar
        cols = [c for c in ["tanggal","curah_hujan","kecepatan_angin","kelembapan","suhu"]
                if c in df.columns]
        df_save = df[cols].sort_values("tanggal")
        df_save.to_excel(DATA_PATH, index=False)

        return df_save.set_index("tanggal")

    except PermissionError:
        # File Excel sedang terbuka — lewati update
        return None
    except Exception:
        return None


def try_update_api_data() -> pd.DataFrame | None:
    """
    Wrapper utama dipanggil dari app.py.
    Ambil data → akumulasi → simpan → kembalikan df atau None.
    Semua notifikasi menggunakan session_state agar tidak crash
    di versi Streamlit lama.
    """
    raw        = get_current_weather()
    updated_df = update_daily_excel(raw)

    if updated_df is not None:
        # Simpan flag ke session_state, ditampilkan di app.py
        st.session_state["api_update_success"] = True
    else:
        st.session_state["api_update_success"] = False

    return updated_df
