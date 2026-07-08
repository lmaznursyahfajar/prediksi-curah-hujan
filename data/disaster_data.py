# ============================================================
# data/disaster_data.py — Data Bencana Aceh Besar
# Kolom: kejadian banjir/longsor/genangan + lingkungan terpapar (ha)
# Sumber: BPBD & Peta Rawan Bencana Kabupaten Aceh Besar
# ============================================================

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta

# ── Data Kejadian + Lingkungan Terpapar ───────────────────────
# lingkungan_banjir_ha  → luas lingkungan terpapar banjir (Ha)
# lingkungan_longsor_ha → luas lingkungan terpapar tanah longsor (Ha)
# Sumber: Peta Rawan Bencana Kab. Aceh Besar (BPBD)
DISASTER_DATA = [
    # --- Kecamatan dengan data kejadian + lingkungan terpapar ---
    {
        "kecamatan": "Lhoong",
        "total_kejadian": 15, "kejadian_banjir": 12, "kejadian_longsor": 3, 
        "lingkungan_banjir_ha": 1312, "lingkungan_longsor_ha": 8262,
        "lat": 5.14, "lon": 95.37,
    },
    {
        "kecamatan": "Lhoknga",
        "total_kejadian": 26, "kejadian_banjir": 24, "kejadian_longsor": 2,
        "lingkungan_banjir_ha": 1510, "lingkungan_longsor_ha": 3963,
        "lat": 5.45, "lon": 95.22,
    },
    {
        "kecamatan": "Leupung",
        "total_kejadian": 22, "kejadian_banjir": 19, "kejadian_longsor": 3, 
        "lingkungan_banjir_ha": 686, "lingkungan_longsor_ha": 12945,
        "lat": 5.27, "lon": 95.27,
    },
    {
        "kecamatan": "Indrapuri",
        "total_kejadian": 26, "kejadian_banjir": 20, "kejadian_longsor": 6, 
        "lingkungan_banjir_ha": 3169, "lingkungan_longsor_ha": 2815,
        "lat": 5.37, "lon": 95.52,
    },
    {
        "kecamatan": "Kuta Cot Glie",
        "total_kejadian": 18, "kejadian_banjir": 10, "kejadian_longsor": 8,
        "lingkungan_banjir_ha": 2182, "lingkungan_longsor_ha": 12910,
        "lat": 5.42, "lon": 95.61,
    },
    {
        "kecamatan": "Seulimeum",
        "total_kejadian": 24, "kejadian_banjir": 18, "kejadian_longsor": 6, 
        "lingkungan_banjir_ha": 2737, "lingkungan_longsor_ha": 4603,
        "lat": 5.47, "lon": 95.71,
    },
    {
        "kecamatan": "Kota Jantho",
        "total_kejadian": 19, "kejadian_banjir": 9, "kejadian_longsor": 10, 
        "lingkungan_banjir_ha": 1117, "lingkungan_longsor_ha": 40655,
        "lat": 5.35, "lon": 95.68,
    },
    {
        "kecamatan": "Lembah Seulawah",
        "total_kejadian": 20, "kejadian_banjir": 8, "kejadian_longsor": 12, 
        "lingkungan_banjir_ha": 1461, "lingkungan_longsor_ha": 10558,
        "lat": 5.38, "lon": 95.62,
    },
    {
        "kecamatan": "Mesjid Raya",
        "total_kejadian": 16, "kejadian_banjir": 15, "kejadian_longsor": 1, 
        "lingkungan_banjir_ha": 1042, "lingkungan_longsor_ha": 345,
        "lat": 5.32, "lon": 95.40,
    },
    {
        "kecamatan": "Darussalam",
        "total_kejadian": 7, "kejadian_banjir": 6, "kejadian_longsor": 1, 
        "lingkungan_banjir_ha": 1592, "lingkungan_longsor_ha": 0,
        "lat": 5.52, "lon": 95.38,
    },
    {
        "kecamatan": "Baitussalam",
        "total_kejadian": 6, "kejadian_banjir": 6, "kejadian_longsor": 0, 
        "lingkungan_banjir_ha": 1351, "lingkungan_longsor_ha": 16,
        "lat": 5.52, "lon": 95.34,
    },
    {
        "kecamatan": "Kuta Baro",
        "total_kejadian": 12, "kejadian_banjir": 10, "kejadian_longsor": 2, 
        "lingkungan_banjir_ha": 2169, "lingkungan_longsor_ha": 0,
        "lat": 5.44, "lon": 95.48,
    },
    {
        "kecamatan": "Montasik",
        "total_kejadian": 10, "kejadian_banjir": 9, "kejadian_longsor": 1, 
        "lingkungan_banjir_ha": 0, "lingkungan_longsor_ha": 0,
        "lat": 5.47, "lon": 95.41,
    },
    {
        "kecamatan": "Ingin Jaya",
        "total_kejadian": 7, "kejadian_banjir": 7, "kejadian_longsor": 0, 
        "lingkungan_banjir_ha": 2102, "lingkungan_longsor_ha": 0,
        "lat": 5.50, "lon": 95.46,
    },
    {
        "kecamatan": "Krueng Barona Jaya",
        "total_kejadian": 5, "kejadian_banjir": 5, "kejadian_longsor": 0, 
        "lingkungan_banjir_ha": 546, "lingkungan_longsor_ha": 0,
        "lat": 5.49, "lon": 95.32,
    },
    {
        "kecamatan": "Sukamakmur",
        "total_kejadian": 19, "kejadian_banjir": 16, "kejadian_longsor": 3, 
        "lingkungan_banjir_ha": 1470, "lingkungan_longsor_ha": 547,
        "lat": 5.53, "lon": 95.43,
    },
    {
        "kecamatan": "Kuta Malaka",
        "total_kejadian": 7, "kejadian_banjir": 6, "kejadian_longsor": 1, 
        "lingkungan_banjir_ha": 831, "lingkungan_longsor_ha": 55,
        "lat": 5.46, "lon": 95.55,
    },
    {
        "kecamatan": "Simpang Tiga",
        "total_kejadian": 6, "kejadian_banjir": 5, "kejadian_longsor": 1, 
        "lingkungan_banjir_ha": 726, "lingkungan_longsor_ha": 668,
        "lat": 5.48, "lon": 95.42,
    },
    {
        "kecamatan": "Darul Imarah",
        "total_kejadian": 8, "kejadian_banjir": 7, "kejadian_longsor": 1, 
        "lingkungan_banjir_ha": 2036, "lingkungan_longsor_ha": 7,
        "lat": 5.48, "lon": 95.35,
    },
    {
        "kecamatan": "Darul Kamal",
        "total_kejadian": 5, "kejadian_banjir": 4, "kejadian_longsor": 1, 
        "lingkungan_banjir_ha": 802, "lingkungan_longsor_ha": 626,
        "lat": 5.49, "lon": 95.44,
    },
    {
        "kecamatan": "Peukan Bada",
        "total_kejadian": 8, "kejadian_banjir": 7, "kejadian_longsor": 1, 
        "lingkungan_banjir_ha": 1012, "lingkungan_longsor_ha": 689,
        "lat": 5.44, "lon": 95.29,
    },
    {
        "kecamatan": "Pulo Aceh",
        "total_kejadian": 4, "kejadian_banjir": 3, "kejadian_longsor": 1, 
        "lingkungan_banjir_ha": 209, "lingkungan_longsor_ha": 1822,
        "lat": 5.60, "lon": 95.10,
    },
    {
        "kecamatan": "Blang Bintang",
        "total_kejadian": 9, "kejadian_banjir": 8, "kejadian_longsor": 1, 
        "lingkungan_banjir_ha": 1471, "lingkungan_longsor_ha": 0,
        "lat": 5.52, "lon": 95.43,
    },
]

# ── Tren Tahunan ──────────────────────────────────────────────
YEARLY_DISASTERS = [
    # =====================================================
    # 2018
    # =====================================================
    {"tahun":2018,"kecamatan":"Lhoong","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Lhoknga","banjir":2,"longsor":0},
    {"tahun":2018,"kecamatan":"Leupung","banjir":2,"longsor":0},
    {"tahun":2018,"kecamatan":"Indrapuri","banjir":2,"longsor":1},
    {"tahun":2018,"kecamatan":"Kuta Cot Glie","banjir":1,"longsor":1},
    {"tahun":2018,"kecamatan":"Seulimeum","banjir":2,"longsor":1},
    {"tahun":2018,"kecamatan":"Kota Jantho","banjir":1,"longsor":2},
    {"tahun":2018,"kecamatan":"Lembah Seulawah","banjir":1,"longsor":2},
    {"tahun":2018,"kecamatan":"Mesjid Raya","banjir":2,"longsor":0},
    {"tahun":2018,"kecamatan":"Darussalam","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Baitussalam","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Kuta Baro","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Montasik","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Blang Bintang","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Ingin Jaya","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Krueng Barona Jaya","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Suka Makmur","banjir":2,"longsor":0},
    {"tahun":2018,"kecamatan":"Kuta Malaka","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Simpang Tiga","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Darul Imarah","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Darul Kamal","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Peukan Bada","banjir":1,"longsor":0},
    {"tahun":2018,"kecamatan":"Pulo Aceh","banjir":0,"longsor":0},

    # =====================================================
    # 2019
    # =====================================================
    {"tahun":2019,"kecamatan":"Lhoong","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Lhoknga","banjir":2,"longsor":0},
    {"tahun":2019,"kecamatan":"Leupung","banjir":2,"longsor":0},
    {"tahun":2019,"kecamatan":"Indrapuri","banjir":2,"longsor":0},
    {"tahun":2019,"kecamatan":"Kuta Cot Glie","banjir":1,"longsor":1},
    {"tahun":2019,"kecamatan":"Seulimeum","banjir":2,"longsor":1},
    {"tahun":2019,"kecamatan":"Kota Jantho","banjir":1,"longsor":1},
    {"tahun":2019,"kecamatan":"Lembah Seulawah","banjir":1,"longsor":1},
    {"tahun":2019,"kecamatan":"Mesjid Raya","banjir":2,"longsor":0},
    {"tahun":2019,"kecamatan":"Darussalam","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Baitussalam","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Kuta Baro","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Montasik","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Blang Bintang","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Ingin Jaya","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Krueng Barona Jaya","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Suka Makmur","banjir":2,"longsor":0},
    {"tahun":2019,"kecamatan":"Kuta Malaka","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Simpang Tiga","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Darul Imarah","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Darul Kamal","banjir":0,"longsor":1},
    {"tahun":2019,"kecamatan":"Peukan Bada","banjir":1,"longsor":0},
    {"tahun":2019,"kecamatan":"Pulo Aceh","banjir":1,"longsor":0},
        
    # =====================================================
    # 2020
    # =====================================================
    {"tahun":2020,"kecamatan":"Lhoong","banjir":2,"longsor":0},
    {"tahun":2020,"kecamatan":"Lhoknga","banjir":3,"longsor":0},
    {"tahun":2020,"kecamatan":"Leupung","banjir":3,"longsor":0},
    {"tahun":2020,"kecamatan":"Indrapuri","banjir":3,"longsor":1},
    {"tahun":2020,"kecamatan":"Kuta Cot Glie","banjir":2,"longsor":1},
    {"tahun":2020,"kecamatan":"Seulimeum","banjir":3,"longsor":1},
    {"tahun":2020,"kecamatan":"Kota Jantho","banjir":2,"longsor":2},
    {"tahun":2020,"kecamatan":"Lembah Seulawah","banjir":1,"longsor":2},
    {"tahun":2020,"kecamatan":"Mesjid Raya","banjir":3,"longsor":0},
    {"tahun":2020,"kecamatan":"Darussalam","banjir":1,"longsor":0},
    {"tahun":2020,"kecamatan":"Baitussalam","banjir":1,"longsor":0},
    {"tahun":2020,"kecamatan":"Kuta Baro","banjir":2,"longsor":1},
    {"tahun":2020,"kecamatan":"Montasik","banjir":2,"longsor":0},
    {"tahun":2020,"kecamatan":"Blang Bintang","banjir":2,"longsor":0},
    {"tahun":2020,"kecamatan":"Ingin Jaya","banjir":1,"longsor":0},
    {"tahun":2020,"kecamatan":"Krueng Barona Jaya","banjir":1,"longsor":0},
    {"tahun":2020,"kecamatan":"Suka Makmur","banjir":3,"longsor":1},
    {"tahun":2020,"kecamatan":"Kuta Malaka","banjir":1,"longsor":0},
    {"tahun":2020,"kecamatan":"Simpang Tiga","banjir":1,"longsor":0},
    {"tahun":2020,"kecamatan":"Darul Imarah","banjir":1,"longsor":0},
    {"tahun":2020,"kecamatan":"Darul Kamal","banjir":1,"longsor":0},
    {"tahun":2020,"kecamatan":"Peukan Bada","banjir":1,"longsor":0},
    {"tahun":2020,"kecamatan":"Pulo Aceh","banjir":0,"longsor":1},

    # =====================================================
    # 2021
    # =====================================================
    {"tahun":2021,"kecamatan":"Lhoong","banjir":3,"longsor":1},
    {"tahun":2021,"kecamatan":"Lhoknga","banjir":5,"longsor":1},
    {"tahun":2021,"kecamatan":"Leupung","banjir":4,"longsor":1},
    {"tahun":2021,"kecamatan":"Indrapuri","banjir":5,"longsor":2},
    {"tahun":2021,"kecamatan":"Kuta Cot Glie","banjir":2,"longsor":2},
    {"tahun":2021,"kecamatan":"Seulimeum","banjir":4,"longsor":2},
    {"tahun":2021,"kecamatan":"Kota Jantho","banjir":2,"longsor":2},
    {"tahun":2021,"kecamatan":"Lembah Seulawah","banjir":2,"longsor":3},
    {"tahun":2021,"kecamatan":"Mesjid Raya","banjir":3,"longsor":1},
    {"tahun":2021,"kecamatan":"Darussalam","banjir":1,"longsor":0},
    {"tahun":2021,"kecamatan":"Baitussalam","banjir":1,"longsor":0},
    {"tahun":2021,"kecamatan":"Kuta Baro","banjir":2,"longsor":0},
    {"tahun":2021,"kecamatan":"Montasik","banjir":2,"longsor":0},
    {"tahun":2021,"kecamatan":"Blang Bintang","banjir":2,"longsor":0},
    {"tahun":2021,"kecamatan":"Ingin Jaya","banjir":1,"longsor":0},
    {"tahun":2021,"kecamatan":"Krueng Barona Jaya","banjir":1,"longsor":0},
    {"tahun":2021,"kecamatan":"Suka Makmur","banjir":3,"longsor":1},
    {"tahun":2021,"kecamatan":"Kuta Malaka","banjir":1,"longsor":1},
    {"tahun":2021,"kecamatan":"Simpang Tiga","banjir":1,"longsor":1},
    {"tahun":2021,"kecamatan":"Darul Imarah","banjir":2,"longsor":0},
    {"tahun":2021,"kecamatan":"Darul Kamal","banjir":1,"longsor":0},
    {"tahun":2021,"kecamatan":"Peukan Bada","banjir":2,"longsor":0},
    {"tahun":2021,"kecamatan":"Pulo Aceh","banjir":1,"longsor":0}, # Diperbaiki (-1 longsor)

    # =====================================================
    # 2022
    # =====================================================
    {"tahun":2022,"kecamatan":"Lhoong","banjir":2,"longsor":0},
    {"tahun":2022,"kecamatan":"Lhoknga","banjir":4,"longsor":0},
    {"tahun":2022,"kecamatan":"Leupung","banjir":3,"longsor":0},
    {"tahun":2022,"kecamatan":"Indrapuri","banjir":3,"longsor":1},
    {"tahun":2022,"kecamatan":"Kuta Cot Glie","banjir":1,"longsor":1},
    {"tahun":2022,"kecamatan":"Seulimeum","banjir":2,"longsor":1},
    {"tahun":2022,"kecamatan":"Kota Jantho","banjir":1,"longsor":1},
    {"tahun":2022,"kecamatan":"Lembah Seulawah","banjir":1,"longsor":1},
    {"tahun":2022,"kecamatan":"Mesjid Raya","banjir":2,"longsor":0},
    {"tahun":2022,"kecamatan":"Darussalam","banjir":0,"longsor":0},
    {"tahun":2022,"kecamatan":"Baitussalam","banjir":1,"longsor":0},
    {"tahun":2022,"kecamatan":"Kuta Baro","banjir":1,"longsor":0},
    {"tahun":2022,"kecamatan":"Montasik","banjir":1,"longsor":0},
    {"tahun":2022,"kecamatan":"Blang Bintang","banjir":1,"longsor":0},
    {"tahun":2022,"kecamatan":"Ingin Jaya","banjir":1,"longsor":0},
    {"tahun":2022,"kecamatan":"Krueng Barona Jaya","banjir":0,"longsor":0},
    {"tahun":2022,"kecamatan":"Suka Makmur","banjir":2,"longsor":0},
    {"tahun":2022,"kecamatan":"Kuta Malaka","banjir":1,"longsor":0},
    {"tahun":2022,"kecamatan":"Simpang Tiga","banjir":0,"longsor":0},
    {"tahun":2022,"kecamatan":"Darul Imarah","banjir":1,"longsor":0},
    {"tahun":2022,"kecamatan":"Darul Kamal","banjir":0,"longsor":0},
    {"tahun":2022,"kecamatan":"Peukan Bada","banjir":1,"longsor":0},
    {"tahun":2022,"kecamatan":"Pulo Aceh","banjir":0,"longsor":0},

    # =====================================================
    # 2023
    # =====================================================
    {"tahun":2023,"kecamatan":"Lhoong","banjir":1,"longsor":0},
    {"tahun":2023,"kecamatan":"Lhoknga","banjir":3,"longsor":0},
    {"tahun":2023,"kecamatan":"Leupung","banjir":2,"longsor":0},
    {"tahun":2023,"kecamatan":"Indrapuri","banjir":2,"longsor":0},
    {"tahun":2023,"kecamatan":"Kuta Cot Glie","banjir":1,"longsor":1},
    {"tahun":2023,"kecamatan":"Seulimeum","banjir":2,"longsor":0},
    {"tahun":2023,"kecamatan":"Kota Jantho","banjir":1,"longsor":0},
    {"tahun":2023,"kecamatan":"Lembah Seulawah","banjir":1,"longsor":1},
    {"tahun":2023,"kecamatan":"Mesjid Raya","banjir":1,"longsor":0},
    {"tahun":2023,"kecamatan":"Darussalam","banjir":0,"longsor":0},
    {"tahun":2023,"kecamatan":"Baitussalam","banjir":0,"longsor":0},
    {"tahun":2023,"kecamatan":"Kuta Baro","banjir":1,"longsor":0},
    {"tahun":2023,"kecamatan":"Montasik","banjir":1,"longsor":0},
    {"tahun":2023,"kecamatan":"Blang Bintang","banjir":1,"longsor":0},
    {"tahun":2023,"kecamatan":"Ingin Jaya","banjir":1,"longsor":0},
    {"tahun":2023,"kecamatan":"Krueng Barona Jaya","banjir":0,"longsor":0},
    {"tahun":2023,"kecamatan":"Suka Makmur","banjir":2,"longsor":0},
    {"tahun":2023,"kecamatan":"Kuta Malaka","banjir":0,"longsor":0},
    {"tahun":2023,"kecamatan":"Simpang Tiga","banjir":0,"longsor":0},
    {"tahun":2023,"kecamatan":"Darul Imarah","banjir":1,"longsor":0},
    {"tahun":2023,"kecamatan":"Darul Kamal","banjir":0,"longsor":0},
    {"tahun":2023,"kecamatan":"Peukan Bada","banjir":1,"longsor":0},
    {"tahun":2023,"kecamatan":"Pulo Aceh","banjir":0,"longsor":0},

    # =====================================================
    # 2024
    # =====================================================
    {"tahun":2024,"kecamatan":"Lhoong","banjir":1,"longsor":1},
    {"tahun":2024,"kecamatan":"Lhoknga","banjir":3,"longsor":0},
    {"tahun":2024,"kecamatan":"Leupung","banjir":2,"longsor":1},
    {"tahun":2024,"kecamatan":"Indrapuri","banjir":2,"longsor":1},
    {"tahun":2024,"kecamatan":"Kuta Cot Glie","banjir":1,"longsor":1},
    {"tahun":2024,"kecamatan":"Seulimeum","banjir":2,"longsor":0},
    {"tahun":2024,"kecamatan":"Kota Jantho","banjir":1,"longsor":1},
    {"tahun":2024,"kecamatan":"Lembah Seulawah","banjir":1,"longsor":1},
    {"tahun":2024,"kecamatan":"Mesjid Raya","banjir":1,"longsor":0},
    {"tahun":2024,"kecamatan":"Darussalam","banjir":1,"longsor":0},
    {"tahun":2024,"kecamatan":"Baitussalam","banjir":1,"longsor":0},
    {"tahun":2024,"kecamatan":"Kuta Baro","banjir":1,"longsor":0},
    {"tahun":2024,"kecamatan":"Montasik","banjir":1,"longsor":0},
    {"tahun":2024,"kecamatan":"Blang Bintang","banjir":0,"longsor":0}, # Diperbaiki (-1 banjir)
    {"tahun":2024,"kecamatan":"Ingin Jaya","banjir":1,"longsor":0},
    {"tahun":2024,"kecamatan":"Krueng Barona Jaya","banjir":0,"longsor":0},
    {"tahun":2024,"kecamatan":"Suka Makmur","banjir":1,"longsor":1},
    {"tahun":2024,"kecamatan":"Kuta Malaka","banjir":1,"longsor":0},
    {"tahun":2024,"kecamatan":"Simpang Tiga","banjir":1,"longsor":0},
    {"tahun":2024,"kecamatan":"Darul Imarah","banjir":0,"longsor":0},
    {"tahun":2024,"kecamatan":"Darul Kamal","banjir":0,"longsor":0},
    {"tahun":2024,"kecamatan":"Peukan Bada","banjir":0,"longsor":0},
    {"tahun":2024,"kecamatan":"Pulo Aceh","banjir":0,"longsor":0},

    # =====================================================
    # 2025
    # =====================================================
    {"tahun":2025,"kecamatan":"Lhoong","banjir":1,"longsor":1},
    {"tahun":2025,"kecamatan":"Lhoknga","banjir":2,"longsor":1},
    {"tahun":2025,"kecamatan":"Leupung","banjir":1,"longsor":1},
    {"tahun":2025,"kecamatan":"Indrapuri","banjir":1,"longsor":0},
    {"tahun":2025,"kecamatan":"Kuta Cot Glie","banjir":1,"longsor":0},
    {"tahun":2025,"kecamatan":"Seulimeum","banjir":1,"longsor":0},
    {"tahun":2025,"kecamatan":"Kota Jantho","banjir":0,"longsor":1}, # Diperbaiki (+1 longsor)
    {"tahun":2025,"kecamatan":"Lembah Seulawah","banjir":0,"longsor":1}, # Diperbaiki (-1 banjir, +1 longsor)
    {"tahun":2025,"kecamatan":"Mesjid Raya","banjir":1,"longsor":0},
    {"tahun":2025,"kecamatan":"Darussalam","banjir":1,"longsor":1}, # Diperbaiki (+1 longsor)
    {"tahun":2025,"kecamatan":"Baitussalam","banjir":0,"longsor":0},
    {"tahun":2025,"kecamatan":"Kuta Baro","banjir":1,"longsor":1}, # Diperbaiki (+1 longsor)
    {"tahun":2025,"kecamatan":"Montasik","banjir":0,"longsor":1},
    {"tahun":2025,"kecamatan":"Blang Bintang","banjir":0,"longsor":1}, # Diperbaiki (-1 banjir, +1 longsor)
    {"tahun":2025,"kecamatan":"Ingin Jaya","banjir":0,"longsor":0},
    {"tahun":2025,"kecamatan":"Krueng Barona Jaya","banjir":1,"longsor":0}, # Diperbaiki (+1 banjir)
    {"tahun":2025,"kecamatan":"Suka Makmur","banjir":1,"longsor":0},
    {"tahun":2025,"kecamatan":"Kuta Malaka","banjir":0,"longsor":0},
    {"tahun":2025,"kecamatan":"Simpang Tiga","banjir":0,"longsor":0}, # Diperbaiki (-1 banjir)
    {"tahun":2025,"kecamatan":"Darul Imarah","banjir":0,"longsor":1}, # Diperbaiki (+1 longsor)
    {"tahun":2025,"kecamatan":"Darul Kamal","banjir":1,"longsor":0},
    {"tahun":2025,"kecamatan":"Peukan Bada","banjir":0,"longsor":1}, # Diperbaiki (-1 banjir, +1 longsor)
    {"tahun":2025,"kecamatan":"Pulo Aceh","banjir":1,"longsor":0},
]


def get_disaster_df() -> pd.DataFrame:
    df = pd.DataFrame(DISASTER_DATA)

    # Dominan bencana
    df["dominan"] = df.apply(
        lambda r: "Longsor" if r["kejadian_longsor"] >= r["kejadian_banjir"] else "Banjir",
        axis=1,
    )
    # Warna & level berdasarkan total kejadian
    df["marker_color"] = df["total_kejadian"].apply(
        lambda x: "#ef4444" if x >= 25 else "#f97316" if x >= 15 else "#eab308" if x >= 10 else "#22c55e"
    )
    df["level"] = df["total_kejadian"].apply(
        lambda x: "Sangat Sering" if x >= 25 else "Sering" if x >= 15 else "Sedang" if x >= 10 else "Jarang"
    )
    # Total lingkungan terpapar
    df["total_terpapar_ha"] = df["lingkungan_banjir_ha"] + df["lingkungan_longsor_ha"]

    return df.sort_values("total_kejadian", ascending=False).reset_index(drop=True)

def get_yearly_df():
    df = pd.DataFrame(YEARLY_DISASTERS)
    df["total"] = df["banjir"] + df["longsor"]
    return df

def generate_event_log(n: int = 80) -> pd.DataFrame:
    random.seed(42)
    np.random.seed(42)
    kec_list = [d["kecamatan"] for d in DISASTER_DATA]
    types    = ["Banjir", "Longsor"]
    levels   = ["Ringan", "Sedang", "Berat"]
    weights  = [0.35, 0.45, 0.20]

    events = []
    base   = datetime(2018, 1, 1)
    for _ in range(n):
        kec   = random.choice(kec_list)
        dtype = random.choice(types)
        sev   = random.choices(levels, weights)[0]
        rain  = round(random.uniform(30, 160), 1)
        events.append({
            "tanggal":           (base + timedelta(days=random.randint(0, 365*6))).strftime("%Y-%m-%d"),
            "kecamatan":         kec,
            "jenis_bencana":     dtype,
            "tingkat_keparahan": sev,
            "curah_hujan_mm":    rain,
        })
    return pd.DataFrame(events).sort_values("tanggal").reset_index(drop=True)