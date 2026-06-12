from __future__ import annotations

from collections.abc import Callable
from time import perf_counter
from typing import Any

from src.gee.gee_auth import initialize_earth_engine
from src.gee.sentinel1_collection import build_aoi_from_geometry
from src.impact_tool.cache import PersistentCache, analysis_hash
from src.impact_tool.dynamic_world import (
    correlate_osm_dynamic_world,
    run_dynamic_world_analysis,
)
from src.impact_tool.models import ImpactToolState
from src.impact_tool.osm import load_osm_categories, retry_osm_category
from src.impact_tool.osm_impact import buffered_geometry, classify_osm_impact
from src.impact_tool.sar import SarParameters, run_sar_analysis
from src.impact_tool.state import record_timing


ProgressCallback = Callable[[int, str], None]


def execute_analysis(
    state: ImpactToolState,
    progress_callback: ProgressCallback | None = None,
    load_osm: bool = True,
    mode: str | None = None,
) -> bool:
    if not state.scenes_confirmed or not state.before_scene or not state.after_scene:
        state.analysis_error = "Confirmă imaginile BEFORE și AFTER înainte de analiză."
        return False
    state.analysis_running = True
    state.analysis_error = ""
    state.analysis_mode = mode or state.analysis_mode or "rapid"
    _progress(state, progress_callback, 5, "Inițializare Google Earth Engine")
    try:
        gee = initialize_earth_engine()
        if not gee.available or gee.ee is None:
            state.analysis_error = gee.message
            return False
        _progress(state, progress_callback, 15, "Pregătire arie activă și parametri SAR")
        aoi = build_aoi_from_geometry(gee.ee, state.active_geometry, state.active_area_bbox)
        parameters = SarParameters(**state.analysis_parameters)
        _progress(state, progress_callback, 25, "Calcul apă observată BEFORE și AFTER")
        sar = run_sar_analysis(
            gee.ee,
            aoi,
            state.before_scene,
            state.after_scene,
            parameters,
        )
        state.analysis_results["sar"] = sar
        record_timing(state, "SAR", sar.get("duration_seconds", 0))
        record_timing(
            state,
            "vectorizare",
            sar.get("vectorization_duration_seconds", 0),
        )
        state.preview_scene_id = ""
        state.preview_scene_tile = ""
        state.cache_events.append("Analiza SAR strict BEFORE / AFTER a fost finalizată.")
        _progress(state, progress_callback, 55, "Calcul apă nouă evidențiată prin SAR")

        if state.analysis_mode == "detaliat":
            _progress(
                state,
                progress_callback,
                62,
                "Analiză Dynamic World și corelare multisursă",
            )
            execute_dynamic_world(state, gee=gee, aoi=aoi)
        else:
            state.analysis_results.pop("dynamic_world", None)
            state.analysis_results.pop("dynamic_world_error", None)
            state.cache_events.append(
                "Mod rapid: etapa Dynamic World a fost omisă intenționat."
            )

        state.analysis_hash = analysis_hash(
            state.active_area_hash,
            state.before_scene["ee_id"],
            state.after_scene["ee_id"],
            {**state.analysis_parameters, "analysis_mode": state.analysis_mode},
        )
        state.analysis_complete = True
        state.active_layers = ["sar_new_water", "buffer", "osm_critical"]
        if load_osm:
            _progress(state, progress_callback, 75, "Încărcare automată OpenStreetMap")
            execute_osm_loading(
                state,
                progress_callback=progress_callback,
                gee_status=gee,
            )
        _progress(state, progress_callback, 100, "Analiza impactului a fost finalizată")
        return True
    except Exception as exc:
        state.analysis_error = f"Analiza SAR nu a putut fi finalizată: {exc}"
        _progress(
            state,
            progress_callback,
            state.analysis_progress,
            "Analiza s-a oprit cu eroare",
        )
        return False
    finally:
        state.analysis_running = False
        state.run_requested = False


def execute_dynamic_world(
    state: ImpactToolState,
    *,
    gee: Any | None = None,
    aoi: Any | None = None,
) -> bool:
    sar = state.analysis_results.get("sar")
    if not sar or not state.before_scene or not state.after_scene:
        state.analysis_results["dynamic_world_error"] = (
            "Dynamic World necesită mai întâi o analiză SAR finalizată."
        )
        state.dynamic_world_requested = False
        return False
    started = perf_counter()
    try:
        gee_status = gee or initialize_earth_engine()
        if not gee_status.available or gee_status.ee is None:
            raise RuntimeError(gee_status.message)
        active_aoi = aoi or build_aoi_from_geometry(
            gee_status.ee,
            state.active_geometry,
            state.active_area_bbox,
        )
        result = run_dynamic_world_analysis(
            gee_status.ee,
            active_aoi,
            state.before_scene,
            state.after_scene,
            sar["products"]["sar_new_water"],
        )
        state.analysis_results["dynamic_world"] = result
        if result.get("status") == "reușit":
            if "dynamic_world_new_water" not in state.active_layers:
                state.active_layers.append("dynamic_world_new_water")
            state.analysis_results.pop("dynamic_world_error", None)
        else:
            state.analysis_results["dynamic_world_error"] = (
                result.get("error") or result.get("status")
            )
        state.cache_events.append(
            "Diferențele observate Dynamic World au fost calculate."
        )
        return True
    except Exception as exc:
        state.analysis_results["dynamic_world_error"] = str(exc)
        state.cache_events.append(
            "Dynamic World nu a putut fi calculat; rezultatul SAR rămâne disponibil."
        )
        return False
    finally:
        record_timing(state, "Dynamic World", perf_counter() - started)
        state.dynamic_world_requested = False


def execute_osm_loading(
    state: ImpactToolState,
    progress_callback: ProgressCallback | None = None,
    gee_status: Any | None = None,
) -> bool:
    if not state.analysis_complete:
        state.analysis_error = "Datele OSM pot fi încărcate numai după analiza SAR."
        return False
    try:
        query_geometry, query_bbox = buffered_geometry(
            state.active_geometry or {},
            1000,
        )
        arguments = {
            "analysis_complete": True,
            "aoi_hash": state.active_area_hash,
            "bbox": query_bbox,
            "geometry": query_geometry,
            "cache": PersistentCache(),
            "analysis_mode": state.analysis_mode,
        }
        osm_started = perf_counter()
        if state.osm_retry_category:
            result = retry_osm_category(
                category=state.osm_retry_category,
                **arguments,
            )
            current = state.analysis_results.get(
                "osm_raw",
                {"layers": {}, "status": {}, "attribution": result["attribution"]},
            )
            current["layers"].update(result["layers"])
            current["status"].update(result["status"])
            state.analysis_results["osm_raw"] = current
            state.osm_status.update(result["status"])
        else:
            categories = (
                ("buildings", "roads", "bridges", "critical")
                if state.analysis_mode == "rapid"
                else ("buildings", "roads", "railways", "bridges", "critical")
            )
            result = load_osm_categories(categories=categories, **arguments)
            state.analysis_results["osm_raw"] = result
            state.osm_status = result["status"]
        record_timing(state, "cache OSM", perf_counter() - osm_started)
        state.cache_events.append("Încărcarea OSM pe categorii a fost finalizată.")
        _progress(
            state,
            progress_callback,
            92,
            "Clasificare impact OSM direct și în buffer",
        )
        recalculate_osm_impact(state)
        dynamic = state.analysis_results.get("dynamic_world")
        impact = state.analysis_results.get("osm_impact")
        if dynamic and impact and dynamic.get("status") == "reușit":
            active_gee = gee_status or initialize_earth_engine()
            if active_gee.available and active_gee.ee is not None:
                state.analysis_results["osm_dynamic_world"] = (
                    correlate_osm_dynamic_world(
                        active_gee.ee,
                        dynamic,
                        impact,
                    )
                )
        return True
    except Exception as exc:
        state.analysis_error = (
            "Analiza raster a fost finalizată, dar datele OSM nu au putut fi "
            f"încărcate: {exc}"
        )
        return False
    finally:
        state.osm_load_requested = False
        state.osm_retry_category = ""


def recalculate_osm_impact(state: ImpactToolState) -> bool:
    raw = state.analysis_results.get("osm_raw")
    sar = state.analysis_results.get("sar")
    water_geometry = (sar or {}).get("new_water_geometry")
    if not raw or not water_geometry:
        return False
    impact_started = perf_counter()
    state.analysis_results["osm_impact"] = classify_osm_impact(
        raw.get("layers", {}),
        water_geometry,
        state.buffer_meters,
        active_geometry=state.active_geometry,
    )
    record_timing(state, "impact OSM", perf_counter() - impact_started)
    state.cache_events.append(
        f"Impactul OSM a fost recalculat pentru bufferul de {state.buffer_meters} m."
    )
    return True


def _progress(
    state: ImpactToolState,
    callback: ProgressCallback | None,
    percent: int,
    stage: str,
) -> None:
    state.analysis_progress = max(0, min(100, int(percent)))
    state.analysis_stage = stage
    if callback:
        callback(state.analysis_progress, stage)
