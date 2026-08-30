# ============================================================
# config.py — AI Climate & Agricultural Intelligence Platform
# Aceh Besar · Hybrid LSTM-XGBoost · v3.0
# ============================================================

from pathlib import Path

# ── Paths ────────────────────────────────────────────────────
ROOT_DIR     = Path(__file__).parent
DATA_PATH    = ROOT_DIR / "data_cuaca_aceh_besar.xlsx"
GEOJSON_PATH = ROOT_DIR / "Aceh_Besar_Kecamatan.geojson"
STYLES_PATH  = ROOT_DIR / "styles" / "main.css"
EXPORTS_DIR  = ROOT_DIR / "exports"
EXPORTS_DIR.mkdir(exist_ok=True)

# ── Pre-trained Model Paths ──────────────────────────────────
# IMPORTANT: Models are pre-trained. Never retrain on app load.
LSTM_MODEL_PATH      = ROOT_DIR / "lstm_model_final.h5"
XGB_MODEL_PATH       = ROOT_DIR / "xgb_model_final.json"
SCALER_PATH          = ROOT_DIR / "scaler.pkl"
MODEL_ARTIFACTS_PATH = ROOT_DIR / "model_artifacts.json"

# ── OpenWeatherMap API ───────────────────────────────────────
OWM_API_KEY      = "d3db6282242ecdb51ec86cdeb1ff7b39"
OWM_BASE_URL     = "https://api.openweathermap.org/data/2.5/weather"
OWM_FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

# ── Location: Aceh Besar ─────────────────────────────────────
LOCATION = {
    "name":       "Aceh Besar",
    "province":   "Aceh",
    "lat":        5.404438378495802,
    "lon":        95.46433643789337,
    "map_center": [5.45, 95.32],
    "zoom":       9,
}

# ── Model Inference Config ───────────────────────────────────
INFERENCE_CONFIG = {
    "lookback":  7,
    "features":  ["curah_hujan", "kecepatan_angin", "kelembapan", "suhu"],
    "n_features": 4,
}

# ── Rainfall Thresholds ──────────────────────────────────────
# SUMBER TUNGGAL KLASIFIKASI CURAH HUJAN — dipakai di SELURUH platform
# (monitoring, prediksi, pertanian, bencana, rekomendasi mitigasi).
# Selaras dengan Tabel 5.20 & sub-bab 2.1.13/5.14.1 laporan skripsi:
# adaptasi kategori operasional BMKG + status kedaruratan BNPB.
# "code" = kunci status (dipakai services/recommendation.py & logika internal)
# "label" = teks tampilan (dipakai UI/kartu/badge)
RAIN_LEVELS = [
    {"code":"NORMAL",  "label":"Normal",  "min":0,   "max":10,   "color":"#22c55e","icon":"☀️","risk":"Rendah", "css":"low"},
    {"code":"WASPADA", "label":"Waspada", "min":10,  "max":30,   "color":"#eab308","icon":"🌦️","risk":"Sedang", "css":"medium"},
    {"code":"SIAGA",   "label":"Siaga",   "min":30,  "max":50,   "color":"#f97316","icon":"⛈️","risk":"Tinggi", "css":"high"},
    {"code":"BAHAYA",  "label":"Bahaya",  "min":50,  "max":100,  "color":"#ef4444","icon":"🌊","risk":"Kritis", "css":"critical"},
    {"code":"BENCANA", "label":"Bencana", "min":100, "max":9999, "color":"#7f1d1d","icon":"🆘","risk":"Bencana","css":"critical"},
]

# ── Agriculture Thresholds ───────────────────────────────────
AGRI_RISK = {
    "rendah":   {"color":"#22c55e","label":"Rendah",  "icon":"✅"},
    "sedang":   {"color":"#eab308","label":"Sedang",  "icon":"⚠️"},
    "tinggi":   {"color":"#f97316","label":"Tinggi",  "icon":"🔶"},
    "kritis":   {"color":"#ef4444","label":"Kritis",  "icon":"🚨"},
}

# ── Disaster Thresholds ──────────────────────────────────────
DISASTER_TYPES = ["Banjir","Longsor","Kekeringan","Gagal Panen"]

# ── Kecamatan Prioritas ──────────────────────────────────────
PRIORITY_KECAMATAN = [
    "Seulimeum","Lembah Seulawah","Indrapuri","Kuta Cot Glie",
    "Kota Jantho","Leupung","Lhoknga","Sukamakmur","Montasik",
]

# ── App Branding ─────────────────────────────────────────────
APP_NAME      = "Prediksi Curah Hujan Aceh Besar"
APP_TAGLINE   = "Platform Prediksi Curah Hujan"
APP_VERSION   = "1.0.0"
AUTHOR        = "L.M. Aznur Syahfajar"
INSTITUTION   = "Universitas Logistik dan Bisnis Internasional"

# ── Chart Theme ──────────────────────────────────────────────
PLOTLY_TEMPLATE = "plotly_dark"
CHART_BG        = "rgba(0,0,0,0)"
CHART_PAPER_BG  = "rgba(0,0,0,0)"
ACCENT_BLUE     = "#3b82f6"
ACCENT_CYAN     = "#06b6d4"
ACCENT_EMERALD  = "#10b981"
ACCENT_AMBER    = "#f59e0b"
ACCENT_ROSE     = "#f43f5e"
ACCENT_VIOLET   = "#8b5cf6"
