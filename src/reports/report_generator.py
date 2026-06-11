from __future__ import annotations

import csv
import base64
from datetime import datetime, timezone
import html
import json
from pathlib import Path
from typing import Any

from config.settings import METHODOLOGICAL_NOTE


REPORT_BASENAME = "flood_impact_report"


def build_report_payload(
    analysis_parameters: dict[str, Any],
    metrics: dict[str, Any],
    land_cover_statistics: dict[str, float],
    warnings: list[str] | None = None,
    layer_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "aoi": analysis_parameters.get("aoi_name", "custom AOI"),
        "bbox": analysis_parameters.get("bbox"),
        "before_period": [
            str(analysis_parameters.get("before_start_date")),
            str(analysis_parameters.get("before_end_date")),
        ],
        "after_period": [
            str(analysis_parameters.get("after_start_date")),
            str(analysis_parameters.get("after_end_date")),
        ],
        "event_date": str(analysis_parameters.get("event_date")),
        "polarization": analysis_parameters.get("polarization"),
        "orbit_pass": analysis_parameters.get("orbit_pass"),
        "before_sar_method": analysis_parameters.get("before_sar_method"),
        "after_sar_method": analysis_parameters.get("after_sar_method"),
        "dynamic_world_after_mode": metrics.get(
            "dynamic_world_after_mode", analysis_parameters.get("dynamic_world_after_mode")
        ),
        "dynamic_world_after_period": metrics.get("dynamic_world_after_period"),
        "load_optional_layers": analysis_parameters.get("load_optional_layers"),
        "scale": analysis_parameters.get("scale"),
        "sar_change_threshold": analysis_parameters.get("threshold"),
        "sar_water_mode": analysis_parameters.get("sar_water_mode"),
        "sar_water_threshold": metrics.get(
            "sar_water_threshold", analysis_parameters.get("sar_water_threshold")
        ),
        "smoothing_radius": analysis_parameters.get("smoothing_radius"),
        "scene_counts": {
            "before": metrics.get("scene_count_before", 0),
            "after": metrics.get("scene_count_after", 0),
        },
        "sar_detected_extent_km2": metrics.get("sar_detected_extent_km2", 0.0),
        "sar_water_before_km2": metrics.get("sar_water_before_area_km2", 0.0),
        "sar_water_after_km2": metrics.get("sar_water_after_area_km2", 0.0),
        "sar_new_water_km2": metrics.get("sar_new_water_area_km2", 0.0),
        "sar_persistent_water_km2": metrics.get("sar_persistent_water_area_km2", 0.0),
        "sar_water_loss_km2": metrics.get("sar_water_loss_area_km2", 0.0),
        "dynamic_world_new_water_km2": metrics.get("dynamic_world_new_water_km2", 0.0),
        "sar_dynamic_world_new_water_overlap_km2": metrics.get(
            "sar_dynamic_world_new_water_intersection_km2", 0.0
        ),
        "new_water_only_sar_km2": metrics.get("new_water_only_sar_area_km2", 0.0),
        "new_water_only_dynamic_world_km2": metrics.get(
            "new_water_only_dynamic_world_area_km2", 0.0
        ),
        "osm_operational_impact": {
            "buildings_potentially_affected": metrics.get("osm_buildings_potentially_affected", 0),
            "roads_intersected_km": metrics.get("osm_roads_intersected_km", 0.0),
            "critical_assets": metrics.get("osm_critical_assets", 0),
            "railways_intersected_km": metrics.get("osm_railways_intersected_km", 0.0),
            "bridges": metrics.get("osm_bridges", 0),
            "query_buffer_m": metrics.get("osm_query_buffer_m"),
            "query_limit": metrics.get("osm_query_limit"),
            "elements_returned": metrics.get("osm_elements_returned", 0),
            "query_errors": metrics.get("osm_query_errors", []),
        },
        "permanent_water_removed_km2": metrics.get("permanent_water_removed_km2", 0.0),
        "land_cover_statistics_km2": land_cover_statistics,
        "available_layers": (layer_registry or {}).get("available", []),
        "unavailable_layers": (layer_registry or {}).get("unavailable", []),
        "dominant_class": metrics.get("dominant_land_cover_class", "not available"),
        "processing_time": metrics.get("processing_time"),
        "warnings": warnings or [],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "methodological_note": METHODOLOGICAL_NOTE,
    }


def generate_reports(
    output_dir: Path,
    analysis_parameters: dict[str, Any],
    metrics: dict[str, Any],
    land_cover_statistics: dict[str, float],
    processing_log: list[str],
    warnings: list[str] | None = None,
    layer_registry: dict[str, Any] | None = None,
    processing_log_json: str | None = None,
    osm_layers: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    charts_dir = output_dir / "charts"
    assets_dir = output_dir / "report_assets"
    charts_dir.mkdir(parents=True, exist_ok=True)
    assets_dir.mkdir(parents=True, exist_ok=True)
    payload = build_report_payload(
        analysis_parameters=analysis_parameters,
        metrics=metrics,
        land_cover_statistics=land_cover_statistics,
        warnings=warnings,
        layer_registry=layer_registry,
    )

    json_path = output_dir / f"{REPORT_BASENAME}.json"
    csv_path = output_dir / f"{REPORT_BASENAME}.csv"
    html_path = output_dir / f"{REPORT_BASENAME}.html"
    log_path = output_dir / "processing_log.txt"
    log_json_path = output_dir / "processing_log.json"

    chart_paths = _write_charts(charts_dir, payload)
    osm_export_paths = _write_osm_exports(output_dir, osm_layers or {})

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["metric", "value"])
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            writer.writerow([key, value])

    html_path.write_text(_render_html(payload, chart_paths), encoding="utf-8")
    log_path.write_text("\n".join(processing_log), encoding="utf-8")
    log_json_path.write_text(processing_log_json or "{}", encoding="utf-8")

    paths = {
        "json": json_path,
        "csv": csv_path,
        "html": html_path,
        "log": log_path,
        "log_json": log_json_path,
        "charts_dir": charts_dir,
        "report_assets_dir": assets_dir,
    }
    paths.update(osm_export_paths)
    return paths


def _write_osm_exports(output_dir: Path, osm_layers: dict[str, dict[str, Any]]) -> dict[str, Path]:
    export_map = {
        "osm_buildings": "osm_exposed_buildings.geojson",
        "osm_roads": "osm_intersected_roads.geojson",
        "osm_critical": "osm_critical_facilities.geojson",
    }
    paths: dict[str, Path] = {}
    for layer_id, file_name in export_map.items():
        layer = osm_layers.get(layer_id)
        if not layer or not layer.get("features"):
            continue
        path = output_dir / file_name
        path.write_text(json.dumps(layer, indent=2, ensure_ascii=False), encoding="utf-8")
        paths[layer_id] = path
    return paths


def _write_charts(charts_dir: Path, payload: dict[str, Any]) -> list[Path]:
    charts = [
        (
            "water_summary.svg",
            "Apa noua observata",
            [
                ("SAR", payload.get("sar_new_water_km2", 0.0)),
                ("Dynamic World", payload.get("dynamic_world_new_water_km2", 0.0)),
                ("Overlap", payload.get("sar_dynamic_world_new_water_overlap_km2", 0.0)),
            ],
            "km2",
        ),
        (
            "land_cover_summary.svg",
            "Tipuri de teren intersectate",
            [
                ("Agricol", payload.get("land_cover_statistics_km2", {}).get("crops", 0.0)),
                ("Vegetatie", payload.get("land_cover_statistics_km2", {}).get("vegetation", 0.0)),
                ("Construit", payload.get("land_cover_statistics_km2", {}).get("built", 0.0)),
            ],
            "km2",
        ),
        (
            "osm_summary.svg",
            "Impact operational OSM",
            [
                ("Cladiri", payload.get("osm_operational_impact", {}).get("buildings_potentially_affected", 0)),
                ("Drumuri km", payload.get("osm_operational_impact", {}).get("roads_intersected_km", 0.0)),
                ("Obiective", payload.get("osm_operational_impact", {}).get("critical_assets", 0)),
                ("Cai ferate km", payload.get("osm_operational_impact", {}).get("railways_intersected_km", 0.0)),
            ],
            "",
        ),
    ]
    paths = []
    for file_name, title, values, unit in charts:
        path = charts_dir / file_name
        path.write_text(_bar_chart_svg(title, values, unit), encoding="utf-8")
        paths.append(path)
    return paths


def _bar_chart_svg(title: str, values: list[tuple[str, Any]], unit: str) -> str:
    numeric_values = [float(value or 0) for _, value in values]
    max_value = max(numeric_values) if numeric_values else 0.0
    max_value = max(max_value, 1.0)
    rows = []
    for index, (label, value) in enumerate(values):
        numeric = float(value or 0)
        width = 300 * numeric / max_value
        y = 56 + index * 42
        rows.append(
            f'<text x="20" y="{y + 15}" class="label">{html.escape(label)}</text>'
            f'<rect x="130" y="{y}" width="{width:.1f}" height="22" rx="3" class="bar"/>'
            f'<text x="{140 + width:.1f}" y="{y + 15}" class="value">{numeric:.2f} {html.escape(unit)}</text>'
        )
    height = 92 + len(values) * 42
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="560" height="{height}" viewBox="0 0 560 {height}" role="img">'
        "<style>.title{font:700 18px Arial;fill:#0f172a}.label{font:13px Arial;fill:#334155}"
        ".value{font:12px Arial;fill:#475569}.bar{fill:#0ea5e9}</style>"
        f'<rect width="560" height="{height}" fill="#f8fafc" rx="8"/>'
        f'<text x="20" y="32" class="title">{html.escape(title)}</text>'
        f"{''.join(rows)}</svg>"
    )


def _chart_img(path: Path) -> str:
    data = base64.b64encode(path.read_bytes()).decode("ascii")
    return f'<img src="data:image/svg+xml;base64,{data}" alt="{html.escape(path.stem)}">'


def _fmt(value: Any, default: str = "indisponibil") -> str:
    if value is None or value == "":
        return default
    return html.escape(str(value))


def _metric_card(label: str, value: Any, unit: str = "") -> str:
    unit_html = f"<span>{html.escape(unit)}</span>" if unit else ""
    return f"<div class=\"metric\"><small>{html.escape(label)}</small><strong>{_fmt(value)}</strong>{unit_html}</div>"


def _render_html(payload: dict[str, Any], chart_paths: list[Path] | None = None) -> str:
    osm = payload.get("osm_operational_impact", {})
    layers = payload.get("available_layers", [])
    unavailable = payload.get("unavailable_layers", [])
    warnings = payload.get("warnings", [])
    sources = [
        "Sentinel-1 SAR: COPERNICUS/S1_GRD",
        "Dynamic World: GOOGLE/DYNAMICWORLD/V1",
        "Apa permanenta: JRC Global Surface Water",
        "OpenStreetMap: Overpass API, daca analiza OSM a fost activata",
        "Limite administrative: Eurostat GISCO NUTS 2024",
    ]
    chart_html = "".join(f"<figure>{_chart_img(path)}</figure>" for path in chart_paths or [])
    threshold_rows = {
        "Prag schimbare SAR": payload.get("sar_change_threshold"),
        "Mod apa SAR": payload.get("sar_water_mode"),
        "Prag apa SAR": payload.get("sar_water_threshold"),
        "Raza netezire": payload.get("smoothing_radius"),
        "Scara analiza": payload.get("scale"),
    }
    technical_rows = []
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        technical_rows.append(
            f"<tr><th>{html.escape(str(key))}</th><td>{html.escape(str(value))}</td></tr>"
        )
    return (
        "<!doctype html><html lang=\"ro\"><head><meta charset=\"utf-8\">"
        "<title>Raport GEOINT preliminar</title>"
        "<style>"
        "body{font-family:Arial,sans-serif;margin:0;color:#0f172a;background:#f8fafc;line-height:1.5}"
        "main{max-width:1120px;margin:0 auto;padding:32px 24px 56px;background:white}"
        "header{border-bottom:4px solid #0ea5e9;margin-bottom:24px;padding-bottom:18px}"
        "h1{font-size:32px;margin:.2rem 0}h2{font-size:20px;margin:28px 0 10px;color:#0f172a}"
        ".subtitle{color:#475569}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px}"
        ".metric{border:1px solid #cbd5e1;border-radius:8px;padding:12px;background:#f8fafc}"
        ".metric small{display:block;color:#475569}.metric strong{display:block;font-size:22px;margin-top:4px}"
        "table{border-collapse:collapse;width:100%;margin-top:8px}th,td{border:1px solid #e2e8f0;padding:.55rem;text-align:left;vertical-align:top}"
        "th{width:34%;background:#f1f5f9}ul{margin-top:6px}.note{background:#ecfeff;border-left:4px solid #0ea5e9;padding:12px}"
        ".warn{background:#fff7ed;border-left:4px solid #f97316;padding:10px}.charts{display:grid;grid-template-columns:repeat(auto-fit,minmax(300px,1fr));gap:14px}"
        "figure{margin:0}figure img{max-width:100%;border:1px solid #cbd5e1;border-radius:8px}"
        "details{border:1px solid #cbd5e1;border-radius:8px;padding:10px;background:#f8fafc}"
        "</style></head><body><main>"
        "<header>"
        "<p class=\"subtitle\">Raport offline generat automat</p>"
        "<h1>Raport GEOINT preliminar</h1>"
        f"<p>Zona analizata: <strong>{_fmt(payload.get('aoi'))}</strong> | Data generarii: {_fmt(payload.get('generated_at'))}</p>"
        "</header>"
        "<section><h2>1. Rezumat executiv</h2><div class=\"grid\">"
        f"{_metric_card('Judet / AOI', payload.get('aoi'))}"
        f"{_metric_card('Data evenimentului', payload.get('event_date'))}"
        f"{_metric_card('Apa noua SAR', payload.get('sar_new_water_km2'), 'km2')}"
        f"{_metric_card('Apa noua Dynamic World', payload.get('dynamic_world_new_water_km2'), 'km2')}"
        f"{_metric_card('Overlap SAR x Dynamic World', payload.get('sar_dynamic_world_new_water_overlap_km2'), 'km2')}"
        f"{_metric_card('Apa permanenta eliminata', payload.get('permanent_water_removed_km2'), 'km2')}"
        f"{_metric_card('Cladiri potential expuse', osm.get('buildings_potentially_affected'))}"
        f"{_metric_card('Drumuri intersectate', osm.get('roads_intersected_km'), 'km')}"
        f"{_metric_card('Obiective critice', osm.get('critical_assets'))}"
        f"{_metric_card('Durata procesarii', payload.get('processing_time'))}"
        "</div></section>"
        "<section><h2>2. Zona analizata</h2>"
        f"<p>AOI: {_fmt(payload.get('aoi'))}. BBOX: {_fmt(payload.get('bbox'))}.</p></section>"
        "<section><h2>3. Date utilizate si pereche Sentinel-1</h2><table>"
        f"<tr><th>Perioada de referinta (BEFORE)</th><td>{_fmt(payload.get('before_period'))}</td></tr>"
        f"<tr><th>Perioada dupa eveniment (AFTER)</th><td>{_fmt(payload.get('after_period'))}</td></tr>"
        f"<tr><th>Polarizare</th><td>{_fmt(payload.get('polarization'))}</td></tr>"
        f"<tr><th>Directia orbitei</th><td>{_fmt(payload.get('orbit_pass'))}</td></tr>"
        f"<tr><th>Metoda BEFORE</th><td>{_fmt(payload.get('before_sar_method'))}</td></tr>"
        f"<tr><th>Metoda AFTER</th><td>{_fmt(payload.get('after_sar_method'))}</td></tr>"
        "</table></section>"
        "<section><h2>4. Metodologie SAR</h2><p>Procesarea raster ramane in Google Earth Engine. Rezultatul principal este "
        "apa observata automat prin SAR si extinderea preliminara filtrata, cu mascare JRC unde este activata.</p>"
        "<table>"
        + "".join(f"<tr><th>{html.escape(key)}</th><td>{_fmt(value)}</td></tr>" for key, value in threshold_rows.items())
        + "</table></section>"
        "<section><h2>5. Dynamic World si corelare multisursa</h2><p>Diferentele observate Dynamic World sunt comparate cu apa noua SAR "
        "pentru a separa zonele confirmate de ambele surse de zonele identificate doar de una dintre metode.</p></section>"
        "<section><h2>6. Impact operational OSM</h2><table>"
        f"<tr><th>Cladiri potential expuse</th><td>{_fmt(osm.get('buildings_potentially_affected'))}</td></tr>"
        f"<tr><th>Drumuri intersectate</th><td>{_fmt(osm.get('roads_intersected_km'))} km</td></tr>"
        f"<tr><th>Obiective critice</th><td>{_fmt(osm.get('critical_assets'))}</td></tr>"
        f"<tr><th>Cai ferate intersectate</th><td>{_fmt(osm.get('railways_intersected_km'))} km</td></tr>"
        f"<tr><th>Poduri</th><td>{_fmt(osm.get('bridges'))}</td></tr>"
        f"<tr><th>Buffer interogare</th><td>{_fmt(osm.get('query_buffer_m'))} m</td></tr>"
        "</table></section>"
        f"<section><h2>7. Grafice</h2><div class=\"charts\">{chart_html}</div></section>"
        "<section><h2>8. Limitari</h2><p class=\"note\">Rezultatele reprezinta produse GEOINT preliminare de suport decizional si nu constituie confirmare oficiala din teren.</p>"
        "<ul><li>Rezultatele SAR pot include suprafete netede, sol umed sau umbre radar.</li>"
        "<li>Datele OSM depind de completitudinea contributiilor OpenStreetMap si de disponibilitatea Overpass API.</li>"
        "<li>Dynamic World depinde de disponibilitatea imaginilor optice si de acoperirea cu nori.</li></ul>"
        + ("".join(f"<p class=\"warn\">{html.escape(str(warning))}</p>" for warning in warnings) if warnings else "")
        + "</section>"
        "<section><h2>9. Surse de date</h2><ul>"
        + "".join(f"<li>{html.escape(source)}</li>" for source in sources)
        + "</ul></section>"
        "<section><h2>10. Layere disponibile</h2><ul>"
        + "".join(f"<li>{html.escape(str(layer.get('display_name', layer.get('id'))))}</li>" for layer in layers)
        + "</ul>"
        + ("<h3>Layere indisponibile</h3><ul>" + "".join(f"<li>{html.escape(str(layer.get('display_name', layer.get('id'))))}: {html.escape(str(layer.get('warning', '')))}</li>" for layer in unavailable) + "</ul>" if unavailable else "")
        + "</section>"
        "<section><h2>11. Anexa tehnica</h2><details><summary>Payload complet al raportului</summary>"
        f"<table>{''.join(technical_rows)}</table></details></section>"
        "</main></body></html>"
    )
