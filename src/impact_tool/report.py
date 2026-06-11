from __future__ import annotations

import base64
from io import BytesIO
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)
from shapely.geometry import shape

from src.impact_tool.cache import PersistentCache
from src.impact_tool.models import ImpactToolState


REPORT_VERSION = "2.0"
MANDATORY_NOTE = (
    "Rezultatele reprezintă produse GEOINT preliminare de suport decizional "
    "și nu constituie confirmare oficială din teren."
)


def report_filename(state: ImpactToolState) -> str:
    event_date = "data-neprecizata"
    if state.after_scene:
        event_date = str(state.after_scene.get("acquisition_time", ""))[:10]
    county = state.county_name.lower().replace(" ", "_")
    return f"raport_geoint_inundatie_{county}_{event_date}.pdf"


def generate_cached_report(
    state: ImpactToolState,
    cache: PersistentCache | None = None,
) -> tuple[bytes, bool]:
    cache = cache or PersistentCache()
    key = cache.key("reports", state.analysis_hash, state.buffer_meters, REPORT_VERSION)
    cached = cache.get("reports", key)
    if cached.hit and isinstance(cached.value, str):
        return base64.b64decode(cached.value), True
    pdf = generate_report_pdf(state)
    cache.set("reports", key, base64.b64encode(pdf).decode("ascii"))
    return pdf, False


def generate_report_pdf(state: ImpactToolState) -> bytes:
    output = BytesIO()
    document = SimpleDocTemplate(
        output,
        pagesize=A4,
        rightMargin=1.5 * cm,
        leftMargin=1.5 * cm,
        topMargin=1.4 * cm,
        bottomMargin=1.4 * cm,
        title="Raport GEOINT privind impactul unei inundații",
        pageCompression=0,
    )
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="CoverTitle",
            parent=styles["Title"],
            alignment=TA_CENTER,
            fontSize=24,
            leading=30,
            textColor=colors.HexColor("#0f172a"),
            spaceAfter=18,
        )
    )
    story: list[Any] = [
        Spacer(1, 3 * cm),
        Paragraph("Evaluarea impactului unei inundații", styles["CoverTitle"]),
        Paragraph("Analiză multisursă SAR, Dynamic World și OpenStreetMap", styles["Heading2"]),
        Spacer(1, 1 * cm),
        _summary_table(state),
        Spacer(1, 1 * cm),
        Paragraph(MANDATORY_NOTE, styles["Italic"]),
        PageBreak(),
    ]
    _section(story, styles, "1. Rezumat executiv", _executive_summary(state))
    _section(
        story,
        styles,
        "2. Județ și AOI",
        f"Județ analizat: {state.county_name}. Arie activă: "
        f"{'AOI desenat' if state.aoi_active else 'județ complet'}, "
        f"{state.active_area_km2:.2f} km².",
    )
    _section(story, styles, "3. Buffer utilizat", f"Buffer de avertizare: {state.buffer_meters} m.")
    _section(story, styles, "4. Scene Sentinel-1 BEFORE / AFTER", "")
    story.append(_scene_table(state))
    _section(
        story,
        styles,
        "5. Metodologia SAR",
        "Analiza este strict BEFORE / AFTER. Apa nouă evidențiată prin SAR este "
        "diferența dintre apa observată AFTER și apa observată BEFORE, după filtrarea "
        "pixelilor izolați și decuparea la aria activă. Nu este utilizat JRC.",
    )
    _section(story, styles, "6. Rezultatele SAR", "")
    story.append(_metrics_table((state.analysis_results.get("sar") or {}).get("metrics", {})))
    _section(story, styles, "7. Dynamic World", _dynamic_world_summary(state))
    _section(story, styles, "8. Corelare SAR × Dynamic World", _correlation_summary(state))
    _section(story, styles, "9. Impact OSM", _osm_summary(state))
    _section(
        story,
        styles,
        "10. Analiza OSM × Dynamic World",
        "Elementele OSM sunt interpretate ca potențial expuse și necesită verificare în teren.",
    )
    story.append(Paragraph("Corelare OSM × Dynamic World", styles["Heading3"]))
    story.append(Paragraph(_osm_dynamic_world_summary(state), styles["BodyText"]))
    story.append(Paragraph("Completitudine OpenStreetMap", styles["Heading3"]))
    story.append(_osm_status_table(state))
    story.append(PageBreak())
    _section(story, styles, "11. Harta sintetică a impactului inundației", "")
    story.append(Image(_synthetic_map(state), width=17 * cm, height=9.5 * cm))
    _section(story, styles, "12. Grafice", "")
    for title, values in _chart_datasets(state):
        story.append(Paragraph(title, styles["Heading3"]))
        story.append(Image(_bar_chart(title, values), width=15.5 * cm, height=6 * cm))
    _section(story, styles, "13. Tabele detaliate", "")
    story.append(_metrics_table((state.analysis_results.get("osm_impact") or {}).get("metrics", {})))
    _section(
        story,
        styles,
        "14. Limitări",
        "Limitările includ sensibilitatea SAR la geometria de achiziție și rugozitatea "
        "suprafeței, clasificarea automată Dynamic World, completitudinea variabilă OSM, "
        "decalaje temporale și necesitatea verificării în teren.",
    )
    _section(
        story,
        styles,
        "15. Surse",
        "Copernicus Sentinel-1, Google Dynamic World și © OpenStreetMap contributors.",
    )
    _section(story, styles, "16. Anexă tehnică", str(state.analysis_parameters))
    _section(
        story,
        styles,
        "17. Durata procesării",
        f"SAR: {(state.analysis_results.get('sar') or {}).get('duration_seconds', 0)} s.",
    )
    _section(
        story,
        styles,
        "18. Informații cache",
        " | ".join(state.cache_events[-8:]) or "Nu există evenimente cache înregistrate.",
    )
    story.append(Paragraph(MANDATORY_NOTE, styles["Italic"]))
    document.build(story)
    return output.getvalue()


def _section(story: list[Any], styles: Any, title: str, text: str) -> None:
    story.append(Paragraph(title, styles["Heading2"]))
    if text:
        story.append(Paragraph(text, styles["BodyText"]))
    story.append(Spacer(1, 0.25 * cm))


def _summary_table(state: ImpactToolState) -> Table:
    table = Table(
        [
            ["Județ", state.county_name],
            ["Arie activă", f"{state.active_area_km2:.2f} km²"],
            ["Buffer", f"{state.buffer_meters} m"],
            ["Metodă principală", "Apă nouă evidențiată prin SAR"],
        ],
        colWidths=[5 * cm, 9 * cm],
    )
    table.setStyle(_table_style())
    return table


def _scene_table(state: ImpactToolState) -> Table:
    rows = [["Rol", "Data", "Polarizare", "Orbit pass", "Orbită relativă"]]
    for role, scene in (("BEFORE", state.before_scene), ("AFTER", state.after_scene)):
        scene = scene or {}
        rows.append(
            [
                role,
                str(scene.get("acquisition_time", "indisponibil"))[:19],
                scene.get("polarization", "indisponibil"),
                scene.get("orbit_pass", "indisponibil"),
                scene.get("relative_orbit", "indisponibil"),
            ]
        )
    table = Table(rows, repeatRows=1)
    table.setStyle(_table_style())
    return table


def _metrics_table(metrics: dict[str, Any]) -> Table:
    rows = [["Indicator", "Valoare"]]
    rows.extend(
        [[_metric_label(key), _format_value(value)] for key, value in metrics.items()]
        or [["Date", "indisponibile"]]
    )
    table = Table(rows, repeatRows=1, colWidths=[10 * cm, 5 * cm])
    table.setStyle(_table_style())
    return table


METRIC_LABELS = {
    "sar_water_before_area_km2": "Suprafață apă BEFORE (km²)",
    "sar_water_after_area_km2": "Suprafață apă AFTER (km²)",
    "sar_new_water_area_km2": "Extindere preliminară SAR (km²)",
    "buildings_direct": "Clădiri intersectate direct",
    "buildings_buffer": "Clădiri în buffer",
    "buildings_area_m2": "Suprafață totală clădiri (m²)",
    "buildings_overlap_m2": "Suprapunere clădiri-apă (m²)",
    "buildings_complete": "Clădiri complet intersectate",
    "buildings_partial": "Clădiri parțial intersectate",
    "roads_direct_km": "Drumuri intersectate direct (km)",
    "roads_buffer_km": "Drumuri în buffer (km)",
    "railways_direct_km": "Căi ferate intersectate direct (km)",
    "railways_buffer_km": "Căi ferate în buffer (km)",
    "bridges_direct": "Poduri intersectate direct",
    "bridges_buffer": "Poduri în buffer",
    "critical_direct": "Obiective critice intersectate direct",
    "critical_buffer": "Obiective critice în buffer",
}


def _metric_label(key: str) -> str:
    return METRIC_LABELS.get(key, key.replace("_", " ").capitalize())


def _format_value(value: Any) -> str:
    if isinstance(value, dict):
        return "; ".join(
            f"{_metric_label(str(key))}: {_format_value(item)}"
            for key, item in value.items()
        ) or "indisponibil"
    if isinstance(value, float):
        return f"{value:.3f}"
    return str(value)


def _osm_status_table(state: ImpactToolState) -> Table:
    rows = [["Categorie OSM", "Obiecte", "Sursă", "Data cache", "Completitudine"]]
    for category, status in state.osm_status.items():
        rows.append(
            [
                category.capitalize(),
                str(status.get("count", 0)),
                status.get("source", "indisponibil"),
                str(status.get("cache_date", "indisponibil"))[:19],
                status.get("completeness", "necunoscută"),
            ]
        )
    if len(rows) == 1:
        rows.append(["Date OSM", "0", "indisponibil", "indisponibil", "necunoscută"])
    table = Table(rows, repeatRows=1)
    table.setStyle(_table_style())
    return table


def _osm_dynamic_world_summary(state: ImpactToolState) -> str:
    dynamic = state.analysis_results.get("dynamic_world") or {}
    osm = state.analysis_results.get("osm_impact") or {}
    overlap = dynamic.get("metrics", {}).get(
        "sar_dynamic_world_new_water_overlap_area_km2",
        0,
    )
    affected = (osm.get("metrics") or {}).get("status_counts", {})
    return (
        f"Suprapunerea SAR–Dynamic World calculată este {overlap} km². "
        f"Distribuția geometrică a elementelor OSM este: {_format_value(affected)}. "
        "Interpretarea este preliminară și necesită verificare în teren."
    )


def _table_style() -> TableStyle:
    return TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#cbd5e1")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("PADDING", (0, 0), (-1, -1), 6),
        ]
    )


def _executive_summary(state: ImpactToolState) -> str:
    metrics = (state.analysis_results.get("sar") or {}).get("metrics", {})
    return (
        f"Analiza preliminară a evidențiat "
        f"{metrics.get('sar_new_water_area_km2', 0)} km² de apă nouă prin SAR. "
        "Rezultatul este destinat suportului decizional."
    )


def _dynamic_world_summary(state: ImpactToolState) -> str:
    result = state.analysis_results.get("dynamic_world")
    return (
        f"Tranziții către apă: {result.get('transitions', {})}."
        if result
        else "Dynamic World nu a fost disponibil pentru această analiză."
    )


def _correlation_summary(state: ImpactToolState) -> str:
    result = state.analysis_results.get("dynamic_world")
    return (
        f"Indicatori de corelare: {result.get('metrics', {})}."
        if result
        else "Corelarea multisursă nu este disponibilă."
    )


def _osm_summary(state: ImpactToolState) -> str:
    impact = state.analysis_results.get("osm_impact")
    return (
        f"Elemente potențial expuse: {impact.get('metrics', {})}."
        if impact
        else "Datele OSM sunt indisponibile sau parțiale."
    )


def _synthetic_map(state: ImpactToolState) -> BytesIO:
    figure, axis = plt.subplots(figsize=(10, 5.5))
    axis.set_facecolor("#f8fafc")
    _plot_geometry(axis, state.active_geometry, "#2563eb", 1.5, 0.02)
    sar = state.analysis_results.get("sar") or {}
    _plot_geometry(axis, sar.get("new_water_geometry"), "#06b6d4", 1.2, 0.6)
    impact = state.analysis_results.get("osm_impact") or {}
    _plot_geometry(axis, impact.get("buffer_geometry"), "#f59e0b", 1.0, 0.12)
    layer_styles = {
        "osm_buildings": ("#dc2626", 0.8, 0.28),
        "osm_roads": ("#f97316", 1.4, 0.9),
        "osm_railways": ("#7c3aed", 1.2, 0.9),
        "osm_bridges": ("#0ea5e9", 2.0, 0.9),
        "osm_critical": ("#b91c1c", 1.0, 1.0),
    }
    for layer_id, layer in impact.get("layers", {}).items():
        color, width, alpha = layer_styles.get(layer_id, ("#64748b", 1.0, 0.7))
        for feature in layer.get("features", []):
            if feature.get("properties", {}).get("status") == "Neexpus":
                continue
            _plot_osm_feature(axis, feature.get("geometry"), color, width, alpha)
    axis.set_title("Harta sintetică a impactului inundației")
    axis.grid(color="#e2e8f0", linewidth=0.5)
    axis.annotate(
        "N",
        xy=(0.96, 0.92),
        xytext=(0.96, 0.78),
        xycoords="axes fraction",
        arrowprops={"arrowstyle": "-|>", "color": "#0f172a", "lw": 1.5},
        ha="center",
        fontsize=11,
        fontweight="bold",
    )
    x_min, x_max = axis.get_xlim()
    y_min, y_max = axis.get_ylim()
    scale_width = (x_max - x_min) * 0.12
    scale_y = y_min + (y_max - y_min) * 0.06
    scale_x = x_min + (x_max - x_min) * 0.05
    axis.plot([scale_x, scale_x + scale_width], [scale_y, scale_y], color="#0f172a", linewidth=3)
    axis.text(scale_x, scale_y + (y_max - y_min) * 0.02, "scară orientativă", fontsize=7)
    axis.legend(
        handles=[
            Patch(facecolor="#06b6d4", alpha=0.6, label="Apă nouă SAR"),
            Patch(facecolor="#f59e0b", alpha=0.2, label="Buffer"),
            Patch(facecolor="#dc2626", alpha=0.35, label="Clădiri"),
            Line2D([0], [0], color="#f97316", lw=2, label="Drumuri"),
            Line2D([0], [0], color="#7c3aed", lw=2, label="Căi ferate"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#b91c1c", label="Obiective"),
        ],
        loc="lower right",
        fontsize=7,
    )
    output = BytesIO()
    figure.subplots_adjust(left=0.08, right=0.98, bottom=0.12, top=0.9)
    figure.savefig(output, format="png", dpi=140)
    plt.close(figure)
    output.seek(0)
    return output


def _plot_geometry(
    axis: Any,
    geometry: dict[str, Any] | None,
    color: str,
    width: float,
    alpha: float,
) -> None:
    if not geometry:
        return
    item = shape(geometry)
    polygons = [item] if item.geom_type == "Polygon" else list(getattr(item, "geoms", []))
    for polygon in polygons:
        if polygon.geom_type == "Polygon":
            x, y = polygon.exterior.xy
            axis.fill(x, y, facecolor=color, edgecolor=color, linewidth=width, alpha=alpha)


def _plot_osm_feature(
    axis: Any,
    geometry: dict[str, Any] | None,
    color: str,
    width: float,
    alpha: float,
) -> None:
    if not geometry:
        return
    item = shape(geometry)
    parts = list(getattr(item, "geoms", [item]))
    for part in parts:
        if part.geom_type == "Polygon":
            x, y = part.exterior.xy
            axis.fill(x, y, facecolor=color, edgecolor=color, linewidth=width, alpha=alpha)
        elif part.geom_type in {"LineString", "LinearRing"}:
            x, y = part.xy
            axis.plot(x, y, color=color, linewidth=width, alpha=alpha)
        elif part.geom_type == "Point":
            axis.scatter([part.x], [part.y], c=[color], s=28, marker="o", zorder=6)


def _chart_datasets(state: ImpactToolState) -> list[tuple[str, dict[str, float]]]:
    sar = (state.analysis_results.get("sar") or {}).get("metrics", {})
    dynamic = state.analysis_results.get("dynamic_world") or {}
    osm = (state.analysis_results.get("osm_impact") or {}).get("metrics", {})
    return [
        (
            "Suprafețe de apă",
            {
                "SAR": float(sar.get("sar_new_water_area_km2", 0)),
                "Dynamic World": float(dynamic.get("metrics", {}).get("dynamic_world_new_water_area_km2", 0)),
                "Suprapunere": float(dynamic.get("metrics", {}).get("sar_dynamic_world_new_water_overlap_area_km2", 0)),
            },
        ),
        ("Tranziții Dynamic World către apă", dynamic.get("transitions", {})),
        (
            "Elemente OSM",
            {
                "Clădiri": float(osm.get("buildings_direct", 0)),
                "Poduri": float(osm.get("bridges_direct", 0)),
                "Obiective": float(osm.get("critical_direct", 0)),
            },
        ),
        (
            "Infrastructură liniară",
            {
                "Drumuri": float(osm.get("roads_direct_km", 0)),
                "Căi ferate": float(osm.get("railways_direct_km", 0)),
            },
        ),
        (
            "Direct vs buffer",
            {
                "Direct": float(
                    sum(v for key, v in osm.items() if key.endswith("_direct") and isinstance(v, (int, float)))
                ),
                "Buffer": float(
                    sum(v for key, v in osm.items() if key.endswith("_buffer") and isinstance(v, (int, float)))
                ),
            },
        ),
    ]


def _bar_chart(title: str, values: dict[str, float]) -> BytesIO:
    labels = list(values) or ["Fără date"]
    numbers = [float(values[label]) for label in labels] if values else [0.0]
    figure, axis = plt.subplots(figsize=(8.5, 3.2))
    axis.bar(labels, numbers, color="#0ea5e9")
    axis.set_title(title)
    axis.tick_params(axis="x", rotation=22)
    axis.grid(axis="y", color="#e2e8f0", linewidth=0.6)
    output = BytesIO()
    figure.tight_layout()
    figure.savefig(output, format="png", dpi=130)
    plt.close(figure)
    output.seek(0)
    return output
