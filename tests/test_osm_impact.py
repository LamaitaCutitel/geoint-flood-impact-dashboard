from src.app.osm_impact import expanded_bbox, fetch_osm_operational_impact, summarize_osm_elements


def test_expanded_bbox_adds_buffer():
    bbox = [27.0, 45.0, 28.0, 46.0]
    expanded = expanded_bbox(bbox, 1000)

    assert expanded[0] < bbox[0]
    assert expanded[1] < bbox[1]
    assert expanded[2] > bbox[2]
    assert expanded[3] > bbox[3]


def test_summarize_osm_elements_counts_operational_assets():
    elements = [
        {"type": "node", "id": 1, "lat": 45.0, "lon": 27.0},
        {"type": "node", "id": 2, "lat": 45.0, "lon": 27.01},
        {"type": "way", "id": 10, "nodes": [1, 2], "tags": {"building": "yes"}},
        {"type": "way", "id": 11, "nodes": [1, 2], "tags": {"highway": "primary"}},
        {"type": "way", "id": 12, "nodes": [1, 2], "tags": {"railway": "rail"}},
        {"type": "node", "id": 3, "lat": 45.0, "lon": 27.02, "tags": {"amenity": "hospital"}},
        {"type": "way", "id": 13, "nodes": [1, 2], "tags": {"bridge": "yes"}},
    ]

    metrics = summarize_osm_elements(elements, 500, 5000)

    assert metrics["osm_buildings_potentially_affected"] == 1
    assert metrics["osm_roads_intersected_km"] > 0
    assert metrics["osm_railways_intersected_km"] > 0
    assert metrics["osm_critical_assets"] == 1
    assert metrics["osm_bridges"] == 1


def test_fetch_osm_operational_impact_uses_injected_fetcher():
    def fetcher(query):
        assert "building" in query
        return {"elements": []}

    metrics = fetch_osm_operational_impact([27.0, 45.0, 28.0, 46.0], fetcher=fetcher)

    assert metrics["osm_elements_returned"] == 0
    assert metrics["osm_query_buffer_m"] == 500
