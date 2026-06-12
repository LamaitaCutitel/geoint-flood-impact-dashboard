from __future__ import annotations

from src.impact_tool import analysis
from src.impact_tool.models import ImpactToolState


class FakeGeeStatus:
    available = True
    ee = object()


def _analysis_state() -> ImpactToolState:
    return ImpactToolState(
        active_area_hash="area",
        active_area_bbox=[27, 45, 28, 46],
        county_geometry={"type": "Polygon", "coordinates": []},
        before_scene={"ee_id": "before"},
        after_scene={"ee_id": "after"},
        scenes_confirmed=True,
    )


def _mock_raster_dependencies(monkeypatch, dynamic_calls: list[str]) -> None:
    monkeypatch.setattr(analysis, "initialize_earth_engine", lambda: FakeGeeStatus())
    monkeypatch.setattr(analysis, "build_aoi_from_geometry", lambda *args: "aoi")
    monkeypatch.setattr(
        analysis,
        "run_sar_analysis",
        lambda *args: {
            "products": {"sar_new_water": "water"},
            "duration_seconds": 0.2,
            "vectorization_duration_seconds": 0.1,
        },
    )
    monkeypatch.setattr(
        analysis,
        "run_dynamic_world_analysis",
        lambda *args: dynamic_calls.append("dynamic") or {"metrics": {}},
    )


def test_rapid_analysis_reports_progress_and_skips_dynamic_world(monkeypatch) -> None:
    state = _analysis_state()
    osm_calls: list[str] = []
    dynamic_calls: list[str] = []
    _mock_raster_dependencies(monkeypatch, dynamic_calls)
    monkeypatch.setattr(
        analysis,
        "execute_osm_loading",
        lambda state, progress_callback=None, **kwargs: osm_calls.append("osm") or True,
    )

    progress = []
    assert analysis.execute_analysis(
        state,
        mode="rapid",
        progress_callback=lambda percent, stage: progress.append((percent, stage)),
    )

    assert osm_calls == ["osm"]
    assert dynamic_calls == []
    assert progress[-1] == (100, "Analiza impactului a fost finalizată")
    assert state.analysis_progress == 100
    assert state.active_layers == ["sar_new_water", "buffer", "osm_critical"]
    assert state.timings["SAR"] == 0.2
    assert state.timings["vectorizare"] == 0.1
    assert any(event.startswith("Timp SAR:") for event in state.cache_events)


def test_detailed_analysis_runs_dynamic_world(monkeypatch) -> None:
    state = _analysis_state()
    dynamic_calls: list[str] = []
    _mock_raster_dependencies(monkeypatch, dynamic_calls)
    monkeypatch.setattr(analysis, "execute_osm_loading", lambda *args, **kwargs: True)

    assert analysis.execute_analysis(state, mode="detaliat")
    assert dynamic_calls == ["dynamic"]
    assert "dynamic_world" in state.analysis_results
    assert "Dynamic World" in state.timings


def test_failed_osm_does_not_mark_workflow_complete(monkeypatch) -> None:
    state = _analysis_state()
    dynamic_calls: list[str] = []
    _mock_raster_dependencies(monkeypatch, dynamic_calls)
    monkeypatch.setattr(analysis, "execute_osm_loading", lambda *args, **kwargs: False)

    assert analysis.execute_analysis(state, mode="rapid")
    assert state.analysis_results["sar_status"] == "reușit"
    assert state.analysis_results["workflow_status"] == "osm_indisponibil"


def test_manual_dynamic_world_invalidates_pdf_and_recalculates_correlation(
    monkeypatch,
) -> None:
    state = _analysis_state()
    state.analysis_results = {
        "sar": {"products": {"sar_new_water": "water"}},
        "osm_impact": {"layers": {}},
    }
    state.report_bytes = b"old"
    state.report_filename = "old.pdf"
    monkeypatch.setattr(analysis, "initialize_earth_engine", lambda: FakeGeeStatus())
    monkeypatch.setattr(analysis, "build_aoi_from_geometry", lambda *args: "aoi")
    monkeypatch.setattr(
        analysis,
        "run_dynamic_world_analysis",
        lambda *args: {"status": "reușit", "metrics": {}},
    )
    monkeypatch.setattr(
        analysis,
        "correlate_osm_dynamic_world",
        lambda *args: {"status": "reușit", "rows": [{"name": "Spital"}]},
    )

    assert analysis.execute_dynamic_world(state)
    assert state.report_bytes is None
    assert state.report_filename == ""
    assert state.analysis_results["osm_dynamic_world"]["rows"]


def test_osm_categories_follow_analysis_mode(monkeypatch) -> None:
    state = ImpactToolState(
        analysis_complete=True,
        analysis_mode="rapid",
        active_area_hash="area",
        county_geometry={
            "type": "Polygon",
            "coordinates": [[[27, 45], [28, 45], [28, 46], [27, 45]]],
        },
        analysis_results={
            "sar": {
                "new_water_geometry": {
                    "type": "Polygon",
                    "coordinates": [[[27, 45], [28, 45], [28, 46], [27, 45]]],
                }
            }
        },
    )
    categories = []
    monkeypatch.setattr(
        analysis,
        "buffered_geometry",
        lambda *args: (state.active_geometry, [27, 45, 28, 46]),
    )
    monkeypatch.setattr(
        analysis,
        "load_osm_categories",
        lambda **kwargs: categories.append(kwargs["categories"])
        or {
            "layers": {},
            "status": {
                category: {"ok": True, "count": 0}
                for category in kwargs["categories"]
            },
            "attribution": "OSM",
        },
    )
    monkeypatch.setattr(analysis, "recalculate_osm_impact", lambda *args: True)

    assert analysis.execute_osm_loading(state)
    assert categories == [("buildings", "roads", "bridges", "critical")]


def test_osm_query_area_stays_at_1000_m_when_analytic_buffer_changes(
    monkeypatch,
) -> None:
    state = ImpactToolState(
        analysis_complete=True,
        analysis_mode="rapid",
        buffer_meters=250,
        active_area_hash="area",
        county_geometry={
            "type": "Polygon",
            "coordinates": [[[27, 45], [28, 45], [28, 46], [27, 45]]],
        },
        analysis_results={
            "sar": {
                "new_water_geometry": {
                    "type": "Polygon",
                    "coordinates": [[[27, 45], [28, 45], [28, 46], [27, 45]]],
                }
            }
        },
    )
    buffer_calls = []
    monkeypatch.setattr(
        analysis,
        "buffered_geometry",
        lambda geometry, meters: buffer_calls.append(meters)
        or (geometry, [27, 45, 28, 46]),
    )
    monkeypatch.setattr(
        analysis,
        "load_osm_categories",
        lambda **kwargs: {
            "layers": {},
            "status": {
                category: {"ok": True, "count": 0}
                for category in kwargs["categories"]
            },
            "attribution": "OSM",
        },
    )
    monkeypatch.setattr(analysis, "recalculate_osm_impact", lambda *args: True)

    assert analysis.execute_osm_loading(state)
    state.buffer_meters = 1000
    assert analysis.execute_osm_loading(state)
    assert buffer_calls == [1000, 1000]


def test_osm_complete_requires_ok_and_complete_for_every_category() -> None:
    assert analysis._osm_load_status(
        {
            "buildings": {"ok": True, "completeness": "complet"},
            "roads": {"ok": True, "completeness": "complet"},
        }
    ) == "osm_complet"
    assert analysis._osm_load_status(
        {
            "buildings": {"ok": True, "completeness": "complet"},
            "roads": {"ok": True, "completeness": "posibil incomplet"},
        }
    ) == "osm_parțial"
    assert analysis._osm_load_status(
        {
            "buildings": {"ok": False, "error": "timeout"},
            "roads": {"ok": False, "error": "timeout"},
        }
    ) == "osm_indisponibil"


def test_osm_partial_reasons_name_category_and_cause() -> None:
    reasons = analysis._osm_partial_reasons(
        {
            "roads": {"ok": True, "completeness": "posibil incomplet"},
            "bridges": {"ok": False, "error": "timeout Overpass"},
        }
    )
    assert "roads: completitudine posibil incomplet" in reasons
    assert "bridges: timeout Overpass" in reasons
