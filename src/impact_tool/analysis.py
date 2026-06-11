from __future__ import annotations

from collections.abc import Callable

from src.gee.gee_auth import initialize_earth_engine
from src.gee.sentinel1_collection import build_aoi_from_geometry
from src.impact_tool.cache import PersistentCache, analysis_hash
from src.impact_tool.dynamic_world import run_dynamic_world_analysis
from src.impact_tool.models import ImpactToolState
from src.impact_tool.osm import load_osm_categories, retry_osm_category
from src.impact_tool.osm_impact import classify_osm_impact
from src.impact_tool.sar import SarParameters, run_sar_analysis


ProgressCallback = Callable[[int, str], None]


def execute_analysis(
    state: ImpactToolState,
    progress_callback: ProgressCallback | None = None,
    load_osm: bool = True,
) -> bool:
    if not state.scenes_confirmed or not state.before_scene or not state.after_scene:
        state.analysis_error = "Confirmă imaginile BEFORE și AFTER înainte de analiză."
        return False
    state.analysis_running = True
    state.analysis_error = ""
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
        state.cache_events.append("Analiza SAR strict BEFORE / AFTER a fost finalizată.")
        _progress(state, progress_callback, 55, "Calcul apă nouă evidențiată prin SAR")
        try:
            _progress(
                state,
                progress_callback,
                62,
                "Analiză Dynamic World și corelare multisursă",
            )
            state.analysis_results["dynamic_world"] = run_dynamic_world_analysis(
                gee.ee,
                aoi,
                state.before_scene,
                state.after_scene,
                sar["products"]["sar_new_water"],
            )
            state.cache_events.append("Diferențele observate Dynamic World au fost calculate.")
        except Exception as exc:
            state.analysis_results["dynamic_world_error"] = str(exc)
            state.cache_events.append(
                "Dynamic World nu a putut fi calculat; rezultatul SAR rămâne disponibil."
            )
        state.analysis_hash = analysis_hash(
            state.active_area_hash,
            state.before_scene["ee_id"],
            state.after_scene["ee_id"],
            state.analysis_parameters,
        )
        state.analysis_complete = True
        state.active_layers = ["sar_new_water", "buffer", "osm_critical"]
        if load_osm:
            _progress(state, progress_callback, 75, "Încărcare automată OpenStreetMap")
            execute_osm_loading(state, progress_callback=progress_callback)
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


def execute_osm_loading(
    state: ImpactToolState,
    progress_callback: ProgressCallback | None = None,
) -> bool:
    if not state.analysis_complete:
        state.analysis_error = "Datele OSM pot fi încărcate numai după analiza SAR."
        return False
    try:
        arguments = {
            "analysis_complete": True,
            "aoi_hash": state.active_area_hash,
            "bbox": state.active_area_bbox,
            "geometry": state.active_geometry or {},
            "cache": PersistentCache(),
        }
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
            result = load_osm_categories(**arguments)
            state.analysis_results["osm_raw"] = result
            state.osm_status = result["status"]
        state.cache_events.append("Încărcarea OSM pe categorii a fost finalizată.")
        _progress(
            state,
            progress_callback,
            92,
            "Clasificare impact OSM direct și în buffer",
        )
        recalculate_osm_impact(state)
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
    state.analysis_results["osm_impact"] = classify_osm_impact(
        raw.get("layers", {}),
        water_geometry,
        state.buffer_meters,
    )
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
