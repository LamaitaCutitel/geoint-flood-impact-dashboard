import json

from src.reports.report_generator import build_report_payload, generate_reports


def _params():
    return {
        "aoi_name": "Galati - September 2024 Floods",
        "bbox": [27.45, 45.35, 28.25, 46.05],
        "before_start_date": "2024-08-20",
        "before_end_date": "2024-09-05",
        "after_start_date": "2024-09-14",
        "after_end_date": "2024-09-25",
        "event_date": "2024-09-14",
        "polarization": "VH",
        "orbit_pass": "BOTH",
        "before_sar_method": "Compozit median din scene compatibile",
        "after_sar_method": "Scena individuala selectata manual",
        "scale": 20,
        "threshold": 1.25,
        "smoothing_radius": 30,
    }


def _metrics():
    return {
        "scene_count_before": 5,
        "scene_count_after": 3,
        "sar_detected_extent_km2": 18.42,
        "permanent_water_removed_km2": 1.2,
        "dominant_land_cover_class": "crops",
        "osm_buildings_potentially_affected": 2,
        "osm_roads_intersected_km": 1.5,
        "osm_critical_assets": 1,
        "osm_railways_intersected_km": 0.25,
        "osm_bridges": 1,
    }


def test_build_report_payload_contains_methodological_note():
    payload = build_report_payload(_params(), _metrics(), {"crops": 10.0}, [])
    assert payload["aoi"] == "Galati - September 2024 Floods"
    assert payload["scene_counts"]["before"] == 5
    assert payload["before_sar_method"] == "Compozit median din scene compatibile"
    assert payload["after_sar_method"] == "Scena individuala selectata manual"
    assert payload["osm_operational_impact"]["buildings_potentially_affected"] == 2
    assert "produse GEOINT preliminare" in payload["methodological_note"]


def test_generate_reports_writes_json_csv_html_and_log(tmp_path):
    paths = generate_reports(
        tmp_path,
        _params(),
        _metrics(),
        {"crops": 10.0, "built": 0.2},
        ["Raport generat."],
        ["warning"],
        osm_layers={
            "osm_buildings": {
                "type": "FeatureCollection",
                "features": [
                    {"type": "Feature", "geometry": None, "properties": {"name": "test"}}
                ],
            }
        },
    )
    assert {"json", "csv", "html", "log", "log_json", "charts_dir", "report_assets_dir"} <= set(paths)
    payload = json.loads(paths["json"].read_text(encoding="utf-8"))
    assert payload["warnings"] == ["warning"]
    html = paths["html"].read_text(encoding="utf-8")
    assert "Raport GEOINT preliminar" in html
    assert "data:image/svg+xml;base64" in html
    assert "Rezultatele reprezinta produse GEOINT preliminare" in html
    assert "Raport generat." in paths["log"].read_text(encoding="utf-8")
    assert paths["log_json"].exists()
    assert paths["charts_dir"].is_dir()
    assert paths["report_assets_dir"].is_dir()
    assert paths["osm_buildings"].exists()


def test_generate_reports_without_osm_still_writes_offline_report(tmp_path):
    paths = generate_reports(
        tmp_path,
        _params(),
        _metrics(),
        {},
        [],
        [],
    )

    assert "osm_buildings" not in paths
    assert paths["html"].exists()
    assert list(paths["charts_dir"].glob("*.svg"))
