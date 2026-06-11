from __future__ import annotations

from src.impact_tool.cache import PersistentCache
from src.impact_tool.models import ImpactToolState
from src.impact_tool.report import (
    MANDATORY_NOTE,
    generate_cached_report,
    generate_report_pdf,
    report_filename,
    _metric_label,
    _osm_dynamic_world_summary,
    _osm_status_table,
    _synthetic_map,
)


def _state() -> ImpactToolState:
    return ImpactToolState(
        county_name="Galati",
        active_area_km2=100,
        analysis_complete=True,
        analysis_hash="analysis",
        after_scene={"acquisition_time": "2024-09-14T10:00:00Z"},
        before_scene={
            "acquisition_time": "2024-09-01T10:00:00Z",
            "polarization": "VH",
            "orbit_pass": "ASCENDING",
        },
        analysis_results={
            "sar": {
                "metrics": {
                    "sar_water_before_area_km2": 1,
                    "sar_water_after_area_km2": 3,
                    "sar_new_water_area_km2": 2,
                },
                "duration_seconds": 1.2,
            }
        },
    )


def test_pdf_is_generated_with_partial_results() -> None:
    pdf = generate_report_pdf(_state())
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 20_000


def test_pdf_supports_aoi_and_buffer_extremes() -> None:
    state = _state()
    state.aoi_geometry = {
        "type": "Polygon",
        "coordinates": [[[27, 45], [28, 45], [28, 46], [27, 46], [27, 45]]],
    }
    state.buffer_meters = 1
    assert generate_report_pdf(state).startswith(b"%PDF")
    state.buffer_meters = 1000
    assert generate_report_pdf(state).startswith(b"%PDF")


def test_report_cache(tmp_path) -> None:
    cache = PersistentCache(tmp_path)
    first, first_hit = generate_cached_report(_state(), cache)
    second, second_hit = generate_cached_report(_state(), cache)
    assert not first_hit
    assert second_hit
    assert first == second


def test_report_has_readable_labels_and_osm_completeness() -> None:
    state = _state()
    state.osm_status = {
        "buildings": {
            "count": 12,
            "source": "cache",
            "cache_date": "2026-06-11T10:00:00Z",
            "completeness": "complet",
        }
    }
    assert _metric_label("roads_direct_km") == "Drumuri intersectate direct (km)"
    assert len(_osm_status_table(state)._cellvalues) == 2


def test_synthetic_map_contains_osm_and_works_offline() -> None:
    state = _state()
    state.county_geometry = {
        "type": "Polygon",
        "coordinates": [[[27, 45], [28, 45], [28, 46], [27, 46], [27, 45]]],
    }
    state.analysis_results["sar"]["new_water_geometry"] = {
        "type": "Polygon",
        "coordinates": [[[27.4, 45.4], [27.6, 45.4], [27.6, 45.6], [27.4, 45.6], [27.4, 45.4]]],
    }
    state.analysis_results["osm_impact"] = {
        "buffer_geometry": state.analysis_results["sar"]["new_water_geometry"],
        "metrics": {"roads_direct_km": 1.2},
        "layers": {
            "osm_roads": {
                "features": [
                    {
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[27.3, 45.5], [27.7, 45.5]],
                        },
                        "properties": {"status": "Intersectat direct"},
                    }
                ]
            },
            "osm_critical": {
                "features": [
                    {
                        "geometry": {"type": "Point", "coordinates": [27.5, 45.5]},
                        "properties": {"status": "Intersectat direct"},
                    }
                ]
            },
        },
    }
    image = _synthetic_map(state)
    assert image.read(8) == b"\x89PNG\r\n\x1a\n"
    assert len(image.getvalue()) > 10_000


def test_osm_dynamic_world_summary_handles_missing_data() -> None:
    text = _osm_dynamic_world_summary(_state())
    assert "0 km" in text
    assert "verificare" in text


def test_report_filename_and_mandatory_note() -> None:
    assert report_filename(_state()) == "raport_geoint_inundatie_galati_2024-09-14.pdf"
    assert "nu constituie confirmare oficială" in MANDATORY_NOTE
