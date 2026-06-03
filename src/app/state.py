from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from config.settings import GALATI_PRESET, PROFILE_SCALES


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
    minimum_connected_pixels: int = 8
    mask_permanent_water: bool = True
    analysis_profile: str = "Standard"
    scale: int = PROFILE_SCALES["Standard"]
    show_permanent_water: bool = True
    show_land_cover: bool = True
    show_sentinel2_rgb: bool = False
    show_sar_before: bool = True
    show_sar_after: bool = True
    show_sar_change: bool = True
    show_detected_flood_extent: bool = True
    use_median_composite: bool = False
    comparison_preset: str = "Before SAR vs After SAR"
    left_layer: str = "Sentinel-1 SAR before"
    right_layer: str = "Sentinel-1 SAR after"

    def as_dict(self) -> dict[str, object]:
        return self.__dict__.copy()
