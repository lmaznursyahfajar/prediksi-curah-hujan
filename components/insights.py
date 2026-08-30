# ============================================================
# components/insights.py — AI Smart Insight Engine
# ============================================================

import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import RAIN_LEVELS
from utils.helpers import classify_rain
from services.recommendation import LEVELS, LEVEL_INFO


def render_insight_cards(
    df: pd.DataFrame,
    forecast: np.ndarray,
    rain_current: float,
) -> None:
    """Insight Cuaca."""
    insights = _generate_insights(df, forecast, rain_current)

    st.markdown("""
    <div style="margin-bottom:16px">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
            <div style="background:linear-gradient(135deg,#3b82f6,#8b5cf6);border-radius:10px;width:36px;height:36px;display:flex;align-items:center;justify-content:center;font-size:18px">🧠</div>
            <div>
                <p style="font-family:'Space Grotesk',sans-serif;font-size:17px;font-weight:700;color:#0f172a;margin:0">Insights Prediksi dan Monitoring</p>
                <p style="font-size:12px;color:#475569;margin:0">Analisis otomatis berdasarkan prediksi & data historis</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    for ins in insights:
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid {ins['border']};border-radius:12px;padding:16px 20px;margin-bottom:12px;position:relative;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.03);">
            <div style="position:absolute;top:0;left:0;right:0;height:3px;background:linear-gradient(90deg,{ins['color']},{ins['color']}44,transparent)"></div>
            <div style="display:flex;align-items:flex-start;gap:14px">
                <div style="background:{ins['color']}15;border:1px solid {ins['color']}33;border-radius:10px;width:40px;height:40px;display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0">{ins['icon']}</div>
                <div style="flex:1">
                    <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                        <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:14px;color:#0f172a">{ins['title']}</span>
                        <span style="background:{ins['color']}15;color:{ins['color']};border:1px solid {ins['color']}33;border-radius:6px;padding:2px 8px;font-size:10px;font-weight:700;font-family:'JetBrains Mono',monospace">{ins['badge']}</span>
                    </div>
                    <p style="font-size:13px;color:#475569;margin:0;line-height:1.7">{ins['text']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)


def _generate_insights(df: pd.DataFrame, forecast: np.ndarray, rain_current: float) -> list:
    insights = []
    level = classify_rain(rain_current)

    # ── Insight 1: Current Status ─────────────────────────────
    trend_7  = df["curah_hujan"].tail(7).mean()
    trend_30 = df["curah_hujan"].tail(30).mean()
    trend_dir = "meningkat" if trend_7 > trend_30 else "menurun"
    trend_pct = abs(trend_7 - trend_30) / max(trend_30, 1) * 100

    insights.append({
        "icon": level["icon"], "title": "Status Curah Hujan Terkini",
        "badge": level["label"], "color": level["color"], "border": f"{level['color']}33",
        "text": (f"Curah hujan saat ini <strong style='color:{level['color']}'>{rain_current:.1f} mm</strong> "
                 f"— kategori <strong>{level['label']}</strong>. "
                 f"Tren 7 hari ({trend_7:.1f} mm) {trend_dir} {trend_pct:.0f}% "
                 f"dibanding rata-rata 30 hari ({trend_30:.1f} mm)."),
    })

    # ── Insight 2: Forecast ───────────────────────────────────
    if forecast is not None and len(forecast) > 0:
        peak_val  = float(np.max(forecast))
        peak_day  = int(np.argmax(forecast)) + 1
        avg_7d    = float(np.mean(forecast[:7]))
        peak_lvl  = classify_rain(peak_val)

        insights.append({
            "icon": "🔮", "title": "Prakiraan 7 Hari ke Depan",
            "badge": f"Puncak H+{peak_day}", "color": peak_lvl["color"],
            "border": f"{peak_lvl['color']}33",
            "text": (f"Model AI memprediksi puncak curah hujan pada <strong>Hari ke-{peak_day}</strong> "
                     f"sebesar <strong style='color:{peak_lvl['color']}'>{peak_val:.1f} mm</strong> "
                     f"({peak_lvl['label']}). Rata-rata 7 hari: <strong>{avg_7d:.1f} mm</strong>. "
                     + ("⚠️ Potensi kejadian ekstrem — aktifkan kesiapsiagaan bencana." if peak_val >= 50
                        else "Kondisi cuaca relatif terkendali dalam rentang prakiraan.")),
        })

    # ── Insight 3: Extreme Detection ─────────────────────────
    extreme_recent = df[df.index >= (df.index.max() - pd.Timedelta(days=30))]
    n_extreme = int((extreme_recent["curah_hujan"] >= 50).sum())
    if n_extreme > 0:
        max_recent = float(extreme_recent["curah_hujan"].max())
        insights.append({
            "icon": "⚡", "title": "Deteksi Kejadian Ekstrem (30 Hari)",
            "badge": f"{n_extreme} Kejadian", "color": "#ef4444", "border": "#ef444433",
            "text": (f"Terdeteksi <strong style='color:#ef4444'>{n_extreme} kejadian hujan ekstrem</strong> "
                     f"(≥50 mm) dalam 30 hari terakhir. Puncak tertinggi: "
                     f"<strong>{max_recent:.1f} mm</strong>. "
                     f"Intensitas ini berkorelasi dengan risiko banjir dan longsor di wilayah hulu."),
        })

    # ── Insight 4: Agricultural Risk ─────────────────────────
    if rain_current >= 20:
        insights.append({
            "icon": "🌾", "title": "Risiko Pertanian Terdeteksi",
            "badge": "AGRI ALERT", "color": "#f59e0b", "border": "#f59e0b33",
            "text": (f"Curah hujan {rain_current:.1f} mm meningkatkan risiko <strong>genangan sawah</strong> "
                     f"di kecamatan dataran rendah (Indrapuri, Ingin Jaya, Sukamakmur). "
                     f"Rekomendasi: aktifkan drainase irigasi, percepat panen padi umur 90+ hari, "
                     f"dan pantau kondisi tanggul sawah."),
        })

    # ── Insight 5: Seasonal ───────────────────────────────────
    month = df.index.max().month
    if month in [11, 12, 1, 2]:
        insights.append({
            "icon": "🌊", "title": "Puncak Musim Hujan Aktif",
            "badge": "MUSIM BASAH", "color": "#3b82f6", "border": "#3b82f633",
            "text": (f"Bulan {['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'][month-1]} "
                     f"merupakan periode puncak curah hujan di Aceh Besar (historis: 248–284 mm/bulan). "
                     f"Tingkatkan frekuensi monitoring dan pastikan sistem drainase berfungsi optimal."),
        })
    elif month in [6, 7, 8]:
        insights.append({
            "icon": "☀️", "title": "Periode Musim Kemarau",
            "badge": "MUSIM KERING", "color": "#22c55e", "border": "#22c55e33",
            "text": (f"Bulan {['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agu','Sep','Okt','Nov','Des'][month-1]} "
                     f"adalah periode curah hujan rendah (historis: 78–94 mm/bulan). "
                     f"Risiko kekeringan pertanian meningkat — pantau ketersediaan air irigasi."),
        })

    return insights

# ── Render Recommendation Cards ───────────────────────────────
def render_mitigation_cards(plan) -> None:
    """Render mitigation recommendation cards, diurutkan dari status level
    paling mendesak (BENCANA) ke paling ringan (NORMAL) — selaras dengan
    klasifikasi 5 level pada services/recommendation.py dan Bab 5.14.1 skripsi."""
    # Urutan tampil: BENCANA → BAHAYA → SIAGA → WASPADA → NORMAL
    priority_order = {lvl: i for i, lvl in enumerate(reversed(LEVELS))}
    sorted_recs = sorted(plan.recommendations, key=lambda r: priority_order.get(r.priority, len(LEVELS)))

    # Warna badge mengikuti warna resmi tiap level (satu sumber kebenaran: LEVEL_INFO)
    priority_colors = {lvl: info["color"] for lvl, info in LEVEL_INFO.items()}

    for rec in sorted_recs:
        p_color = priority_colors.get(rec.priority, "#0f172a")
        
        # HTML dirapatkan (tanpa enter/baris kosong) agar Streamlit merendernya dengan sempurna
        st.markdown(f"""
        <div style="background:#ffffff;border:1px solid #e2e8f0;border-left:4px solid {rec.color};border-radius:12px;padding:18px 20px;margin-bottom:12px;box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05), 0 2px 4px -1px rgba(0,0,0,0.03);">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                <div style="display:flex;align-items:center;gap:12px">
                    <span style="font-size:22px">{rec.icon}</span>
                    <span style="font-family:'Space Grotesk',sans-serif;font-weight:700;font-size:15px;color:#0f172a">{rec.action}</span>
                </div>
                <div style="display:flex;gap:8px">
                    <span style="background:{p_color}15;color:{p_color};border:1px solid {p_color}30;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:700;font-family:'JetBrains Mono',monospace">{rec.priority}</span>
                    <span style="background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;border-radius:6px;padding:3px 10px;font-size:11px;font-weight:600">{rec.category}</span>
                </div>
            </div>
            <p style="font-size:13.5px;color:#475569;margin:0;line-height:1.6;">{rec.detail}</p>
        </div>
        """, unsafe_allow_html=True)
