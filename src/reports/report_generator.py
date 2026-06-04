from __future__ import annotations

import csv
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
) -> dict[str, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
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

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(["metric", "value"])
        for key, value in payload.items():
            if isinstance(value, (dict, list)):
                value = json.dumps(value, ensure_ascii=False)
            writer.writerow([key, value])

    html_path.write_text(_render_html(payload), encoding="utf-8")
    log_path.write_text("\n".join(processing_log), encoding="utf-8")
    log_json_path.write_text(processing_log_json or "{}", encoding="utf-8")

    return {
        "json": json_path,
        "csv": csv_path,
        "html": html_path,
        "log": log_path,
        "log_json": log_json_path,
    }


def _render_html(payload: dict[str, Any]) -> str:
    rows = []
    for key, value in payload.items():
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        rows.append(
            f"<tr><th>{html.escape(str(key))}</th><td>{html.escape(str(value))}</td></tr>"
        )
    return (
        "<!doctype html><html lang=\"ro\"><head><meta charset=\"utf-8\">"
        "<title>Flood Impact Report</title>"
        "<style>body{font-family:Arial,sans-serif;margin:2rem;line-height:1.45}"
        "table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;"
        "padding:.55rem;text-align:left}th{width:32%;background:#f5f7fa}</style>"
        "</head><body><h1>Raport GEOINT preliminar</h1>"
        "<p>Produs GEOINT preliminar de suport decizional.</p>"
        f"<table>{''.join(rows)}</table></body></html>"
    )
