# ============================================================
# data/agriculture_data.py — Data Pertanian Aceh Besar
# Hanya: kecamatan, luas_sawah, produksi_padi, produktivitas
# Sumber: BPS Kabupaten Aceh Besar 2022
# ============================================================

import pandas as pd

AGRICULTURE_DATA = [
    {"kecamatan": "Lhoong",           "luas_sawah": 1465,    "produksi_padi": 8083,      "produktivitas": 5.90,  "lat": 5.25, "lon": 95.25},
    {"kecamatan": "Lhoknga",          "luas_sawah": 1251,    "produksi_padi": 5916,      "produktivitas": 6.00,  "lat": 5.45, "lon": 95.22},
    {"kecamatan": "Leupung",          "luas_sawah": 192,     "produksi_padi": 1210,      "produktivitas": 5.50,  "lat": 5.27, "lon": 95.27},
    {"kecamatan": "Indrapuri",        "luas_sawah": 5850,    "produksi_padi": 43258.32,  "produktivitas": 7.56,  "lat": 5.37, "lon": 95.52},
    {"kecamatan": "Kuta Cot Glie",    "luas_sawah": 3342.23, "produksi_padi": 28451.55,  "produktivitas": 6.70,  "lat": 5.42, "lon": 95.61},
    {"kecamatan": "Seulimeum",        "luas_sawah": 4096,    "produksi_padi": 33111,     "produktivitas": 6.50,  "lat": 5.47, "lon": 95.71},
    {"kecamatan": "Kota Jantho",      "luas_sawah": 1797,    "produksi_padi": 25212,     "produktivitas": 6.00,  "lat": 5.35, "lon": 95.68},
    {"kecamatan": "Lembah Seulawah",  "luas_sawah": 1084,    "produksi_padi": 8750.95,   "produktivitas": 6.50,  "lat": 5.38, "lon": 95.62},
    {"kecamatan": "Mesjid Raya",      "luas_sawah": 30,      "produksi_padi": 91,        "produktivitas": 6.50,  "lat": 5.32, "lon": 95.40},
    {"kecamatan": "Darussalam",       "luas_sawah": 1102,    "produksi_padi": 6719.25,   "produktivitas": 6.20,  "lat": 5.52, "lon": 95.38},
    {"kecamatan": "Baitussalam",      "luas_sawah": 57,      "produksi_padi": 16.445,    "produktivitas": 0.30,  "lat": 5.58, "lon": 95.37},
    {"kecamatan": "Kuta Baro",        "luas_sawah": 3218.65, "produksi_padi": 12747.213, "produktivitas": 4.82,  "lat": 5.44, "lon": 95.48},
    {"kecamatan": "Montasik",         "luas_sawah": 4607,    "produksi_padi": 29124.9,   "produktivitas": 6.90,  "lat": 5.47, "lon": 95.41},
    {"kecamatan": "Blang Bintang",    "luas_sawah": 1480,    "produksi_padi": 15714.3,   "produktivitas": 7.35,  "lat": 5.52, "lon": 95.43},
    {"kecamatan": "Ingin Jaya",       "luas_sawah": 2386,    "produksi_padi": 10875.2,   "produktivitas": 5.60,  "lat": 5.50, "lon": 95.46},
    {"kecamatan": "Krueng Barona Jaya","luas_sawah": 182,    "produksi_padi": 833,       "produktivitas": 4.90,  "lat": 5.56, "lon": 95.36},
    {"kecamatan": "Sukamakmur",       "luas_sawah": 1963.5,  "produksi_padi": 17253.75,  "produktivitas": 7.50,  "lat": 5.53, "lon": 95.43},
    {"kecamatan": "Kuta Malaka",      "luas_sawah": 1227,    "produksi_padi": 9430.2,    "produktivitas": 6.76,  "lat": 5.46, "lon": 95.55},
    {"kecamatan": "Simpang Tiga",     "luas_sawah": 988,     "produksi_padi": 116.352,   "produktivitas": 0.12,  "lat": 5.48, "lon": 95.42},
    {"kecamatan": "Darul Imarah",     "luas_sawah": 1148,    "produksi_padi": 5970,      "produktivitas": 6.00,  "lat": 5.48, "lon": 95.35},
    {"kecamatan": "Darul Kamal",      "luas_sawah": 58,      "produksi_padi": 2223,      "produktivitas": 6.50,  "lat": 5.50, "lon": 95.33},
    {"kecamatan": "Peukan Bada",      "luas_sawah": 526,     "produksi_padi": 4267.5,    "produktivitas": 7.50,  "lat": 5.56, "lon": 95.29},
    {"kecamatan": "Pulo Aceh",        "luas_sawah": 323,     "produksi_padi": 2732.58,   "produktivitas": 8.46,  "lat": 5.63, "lon": 94.97},
]

# Produksi bulanan (pola musiman, tanpa perubahan)
MONTHLY_PRODUCTION = {
    "Bulan":           ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agu","Sep","Okt","Nov","Des"],
    "Produksi_Ton":    [8240, 9120, 11480, 13640, 14820, 11240, 9840, 8620, 10240, 13480, 15820, 12640],
    "Luas_Panen_Ha":   [1640, 1820, 2280,  2740,  2960,  2240,  1960, 1720, 2040,  2680,  3160,  2520],
    "Curah_Hujan_Avg": [220,  185,  156,   132,   98,    82,    94,   78,   112,   168,   248,   284],
}


def get_agriculture_df() -> pd.DataFrame:
    """Kembalikan DataFrame pertanian sederhana."""
    df = pd.DataFrame(AGRICULTURE_DATA)
    df = df.sort_values("luas_sawah", ascending=False).reset_index(drop=True)
    return df


def get_monthly_df() -> pd.DataFrame:
    return pd.DataFrame(MONTHLY_PRODUCTION)
