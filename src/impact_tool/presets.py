from __future__ import annotations

from datetime import date
from typing import Any, MutableMapping

from src.impact_tool.models import ImpactToolState
from src.impact_tool.state import set_county, update_buffer


GALATI_PRESET_NAME = "Inundații Galați — septembrie 2024"
GALATI_EVENT_DATE = "2024-09-14"


def apply_galati_preset(
    state: ImpactToolState,
    session_state: MutableMapping[str, Any],
    county_geometry: dict[str, Any],
    county_bbox: list[float],
) -> None:
    set_county(state, "Galati", county_geometry, county_bbox)
    update_buffer(state, 250)
    state.preset_name = GALATI_PRESET_NAME
    state.event_date = GALATI_EVENT_DATE
    session_state["impact_scene_start_preset"] = date(2024, 9, 1)
    session_state["impact_scene_end_preset"] = date(2024, 9, 30)
    session_state["impact_scene_polarization_preset"] = "VH"
    state.cache_events.append("Cache Galați pregătit pentru rulare rapidă")
