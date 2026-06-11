from __future__ import annotations

from src.impact_tool.cache import PersistentCache
from src.impact_tool.scenes import confirm_scene_pair, search_scenes, select_scene_pair


def _scene(scene_id: str, timestamp: str, orbit: int = 80) -> dict:
    return {
        "ee_id": scene_id,
        "display_id": scene_id,
        "acquisition_time": timestamp,
        "polarization": "VH",
        "orbit_pass": "ASCENDING",
        "relative_orbit": orbit,
        "instrument_mode": "IW",
        "coverage_percent": 100,
    }


def test_scene_search_cache(tmp_path) -> None:
    calls = []

    def searcher(*args):
        calls.append(args)
        return {"scenes": [_scene("a", "2024-01-01T00:00:00Z")], "warnings": [], "errors": []}

    cache = PersistentCache(tmp_path)
    first = search_scenes(
        cache=cache,
        aoi_hash="area",
        start_date="2024-01-01",
        end_date="2024-02-01",
        polarization="VH",
        orbit_pass="ASCENDING",
        searcher=searcher,
    )
    second = search_scenes(
        cache=cache,
        aoi_hash="area",
        start_date="2024-01-01",
        end_date="2024-02-01",
        polarization="VH",
        orbit_pass="ASCENDING",
        searcher=searcher,
    )
    assert not first.from_cache
    assert second.from_cache
    assert len(calls) == 1


def test_zero_scenes_and_error_are_preserved(tmp_path) -> None:
    result = search_scenes(
        cache=PersistentCache(tmp_path),
        aoi_hash="area",
        start_date="2024-01-01",
        end_date="2024-02-01",
        polarization="VH",
        orbit_pass="BOTH",
        searcher=lambda *args: {
            "scenes": [],
            "warnings": ["Nicio scenă"],
            "errors": [{"message": "GEE indisponibil"}],
        },
    )
    assert result.scenes == []
    assert result.warnings == ["Nicio scenă"]
    assert result.errors == ["GEE indisponibil"]


def test_selection_and_confirmation() -> None:
    scenes = [
        _scene("before", "2024-01-01T00:00:00Z"),
        _scene("after", "2024-01-13T00:00:00Z"),
    ]
    before, after = select_scene_pair(scenes, "before", "after")
    result = confirm_scene_pair(before, after)
    assert result["confirmed"]


def test_incompatible_pair_is_blocked() -> None:
    before = _scene("before", "2024-01-13T00:00:00Z")
    after = _scene("after", "2024-01-01T00:00:00Z")
    assert not confirm_scene_pair(before, after)["confirmed"]


def test_relative_orbit_warning_requires_acceptance() -> None:
    before = _scene("before", "2024-01-01T00:00:00Z", 80)
    after = _scene("after", "2024-01-13T00:00:00Z", 81)
    assert not confirm_scene_pair(before, after)["confirmed"]
    assert confirm_scene_pair(before, after, warnings_accepted=True)["confirmed"]


def test_swipe_has_single_control_and_fallback() -> None:
    from src.impact_tool.map.builder import build_shell_map

    html = build_shell_map(None, "Galati", preview_tiles={"before": "a", "after": "b"}).get_root().render()
    assert html.count("leaflet-side-by-side@2.2.0") == 1
    assert "Separator indisponibil" in html
