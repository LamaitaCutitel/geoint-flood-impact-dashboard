from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from config.settings import GALATI_PRESET, PROFILE_SCALES


COUNTY_DEPENDENT_STATE_KEYS = (
    "sar_scene_results",
    "sar_before_scene",
    "sar_after_scene",
    "sar_pair_status",
    "sar_pair_confirmed",
    "sar_candidate_compare",
    "sar_preview",
    "confirm_relative_orbit_mismatch",
    "last_analysis_result",
)


def reset_county_dependent_state(session_state: object) -> None:
    for key in COUNTY_DEPENDENT_STATE_KEYS:
        session_state.pop(key, None)


def county_dependent_parameter_key(params: "AnalysisParameters") -> tuple[str, str, str, str, str, str, str]:
    return (
        params.county_name,
        str(params.before_start_date),
        str(params.before_end_date),
        str(params.after_start_date),
        str(params.after_end_date),
        params.polarization,
        params.orbit_pass,
    )


@dataclass
class AnalysisParameters:
    aoi_name: str = GALATI_PRESET["name"]
    county_name: str = "Galati"
    county_geometry: dict | None = None
    bbox: list[float] = field(default_factory=lambda: list(GALATI_PRESET["bbox"]))
    event_date: date = GALATI_PRESET["event_date"]
    before_start_date: date = GALATI_PRESET["before_start_date"]
    before_end_date: date = GALATI_PRESET["before_end_date"]
    after_start_date: date = GALATI_PRESET["after_start_date"]
    after_end_date: date = GALATI_PRESET["after_end_date"]
    polarization: str = "VH"
    orbit_pass: str = "BOTH"
    smoothing_radius: int = 30
    threshold: float = 1.25
    sar_water_mode: str = "Echilibrat"
    sar_water_threshold: float = -18.0
    minimum_connected_pixels: int = 8
    mask_permanent_water: bool = True
    jrc_water_mode: str = "Echilibrat"
    analysis_profile: str = "Standard"
    scale: int = PROFILE_SCALES["Standard"]
    show_permanent_water: bool = True
    show_land_cover: bool = True
    show_sentinel2_rgb: bool = False
    show_sar_before: bool = True
    show_sar_after: bool = True
    show_sar_change: bool = True
    show_detected_flood_extent: bool = True
    show_sar_water_layers: bool = True
    show_sar_dynamic_world_correlation: bool = True
    before_sar_method: str = "Compozit median din scene compatibile"
    after_sar_method: str = "Scena individuala selectata manual"
    dynamic_world_after_mode: str = "Fereastra apropiata de scena SAR AFTER"
    load_optional_layers: bool = False
    show_osm_impact: bool = False
    osm_buffer_meters: int = 500
    osm_query_limit: int = 5000
    use_median_composite: bool = False
    comparison_preset: str = "Before SAR vs After SAR"
    left_layer: str = "Sentinel-1 SAR before"
    right_layer: str = "Sentinel-1 SAR after"

    def as_dict(self) -> dict[str, object]:
        return self.__dict__.copy()
