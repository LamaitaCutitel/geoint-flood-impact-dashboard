from __future__ import annotations

from src.impact_tool.cache import PersistentCache
from src.impact_tool.models import ImpactToolState
from src.impact_tool.report import (
    MANDATORY_NOTE,
    generate_cached_report,
    generate_report_pdf,
    report_filename,
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


def test_report_filename_and_mandatory_note() -> None:
    assert report_filename(_state()) == "raport_geoint_inundatie_galati_2024-09-14.pdf"
    assert "nu constituie confirmare oficială" in MANDATORY_NOTE
