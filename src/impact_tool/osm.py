from __future__ import annotations

from datetime import date
from typing import Any, Callable

from src.app.osm_impact import (
    _cached_overpass,
    _node_feature,
    _way_feature,
    _with_exposure,
    build_osm_geojson_layers,
    build_overpass_query,
    filter_osm_layers_to_geometry,
)
from src.impact_tool.cache import PersistentCache


OSM_CATEGORIES = ("buildings", "roads", "railways", "bridges", "critical")
LAYER_BY_CATEGORY = {
    "buildings": "osm_buildings",
    "roads": "osm_roads",
    "railways": "osm_railways",
    "bridges": "osm_bridges",
    "critical": "osm_critical",
}
OSM_ATTRIBUTION = "© OpenStreetMap contributors"


def load_osm_categories(
    *,
    analysis_complete: bool,
    aoi_hash: str,
    bbox: list[float],
    geometry: dict[str, Any],
    cache: PersistentCache,
    categories: tuple[str, ...] = OSM_CATEGORIES,
    fetcher: Callable[[str], dict[str, Any]] = _cached_overpass,
    ttl_seconds: int = 7 * 24 * 60 * 60,
) -> dict[str, Any]:
    if not analysis_complete:
        raise RuntimeError("Datele OSM pot fi încărcate numai după analiza SAR.")
    layers: dict[str, dict[str, Any]] = {}
    status: dict[str, dict[str, Any]] = {}
    query_day = date.today().isoformat()
    for category in categories:
        key = cache.key("osm", aoi_hash, category, query_day)
        cached = cache.get("osm", key, ttl_seconds=ttl_seconds)
        try:
            if cached.hit:
                elements = cached.value or []
                source = "cache"
            else:
                payload = fetcher(build_category_query(bbox, category, 5000))
                elements = payload.get("elements", [])
                cache.set("osm", key, elements)
                source = "Overpass API"
            parsed = build_osm_geojson_layers(elements)
            if category == "critical":
                parsed["osm_critical"] = _critical_layer(elements)
            filtered = filter_osm_layers_to_geometry(parsed, geometry)
            layer_id = LAYER_BY_CATEGORY[category]
            layers[layer_id] = filtered[layer_id]
            status[category] = {
                "ok": True,
                "count": len(layers[layer_id].get("features", [])),
                "source": source,
            }
        except Exception as exc:
            status[category] = {"ok": False, "count": 0, "error": str(exc)}
    return {"layers": layers, "status": status, "attribution": OSM_ATTRIBUTION}


def retry_osm_category(**kwargs: Any) -> dict[str, Any]:
    category = kwargs.pop("category")
    return load_osm_categories(categories=(category,), **kwargs)


def build_category_query(bbox: list[float], category: str, limit: int = 5000) -> str:
    if category != "critical":
        return build_overpass_query(bbox, limit, category=category)
    west, south, east, north = bbox
    area = f"{south},{west},{north},{east}"
    return f"""
[out:json][timeout:25][maxsize:536870912];
(
  nwr["amenity"~"^(hospital|clinic|pharmacy|fire_station|police|school|kindergarten|fuel)$"]({area});
  nwr["healthcare"]({area});
  nwr["emergency"]({area});
  nwr["power"]({area});
);
out body {limit};
>;
out skel qt;
"""


def _critical_layer(elements: list[dict[str, Any]]) -> dict[str, Any]:
    critical_amenities = {
        "hospital",
        "clinic",
        "pharmacy",
        "fire_station",
        "police",
        "school",
        "kindergarten",
        "fuel",
    }
    nodes = {
        element["id"]: (float(element["lon"]), float(element["lat"]))
        for element in elements
        if element.get("type") == "node" and "lat" in element and "lon" in element
    }
    collection = {
        "type": "FeatureCollection",
        "display_name": "Obiective critice potențial expuse OSM",
        "color": "#dc2626",
        "features": [],
    }
    for element in elements:
        tags = element.get("tags") or {}
        relevant = (
            tags.get("amenity") in critical_amenities
            or bool(tags.get("healthcare"))
            or bool(tags.get("emergency"))
            or bool(tags.get("power"))
        )
        if not relevant:
            continue
        feature = (
            _node_feature(element)
            if element.get("type") == "node"
            else _way_feature(element, nodes)
            if element.get("type") == "way"
            else None
        )
        if not feature:
            continue
        properties = feature.setdefault("properties", {})
        properties["power"] = tags.get("power")
        collection["features"].append(
            _with_exposure(feature, "high", "obiectiv critic potențial expus")
        )
    return collection
