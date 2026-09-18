# 🌧️ AcehRain Intelligence
### AI-Powered Extreme Rainfall Prediction & Agricultural Intelligence Platform
**Hybrid LSTM–XGBoost · Real-time Monitoring · GIS Visualization · Streamlit**

---

<div align="center">

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![TensorFlow](https://img.shields.io/badge/TensorFlow-2.13%2B-FF6F00?logo=tensorflow&logoColor=white)
![XGBoost](https://img.shields.io/badge/XGBoost-2.0%2B-189AB4)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35%2B-FF4B4B?logo=streamlit&logoColor=white)
![Folium](https://img.shields.io/badge/Folium-GIS%20Map-77B255)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 📋 Daftar Isi

- [Tentang Proyek](#-tentang-proyek)
- [Fitur Utama](#-fitur-utama)
- [Arsitektur Model](#-arsitektur-model)
- [Struktur Folder](#-struktur-folder)
- [Persyaratan Sistem](#-persyaratan-sistem)
- [Instalasi](#-instalasi)
- [File yang Diperlukan](#-file-yang-diperlukan)
- [Konfigurasi](#-konfigurasi)
- [Cara Menjalankan](#-cara-menjalankan)
- [Training Model](#-training-model)
- [Deployment](#-deployment)
- [Tech Stack](#-tech-stack)
- [Hasil Evaluasi](#-hasil-evaluasi)
- [Penulis](#-penulis)

---

## 🔍 Tentang Proyek

**AcehRain Intelligence** adalah platform AI terpadu untuk monitoring dan prediksi curah hujan ekstrem di **Kabupaten Aceh Besar, Provinsi Aceh**. Platform ini dikembangkan sebagai bagian dari penelitian skripsi Program Studi S1 Sains Data, Universitas Logistik dan Bisnis Internasional (ULBI), Bandung.

Platform menggabungkan:
- **Deep Learning (LSTM)** untuk menangkap pola temporal curah hujan
- **Gradient Boosting (XGBoost)** untuk koreksi residual error non-linear
- **Data real-time** via OpenWeatherMap API (akumulasi harian otomatis)
- **GIS Visualization** dengan batas kecamatan Aceh Besar berbasis GeoJSON
- **Analisis risiko** pertanian dan bencana per kecamatan

> Prediksi akhir menggunakan formulasi:  
> **Ŷ_Hybrid = Ŷ_LSTM + ê_XGBoost**

---

## ✨ Fitur Utama

| Menu | Deskripsi |
|------|-----------|
| 🏠 **Beranda** | Dashboard utama: KPI cards, tren curah hujan, AI smart insights |
| 📡 **Live Monitoring** | Data cuaca real-time + peta GIS choropleth + heatmap |
| 🤖 **Prediksi Curah Hujan Ekstrem** | Inferensi model Hybrid LSTM–XGBoost + forecast 3–14 hari |
| 🌾 **Analisis Pertanian** | Data luas sawah & produksi padi per kecamatan + peta GIS |
| 🚨 **Analisis Bencana** | Frekuensi kejadian & lingkungan terpapar per kecamatan + choropleth |
| 📊 **Statistik Curah Hujan** | Tren, distribusi, korelasi, pola musiman, deteksi ekstrem |
| ℹ️ **Tentang** | Metodologi, arsitektur model, referensi, dan info pengembang |

### Fitur Teknis
- ✅ **Update otomatis harian** — Curah hujan diakumulasi, suhu & kelembapan dirata-rata, angin diambil maksimum
- ✅ **Inference only** — Model tidak dilatih ulang saat runtime (load dari file)
- ✅ **GIS Choropleth** — Batas 23 kecamatan Aceh Besar dari GeoJSON resmi
- ✅ **Export data** — Download CSV & Excel di semua modul
- ✅ **Rekomendasi AI** — Mitigasi otomatis per kecamatan berdasarkan threshold BMKG
- ✅ **Cache optimal** — `@st.cache_data` + `@st.cache_resource` untuk performa

---

## 🧠 Arsitektur Model

### LSTM (Long Short-Term Memory)
```
Input  (7 × 4)
  → LSTM Layer 1  (128 units, return_sequences=True)
  → BatchNormalization
  → Dropout (0.4)
  → LSTM Layer 2  (64 units)
  → BatchNormalization
  → Dropout (0.4)
  → Dense (32, ReLU)
  → Dense (1)  → log(curah_hujan + 1)
```

### XGBoost (Residual Corrector)
- **Input:** 18 fitur (LSTM pred, lag 1–7, rolling stats, sin/cos bulan, interaksi)
- **Target:** Residual = Aktual − Prediksi LSTM
- **Output:** Koreksi residual yang dijumlahkan ke prediksi LSTM

### Preprocessing
- Normalisasi: **MinMaxScaler** `[0, 1]`
- Target transformation: **log1p** (curah hujan)
- Lookback window: **7 hari**
- Train/test split: **80% / 20%** (kronologis)
- Data cuaca harian: RR, Tavg, RHAvg, ffx (BMKG Blang Bintang)

---

## 📁 Struktur Folder

```
acehrain_v3/
├── app.py                          # Entry point & page router
├── config.py                       # Konfigurasi global & parameter model
├── requirements.txt
├── README.md
│
├── pages/                          # Halaman aplikasi (7 modul)
│   ├── home.py                     # Beranda + KPI + AI insights
│   ├── monitoring.py               # Live monitoring + GIS map
│   ├── prediction.py               # Prediksi AI + forecast
│   ├── agriculture.py              # Analisis pertanian + peta sawah
│   ├── disaster.py                 # Analisis bencana + choropleth
│   ├── analysis.py                 # Statistik curah hujan
│   └── about.py                    # Info metodologi & developer
│
├── models/
│   └── inference.py                # Load model + inferensi (NO retraining)
│
├── services/
│   └── recommendation.py          # AI Mitigation Recommendation Engine
│
├── components/
│   ├── charts.py                   # 15+ Plotly enterprise charts
│   ├── map_view.py                 # GIS choropleth (Folium + GeoJSON)
│   └── insights.py                 # AI Smart Insight Engine
│
├── utils/
│   ├── api.py                      # OWM API: akumulasi harian → Excel
│   ├── data_loader.py              # Load data + cache + compute stats
│   └── helpers.py                  # CSS, sidebar, hero, alert, export
│
├── data/
│   ├── agriculture_data.py         # Luas sawah & produksi padi 17 kecamatan
│   └── disaster_data.py            # Kejadian & lingkungan terpapar 23 kecamatan
│
├── styles/
│   └── main.css                    # Dark premium theme (400+ baris)
│
│── Data & Model Files (letakkan di root)
├── data_cuaca_aceh_besar.xlsx      # ← Dataset historis cuaca (WAJIB)
├── Aceh_Besar_Kecamatan.geojson   # ← Batas kecamatan GIS (WAJIB)
├── lstm_weights.weights.h5         # ← Bobot LSTM pre-trained (WAJIB)
└── xgb_model_final.json            # ← Model XGBoost pre-trained (WAJIB)
```

---

## 💻 Persyaratan Sistem

| Komponen | Minimum | Rekomendasi |
|----------|---------|-------------|
| Python | 3.9 | 3.10 / 3.11 |
| RAM | 4 GB | 8 GB |
| Storage | 2 GB | 5 GB |
| OS | Windows 10 / Ubuntu 20.04 / macOS 12 | - |

---

## 🚀 Instalasi

### 1. Clone / Download project
```bash
# Via Git
git clone https://github.com/username/acehrain-intelligence.git
cd acehrain-intelligence

# Atau ekstrak ZIP yang didownload
```

### 2. Buat virtual environment (sangat dianjurkan)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Letakkan file data & model di folder root
```
acehrain_v3/
├── data_cuaca_aceh_besar.xlsx
├── Aceh_Besar_Kecamatan.geojson
├── lstm_weights.weights.h5
└── xgb_model_final.json
```

---

## 📂 File yang Diperlukan

### Dataset Cuaca (`data_cuaca_aceh_besar.xlsx`)
Format kolom yang wajib ada:

| Kolom | Tipe | Keterangan |
|-------|------|------------|
| `tanggal` | Date | Tanggal pengamatan |
| `curah_hujan` | Float | Curah hujan harian (mm) |
| `kecepatan_angin` | Float | Kecepatan angin maksimum (m/s) |
| `kelembapan` | Float | Kelembapan rata-rata (%) |
| `suhu` | Float | Suhu rata-rata (°C) |

Sumber: **BMKG Stasiun Meteorologi Blang Bintang**, Aceh Besar  
Periode: Januari 2020 – sekarang (diperbarui otomatis setiap hari)

### Model Files
| File | Keterangan |
|------|------------|
| `lstm_weights.weights.h5` | Bobot LSTM (disimpan dari training) |
| `xgb_model_final.json` | Model XGBoost dalam format JSON |

> ⚠️ **Penting:** Jika terdapat error `Unrecognized keyword arguments: ['batch_shape']`, gunakan file `lstm_weights.weights.h5` (bukan `.keras`). Inference engine akan otomatis rebuild arsitektur + load bobot.

---

## ⚙️ Konfigurasi

Edit `config.py` sesuai kebutuhan:

```python
# API Key OpenWeatherMap
OWM_API_KEY = "your_api_key_here"

# Lokasi stasiun
LOCATION = {
    "lat": 5.404438378495802,
    "lon": 95.46433643789337,
    "map_center": [5.45, 95.32],
    "zoom": 9,
}

# Konfigurasi model (harus sama dengan saat training)
INFERENCE_CONFIG = {
    "lookback":   7,
    "features":   ["curah_hujan", "kecepatan_angin", "kelembapan", "suhu"],
    "n_features": 4,
}

# Path model
LSTM_WEIGHTS_PATH = ROOT_DIR / "lstm_weights.weights.h5"
XGB_MODEL_PATH    = ROOT_DIR / "xgb_model_final.json"
```

---

## ▶️ Cara Menjalankan

```bash
# Pastikan virtual environment aktif dan berada di folder project
streamlit run app.py
```

Aplikasi akan terbuka di browser: `http://localhost:8501`

### Opsi tambahan
```bash
# Jalankan di port tertentu
streamlit run app.py --server.port 8080

# Nonaktifkan CORS (untuk deployment internal)
streamlit run app.py --server.enableCORS false

# Mode headless (untuk server tanpa browser)
streamlit run app.py --server.headless true
```

---

## 🤖 Training Model

Untuk melatih ulang model dari awal, buka **Google Colab** dan jalankan `training_fixed.py`.

### Langkah Training
```
1. Upload data_cuaca_aceh_besar.xlsx ke Colab
2. Jalankan training_fixed.py
3. Download hasil:
   - lstm_weights.weights.h5  ← WAJIB
   - xgb_model_final.json     ← WAJIB
4. Letakkan di folder root acehrain_v3/
5. Restart aplikasi Streamlit
```

### Konfigurasi Training
```python
LOOKBACK     = 7          # Window 7 hari
LSTM_UNITS_1 = 128        # Layer 1
LSTM_UNITS_2 = 64         # Layer 2
DROPOUT      = 0.4        # Dropout rate
BATCH_SIZE   = 32         # Batch size
EPOCHS       = 200        # Max epochs (EarlyStopping patience=10)
LEARNING_RATE = 0.0005    # Adam optimizer
XGB_ESTIMATORS = 300-700  # RandomizedSearchCV
```

---

## 🌐 Deployment

### Streamlit Community Cloud (Gratis)
```
1. Push project ke GitHub (public/private)
2. Buka share.streamlit.io
3. Connect repo → pilih app.py
4. Tambah Secrets:
   [secrets]
   OWM_API_KEY = "your_key"
5. Upload file data & model via Git LFS atau external storage
```

### Docker
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

```bash
docker build -t acehrain .
docker run -p 8501:8501 acehrain
```

### Railway / Render
```
# railway.toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true"
```

---

## 🛠️ Tech Stack

| Kategori | Library | Versi |
|----------|---------|-------|
| Web Framework | Streamlit | ≥ 1.35 |
| Deep Learning | TensorFlow / Keras | ≥ 2.13 |
| Gradient Boosting | XGBoost | ≥ 2.0 |
| Data Processing | Pandas, NumPy | Latest |
| ML Utilities | scikit-learn | ≥ 1.3 |
| Visualization | Plotly | ≥ 5.18 |
| GIS Maps | Folium + streamlit-folium | ≥ 0.15 |
| Geospatial | GeoPandas | ≥ 0.14 |
| Excel I/O | openpyxl | ≥ 3.1 |
| Weather API | OpenWeatherMap | v2.5 |

---

## 📊 Hasil Evaluasi

Evaluasi dilakukan pada **20% data uji** (data tidak dilihat model saat training):

| Model | MAE (mm) | RMSE (mm) | R² |
|-------|----------|-----------|-----|
| LSTM (Baseline) | 7.028 | 13.411 | 0.151 |
| **Hybrid LSTM–XGBoost** | **2.189** | **4.671** | **0.887** |
| Peningkatan | ↓ 68.84% | ↓ 65.17% | ↑ +0.736 |

> Model hybrid mampu menjelaskan **88.7% variasi** curah hujan aktual pada data uji.

### Interpretasi
- **MAE 2.189 mm** → rata-rata kesalahan prediksi hanya ~2.2 mm per hari
- **R² 0.887** → sangat baik untuk data klimatologi harian yang nonlinier
- Peningkatan signifikan terjadi terutama pada hari-hari **hujan lebat (20–50 mm)** dan **ekstrem (>50 mm)**

---

## 📦 requirements.txt

```
streamlit>=1.35.0
pandas>=2.0.0
numpy>=1.24.0
tensorflow>=2.13.0
xgboost>=2.0.0
scikit-learn>=1.3.0
plotly>=5.18.0
folium>=0.15.0
streamlit-folium>=0.18.0
geopandas>=0.14.0
openpyxl>=3.1.0
requests>=2.31.0
joblib>=1.3.0
```

---

## 🗂️ Sumber Data

| Data | Sumber | Keterangan |
|------|--------|------------|
| Cuaca Historis | BMKG Blang Bintang | Januari 2020 – April 2026 |
| Cuaca Real-time | OpenWeatherMap API | Update otomatis setiap jam |
| Batas Kecamatan | BIG / BNPB | GeoJSON 23 kecamatan |
| Produksi Padi | BPS Kabupaten Aceh Besar | 2022 |
| Data Bencana | BPBD Kabupaten Aceh Besar | 2018–2024 |
| Peta Rawan Bencana | BNPB / BPBD | Lingkungan terpapar (Ha) |

---

## 🔖 Lisensi

Proyek ini dikembangkan untuk keperluan penelitian akademik.  
© 2026 L.M. Aznur Syahfajar — Universitas Logistik dan Bisnis Internasional

---

## 👨‍💻 Penulis

**L.M. Aznur Syahfajar**  
NIM: 184220008  
Program Studi S1 Sains Data  
Universitas Logistik dan Bisnis Internasional (ULBI), Bandung

**Pembimbing:**
- Kiki Mustaqim
- Woro Isti Rahayu

---

## 📚 Referensi

1. Hochreiter, S. & Schmidhuber, J. (1997). Long Short-Term Memory. *Neural Computation*, 9(8), 1735–1780.
2. Chen, T. & Guestrin, C. (2016). XGBoost: A Scalable Tree Boosting System. *KDD '16*.
3. BMKG (2024). Pedoman Pengamatan dan Klasifikasi Curah Hujan. Jakarta: BMKG.
4. BPS Kabupaten Aceh Besar (2022). *Aceh Besar Dalam Angka 2022*. Aceh.
5. BPBD Kabupaten Aceh Besar (2024). Data Kejadian Bencana Hidrometeorologi 2018–2024.
6. Salam, A., Saiku, M. & Buliali, J.L. (2025). Prediksi Curah Hujan dengan Model Hybrid XGBoost-LSTM.
7. Padang, Y. et al. (2025). Bidirectional LSTM for Rainfall Prediction in Papua.

---

<div align="center">
<sub>🌧️ AcehRain Intelligence v3.0 · Hybrid LSTM–XGBoost · OpenWeatherMap API · Streamlit</sub>
</div>
