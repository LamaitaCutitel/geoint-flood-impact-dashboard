from __future__ import annotations

import json
from functools import lru_cache
from math import atan2, cos, radians, sin, sqrt
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


OVERPASS_URL = "https://overpass-api.de/api/interpreter"
OVERPASS_FALLBACK_URLS = (
    OVERPASS_URL,
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.osm.ch/api/interpreter",
    "https://overpass.openstreetmap.ru/api/interpreter",
)
USER_AGENT = "geoint-flood-impact-dashboard/1.0"
CRITICAL_AMENITIES = {"hospital", "clinic", "doctors", "fire_station", "police", "school"}
ROAD_TAGS = {"motorway", "trunk", "primary", "secondary", "tertiary", "residential", "service", "unclassified"}
OSM_QUERY_CATEGORIES = ("buildings", "roads", "critical", "railways", "bridges")


def expanded_bbox(bbox: list[float], buffer_meters: int) -> list[float]:
    west, south, east, north = [float(value) for value in bbox]
    delta_lat = buffer_meters / 111_320
    center_lat = (south + north) / 2
    delta_lon = buffer_meters / max(1, 111_320 * cos(radians(center_lat)))
    return [west - delta_lon, south - delta_lat, east + delta_lon, north + delta_lat]


def build_overpass_query(bbox: list[float], limit: int = 5000, category: str | None = None) -> str:
    west, south, east, north = bbox
    area = f"{south},{west},{north},{east}"
    body = "\n".join(_category_query_lines(area, category))
    return f"""
[out:json][timeout:18][maxsize:536870912];
(
{body}
);
out body {limit};
>;
out skel qt;
"""


def _category_query_lines(area: str, category: str | None) -> list[str]:
    categories = OSM_QUERY_CATEGORIES if category is None else (category,)
    lines: list[str] = []
    if "buildings" in categories:
        lines.append(f'  way["building"]({area});')
    if "roads" in categories:
        lines.append(f'  way["highway"~"^(motorway|trunk|primary|secondary|tertiary|residential|service|unclassified)$"]({area});')
    if "critical" in categories:
        amenities = "|".join(sorted(CRITICAL_AMENITIES))
        lines.append(f'  node["amenity"~"^({amenities})$"]({area});')
        lines.append(f'  way["amenity"~"^({amenities})$"]({area});')
    if "railways" in categories:
        lines.append(f'  way["railway"~"^(rail|tram|light_rail|subway)$"]({area});')
    if "bridges" in categories:
        lines.append(f'  way["bridge"]({area});')
        lines.append(f'  node["bridge"]({area});')
    return lines


def fetch_osm_operational_impact(
    bbox: list[float],
    buffer_meters: int = 500,
    limit: int = 5000,
    fetcher: Any | None = None,
) -> dict[str, Any]:
    return fetch_osm_operational_impact_payload(
        bbox,
        buffer_meters=buffer_meters,
        limit=limit,
        fetcher=fetcher,
    )["metrics"]


def fetch_osm_operational_impact_payload(
    bbox: list[float],
    buffer_meters: int = 500,
    limit: int = 5000,
    fetcher: Any | None = None,
) -> dict[str, Any]:
    query_bbox = expanded_bbox(bbox, buffer_meters)
    if fetcher is not None:
        query = build_overpass_query(query_bbox, limit)
        data = fetcher(query)
        elements = data.get("elements", [])
        query_errors: list[str] = []
    else:
        elements, query_errors = _fetch_overpass_by_category(query_bbox, limit)
    metrics = summarize_osm_elements(elements, buffer_meters, limit)
    metrics["osm_query_errors"] = query_errors
    return {
        "metrics": metrics,
        "layers": build_osm_geojson_layers(elements),
    }


@lru_cache(maxsize=16)
def _cached_overpass(query: str) -> dict[str, Any]:
    payload = urlencode({"data": query}).encode("utf-8")
    last_error: Exception | None = None
    for endpoint in OVERPASS_FALLBACK_URLS:
        try:
            request = Request(endpoint, data=payload, headers={"User-Agent": USER_AGENT})
            with urlopen(request, timeout=20) as response:
                return json.loads(response.read().decode("utf-8"))
        except Exception as exc:
            last_error = exc
    if last_error:
        raise last_error
    return {"elements": []}


def _fetch_overpass_by_category(bbox: list[float], limit: int) -> tuple[list[dict[str, Any]], list[str]]:
    elements_by_key: dict[tuple[str, int], dict[str, Any]] = {}
    errors: list[str] = []
    effective_limit = max(50, min(int(limit), 500))
    for category in OSM_QUERY_CATEGORIES:
        query = build_overpass_query(bbox, effective_limit, category=category)
        try:
            data = _cached_overpass(query)
        except Exception as exc:
            errors.append(f"{category}: {exc}")
            continue
        for element in data.get("elements", []):
            if "id" in element and "type" in element:
                elements_by_key[(str(element["type"]), int(element["id"]))] = element
    return list(elements_by_key.values()), errors


def summarize_osm_elements(elements: list[dict[str, Any]], buffer_meters: int, limit: int) -> dict[str, Any]:
    nodes = {
        element["id"]: (float(element["lat"]), float(element["lon"]))
        for element in elements
        if element.get("type") == "node" and "lat" in element and "lon" in element
    }
    buildings = 0
    road_km = 0.0
    rail_km = 0.0
    critical = 0
    bridges = 0

    for element in elements:
        tags = element.get("tags") or {}
        element_type = element.get("type")
        if "building" in tags and element_type in {"way", "relation"}:
            buildings += 1
        amenity = tags.get("amenity")
        if amenity in CRITICAL_AMENITIES:
            critical += 1
        if "bridge" in tags:
            bridges += 1
        if element_type != "way":
            continue
        length_km = _way_length_km(element.get("nodes") or [], nodes)
        if tags.get("highway") in ROAD_TAGS:
            road_km += length_km
        if tags.get("railway") and tags.get("railway") != "abandoned":
            rail_km += length_km

    return {
        "osm_buildings_potentially_affected": buildings,
        "osm_roads_intersected_km": round(road_km, 3),
        "osm_critical_assets": critical,
        "osm_railways_intersected_km": round(rail_km, 3),
        "osm_bridges": bridges,
        "osm_query_buffer_m": buffer_meters,
        "osm_query_limit": limit,
        "osm_elements_returned": len(elements),
    }


def build_osm_geojson_layers(elements: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    nodes = {
        element["id"]: (float(element["lon"]), float(element["lat"]))
        for element in elements
        if element.get("type") == "node" and "lat" in element and "lon" in element
    }
    layers = {
        "osm_buildings": _feature_collection("Cladiri potential afectate OSM", "#ef4444"),
        "osm_roads": _feature_collection("Drumuri potential afectate OSM", "#f97316"),
        "osm_critical": _feature_collection("Obiective critice potential expuse OSM", "#7c3aed"),
        "osm_railways": _feature_collection("Cai ferate intersectate OSM", "#111827"),
        "osm_bridges": _feature_collection("Poduri intersectate OSM", "#0ea5e9"),
    }
    for element in elements:
        tags = element.get("tags") or {}
        if element.get("type") == "node":
            feature = _node_feature(element)
        elif element.get("type") == "way":
            feature = _way_feature(element, nodes)
        else:
            feature = None
        if not feature:
            continue
        if "building" in tags:
            layers["osm_buildings"]["features"].append(
                _with_exposure(feature, "high", "cladire potential afectata")
            )
        if tags.get("highway") in ROAD_TAGS:
            layers["osm_roads"]["features"].append(
                _with_exposure(feature, "medium", "drum potential afectat")
            )
        if tags.get("railway") and tags.get("railway") != "abandoned":
            layers["osm_railways"]["features"].append(
                _with_exposure(feature, "medium", "cale ferata intersectata")
            )
        if tags.get("amenity") in CRITICAL_AMENITIES:
            layers["osm_critical"]["features"].append(
                _with_exposure(feature, "high", "obiectiv critic potential expus")
            )
        if "bridge" in tags:
            layers["osm_bridges"]["features"].append(
                _with_exposure(feature, "high", "pod intersectat")
            )
    return layers


def _feature_collection(display_name: str, color: str) -> dict[str, Any]:
    return {
        "type": "FeatureCollection",
        "display_name": display_name,
        "color": color,
        "features": [],
    }


def _node_feature(element: dict[str, Any]) -> dict[str, Any] | None:
    if "lat" not in element or "lon" not in element:
        return None
    return {
        "type": "Feature",
        "geometry": {"type": "Point", "coordinates": [float(element["lon"]), float(element["lat"])]},
        "properties": _properties(element),
    }


def _way_feature(element: dict[str, Any], nodes: dict[int, tuple[float, float]]) -> dict[str, Any] | None:
    coordinates = [nodes[node_id] for node_id in element.get("nodes", []) if node_id in nodes]
    if len(coordinates) < 2:
        return None
    is_polygon = len(coordinates) >= 4 and coordinates[0] == coordinates[-1] and "building" in (element.get("tags") or {})
    geometry = {
        "type": "Polygon" if is_polygon else "LineString",
        "coordinates": [coordinates] if is_polygon else coordinates,
    }
    return {"type": "Feature", "geometry": geometry, "properties": _properties(element)}


def _properties(element: dict[str, Any]) -> dict[str, Any]:
    tags = element.get("tags") or {}
    return {
        "osm_id": element.get("id"),
        "name": tags.get("name", "fara nume"),
        "amenity": tags.get("amenity"),
        "highway": tags.get("highway"),
        "railway": tags.get("railway"),
        "building": tags.get("building"),
        "bridge": tags.get("bridge"),
    }


def _with_exposure(feature: dict[str, Any], level: str, label: str) -> dict[str, Any]:
    properties = dict(feature.get("properties") or {})
    properties["exposure_level"] = level
    properties["exposure_label"] = label
    return {**feature, "properties": properties}


def _way_length_km(node_ids: list[int], nodes: dict[int, tuple[float, float]]) -> float:
    total = 0.0
    for previous_id, current_id in zip(node_ids, node_ids[1:]):
        if previous_id in nodes and current_id in nodes:
            total += _haversine_km(nodes[previous_id], nodes[current_id])
    return total


def _haversine_km(start: tuple[float, float], end: tuple[float, float]) -> float:
    lat1, lon1 = start
    lat2, lon2 = end
    radius_km = 6371.0
    d_lat = radians(lat2 - lat1)
    d_lon = radians(lon2 - lon1)
    a = sin(d_lat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(d_lon / 2) ** 2
    return radius_km * 2 * atan2(sqrt(a), sqrt(1 - a))
