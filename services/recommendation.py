# ============================================================
# services/recommendation.py — AI Mitigation Recommendation Engine
# Rekomendasi dibentuk murni berdasarkan STATUS LEVEL klasifikasi
# curah hujan (NORMAL / WASPADA / SIAGA / BAHAYA / BENCANA),
# selaras dengan Bab V (5.14.1–5.14.2) laporan skripsi.
# ============================================================

from dataclasses import dataclass, field
from typing import List, Dict
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import RAIN_LEVELS


# ── Urutan resmi status level — DIAMBIL LANGSUNG dari config.RAIN_LEVELS,
#    yang merupakan satu-satunya sumber kebenaran klasifikasi curah hujan
#    di seluruh platform (acuan: BMKG kategori operasional + BNPB status
#    kedaruratan bencana, lihat sub-bab 2.1.13 & Tabel 5.20 laporan). ──
LEVELS = [lvl["code"] for lvl in RAIN_LEVELS]

LEVEL_INFO = {
    lvl["code"]: {
        "color": lvl["color"],
        "min_mm": lvl["min"],
        "max_mm": None if lvl["max"] >= 9999 else lvl["max"],
    }
    for lvl in RAIN_LEVELS
}

ALERT_TEMPLATE = {
    "NORMAL":  "Kondisi cuaca normal di {kec}.",
    "WASPADA": "Hujan sedang di {kec}. Pantau perkembangan.",
    "SIAGA":   "Hujan lebat di {kec}! Aktifkan protokol siaga banjir.",
    "BAHAYA":  "CURAH HUJAN EKSTREM di {kec}! Risiko banjir dan longsor tinggi.",
    "BENCANA": "🆘 DARURAT: Curah hujan katastrofik di {kec}! Evakuasi segera.",
}


def classify_level(rain_mm: float) -> str:
    """Tentukan status level berdasarkan curah hujan (mm).
    Menggunakan tabel yang sama persis dengan classify_rain() di
    utils/helpers.py — keduanya membaca config.RAIN_LEVELS."""
    for lvl in RAIN_LEVELS:
        if lvl["min"] <= rain_mm < lvl["max"]:
            return lvl["code"]
    return RAIN_LEVELS[-1]["code"]


def _at_least(level: str, floor_level: str) -> bool:
    """True jika `level` sudah mencapai atau melampaui `floor_level`."""
    return LEVELS.index(level) >= LEVELS.index(floor_level)


@dataclass
class Recommendation:
    priority: str          # = status level saat rekomendasi ini dipicu:
                            # "NORMAL" | "WASPADA" | "SIAGA" | "BAHAYA" | "BENCANA"
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


def _is_longsor_prone(profile: dict) -> bool:
    return ("longsor" in profile["main_risk"]
            or profile["topografi"] in ("lereng-pegunungan", "lereng-sedang", "perbukitan-rendah", "bukit-sedang"))


# ── SEKTOR 1: PERTANIAN ───────────────────────────────────────
def _rec_pertanian(level: str, kecamatan: str, profile: dict) -> List[Recommendation]:
    recs = []
    luas = profile["sawah_luas"]
    c = LEVEL_INFO[level]["color"]

    if level == "NORMAL":
        recs.append(Recommendation(
            priority=level, category="Pertanian",
            action="Monitoring Rutin Lahan",
            detail=f"Kondisi curah hujan normal. Lakukan pemantauan rutin kondisi sawah "
                   f"seluas {luas:,} ha di {kecamatan} sebagai bagian dari kesiapsiagaan dini.",
            icon="🌱", color=c,
        ))
        return recs

    if level == "WASPADA":
        recs.append(Recommendation(
            priority=level, category="Pertanian",
            action="Periksa Kesiapan Drainase Sawah",
            detail=f"Curah hujan mulai meningkat. Periksa kondisi saluran tersier dan kesiapan "
                   f"pompa portable pada {luas:,} ha lahan sawah di {kecamatan} sebelum hujan memuncak.",
            icon="💧", color=c,
        ))
        if profile["irigasi_kritis"]:
            recs.append(Recommendation(
                priority=level, category="Pertanian",
                action="Cek Fungsi Pintu Air Irigasi Kritis",
                detail="Pastikan pintu air dan jaringan irigasi utama berfungsi normal "
                       "sebagai antisipasi kenaikan debit air pada level berikutnya.",
                icon="🚰", color=c,
            ))
        return recs

    if level == "SIAGA":
        recs.append(Recommendation(
            priority=level, category="Pertanian",
            action="Percepatan Panen Dini",
            detail=f"Lakukan panen lebih awal untuk sawah yang mendekati matang di {kecamatan} "
                   f"({luas:,} ha). Hujan lebat berpotensi merendam padi dalam waktu dekat.",
            icon="🌾", color=c,
        ))
        if profile["irigasi_kritis"]:
            recs.append(Recommendation(
                priority=level, category="Pertanian",
                action="Buka Pintu Irigasi & Pompanisasi",
                detail="Buka saluran drainase dan aktifkan pompa air untuk mencegah genangan "
                       "lahan sawah. Cek kondisi pintu air irigasi di seluruh sub-petak sawah.",
                icon="💧", color=c,
            ))
        if profile["coastal"]:
            recs.append(Recommendation(
                priority=level, category="Pertanian",
                action="Perkuat Tanggul Tambak Pesisir",
                detail="Perkuat tanggul tambak dan jaring budidaya ikan/udang. Pantau pasang "
                       "surut dan potensi rob. Koordinasi dengan kelompok nelayan dan petambak.",
                icon="🐟", color=c,
            ))
        return recs

    if level == "BAHAYA":
        recs.append(Recommendation(
            priority=level, category="Pertanian",
            action="Percepatan Panen Prioritas Tinggi",
            detail=f"Curah hujan ekstrem — percepat panen seluruh sawah yang memungkinkan di "
                   f"{kecamatan} ({luas:,} ha) sebelum genangan meluas.",
            icon="🌾", color=c,
        ))
        recs.append(Recommendation(
            priority=level, category="Pertanian",
            action="Proteksi Komoditas & Pemindahan Peralatan",
            detail="Pindahkan peralatan pertanian dan hasil panen ke lokasi aman. "
                   "Dokumentasikan kondisi lahan untuk klaim asuransi pertanian jika diperlukan.",
            icon="🚜", color=c,
        ))
        if profile["irigasi_kritis"]:
            recs.append(Recommendation(
                priority=level, category="Pertanian",
                action="Pompanisasi Maksimal Jaringan Irigasi",
                detail="Operasikan seluruh pompa pada kapasitas maksimal untuk mencegah "
                       "kelebihan debit air merusak jaringan irigasi utama.",
                icon="💧", color=c,
            ))
        if profile["coastal"]:
            recs.append(Recommendation(
                priority=level, category="Pertanian",
                action="Penguatan Tanggul Tambak Darurat",
                detail="Lakukan penguatan tanggul tambak secara darurat dan siapkan rencana "
                       "evakuasi hasil budi daya jika tanggul berisiko jebol.",
                icon="🐟", color=c,
            ))
        return recs

    # BENCANA
    recs.append(Recommendation(
        priority=level, category="Pertanian",
        action="Hentikan Aktivitas Pertanian — Fokus Keselamatan",
        detail=f"Seluruh aktivitas pertanian di {kecamatan} dihentikan sementara. "
               f"Keselamatan petani dan warga menjadi prioritas mutlak di atas penyelamatan aset. "
               f"Dokumentasikan kerugian setelah kondisi aman untuk keperluan klaim.",
        icon="🛑", color=c,
    ))
    return recs


# ── SEKTOR 2: INFRASTRUKTUR ───────────────────────────────────
def _rec_infrastruktur(level: str, kecamatan: str, profile: dict) -> List[Recommendation]:
    recs = []
    c = LEVEL_INFO[level]["color"]
    longsor_prone = _is_longsor_prone(profile)
    banjir_prone = "banjir" in profile["main_risk"] or "banjir_pesisir" in profile["main_risk"]

    if level == "NORMAL":
        recs.append(Recommendation(
            priority=level, category="Infrastruktur",
            action="Inspeksi Berkala Saluran Drainase",
            detail="Lakukan inspeksi rutin kondisi saluran drainase dan sarana pengendali "
                   "banjir sebagai bagian dari pemeliharaan preventif.",
            icon="🔍", color=c,
        ))
        return recs

    if level == "WASPADA":
        if banjir_prone:
            recs.append(Recommendation(
                priority=level, category="Infrastruktur",
                action="Pembersihan Saluran Drainase Preventif",
                detail="Bersihkan saluran drainase dari sampah dan sedimentasi sebelum "
                       "intensitas hujan meningkat lebih lanjut.",
                icon="🧹", color=c,
            ))
        if longsor_prone:
            recs.append(Recommendation(
                priority=level, category="Infrastruktur",
                action="Pemeriksaan Awal Kondisi Lereng",
                detail="Periksa tanda-tanda awal pergerakan tanah pada lereng kritis, "
                       "seperti retakan tanah atau rembesan air, sesuai arahan PVMBG.",
                icon="⛰️", color=c,
            ))
        return recs

    if level == "SIAGA":
        if banjir_prone:
            recs.append(Recommendation(
                priority=level, category="Infrastruktur",
                action="Aktivasi Pompa Banjir & Drainase",
                detail="Aktifkan seluruh pompa pengendali banjir. Bersihkan saluran drainase "
                       "dari sampah dan sedimentasi. Koordinasi dengan Dinas PU setempat.",
                icon="🚧", color=c,
            ))
        if longsor_prone:
            recs.append(Recommendation(
                priority=level, category="Infrastruktur",
                action="Pemeriksaan Retakan Tanah & Rambu Peringatan Lereng",
                detail="Pasang rambu peringatan pada lereng kritis dan pantau kemunculan "
                       "retakan berbentuk tapal kuda atau rembesan air bercampur lumpur.",
                icon="⛰️", color=c,
            ))
        return recs

    if level == "BAHAYA":
        if banjir_prone:
            recs.append(Recommendation(
                priority=level, category="Infrastruktur",
                action="Aktivasi Penuh Pompa Banjir & Koordinasi Darurat",
                detail="Operasikan seluruh pompa banjir pada kapasitas maksimal. Koordinasi "
                       "intensif dengan Dinas PU dan BPBD untuk penanganan titik genangan kritis.",
                icon="🚧", color=c,
            ))
        if longsor_prone:
            recs.append(Recommendation(
                priority=level, category="Infrastruktur",
                action="Penutupan Akses Zona Lereng Kritis",
                detail="Larang aktivitas pertanian dan pemukiman sementara di zona lereng >30°. "
                       "Pasang barrier dan lakukan monitoring pergerakan tanah secara intensif.",
                icon="🚫", color=c,
            ))
        return recs

    # BENCANA
    recs.append(Recommendation(
        priority=level, category="Infrastruktur",
        action="Siaga Kerusakan Infrastruktur Kritis",
        detail="Laporkan segera kerusakan tanggul, jembatan, atau saluran utama ke Dinas PU "
               "dan BPBD. Utamakan penanganan titik yang mengancam keselamatan warga.",
        icon="🆘", color=c,
    ))
    if longsor_prone:
        recs.append(Recommendation(
            priority=level, category="Infrastruktur",
            action="Evakuasi Total Zona Lereng",
            detail="Hentikan seluruh aktivitas di zona lereng kritis dan pastikan warga di "
                   "sekitarnya telah dievakuasi ke tempat evakuasi yang aman.",
            icon="⛰️", color=c,
        ))
    return recs


# ── SEKTOR 3: EVAKUASI ────────────────────────────────────────
# Mengacu pada uraian 2.1.14 & 5.14.2 — rekomendasi evakuasi baru
# muncul mulai level SIAGA, dengan intensitas meningkat bertahap.
def _rec_evakuasi(level: str, kecamatan: str, profile: dict) -> List[Recommendation]:
    recs = []
    c = LEVEL_INFO[level]["color"]

    if level in ("NORMAL", "WASPADA"):
        return recs  # belum diperlukan tindakan evakuasi

    if level == "SIAGA":
        recs.append(Recommendation(
            priority=level, category="Evakuasi",
            action="Peringatan Dini & Identifikasi Jalur Evakuasi",
            detail=f"Sebarkan informasi peringatan dini kepada warga di bantaran sungai dan "
                   f"lereng di {kecamatan}. Identifikasi awal jalur dan titik kumpul evakuasi terdekat.",
            icon="📢", color=c,
        ))
        return recs

    if level == "BAHAYA":
        recs.append(Recommendation(
            priority=level, category="Evakuasi",
            action="Kesiapsiagaan Evakuasi Aktif",
            detail=f"Siapkan jalur evakuasi menuju tempat evakuasi sementara di {kecamatan}. "
                   f"Jauhi bantaran sungai dan zona rawan longsor pada wilayah berlereng. "
                   f"Pantau intensif daerah dengan riwayat genangan.",
            icon="🚸", color=c,
        ))
        return recs

    # BENCANA — prioritas tertinggi, mengesampingkan rekomendasi sektor lain
    recs.append(Recommendation(
        priority=level, category="Evakuasi",
        action="Evakuasi Segera — Prioritas Tertinggi",
        detail=f"🆘 Laksanakan evakuasi segera menuju tempat evakuasi akhir di {kecamatan}. "
               f"Jauhi bantaran sungai, lereng curam, dan area dengan riwayat longsor/banjir "
               f"bandang. Gunakan jalur evakuasi bertanda resmi. Koordinasi dengan BPBD, dan "
               f"libatkan Basarnas apabila kapasitas penanganan mandiri warga terlampaui.",
        icon="🆘", color=c,
    ))
    return recs


# ── SEKTOR 4: MONITORING ──────────────────────────────────────
# Selalu ada di semua level (lintas level, lihat 5.14.2 poin 4),
# namun intensitas & isi pesan meningkat sesuai level.
def _rec_monitoring(level: str, kecamatan: str, forecast_7d: float, rain_mm: float) -> List[Recommendation]:
    c = LEVEL_INFO[level]["color"]

    detail_by_level = {
        "NORMAL":  "Pemantauan rutin curah hujan setiap 3 jam sudah memadai pada kondisi ini.",
        "WASPADA": "Tingkatkan frekuensi pemantauan curah hujan dan perbarui data secara berkala.",
        "SIAGA":   "Lakukan pemantauan intensif dan pembaruan informasi cuaca setiap 1–2 jam.",
        "BAHAYA":  "Lakukan pemantauan kontinu (real-time) terhadap perkembangan curah hujan dan dampaknya.",
        "BENCANA": "Aktifkan pemantauan darurat 24 jam berkoordinasi penuh dengan BPBD dan BMKG.",
    }

    recs = [Recommendation(
        priority=level, category="Monitoring",
        action="Pemantauan Cuaca Berkala",
        detail=f"{detail_by_level[level]} Koordinasi dengan BPBD Aceh Besar dan BMKG "
               f"untuk update peringatan dini terkini di {kecamatan}.",
        icon="🌦️", color=c,
    )]

    # Rekomendasi berbasis tren prakiraan — relevan di semua level (lintas level)
    if forecast_7d > rain_mm * 1.2 and forecast_7d >= LEVEL_INFO["WASPADA"]["min_mm"]:
        recs.append(Recommendation(
            priority=level, category="Monitoring",
            action="Pantau Tren Kenaikan Hujan 7 Hari ke Depan",
            detail=f"Model memprediksi rata-rata curah hujan {forecast_7d:.1f} mm dalam 7 hari "
                   f"ke depan, lebih tinggi dari kondisi aktual. Tingkatkan kewaspadaan dan "
                   f"perbarui rencana mitigasi secara berkala.",
            icon="📡", color=c,
        ))
    return recs


# ── Recommendation Engine ─────────────────────────────────────
def generate_recommendations(
    kecamatan: str,
    rain_mm: float,
    forecast_7d: float = 0.0,
) -> KecamatanMitigationPlan:
    """Bentuk rencana mitigasi berbasis status level klasifikasi curah hujan."""

    profile = KECAMATAN_PROFILE.get(kecamatan, _default_profile(kecamatan))
    level = classify_level(rain_mm)
    color = LEVEL_INFO[level]["color"]
    alert = ALERT_TEMPLATE[level].format(kec=kecamatan)

    recs: List[Recommendation] = []
    recs += _rec_pertanian(level, kecamatan, profile)
    recs += _rec_infrastruktur(level, kecamatan, profile)
    recs += _rec_evakuasi(level, kecamatan, profile)
    recs += _rec_monitoring(level, kecamatan, forecast_7d, rain_mm)

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
    import random
    random.seed(int(rain_mm * 100))
    plans = []
    for kec in KECAMATAN_PROFILE:
        # Slight variation per kecamatan based on profile
        noise    = random.uniform(-8, 12)
        kec_rain = max(0, rain_mm + noise)
        plans.append(generate_recommendations(kec, kec_rain, forecast_7d_avg))
    return plans