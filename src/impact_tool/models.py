from __future__ import annotations

from dataclasses import dataclass, field


BUFFER_MIN_METERS = 1
BUFFER_MAX_METERS = 1000
BUFFER_DEFAULT_METERS = 250

APP_TITLE = "Evaluarea impactului unei inundații"
APP_SUBTITLE = "Analiză multisursă SAR, Dynamic World și OpenStreetMap"

TAB_NAMES = (
    "Hartă",
    "Rezumat impact",
    "Dynamic World",
    "Elemente OSM",
    "Raport",
)

WIZARD_STEPS = (
    "Selectează județul",
    "Desenează AOI (opțional)",
    "Alege imaginile BEFORE și AFTER",
    "Compară imaginile",
    "Rulează analiza impactului",
    "Generează raportul PDF",
)

LAYER_GROUPS = (
    "Analiză SAR",
    "Dynamic World",
    "Corelare multisursă",
    "Impact OSM",
)


@dataclass
class ImpactToolState:
    county_name: str = "Galati"
    county_geometry: dict | None = None
    county_bbox: list[float] = field(default_factory=list)
    aoi_geometry: dict | None = None
    active_area_bbox: list[float] = field(default_factory=list)
    active_area_centroid: list[float] = field(default_factory=list)
    active_area_km2: float = 0.0
    active_area_hash: str = ""
    area_warnings: list[str] = field(default_factory=list)
    area_errors: list[str] = field(default_factory=list)
    before_scene: dict | None = None
    after_scene: dict | None = None
    scene_candidates: list[dict] = field(default_factory=list)
    scene_errors: list[str] = field(default_factory=list)
    scene_warnings: list[str] = field(default_factory=list)
    scene_query: dict = field(default_factory=dict)
    scene_gallery_limit: int = 8
    scene_current_id: str = ""
    preview_scene_id: str = ""
    preview_scene_tile: str = ""
    scenes_confirmed: bool = False
    comparison_ready: bool = False
    preview_mode: str = "Radar brut în tonuri de gri"
    preview_tiles: dict[str, str] = field(default_factory=dict)
    swipe_enabled: bool = False
    scene_compare_active: bool = False
    scene_compare_tiles: dict[str, str] = field(default_factory=dict)
    layer_compare_active: bool = False
    layer_compare_left_id: str = "sar_water_before"
    layer_compare_right_id: str = "sar_water_after"
    analysis_complete: bool = False
    buffer_meters: int = BUFFER_DEFAULT_METERS
    active_layers: list[str] = field(
        default_factory=lambda: ["sar_new_water", "buffer", "osm_critical"]
    )
    analysis_results: dict = field(default_factory=dict)
    analysis_parameters: dict = field(
        default_factory=lambda: {
            "water_threshold": -18.0,
            "smoothing_meters": 0,
            "minimum_connected_pixels": 8,
        }
    )
    analysis_error: str = ""
    analysis_running: bool = False
    analysis_mode: str = "rapid"
    run_requested: bool = False
    dynamic_world_requested: bool = False
    analysis_progress: int = 0
    analysis_stage: str = "Pregătit pentru analiză"
    osm_status: dict = field(default_factory=dict)
    osm_cache_refs: dict[str, str] = field(default_factory=dict)
    osm_load_requested: bool = False
    osm_retry_category: str = ""
    osm_filters: dict = field(
        default_factory=lambda: {
            "buildings": True,
            "roads": True,
            "railways": True,
            "bridges": True,
            "critical": True,
            "reference_buildings": True,
        }
    )
    critical_mode: bool = False
    presentation_mode: bool = False
    map_focus: list[float] = field(default_factory=list)
    preset_name: str = ""
    preset_cache_status: dict[str, dict] = field(default_factory=dict)
    event_date: str = ""
    reusable_cache: dict = field(default_factory=dict)
    cache_events: list[str] = field(default_factory=list)
    timings: dict[str, float] = field(default_factory=dict)
    analysis_hash: str = ""
    report_bytes: bytes | None = None
    report_requested: bool = False
    report_filename: str = ""
    draw_requested: bool = False

    @property
    def aoi_active(self) -> bool:
        return self.aoi_geometry is not None

    @property
    def can_run_analysis(self) -> bool:
        return self.scenes_confirmed

    @property
    def can_download_report(self) -> bool:
        return self.analysis_complete

    @property
    def active_geometry(self) -> dict | None:
        return self.aoi_geometry or self.county_geometry
