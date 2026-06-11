from __future__ import annotations

import pytest

from src.impact_tool.cache import PersistentCache
from src.impact_tool.osm import _critical_layer, build_category_query, load_osm_categories
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
