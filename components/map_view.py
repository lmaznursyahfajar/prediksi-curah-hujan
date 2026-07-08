# ============================================================
# components/map_view.py — Full GIS Choropleth Map Engine
# Menampilkan batas wilayah seluruh kecamatan Aceh Besar
# Choropleth: Monitoring, Pertanian, Bencana
# ============================================================

import folium
from folium.plugins import HeatMap, Fullscreen, MiniMap
import geopandas as gpd
import pandas as pd
import numpy as np
import json
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from config import LOCATION

# ── Mapping: NAME_3 (GeoJSON) → nama kecamatan di data ───────
# GeoJSON menggunakan nama tanpa spasi (CamelCase)
NAME3_TO_KEC = {
    "Baitussalam":     "Baitussalam",
    "BlangBintang":    "Blang Bintang",
    "DarulImarah":     "Darul Imarah",
    "DarulKamal":      "Darul Kamal",
    "Darussalam":      "Darussalam",
    "Indrapuri":       "Indrapuri",
    "InginJaya":       "Ingin Jaya",
    "KotaJantho":      "Kota Jantho",
    "KruengBaronaJaya":"Krueng Barona Jaya",
    "KutaBaro":        "Kuta Baro",
    "KutaCotGlie":     "Kuta Cot Glie",
    "KutaMalaka":      "Kuta Malaka",
    "LembahSeulawah":  "Lembah Seulawah",
    "Leupung":         "Leupung",
    "Lhoknga":         "Lhoknga",
    "Lhoong":          "Lhoong",
    "MesjidRaya":      "Mesjid Raya",
    "Montasik":        "Montasik",
    "PeukanBada":      "Peukan Bada",
    "PuloAceh":        "Pulo Aceh",
    "Seulimeum":       "Seulimeum",
    "SimpangTiga":     "Simpang Tiga",
    "SukaMakmur":      "Sukamakmur",
}

# ── Base map ──────────────────────────────────────────────────
def _base_map(zoom: int = None) -> folium.Map:
    m = folium.Map(
        location=LOCATION["map_center"],
        zoom_start=zoom or LOCATION["zoom"],
        tiles="OpenStreetMap",
    )
    folium.TileLayer(
        tiles="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
        name="Dark Mode", attr="© CARTO", subdomains="abcd",
    ).add_to(m)
    folium.TileLayer("OpenStreetMap", name="Street Map").add_to(m)
    return m


# ── Color scales ──────────────────────────────────────────────
def _rain_color(mm: float) -> str:
    if mm < 5:    return "#22c55e"
    if mm < 20:   return "#eab308"
    if mm < 50:   return "#f97316"
    if mm < 100:  return "#ef4444"
    return "#7f1d1d"

def _agri_color(luas: float, max_luas: float) -> str:
    pct = luas / max(max_luas, 1)
    if pct > 0.75: return "#064e3b"
    if pct > 0.50: return "#065f46"
    if pct > 0.25: return "#10b981"
    return "#34d399"

def _disaster_color(n: int) -> str:
    if n >= 25: return "#ef4444"
    if n >= 15: return "#f97316"
    if n >= 10: return "#eab308"
    return "#22c55e"

def _terpapar_color(ha: float) -> str:
    if ha >= 3000: return "#7f1d1d"
    if ha >= 2000: return "#ef4444"
    if ha >= 1000: return "#f97316"
    if ha > 0:     return "#eab308"
    return "#94a3b8"

def _opacity(val: float, min_val: float, max_val: float,
             lo: float = 0.25, hi: float = 0.80) -> float:
    if max_val <= min_val:
        return 0.5
    return lo + (hi - lo) * (val - min_val) / (max_val - min_val)


# ══════════════════════════════════════════════════════════════
# 1. MONITORING MAP — choropleth curah hujan
# ══════════════════════════════════════════════════════════════
def build_monitoring_map(
    gdf,
    rain_mm: float,
    df_recent: pd.DataFrame = None,
) -> folium.Map:
    m = _base_map()

    if gdf is not None:
        _add_choropleth_monitoring(m, gdf, rain_mm)

    # Rainfall heatmap overlay
    if df_recent is not None and len(df_recent) > 0:
        rain_vals = df_recent["curah_hujan"].tail(30).values
        rmax = rain_vals.max() + 1e-6
        heat_data = [
            [LOCATION["map_center"][0] + np.random.uniform(-0.18, 0.18),
             LOCATION["map_center"][1] + np.random.uniform(-0.18, 0.18),
             float(v / rmax)]
            for v in rain_vals if v > 0
        ]
        if heat_data:
            HeatMap(heat_data, name="Heatmap Curah Hujan", radius=30,
                    gradient={0.2:"#3b82f6", 0.5:"#f59e0b", 1.0:"#ef4444"},
                    blur=18, min_opacity=0.25).add_to(m)

    # Station marker
    rain_color = _rain_color(rain_mm)
    popup_html = f"""<div style="font-family:sans-serif;padding:10px">
        <b style="color:{rain_color}">🌧️ Stasiun Klimatologi Aceh Besar</b><hr style="margin:6px 0">
        <table style="font-size:12px"><tr><td>Curah Hujan</td>
        <td><b style="color:{rain_color}">{rain_mm:.2f} mm</b></td></tr></table>
    </div>"""
    folium.CircleMarker(location=LOCATION["map_center"], radius=14,
        color=rain_color, fill=True, fill_color=rain_color, fill_opacity=0.9, weight=2,
        popup=folium.Popup(popup_html, max_width=200),
        tooltip="Stasiun Klimatologi Aceh Besar").add_to(m)

    folium.LayerControl(position="topright", collapsed=False).add_to(m)
    Fullscreen(position="topright").add_to(m)
    _add_legend_rain(m)
    return m


def _add_choropleth_monitoring(m, gdf, rain_mm):
    rain_color = _rain_color(rain_mm)

    def style_fn(feature):
        return {
            "fillColor":   rain_color,
            "color":       "#60a5fa",
            "weight":      1.2,
            "fillOpacity": 0.35,
            "dashArray":   "3",
        }

    def highlight_fn(feature):
        return {
            "fillColor":   rain_color,
            "color":       "#ffffff",
            "weight":      2.5,
            "fillOpacity": 0.6,
        }

    folium.GeoJson(
        gdf.__geo_interface__,
        name="Batas Kecamatan",
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["NAME_3"],
            aliases=["Kecamatan:"],
            style="font-family:sans-serif;font-size:12px;padding:6px;",
            localize=True,
        ),
    ).add_to(m)


# ══════════════════════════════════════════════════════════════
# 2. AGRICULTURE MAP — choropleth luas sawah
# ══════════════════════════════════════════════════════════════
def build_agriculture_map(
    gdf,
    df_agri: pd.DataFrame,
) -> folium.Map:
    m = _base_map()

    if gdf is None:
        return m

    # Buat lookup: nama kecamatan → data
    agri_lookup = df_agri.set_index("kecamatan").to_dict("index")
    max_luas    = df_agri["luas_sawah"].max()
    max_prod    = df_agri["produksi_padi"].max()

    def style_fn(feature):
        name3 = feature["properties"].get("NAME_3", "")
        kec   = NAME3_TO_KEC.get(name3, name3)
        row   = agri_lookup.get(kec)
        if row:
            color = _agri_color(row["luas_sawah"], max_luas)
            opac  = _opacity(row["luas_sawah"], 0, max_luas, 0.30, 0.85)
        else:
            color, opac = "#374151", 0.20
        return {
            "fillColor":   color,
            "color":       "#6ee7b7",
            "weight":      1.2,
            "fillOpacity": opac,
        }

    def highlight_fn(feature):
        return {"color":"#ffffff","weight":2.5,"fillOpacity":0.75}

    # Tooltip + Popup
    def popup_fn(feature):
        name3 = feature["properties"].get("NAME_3", "")
        kec   = NAME3_TO_KEC.get(name3, name3)
        row   = agri_lookup.get(kec)
        if row:
            html = f"""<div style="font-family:sans-serif;padding:10px;min-width:180px">
                <b style="color:#10b981">🌾 {kec}</b><hr style="margin:6px 0">
                <table style="font-size:12px;width:100%">
                  <tr><td style="color:#666">Luas Sawah</td>
                      <td style="font-weight:bold;text-align:right">{row['luas_sawah']:,} ha</td></tr>
                  <tr><td style="color:#666">Produksi Padi</td>
                      <td style="font-weight:bold;text-align:right">{row['produksi_padi']:,} ton</td></tr>
                  <tr><td style="color:#666">Produktivitas</td>
                      <td style="font-weight:bold;text-align:right">{row['produktivitas']:.2f} ton/ha</td></tr>
                </table></div>"""
        else:
            html = f"<div style='padding:8px'><b>{kec}</b><br><i>Data tidak tersedia</i></div>"
        return html

    # GeoJson layer dengan popup dinamis
    geo_layer = folium.GeoJson(
        gdf.__geo_interface__,
        name="Luas Sawah",
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["NAME_3"],
            aliases=["Kecamatan:"],
            style="font-family:sans-serif;font-size:12px;padding:6px;",
        ),
    )
    # Tambahkan popup per feature
    for _, row_gdf in gdf.iterrows():
        name3 = row_gdf.get("NAME_3", "")
        kec   = NAME3_TO_KEC.get(name3, name3)
        data  = agri_lookup.get(kec)
        if data:
            # Centroid untuk popup marker
            try:
                centroid = row_gdf.geometry.centroid
                folium.Marker(
                    location=[centroid.y, centroid.x],
                    icon=folium.DivIcon(
                        html=f"""<div style="font-size:9px;font-family:sans-serif;
                                    color:white;font-weight:600;text-align:center;
                                    text-shadow:1px 1px 2px black;white-space:nowrap">
                                {data['luas_sawah']:,}</div>""",
                        icon_size=(60, 16), icon_anchor=(30, 8),
                    ),
                    popup=folium.Popup(popup_fn({"properties":{"NAME_3":name3}}), max_width=220),
                ).add_to(m)
            except Exception:
                pass

    geo_layer.add_to(m)
    folium.LayerControl(position="topright", collapsed=False).add_to(m)
    Fullscreen(position="topright").add_to(m)
    _add_legend_agri(m, max_luas)
    return m


# ══════════════════════════════════════════════════════════════
# 3. DISASTER MAP — choropleth berdasarkan pilihan kolom
# ══════════════════════════════════════════════════════════════
def build_disaster_map(
    gdf,
    df_disaster: pd.DataFrame,
    color_by: str = "total_kejadian",
) -> folium.Map:
    m = _base_map()

    if gdf is None:
        return m

    dis_lookup = df_disaster.set_index("kecamatan").to_dict("index")

    # Tentukan fungsi warna berdasarkan pilihan
    col_max = df_disaster[color_by].max() if color_by in df_disaster.columns else 1

    def _get_color(val: float) -> str:
        if color_by == "total_kejadian":
            return _disaster_color(int(val))
        elif color_by in ("lingkungan_banjir_ha","lingkungan_longsor_ha","total_terpapar_ha"):
            return _terpapar_color(val)
        return _disaster_color(int(val))

    def style_fn(feature):
        name3 = feature["properties"].get("NAME_3", "")
        kec   = NAME3_TO_KEC.get(name3, name3)
        row   = dis_lookup.get(kec)
        if row and color_by in row:
            val   = float(row[color_by])
            color = _get_color(val)
            opac  = _opacity(val, 0, col_max, 0.25, 0.80)
        else:
            color, opac = "#374151", 0.15
        return {
            "fillColor":   color,
            "color":       "#fca5a5",
            "weight":      1.2,
            "fillOpacity": opac,
        }

    def highlight_fn(feature):
        return {"color":"#ffffff","weight":2.5,"fillOpacity":0.80}

    # Layer utama
    folium.GeoJson(
        gdf.__geo_interface__,
        name="Batas Kecamatan",
        style_function=style_fn,
        highlight_function=highlight_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["NAME_3"],
            aliases=["Kecamatan:"],
            style="font-family:sans-serif;font-size:12px;padding:6px;",
        ),
    ).add_to(m)

    # Label + popup per kecamatan (centroid)
    for _, row_gdf in gdf.iterrows():
        name3 = row_gdf.get("NAME_3", "")
        kec   = NAME3_TO_KEC.get(name3, name3)
        row   = dis_lookup.get(kec)
        if row is None:
            continue
        try:
            centroid = row_gdf.geometry.centroid
            cx, cy   = centroid.x, centroid.y
            val      = float(row.get(color_by, 0))
            color    = _get_color(val)
            unit     = " ha" if "ha" in color_by else " kejadian"

            popup_html = f"""
            <div style="font-family:sans-serif;padding:10px;min-width:200px">
                <b style="color:{color}">🚨 {kec}</b><hr style="margin:6px 0">
                <table style="font-size:12px;width:100%">
                  <tr><td style="color:#666">Total Kejadian</td>
                      <td style="font-weight:bold;text-align:right">{row['total_kejadian']}</td></tr>
                  <tr><td style="color:#666">Banjir</td>
                      <td style="font-weight:bold;text-align:right">{row['kejadian_banjir']}</td></tr>
                  <tr><td style="color:#666">Longsor</td>
                      <td style="font-weight:bold;text-align:right">{row['kejadian_longsor']}</td></tr>
                  <tr><td style="color:#3b82f6">Terpapar Banjir</td>
                      <td style="font-weight:bold;text-align:right">{row.get('lingkungan_banjir_ha',0):,.0f} ha</td></tr>
                  <tr><td style="color:#8b5cf6">Terpapar Longsor</td>
                      <td style="font-weight:bold;text-align:right">{row.get('lingkungan_longsor_ha',0):,.0f} ha</td></tr>
                </table>
            </div>"""

            # Label nilai di tengah poligon
            label = f"{val:,.0f}{unit}" if val > 0 else "—"
            folium.Marker(
                location=[cy, cx],
                icon=folium.DivIcon(
                    html=f"""<div style="font-size:9px;font-family:sans-serif;
                                color:white;font-weight:700;text-align:center;
                                text-shadow:1px 1px 3px rgba(0,0,0,0.8);
                                white-space:nowrap">{label}</div>""",
                    icon_size=(80, 16), icon_anchor=(40, 8),
                ),
                popup=folium.Popup(popup_html, max_width=230),
            ).add_to(m)
        except Exception:
            pass

    folium.LayerControl(position="topright", collapsed=False).add_to(m)
    Fullscreen(position="topright").add_to(m)
    _add_legend_disaster(m, color_by)
    return m


# ══════════════════════════════════════════════════════════════
# LEGENDS
# ══════════════════════════════════════════════════════════════
def _add_legend_rain(m):
    html = """<div style="position:fixed;bottom:25px;left:12px;z-index:9999;
        background:rgba(255,255,255,0.93);border:1px solid #ccc;
        border-radius:10px;padding:12px 15px;font-family:sans-serif;min-width:155px;
        box-shadow:0 2px 8px rgba(0,0,0,0.2)">
        <b style="font-size:12px;color:#333">INTENSITAS HUJAN</b><br><br>"""
    for c,l in [("#22c55e","Sangat Ringan <5mm"),("#eab308","Ringan 5–20mm"),
                ("#f97316","Sedang 20–50mm"),("#ef4444","Lebat 50–100mm"),
                ("#7f1d1d","Ekstrem >100mm")]:
        html += f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:5px">' \
                f'<div style="width:14px;height:14px;border-radius:3px;background:{c};flex-shrink:0"></div>' \
                f'<span style="font-size:11px">{l}</span></div>'
    html += "</div>"
    m.get_root().html.add_child(folium.Element(html))


def _add_legend_agri(m, max_luas: float):
    html = """<div style="position:fixed;bottom:25px;left:12px;z-index:9999;
        background:rgba(255,255,255,0.93);border:1px solid #ccc;
        border-radius:10px;padding:12px 15px;font-family:sans-serif;min-width:165px;
        box-shadow:0 2px 8px rgba(0,0,0,0.2)">
        <b style="font-size:12px;color:#333">LUAS SAWAH</b><br>
        <span style="font-size:10px;color:#666">(ha — lebih gelap = lebih luas)</span><br><br>"""
    thresholds = [
        ("#064e3b", f"> {max_luas*0.75:,.0f} ha"),
        ("#065f46", f"{max_luas*0.5:,.0f}–{max_luas*0.75:,.0f} ha"),
        ("#10b981", f"{max_luas*0.25:,.0f}–{max_luas*0.5:,.0f} ha"),
        ("#34d399", f"< {max_luas*0.25:,.0f} ha"),
        ("#374151", "Data tidak tersedia"),
    ]
    for c, l in thresholds:
        html += f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:5px">' \
                f'<div style="width:14px;height:14px;border-radius:3px;background:{c};flex-shrink:0"></div>' \
                f'<span style="font-size:11px">{l}</span></div>'
    html += "</div>"
    m.get_root().html.add_child(folium.Element(html))


def _add_legend_disaster(m, color_by: str):
    if "ha" in color_by:
        title = "LINGKUNGAN TERPAPAR (Ha)"
        items = [
            ("#7f1d1d","≥ 3.000 ha"),("#ef4444","2.000–3.000 ha"),
            ("#f97316","1.000–2.000 ha"),("#eab308","< 1.000 ha"),("#94a3b8","Tidak ada"),
        ]
    else:
        title = "TOTAL KEJADIAN BENCANA"
        items = [
            ("#ef4444","Sangat Sering ≥ 25"),("#f97316","Sering 15–25"),
            ("#eab308","Sedang 10–15"),("#22c55e","Jarang < 10"),
            ("#374151","Data tidak tersedia"),
        ]
    html = f"""<div style="position:fixed;bottom:25px;left:12px;z-index:9999;
        background:rgba(255,255,255,0.93);border:1px solid #ccc;
        border-radius:10px;padding:12px 15px;font-family:sans-serif;min-width:185px;
        box-shadow:0 2px 8px rgba(0,0,0,0.2)">
        <b style="font-size:12px;color:#333">{title}</b><br><br>"""
    for c, l in items:
        html += f'<div style="display:flex;align-items:center;gap:7px;margin-bottom:5px">' \
                f'<div style="width:14px;height:14px;border-radius:3px;background:{c};flex-shrink:0"></div>' \
                f'<span style="font-size:11px">{l}</span></div>'
    html += "</div>"
    m.get_root().html.add_child(folium.Element(html))