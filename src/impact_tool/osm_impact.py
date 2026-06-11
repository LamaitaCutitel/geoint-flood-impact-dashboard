from __future__ import annotations

from collections import Counter
from typing import Any

from pyproj import Transformer
from shapely.geometry import mapping, shape
from shapely.ops import transform


STATUS_DIRECT = "Intersectat direct"
STATUS_BUFFER = "În buffer de avertizare"
STATUS_UNEXPOSED = "Neexpus"

SYMBOLS = {
    "hospital": "✚",
    "clinic": "✚",
    "pharmacy": "+",
    "fire_station": "♨",
    "police": "◆",
    "school": "▣",
    "kindergarten": "▣",
    "fuel": "⛽",
    "power": "⚡",
    "bridge": "⌒",
    "station": "◆",
    "fallback": "●",
}


def classify_osm_impact(
    layers: dict[str, dict[str, Any]],
    water_geometry: dict[str, Any],
    buffer_meters: int,
) -> dict[str, Any]:
    if not 1 <= buffer_meters <= 1000:
        raise ValueError("Bufferul trebuie să fie între 1 și 1000 m.")
    transformer = Transformer.from_crs("EPSG:4326", "EPSG:3035", always_xy=True)
    reverse = Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True)
    project = lambda geom: transform(transformer.transform, geom)
    unproject = lambda geom: transform(reverse.transform, geom)
    water = project(shape(water_geometry))
    warning_area = water.buffer(buffer_meters)
    classified: dict[str, dict[str, Any]] = {}
    status_counts: Counter[str] = Counter()
    metrics = {
        "buildings_direct": 0,
        "buildings_buffer": 0,
        "buildings_area_m2": 0.0,
        "roads_direct_km": 0.0,
        "roads_buffer_km": 0.0,
        "railways_direct_km": 0.0,
        "railways_buffer_km": 0.0,
        "bridges_direct": 0,
        "bridges_buffer": 0,
        "critical_direct": 0,
        "critical_buffer": 0,
        "road_classes": {},
    }
    for layer_id, collection in layers.items():
        features = []
        for feature in collection.get("features", []):
            source_geometry = shape(feature["geometry"])
            projected = project(source_geometry)
            if projected.intersects(water):
                status = STATUS_DIRECT
            elif projected.intersects(warning_area):
                status = STATUS_BUFFER
            else:
                status = STATUS_UNEXPOSED
            properties = dict(feature.get("properties") or {})
            properties["status"] = status
            properties["distance_to_water_m"] = round(projected.distance(water), 1)
            properties["symbol"] = symbol_for_feature(properties, layer_id)
            features.append({**feature, "properties": properties})
            status_counts[status] += 1
            _accumulate_metrics(metrics, layer_id, projected, water, status, properties)
        classified[layer_id] = {**collection, "features": features}
    return {
        "layers": classified,
        "buffer_geometry": mapping(unproject(warning_area)),
        "metrics": {**metrics, "status_counts": dict(status_counts)},
        "buffer_meters": buffer_meters,
    }


def symbol_for_feature(properties: dict[str, Any], layer_id: str) -> str:
    tags = properties.get("tags") if isinstance(properties.get("tags"), dict) else properties
    amenity = tags.get("amenity") or tags.get("healthcare")
    if amenity in SYMBOLS:
        return SYMBOLS[amenity]
    if layer_id == "osm_bridges":
        return SYMBOLS["bridge"]
    if tags.get("power"):
        return SYMBOLS["power"]
    if tags.get("railway") == "station":
        return SYMBOLS["station"]
    return SYMBOLS["fallback"]


def visible_impact_layers(
    impact: dict[str, Any],
    filters: dict[str, bool],
    critical_only: bool,
) -> dict[str, dict[str, Any]]:
    mapping_ids = {
        "osm_buildings": "buildings",
        "osm_roads": "roads",
        "osm_railways": "railways",
        "osm_bridges": "bridges",
        "osm_critical": "critical",
    }
    result = {}
    for layer_id, collection in impact.get("layers", {}).items():
        if not filters.get(mapping_ids[layer_id], True):
            continue
        if critical_only and layer_id not in {"osm_roads", "osm_bridges", "osm_critical"}:
            continue
        features = [
            feature
            for feature in collection.get("features", [])
            if feature.get("properties", {}).get("status") != STATUS_UNEXPOSED
        ]
        result[layer_id] = {**collection, "features": features}
    return result


def _accumulate_metrics(
    metrics: dict[str, Any],
    layer_id: str,
    geometry: Any,
    water: Any,
    status: str,
    properties: dict[str, Any],
) -> None:
    suffix = "direct" if status == STATUS_DIRECT else "buffer" if status == STATUS_BUFFER else ""
    if not suffix:
        return
    if layer_id == "osm_buildings":
        metrics[f"buildings_{suffix}"] += 1
        if status == STATUS_DIRECT:
            metrics["buildings_area_m2"] += round(geometry.area, 1)
            properties["intersection_type"] = (
                "completă" if geometry.within(water) else "parțială"
            )
    elif layer_id == "osm_roads":
        length_km = round(geometry.length / 1000, 3)
        metrics[f"roads_{suffix}_km"] += length_km
        road_class = properties.get("highway") or "necunoscut"
        class_metrics = metrics["road_classes"].setdefault(
            road_class,
            {"direct_km": 0.0, "buffer_km": 0.0},
        )
        class_metrics[f"{suffix}_km"] = round(
            class_metrics[f"{suffix}_km"] + length_km,
            3,
        )
    elif layer_id == "osm_railways":
        metrics[f"railways_{suffix}_km"] += round(geometry.length / 1000, 3)
    elif layer_id == "osm_bridges":
        metrics[f"bridges_{suffix}"] += 1
    elif layer_id == "osm_critical":
        metrics[f"critical_{suffix}"] += 1
