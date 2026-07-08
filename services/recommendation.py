# ============================================================
# services/recommendation.py — AI Mitigation Recommendation Engine
# ============================================================

from dataclasses import dataclass, field
from typing import List, Dict
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import RAIN_LEVELS


@dataclass
class Recommendation:
    priority: str          # "SEGERA" | "PENTING" | "SIAGA" | "MONITOR"
    category: str          # "Pertanian" | "Infrastruktur" | "Evakuasi" | "Monitoring"
    action: str
    detail: str
    icon: str
    color: str


@dataclass
class KecamatanMitigationPlan:
    kecamatan: str
    risk_level: str
    risk_color: str
    severity_mm: float
    alert_message: str
    recommendations: List[Recommendation] = field(default_factory=list)
    smart_insight: str = ""


# ── Kecamatan Risk Profile ────────────────────────────────────
KECAMATAN_PROFILE = {

    "Lhoong": {
        "topografi": "pesisir-pegunungan",
        "main_risk": ["banjir", "longsor"],
        "sawah_luas": 1465,
        "population_risk": "tinggi",
        "irigasi_kritis": False,
        "coastal": True,
    },

    "Lhoknga": {
        "topografi": "pesisir-datar",
        "main_risk": ["banjir_pesisir", "genangan"],
        "sawah_luas": 1251,
        "population_risk": "kritis",
        "irigasi_kritis": False,
        "coastal": True,
    },

    "Leupung": {
        "topografi": "pesisir-pegunungan",
        "main_risk": ["banjir", "banjir_bandang"],
        "sawah_luas": 192,
        "population_risk": "tinggi",
        "irigasi_kritis": False,
        "coastal": True,
    },

    "Indrapuri": {
        "topografi": "dataran-rendah",
        "main_risk": ["banjir", "genangan"],
        "sawah_luas": 5850,
        "population_risk": "kritis",
        "irigasi_kritis": True,
        "coastal": False,
    },

    "Kota Cot Glie": {
        "topografi": "lereng-sedang",
        "main_risk": ["longsor", "banjir"],
        "sawah_luas": 3342,
        "population_risk": "tinggi",
        "irigasi_kritis": True,
        "coastal": False,
    },

    "Seulimeum": {
        "topografi": "pegunungan-lembah",
        "main_risk": ["banjir", "longsor"],
        "sawah_luas": 4096,
        "population_risk": "tinggi",
        "irigasi_kritis": True,
        "coastal": False,
    },

    "Kota Jantho": {
        "topografi": "bukit-sedang",
        "main_risk": ["longsor", "banjir"],
        "sawah_luas": 1797,
        "population_risk": "sedang",
        "irigasi_kritis": False,
        "coastal": False,
    },

    "Lembah Seulawah": {
        "topografi": "lereng-pegunungan",
        "main_risk": ["longsor", "erosi"],
        "sawah_luas": 1084,
        "population_risk": "sedang",
        "irigasi_kritis": False,
        "coastal": False,
    },

    "Mesjid Raya": {
        "topografi": "pesisir-datar",
        "main_risk": ["banjir_pesisir"],
        "sawah_luas": 30,
        "population_risk": "sedang",
        "irigasi_kritis": False,
        "coastal": True,
    },

    "Darussalam": {
        "topografi": "dataran-rendah",
        "main_risk": ["banjir", "genangan"],
        "sawah_luas": 1102,
        "population_risk": "kritis",
        "irigasi_kritis": False,
        "coastal": False,
    },

    "Baitussalam": {
        "topografi": "dataran-rendah-pesisir",
        "main_risk": ["banjir_pesisir", "genangan"],
        "sawah_luas": 57,
        "population_risk": "kritis",
        "irigasi_kritis": False,
        "coastal": True,
    },

    "Kuta Baro": {
        "topografi": "dataran-rendah",
        "main_risk": ["banjir", "genangan"],
        "sawah_luas": 3218,
        "population_risk": "tinggi",
        "irigasi_kritis": True,
        "coastal": False,
    },

    "Montasik": {
        "topografi": "dataran-rendah",
        "main_risk": ["genangan", "banjir"],
        "sawah_luas": 4607,
        "population_risk": "sedang",
        "irigasi_kritis": True,
        "coastal": False,
    },

    "Blang Bintang": {
        "topografi": "dataran-rendah",
        "main_risk": ["banjir", "genangan"],
        "sawah_luas": 1480,
        "population_risk": "tinggi",
        "irigasi_kritis": False,
        "coastal": False,
    },

    "Ingin Jaya": {
        "topografi": "dataran-rendah",
        "main_risk": ["banjir", "genangan"],
        "sawah_luas": 2386,
        "population_risk": "kritis",
        "irigasi_kritis": True,
        "coastal": False,
    },

    "Krueng Barona Jaya": {
        "topografi": "dataran-rendah",
        "main_risk": ["genangan"],
        "sawah_luas": 182,
        "population_risk": "kritis",
        "irigasi_kritis": False,
        "coastal": False,
    },

    "Suka Makmur": {
        "topografi": "dataran-medium",
        "main_risk": ["banjir", "genangan"],
        "sawah_luas": 1963,
        "population_risk": "tinggi",
        "irigasi_kritis": False,
        "coastal": False,
    },

    "Kuta Malaka": {
        "topografi": "perbukitan-rendah",
        "main_risk": ["banjir", "longsor"],
        "sawah_luas": 1227,
        "population_risk": "sedang",
        "irigasi_kritis": False,
        "coastal": False,
    },

    "Simpang Tiga": {
        "topografi": "dataran-rendah",
        "main_risk": ["banjir", "genangan"],
        "sawah_luas": 988,
        "population_risk": "sedang",
        "irigasi_kritis": False,
        "coastal": False,
    },

    "Darul Imarah": {
        "topografi": "dataran-rendah",
        "main_risk": ["banjir", "genangan"],
        "sawah_luas": 1148,
        "population_risk": "kritis",
        "irigasi_kritis": False,
        "coastal": False,
    },

    "Darul Kamal": {
        "topografi": "dataran-rendah",
        "main_risk": ["banjir"],
        "sawah_luas": 58,
        "population_risk": "sedang",
        "irigasi_kritis": False,
        "coastal": False,
    },

    "Peukan Bada": {
        "topografi": "pesisir-datar",
        "main_risk": ["banjir_pesisir", "genangan"],
        "sawah_luas": 526,
        "population_risk": "tinggi",
        "irigasi_kritis": False,
        "coastal": True,
    },

    "Pulo Aceh": {
        "topografi": "kepulauan-pesisir",
        "main_risk": ["longsor", "banjir_pesisir"],
        "sawah_luas": 323,
        "population_risk": "sedang",
        "irigasi_kritis": False,
        "coastal": True,
    },
}


def _default_profile(kec: str) -> dict:
    return {
        "topografi": "dataran-sedang",
        "main_risk": ["banjir"],
        "sawah_luas": 2000,
        "population_risk": "sedang",
        "irigasi_kritis": False,
        "coastal": False,
    }


# ── Recommendation Engine ─────────────────────────────────────
def generate_recommendations(
    kecamatan: str,
    rain_mm: float,
    forecast_7d: float = 0.0,
) -> KecamatanMitigationPlan:
    """Generate context-aware mitigation recommendations."""

    profile = KECAMATAN_PROFILE.get(kecamatan, _default_profile(kecamatan))
    recs    = []

    # Determine level
    if rain_mm < 10:
        level, color, alert = "NORMAL", "#22c55e", f"Kondisi cuaca normal di {kecamatan}."
    elif rain_mm < 30:
        level, color, alert = "WASPADA", "#eab308", f"Hujan sedang di {kecamatan}. Pantau perkembangan."
    elif rain_mm < 50:
        level, color, alert = "SIAGA", "#f97316", f"Hujan lebat di {kecamatan}! Aktifkan protokol siaga banjir."
    elif rain_mm < 100:
        level, color, alert = "BAHAYA", "#ef4444", f"CURAH HUJAN EKSTREM di {kecamatan}! Risiko banjir dan longsor tinggi."
    else:
        level, color, alert = "BENCANA", "#7f1d1d", f"🆘 DARURAT: Curah hujan katastrofik di {kecamatan}! Evakuasi segera."

    # ── Agriculture Recommendations ─────────────────────────
    if rain_mm >= 20:
        recs.append(Recommendation(
            priority="SEGERA", category="Pertanian",
            action="Percepatan Panen Dini",
            detail=f"Lakukan panen lebih awal untuk sawah yang mendekati matang di {kecamatan} "
                   f"({profile['sawah_luas']:,} ha). Hujan {rain_mm:.0f} mm berpotensi merendam padi.",
            icon="🌾", color="#eab308",
        ))
    if rain_mm >= 20 and profile["irigasi_kritis"]:
        recs.append(Recommendation(
            priority="PENTING", category="Pertanian",
            action="Buka Pintu Irigasi & Pompanisasi",
            detail="Buka saluran drainase dan aktifkan pompa air untuk mencegah genangan lahan sawah. "
                   "Cek kondisi pintu air irigasi di seluruh sub-petak sawah.",
            icon="💧", color="#06b6d4",
        ))
    if rain_mm >= 50:
        recs.append(Recommendation(
            priority="SEGERA", category="Pertanian",
            action="Proteksi Komoditas & Pemindahan Alsintan",
            detail="Pindahkan peralatan pertanian dan hasil panen ke lokasi aman. Dokumentasikan "
                   "kondisi lahan untuk klaim asuransi pertanian jika diperlukan.",
            icon="🚜", color="#f97316",
        ))

    # ── Flood Recommendations ────────────────────────────────
    if "banjir" in profile["main_risk"] and rain_mm >= 20:
        recs.append(Recommendation(
            priority="SIAGA" if rain_mm < 50 else "SEGERA",
            category="Infrastruktur",
            action="Aktivasi Pompa Banjir & Drainase",
            detail="Aktifkan seluruh pompa pengendali banjir. Bersihkan saluran drainase dari "
                   "sampah dan sedimentasi. Koordinasi dengan Dinas PU setempat.",
            icon="🚧", color="#3b82f6",
        ))
    if rain_mm >= 50:
        recs.append(Recommendation(
            priority="SEGERA", category="Evakuasi",
            action="Peringatan Dini Masyarakat",
            detail=f"Siarkan peringatan cuaca ekstrem via pengeras suara masjid dan media sosial. "
                   f"Siapkan jalur evakuasi dan lokasi pengungsian sementara di {kecamatan}.",
            icon="📢", color="#ef4444",
        ))

    # ── Landslide Recommendations ────────────────────────────
    if "longsor" in profile["main_risk"] or profile["topografi"] in ("lereng-pegunungan", "lereng-sedang"):
        if rain_mm >= 20:
            recs.append(Recommendation(
                priority="PENTING" if rain_mm < 50 else "SEGERA",
                category="Infrastruktur",
                action="Mitigasi Longsor & Penutupan Lereng",
                detail="Pasang barrier dan geotextile di lereng kritis. Larang aktivitas pertanian "
                       "dan pemukiman di zona lereng >30°. Monitoring pergerakan tanah real-time.",
                icon="⛰️", color="#8b5cf6",
            ))
            recs.append(Recommendation(
                priority="MONITOR", category="Infrastruktur",
                action="Larangan Tanam di Lereng Kritis",
                detail="Hentikan sementara aktivitas pertanian di lereng >25°. "
                       "Koordinasi dengan penyuluh pertanian untuk alih lokasi tanam.",
                icon="🚫", color="#f59e0b",
            ))

    # ── Coastal Recommendations ──────────────────────────────
    if profile["coastal"] and rain_mm >= 20:
        recs.append(Recommendation(
            priority="PENTING", category="Pertanian",
            action="Proteksi Tambak & Budidaya Pesisir",
            detail="Perkuat tanggul tambak dan jaring budidaya ikan/udang. Pantau pasang surut "
                   "dan potensi rob. Koordinasi dengan kelompok nelayan dan petambak.",
            icon="🐟", color="#06b6d4",
        ))

    # ── Forecast-based Recommendations ──────────────────────
    if forecast_7d > rain_mm * 1.2 and forecast_7d >= 20:
        recs.append(Recommendation(
            priority="MONITOR", category="Monitoring",
            action="Pantau Tren Hujan 7 Hari ke Depan",
            detail=f"AI memprediksi rata-rata curah hujan {forecast_7d:.1f} mm dalam 7 hari ke depan. "
                   f"Tingkatkan frekuensi monitoring dan perbarui rencana mitigasi.",
            icon="📡", color="#3b82f6",
        ))

    # ── Always: Monitoring ───────────────────────────────────
    recs.append(Recommendation(
        priority="MONITOR", category="Monitoring",
        action="Pemantauan Cuaca Berkala",
        detail="Pantau data curah hujan setiap 3 jam. Koordinasi dengan BPBD Aceh Besar dan BMKG "
               "untuk update peringatan dini terkini.",
        icon="🌦️", color="#94a3b8",
    ))

    # ── Smart Insight ────────────────────────────────────────
    insight = _generate_insight(kecamatan, rain_mm, forecast_7d, profile, level)

    return KecamatanMitigationPlan(
        kecamatan=kecamatan,
        risk_level=level,
        risk_color=color,
        severity_mm=rain_mm,
        alert_message=alert,
        recommendations=recs,
        smart_insight=insight,
    )


def _generate_insight(kec, rain_mm, forecast_7d, profile, level) -> str:
    luas = profile.get("sawah_luas", 2000)
    risks = profile.get("main_risk", [])

    if level == "NORMAL":
        return (f"Kondisi cuaca di {kec} dalam batas normal. "
                f"Monitoring rutin cukup untuk memantau perkembangan curah hujan.")
    elif level == "WASPADA":
        return (f"Curah hujan {rain_mm:.1f} mm di {kec} termasuk kategori sedang. "
                f"Petani dengan {luas:,} ha sawah disarankan memeriksa kondisi drainase "
                f"dan kesiapan lahan sebelum musim hujan intensif.")
    elif level == "SIAGA":
        primary = "risiko banjir" if "banjir" in risks else "risiko longsor"
        return (f"⚠️ Curah hujan lebat ({rain_mm:.1f} mm) meningkatkan {primary} di {kec}. "
                f"Sawah seluas {luas:,} ha berpotensi tergenang. Rekomendasi percepatan panen "
                f"dan aktivasi pompa air diprioritaskan. Koordinasi BPBD diperlukan.")
    elif level == "BAHAYA":
        return (f"🚨 CURAH HUJAN EKSTREM {rain_mm:.1f} mm terdeteksi di {kec}! "
                f"Potensi kerugian pertanian signifikan untuk {luas:,} ha lahan. "
                f"{'Risiko longsor kritis di lereng.' if 'longsor' in risks else 'Banjir bandang berpotensi terjadi.'} "
                f"Aktifkan protokol darurat segera dan evakuasi warga di zona merah.")
    else:
        return (f"🆘 DARURAT BENCANA di {kec}! Curah hujan {rain_mm:.1f} mm melampaui batas kritis. "
                f"Evakuasi mandiri warga di bantaran sungai dan lereng. "
                f"Semua aktivitas pertanian dihentikan. Koordinasi darurat dengan Pemkab Aceh Besar.")


# ── Bulk Recommendations for All Kecamatan ───────────────────
def generate_bulk_recommendations(
    rain_mm: float,
    forecast_7d_avg: float = 0.0,
) -> List[KecamatanMitigationPlan]:
    """Generate recommendations for all tracked kecamatan."""
    import random, numpy as np
    random.seed(int(rain_mm * 100))
    plans = []
    for kec in KECAMATAN_PROFILE:
        # Slight variation per kecamatan based on profile
        noise    = random.uniform(-8, 12)
        kec_rain = max(0, rain_mm + noise)
        plans.append(generate_recommendations(kec, kec_rain, forecast_7d_avg))
    return plans
