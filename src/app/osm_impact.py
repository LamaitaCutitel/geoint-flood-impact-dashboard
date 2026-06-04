from __future__ import annotations

import json
from functools import lru_cache
from math import atan2, cos, radians, sin, sqrt
from typing import Any
from urllib.parse import urlencode
from urllib.request import urlopen


OVERPASS_URL = "https://overpass-api.de/api/interpreter"
CRITICAL_AMENITIES = {"hospital", "clinic", "doctors", "fire_station", "police", "school"}
ROAD_TAGS = {"motorway", "trunk", "primary", "secondary", "tertiary", "residential", "service", "unclassified"}


def expanded_bbox(bbox: list[float], buffer_meters: int) -> list[float]:
    west, south, east, north = [float(value) for value in bbox]
    delta_lat = buffer_meters / 111_320
    center_lat = (south + north) / 2
    delta_lon = buffer_meters / max(1, 111_320 * cos(radians(center_lat)))
    return [west - delta_lon, south - delta_lat, east + delta_lon, north + delta_lat]


def build_overpass_query(bbox: list[float], limit: int = 5000) -> str:
    west, south, east, north = bbox
    area = f"{south},{west},{north},{east}"
    return f"""
[out:json][timeout:25][maxsize:1073741824];
(
  way["building"]({area});
  relation["building"]({area});
  way["highway"]({area});
  way["railway"]({area});
  node["amenity"]({area});
  way["amenity"]({area});
  node["bridge"]({area});
  way["bridge"]({area});
);
out body {limit};
>;
out skel qt;
"""


def fetch_osm_operational_impact(
    bbox: list[float],
    buffer_meters: int = 500,
    limit: int = 5000,
    fetcher: Any | None = None,
) -> dict[str, Any]:
    query_bbox = expanded_bbox(bbox, buffer_meters)
    query = build_overpass_query(query_bbox, limit)
    data = _cached_overpass(query) if fetcher is None else fetcher(query)
    return summarize_osm_elements(data.get("elements", []), buffer_meters, limit)


@lru_cache(maxsize=16)
def _cached_overpass(query: str) -> dict[str, Any]:
    payload = urlencode({"data": query}).encode("utf-8")
    with urlopen(OVERPASS_URL, data=payload, timeout=35) as response:
        return json.loads(response.read().decode("utf-8"))


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
