from __future__ import annotations

import pytest

from src.impact_tool.cache import PersistentCache
from src.impact_tool.osm import (
    OSM_LIMITS,
    _append_relation_features,
    _critical_layer,
    build_category_query,
    deduplicate_elements,
    load_osm_categories,
    split_bbox,
)
from src.impact_tool.osm_impact import (
    STATUS_BUFFER,
    STATUS_DIRECT,
    classify_osm_impact,
    symbol_for_feature,
)


COUNTY = {
    "type": "Polygon",
    "coordinates": [[[27.0, 45.0], [28.0, 45.0], [28.0, 46.0], [27.0, 46.0], [27.0, 45.0]]],
}


def test_osm_is_blocked_before_analysis(tmp_path) -> None:
    with pytest.raises(RuntimeError):
        load_osm_categories(
            analysis_complete=False,
            aoi_hash="a",
            bbox=[27, 45, 28, 46],
            geometry=COUNTY,
            cache=PersistentCache(tmp_path),
        )


def test_osm_partial_failure_continues(tmp_path) -> None:
    def fetcher(query):
        if '"highway"' in query:
            raise TimeoutError("timeout")
        return {"elements": []}

    result = load_osm_categories(
        analysis_complete=True,
        aoi_hash="a",
        bbox=[27, 45, 28, 46],
        geometry=COUNTY,
        cache=PersistentCache(tmp_path),
        categories=("buildings", "roads"),
        fetcher=fetcher,
    )
    assert result["status"]["buildings"]["ok"]
    assert not result["status"]["roads"]["ok"]
    assert "OpenStreetMap" in result["attribution"]


def test_osm_cache_avoids_second_request(tmp_path) -> None:
    calls = []

    def fetcher(query):
        calls.append(query)
        return {"elements": []}

    kwargs = dict(
        analysis_complete=True,
        aoi_hash="a",
        bbox=[27, 45, 28, 46],
        geometry=COUNTY,
        cache=PersistentCache(tmp_path),
        categories=("buildings",),
        fetcher=fetcher,
    )
    load_osm_categories(**kwargs)
    second = load_osm_categories(**kwargs)
    assert len(calls) == 1
    assert second["status"]["buildings"]["source"] == "cache"


def test_category_limits_and_timeout() -> None:
    for category, limit in OSM_LIMITS.items():
        query = build_category_query([27, 45, 28, 46], category)
        assert f"out body {limit}" in query
        assert "[timeout:60]" in query


def test_bbox_tiling_and_deduplication() -> None:
    tiles = split_bbox([27, 45, 28, 46])
    assert len(tiles) == 4
    assert tiles[0] == [27, 45, 27.5, 45.5]
    elements = [
        {"type": "way", "id": 1},
        {"type": "way", "id": 1, "tags": {"building": "yes"}},
        {"type": "node", "id": 1},
    ]
    assert len(deduplicate_elements(elements)) == 2


def test_limit_triggers_four_tiles_and_completeness_warning(tmp_path) -> None:
    calls = []

    def fetcher(query):
        calls.append(query)
        return {
            "elements": [
                {"type": "node", "id": index, "lat": 45.5, "lon": 27.5}
                for index in range(OSM_LIMITS["critical"])
            ]
        }

    result = load_osm_categories(
        analysis_complete=True,
        aoi_hash="a",
        bbox=[27, 45, 28, 46],
        geometry=COUNTY,
        cache=PersistentCache(tmp_path),
        categories=("critical",),
        fetcher=fetcher,
    )
    assert len(calls) == 5
    assert result["status"]["critical"]["completeness"] == "posibil incomplet"
    assert result["status"]["critical"]["warnings"]


def test_galati_prewarm_script_exists() -> None:
    from pathlib import Path

    script = Path("scripts/prewarm_galati_cache.py")
    assert script.exists()
    assert "Galati" in script.read_text(encoding="utf-8")


def test_exposure_direct_and_buffer() -> None:
    water = {
        "type": "Polygon",
        "coordinates": [[[27.4, 45.4], [27.6, 45.4], [27.6, 45.6], [27.4, 45.6], [27.4, 45.4]]],
    }
    layers = {
        "osm_critical": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"name": "Spital", "amenity": "hospital"},
                    "geometry": {"type": "Point", "coordinates": [27.5, 45.5]},
                },
                {
                    "type": "Feature",
                    "properties": {"name": "Clinic", "amenity": "clinic"},
                    "geometry": {"type": "Point", "coordinates": [27.6005, 45.5]},
                },
            ],
        }
    }
    result = classify_osm_impact(layers, water, 100)
    statuses = [
        feature["properties"]["status"]
        for feature in result["layers"]["osm_critical"]["features"]
    ]
    assert statuses == [STATUS_DIRECT, STATUS_BUFFER]
    assert result["buffer_meters"] == 100


def test_partial_lengths_and_building_overlap() -> None:
    water = {
        "type": "Polygon",
        "coordinates": [[[27.4, 45.4], [27.6, 45.4], [27.6, 45.6], [27.4, 45.6], [27.4, 45.4]]],
    }
    layers = {
        "osm_roads": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"highway": "primary"},
                    "geometry": {
                        "type": "LineString",
                        "coordinates": [[27.3, 45.5], [27.7, 45.5]],
                    },
                }
            ],
        },
        "osm_buildings": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {"building": "yes"},
                    "geometry": {
                        "type": "Polygon",
                        "coordinates": [[[27.55, 45.55], [27.65, 45.55], [27.65, 45.65], [27.55, 45.65], [27.55, 45.55]]],
                    },
                }
            ],
        },
    }
    result = classify_osm_impact(layers, water, 250)
    metrics = result["metrics"]
    assert 0 < metrics["roads_direct_km"] < 40
    assert metrics["buildings_overlap_m2"] < metrics["buildings_area_m2"]
    assert metrics["buildings_partial"] == 1
    building = result["layers"]["osm_buildings"]["features"][0]
    assert building["original_geometry"]
    assert building["clipped_geometry"]


def test_multipolygon_with_hole_and_outside_aoi_buffer_status() -> None:
    water = {
        "type": "Polygon",
        "coordinates": [[[27.49, 45.49], [27.51, 45.49], [27.51, 45.51], [27.49, 45.51], [27.49, 45.49]]],
    }
    active = {
        "type": "Polygon",
        "coordinates": [[[27.48, 45.48], [27.52, 45.48], [27.52, 45.52], [27.48, 45.52], [27.48, 45.48]]],
    }
    layers = {
        "osm_buildings": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {
                        "type": "MultiPolygon",
                        "coordinates": [[
                            [[27.509, 45.499], [27.514, 45.499], [27.514, 45.504], [27.509, 45.504], [27.509, 45.499]],
                            [[27.510, 45.500], [27.511, 45.500], [27.511, 45.501], [27.510, 45.501], [27.510, 45.500]],
                        ]],
                    },
                }
            ],
        }
    }
    result = classify_osm_impact(layers, water, 1000, active_geometry=active)
    feature = result["layers"]["osm_buildings"]["features"][0]
    assert feature["properties"]["status"] in {STATUS_DIRECT, STATUS_BUFFER}
    assert not feature["properties"]["outside_active_area"]


def test_osm_relation_multipolygon_with_hole_is_parsed() -> None:
    nodes = [
        {"type": "node", "id": index + 1, "lon": lon, "lat": lat}
        for index, (lon, lat) in enumerate(
            [
                (27.0, 45.0), (28.0, 45.0), (28.0, 46.0), (27.0, 46.0), (27.0, 45.0),
                (27.4, 45.4), (27.6, 45.4), (27.6, 45.6), (27.4, 45.6), (27.4, 45.4),
            ]
        )
    ]
    elements = nodes + [
        {"type": "way", "id": 20, "nodes": [1, 2, 3, 4, 5]},
        {"type": "way", "id": 21, "nodes": [6, 7, 8, 9, 10]},
        {
            "type": "relation",
            "id": 30,
            "tags": {"type": "multipolygon", "building": "yes"},
            "members": [
                {"type": "way", "ref": 20, "role": "outer"},
                {"type": "way", "ref": 21, "role": "inner"},
            ],
        },
    ]
    layers = {
        key: {"type": "FeatureCollection", "features": []}
        for key in ("osm_buildings", "osm_roads", "osm_critical", "osm_railways", "osm_bridges")
    }
    _append_relation_features(layers, elements)
    geometry = layers["osm_buildings"]["features"][0]["geometry"]
    assert geometry["type"] == "Polygon"
    assert len(geometry["coordinates"]) == 2


def test_building_reference_is_limited_to_500_m() -> None:
    from src.impact_tool.osm_impact import STATUS_REFERENCE

    water = {"type": "Point", "coordinates": [27.5, 45.5]}
    layers = {
        "osm_buildings": {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {"type": "Point", "coordinates": [27.505, 45.5]},
                },
                {
                    "type": "Feature",
                    "properties": {},
                    "geometry": {"type": "Point", "coordinates": [27.52, 45.5]},
                },
            ],
        }
    }
    result = classify_osm_impact(layers, water, 1)
    statuses = [
        feature["properties"]["status"]
        for feature in result["layers"]["osm_buildings"]["features"]
    ]
    assert statuses[0] == STATUS_REFERENCE
    assert statuses[1] == "Neexpus"


def test_buffer_limits_and_symbols() -> None:
    with pytest.raises(ValueError):
        classify_osm_impact({}, COUNTY, 0)
    with pytest.raises(ValueError):
        classify_osm_impact({}, COUNTY, 1001)
    assert symbol_for_feature({"amenity": "hospital"}, "osm_critical") == "✚"
    assert symbol_for_feature({}, "osm_bridges") == "⌒"


def test_critical_query_contains_all_required_categories() -> None:
    query = build_category_query([27, 45, 28, 46], "critical")
    for tag in ("pharmacy", "kindergarten", "fuel", "healthcare", "emergency", "power"):
        assert tag in query


def test_critical_parser_keeps_healthcare_power_and_pharmacy() -> None:
    elements = [
        {"type": "node", "id": 1, "lat": 45.5, "lon": 27.5, "tags": {"amenity": "pharmacy"}},
        {"type": "node", "id": 2, "lat": 45.6, "lon": 27.6, "tags": {"healthcare": "doctor"}},
        {"type": "node", "id": 3, "lat": 45.7, "lon": 27.7, "tags": {"power": "substation"}},
    ]
    layer = _critical_layer(elements)
    assert len(layer["features"]) == 3
    assert layer["features"][2]["properties"]["power"] == "substation"
