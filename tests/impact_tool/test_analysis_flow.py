from __future__ import annotations

from src.impact_tool import analysis
from src.impact_tool.models import ImpactToolState


class FakeGeeStatus:
    available = True
    ee = object()


def test_analysis_reports_progress_and_loads_osm_automatically(monkeypatch) -> None:
    state = ImpactToolState(
        active_area_hash="area",
        active_area_bbox=[27, 45, 28, 46],
        county_geometry={"type": "Polygon", "coordinates": []},
        before_scene={"ee_id": "before"},
        after_scene={"ee_id": "after"},
        scenes_confirmed=True,
    )
    calls = []
    monkeypatch.setattr(analysis, "initialize_earth_engine", lambda: FakeGeeStatus())
    monkeypatch.setattr(analysis, "build_aoi_from_geometry", lambda *args: "aoi")
    monkeypatch.setattr(
        analysis,
        "run_sar_analysis",
        lambda *args: {"products": {"sar_new_water": "water"}},
    )
    monkeypatch.setattr(analysis, "run_dynamic_world_analysis", lambda *args: {})
    monkeypatch.setattr(
        analysis,
        "execute_osm_loading",
        lambda state, progress_callback=None: calls.append("osm") or True,
    )

    progress = []
    assert analysis.execute_analysis(
        state,
        progress_callback=lambda percent, stage: progress.append((percent, stage)),
    )

    assert calls == ["osm"]
    assert progress[-1] == (100, "Analiza impactului a fost finalizată")
    assert state.analysis_progress == 100
    assert state.active_layers == ["sar_new_water", "buffer", "osm_critical"]
