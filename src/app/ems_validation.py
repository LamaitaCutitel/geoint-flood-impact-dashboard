from __future__ import annotations

import json
from math import cos, radians
from typing import Any


def validation_metrics(sar_area_km2: float, ems_area_km2: float, intersection_km2: float) -> dict[str, float]:
    sar_area = max(0.0, float(sar_area_km2 or 0))
    ems_area = max(0.0, float(ems_area_km2 or 0))
    intersection = min(max(0.0, float(intersection_km2 or 0)), sar_area, ems_area)
    union = max(0.0, sar_area + ems_area - intersection)
    false_positive = max(0.0, sar_area - intersection)
    false_negative = max(0.0, ems_area - intersection)
    precision = intersection / sar_area if sar_area else 0.0
    recall = intersection / ems_area if ems_area else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if precision + recall else 0.0
    return {
        "sar_area_km2": round(sar_area, 4),
        "ems_area_km2": round(ems_area, 4),
        "intersection_km2": round(intersection, 4),
        "union_km2": round(union, 4),
        "iou": round(intersection / union, 4) if union else 0.0,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "f1": round(f1, 4),
        "false_positive_area_km2": round(false_positive, 4),
        "false_negative_area_km2": round(false_negative, 4),
    }


def geojson_area_km2(content: str | bytes) -> float:
    payload = json.loads(content.decode("utf-8") if isinstance(content, bytes) else content)
    return round(sum(_geometry_area_km2(feature.get("geometry")) for feature in _features(payload)), 4)


def _features(payload: dict[str, Any]) -> list[dict[str, Any]]:
    if payload.get("type") == "FeatureCollection":
        return payload.get("features") or []
    if payload.get("type") == "Feature":
        return [payload]
    if payload.get("type") in {"Polygon", "MultiPolygon"}:
        return [{"type": "Feature", "geometry": payload, "properties": {}}]
    return []


def _geometry_area_km2(geometry: dict[str, Any] | None) -> float:
    if not geometry:
        return 0.0
    geometry_type = geometry.get("type")
    coordinates = geometry.get("coordinates") or []
    if geometry_type == "Polygon":
        return _polygon_area_km2(coordinates)
    if geometry_type == "MultiPolygon":
        return sum(_polygon_area_km2(polygon) for polygon in coordinates)
    return 0.0


def _polygon_area_km2(rings: list[Any]) -> float:
    if not rings:
        return 0.0
    outer = abs(_ring_area_km2(rings[0]))
    holes = sum(abs(_ring_area_km2(ring)) for ring in rings[1:])
    return max(0.0, outer - holes)


def _ring_area_km2(ring: list[list[float]]) -> float:
    if len(ring) < 4:
        return 0.0
    mean_lat = sum(float(point[1]) for point in ring) / len(ring)
    meters_per_degree_lon = 111_320 * cos(radians(mean_lat))
    meters_per_degree_lat = 111_320
    projected = [
        (float(lon) * meters_per_degree_lon, float(lat) * meters_per_degree_lat)
        for lon, lat, *_ in ring
    ]
    area_sqm = 0.0
    for (x1, y1), (x2, y2) in zip(projected, projected[1:]):
        area_sqm += x1 * y2 - x2 * y1
    return area_sqm / 2 / 1_000_000
