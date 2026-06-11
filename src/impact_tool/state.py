from __future__ import annotations

from collections.abc import MutableMapping
from dataclasses import asdict
from typing import Any

from src.impact_tool.aoi import area_metadata, validate_aoi
from src.impact_tool.models import ImpactToolState


STATE_KEY = "impact_tool_state"


def initialize_state(session_state: MutableMapping[str, Any]) -> ImpactToolState:
    current = session_state.get(STATE_KEY)
    if isinstance(current, ImpactToolState):
        return current
    state = ImpactToolState()
    session_state[STATE_KEY] = state
    return state


def state_snapshot(state: ImpactToolState) -> dict[str, Any]:
    return asdict(state)


def reset_scene_selection(state: ImpactToolState) -> None:
    state.before_scene = None
    state.after_scene = None
    state.scenes_confirmed = False
    state.comparison_ready = False
    state.swipe_enabled = False
    state.preview_tiles.clear()
    state.preview_scene_id = ""
    state.preview_scene_tile = ""
    state.cache_events.append("Selecția scenelor a fost resetată.")


def reset_analysis_results(state: ImpactToolState) -> None:
    state.analysis_complete = False
    state.analysis_results.clear()
    state.active_layers = ["sar_new_water", "buffer", "osm_critical"]
    state.analysis_hash = ""
    state.report_bytes = None
    state.analysis_progress = 0
    state.analysis_stage = "Pregătit pentru analiză"


def reset_area_dependent_state(state: ImpactToolState) -> None:
    reset_scene_selection(state)
    reset_analysis_results(state)
    state.cache_events.append("Cache-ul dependent de aria activă trebuie revalidat.")


def update_buffer(state: ImpactToolState, buffer_meters: int) -> bool:
    if buffer_meters == state.buffer_meters:
        return False
    state.buffer_meters = buffer_meters
    state.analysis_results.pop("osm_impact", None)
    state.report_bytes = None
    state.cache_events.append(
        f"Se recalculează impactul pentru bufferul de {buffer_meters} m."
    )
    return True


def apply_scene_pair(
    state: ImpactToolState,
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    confirmed: bool,
) -> None:
    changed = (
        (state.before_scene or {}).get("ee_id") != (before or {}).get("ee_id")
        or (state.after_scene or {}).get("ee_id") != (after or {}).get("ee_id")
    )
    state.before_scene = before
    state.after_scene = after
    state.scenes_confirmed = confirmed
    state.comparison_ready = bool(before and after)
    if changed:
        reset_analysis_results(state)
        state.cache_events.append("Scenele s-au schimbat; rezultatele dependente au fost invalidate.")


def set_county(
    state: ImpactToolState,
    county_name: str,
    county_geometry: dict | None,
    county_bbox: list[float],
) -> bool:
    changed = county_name != state.county_name
    state.county_name = county_name
    state.county_geometry = county_geometry
    state.county_bbox = list(county_bbox)
    if changed:
        state.aoi_geometry = None
        state.draw_requested = False
        state.area_warnings.clear()
        state.area_errors.clear()
        reset_area_dependent_state(state)
    _set_active_area_metadata(state, state.active_geometry)
    return changed


def set_aoi(state: ImpactToolState, geometry: dict | None) -> bool:
    validation = validate_aoi(geometry, state.county_geometry)
    state.area_errors = validation.errors
    state.area_warnings = validation.warnings
    if not validation.valid or not validation.geometry:
        return False
    metadata = area_metadata(validation.geometry, validation.warnings)
    if metadata.area_hash == state.active_area_hash and state.aoi_geometry is not None:
        return False
    state.aoi_geometry = metadata.geometry
    state.draw_requested = False
    reset_area_dependent_state(state)
    _apply_metadata(state, metadata)
    return True


def clear_aoi(state: ImpactToolState) -> bool:
    if state.aoi_geometry is None:
        return False
    state.aoi_geometry = None
    state.draw_requested = False
    state.area_warnings.clear()
    state.area_errors.clear()
    reset_area_dependent_state(state)
    _set_active_area_metadata(state, state.county_geometry)
    return True


def _set_active_area_metadata(
    state: ImpactToolState,
    geometry: dict | None,
) -> None:
    if not geometry:
        state.active_area_bbox = []
        state.active_area_centroid = []
        state.active_area_km2 = 0.0
        state.active_area_hash = ""
        return
    _apply_metadata(state, area_metadata(geometry, state.area_warnings))


def _apply_metadata(state: ImpactToolState, metadata: Any) -> None:
    state.active_area_bbox = list(metadata.bbox)
    state.active_area_centroid = list(metadata.centroid)
    state.active_area_km2 = metadata.area_km2
    state.active_area_hash = metadata.area_hash
    state.area_warnings = list(metadata.warnings)
