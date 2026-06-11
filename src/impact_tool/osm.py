from __future__ import annotations

from datetime import date, datetime, timezone
import re
from typing import Any, Callable
from shapely.geometry import LineString, mapping
from shapely.ops import polygonize, unary_union

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
OSM_LIMITS = {
    "buildings": 50000,
    "roads": 25000,
    "railways": 10000,
    "bridges": 10000,
    "critical": 15000,
}
OVERPASS_TIMEOUT_SECONDS = 60
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
    for category in categories:
        try:
            fetched = _load_category_tiles(
                bbox=bbox,
                category=category,
                cache=cache,
                fetcher=fetcher,
                ttl_seconds=ttl_seconds,
            )
            elements = fetched["elements"]
            parsed = build_osm_geojson_layers(elements)
            _append_relation_features(parsed, elements)
            if category == "critical":
                parsed["osm_critical"] = _critical_layer(elements)
            filtered = filter_osm_layers_to_geometry(parsed, geometry)
            layer_id = LAYER_BY_CATEGORY[category]
            layers[layer_id] = filtered[layer_id]
            status[category] = {
                "ok": True,
                "count": len(layers[layer_id].get("features", [])),
                "source": fetched["source"],
                "cache_date": fetched["cache_date"],
                "completeness": fetched["completeness"],
                "warnings": fetched["warnings"],
            }
        except Exception as exc:
            status[category] = {"ok": False, "count": 0, "error": str(exc)}
    return {"layers": layers, "status": status, "attribution": OSM_ATTRIBUTION}


def retry_osm_category(**kwargs: Any) -> dict[str, Any]:
    category = kwargs.pop("category")
    return load_osm_categories(categories=(category,), **kwargs)


def build_category_query(
    bbox: list[float],
    category: str,
    limit: int | None = None,
) -> str:
    limit = limit or OSM_LIMITS[category]
    if category != "critical":
        return re.sub(
            r"\[timeout:\d+\]",
            f"[timeout:{OVERPASS_TIMEOUT_SECONDS}]",
            build_overpass_query(bbox, limit, category=category),
        )
    west, south, east, north = bbox
    area = f"{south},{west},{north},{east}"
    return f"""
[out:json][timeout:{OVERPASS_TIMEOUT_SECONDS}][maxsize:536870912];
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


def split_bbox(bbox: list[float]) -> list[list[float]]:
    west, south, east, north = bbox
    middle_x = (west + east) / 2
    middle_y = (south + north) / 2
    return [
        [west, south, middle_x, middle_y],
        [middle_x, south, east, middle_y],
        [west, middle_y, middle_x, north],
        [middle_x, middle_y, east, north],
    ]


def deduplicate_elements(elements: list[dict[str, Any]]) -> list[dict[str, Any]]:
    unique: dict[tuple[str, Any], dict[str, Any]] = {}
    for element in elements:
        key = (str(element.get("type", "")), element.get("id"))
        unique[key] = element
    return list(unique.values())


def _load_category_tiles(
    *,
    bbox: list[float],
    category: str,
    cache: PersistentCache,
    fetcher: Callable[[str], dict[str, Any]],
    ttl_seconds: int,
) -> dict[str, Any]:
    limit = OSM_LIMITS[category]
    query_day = date.today().isoformat()
    warnings: list[str] = []
    sources: set[str] = set()
    cache_dates: list[str] = []

    def fetch_tile(tile_bbox: list[float], depth: int = 0) -> tuple[list[dict[str, Any]], bool]:
        key = cache.key("osm", category, tile_bbox, query_day)
        cached = cache.get("osm", key, ttl_seconds=ttl_seconds)
        if cached.hit:
            value = cached.value or {}
            if isinstance(value, list):
                elements = value
                cached_at = query_day
            else:
                elements = value.get("elements", [])
                cached_at = value.get("fetched_at", query_day)
            sources.add("cache")
            cache_dates.append(cached_at)
        else:
            payload = fetcher(build_category_query(tile_bbox, category, limit))
            elements = payload.get("elements", [])
            cached_at = datetime.now(timezone.utc).isoformat()
            cache.set(
                "osm",
                key,
                {"elements": elements, "fetched_at": cached_at, "bbox": tile_bbox},
            )
            sources.add("Overpass API")
            cache_dates.append(cached_at)

        limit_reached = len(elements) >= limit
        if limit_reached and depth == 0:
            tiled_elements: list[dict[str, Any]] = []
            complete = True
            for child_bbox in split_bbox(tile_bbox):
                child_elements, child_complete = fetch_tile(child_bbox, depth + 1)
                tiled_elements.extend(child_elements)
                complete = complete and child_complete
            return tiled_elements, complete
        if limit_reached:
            warnings.append(
                f"Categoria {category} a atins limita de {limit} elemente intr-un tile."
            )
            return elements, False
        return elements, True

    elements, complete = fetch_tile(bbox)
    return {
        "elements": deduplicate_elements(elements),
        "source": "cache" if sources == {"cache"} else "Overpass API",
        "cache_date": max(cache_dates) if cache_dates else query_day,
        "completeness": "complet" if complete else "posibil incomplet",
        "warnings": warnings,
    }


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


def _append_relation_features(
    layers: dict[str, dict[str, Any]],
    elements: list[dict[str, Any]],
) -> None:
    nodes = {
        element["id"]: (float(element["lon"]), float(element["lat"]))
        for element in elements
        if element.get("type") == "node" and "lat" in element and "lon" in element
    }
    ways = {
        element["id"]: [
            nodes[node_id] for node_id in element.get("nodes", []) if node_id in nodes
        ]
        for element in elements
        if element.get("type") == "way"
    }
    for relation in elements:
        tags = relation.get("tags") or {}
        if relation.get("type") != "relation" or tags.get("type") != "multipolygon":
            continue
        outer_lines = []
        inner_lines = []
        for member in relation.get("members", []):
            coordinates = ways.get(member.get("ref"), [])
            if len(coordinates) < 2:
                continue
            target = inner_lines if member.get("role") == "inner" else outer_lines
            target.append(LineString(coordinates))
        outer = unary_union(list(polygonize(outer_lines)))
        if outer.is_empty:
            continue
        inner = unary_union(list(polygonize(inner_lines)))
        geometry = outer.difference(inner) if not inner.is_empty else outer
        feature = {
            "type": "Feature",
            "geometry": mapping(geometry),
            "properties": {
                **tags,
                "tags": tags,
                "osm_type": "relation",
                "osm_id": relation.get("id"),
            },
        }
        if tags.get("building"):
            layers["osm_buildings"]["features"].append(
                _with_exposure(feature, "high", "cladire potential afectata")
            )
