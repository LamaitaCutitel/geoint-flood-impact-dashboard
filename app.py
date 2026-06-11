from __future__ import annotations

import json
from datetime import datetime, timedelta
from typing import Any

from config.settings import (
    METHODOLOGICAL_NOTE,
    REPORTS_DIR,
    ensure_output_dirs,
    load_settings,
    validate_analysis_parameters,
)
from src.app.county_boundaries import (
    county_geometry,
    county_names,
    feature_bbox,
    load_or_download_counties,
    normalize_county_name,
    selected_county_feature,
)
from src.app.ems_validation import geojson_area_km2, validation_metrics
from src.app.layer_registry import LayerRegistry
from src.app.layout import configure_page, sidebar_parameters
from src.app.map_builder import (
    build_county_overview_map,
    build_maps,
    build_result_map_from_registry_payload,
    build_sar_candidate_compare_map,
    build_sar_preview_map,
)
from src.app.osm_impact import fetch_osm_operational_impact_payload
from src.app.progress_logger import ProgressLogger, bootstrap_startup_logger, render_progress
from src.app.results_panel import render_land_cover, render_metric_cards
from src.app.layer_styles import layer_style
from src.app.state import reset_county_dependent_state
from src.gee.dynamic_world import (
    dynamic_world_change_map,
    dynamic_world_mode,
    dynamic_world_water_change_masks,
    land_cover_intersection_stats,
    mask_area_km2,
    summarize_land_cover,
)
from src.gee.collection_metadata import collection_scene_dates, dates_metadata
from src.gee.gee_config import COLLECTIONS
from src.gee.dem_layers import build_dem_products
from src.gee.gee_auth import AUTH_COMMANDS, initialize_earth_engine, local_earthengine_status
from src.gee.permanent_water import permanent_water_mask
from src.gee.sar_flood_detection import detect_flood_extent
from src.gee.sar_preprocessing import median_composite, minimum_composite, smooth_sar
from src.gee.gee_tile_layers import ee_tile_url
from src.gee.sar_water_masks import (
    overlap_percent,
    sar_dynamic_world_overlap,
    sar_water_area_metrics,
    sar_water_change_masks,
    sar_water_mask,
    sar_water_threshold_for_mode,
)
from src.gee.sentinel1_collection import (
    build_aoi_from_geometry,
    count_scenes,
    get_sentinel1_collection,
)
from src.gee.sentinel1_scene_explorer import (
    scene_recommendation_labels,
    search_sentinel1_scenes_result,
    selected_scene_image,
    validate_scene_pair,
)
from src.gee.sentinel2_context import build_sentinel2_products
from src.reports.report_generator import generate_reports


GEE_NOT_READY_MESSAGE = (
    "Google Earth Engine nu este initializat. Ruleaza o singura data: "
    "python -m src.gee.gee_auth, apoi reporneste aplicatia. Verifica si "
    "GEE_PROJECT_ID in fisierul .env."
)

SHOW_DEBUG_PANELS = False


def main() -> None:
    import streamlit as st
    from streamlit_folium import st_folium

    configure_page(st)

    boundary_result = load_or_download_counties()
    counties_geojson = boundary_result.geojson
    names = county_names(counties_geojson) if counties_geojson else []
    selected_county = _selected_county(st, names)
    feature = selected_county_feature(counties_geojson, selected_county) if counties_geojson else None
    bbox = feature_bbox(feature)
    geometry = county_geometry(feature)

    settings = load_settings()
    local_gee = local_earthengine_status()
    gee_available = bool(st.session_state.get("gee_available", local_gee.available))
    analysis_can_start = bool(settings.gee_project_id)
    startup_logger = bootstrap_startup_logger(
        st,
        county_count=len(names),
        warnings=boundary_result.warnings,
        gee_available=gee_available,
        project_configured=bool(settings.gee_project_id),
    )
    _update_pair_status(st)

    params, search_images, run_analysis = sidebar_parameters(
        st,
        county_names=names,
        selected_county=selected_county,
        county_geometry=geometry,
        county_bbox=bbox,
        gee_available=analysis_can_start,
    )

    feature = selected_county_feature(counties_geojson, params.county_name) if counties_geojson else None
    params.bbox = feature_bbox(feature)
    params.county_geometry = county_geometry(feature)
    st.session_state._current_params_for_compare = params

    st.subheader("Harta interactiva")
    map_slot = st.container()

    if boundary_result.warnings:
        _render_friendly_error(
            st,
            "Limitele administrative nu sunt disponibile.",
            "Aplicatia poate porni, dar harta judetelor nu poate fi desenata complet.",
            "Verifica fisierul data/boundaries/romania_counties.geojson sau conexiunea catre Eurostat GISCO.",
            "\n".join(boundary_result.warnings),
        )

    if not gee_available:
        st.warning(GEE_NOT_READY_MESSAGE)
        st.code("\n".join(AUTH_COMMANDS), language="powershell")
    elif SHOW_DEBUG_PANELS:
        st.info(local_gee.message)

    validation_warnings = validate_analysis_parameters(params.as_dict())
    for warning in validation_warnings:
        st.warning(warning)

    _render_top_status_and_workflow(
        st,
        gee_available=bool(st.session_state.get("gee_available", gee_available)),
        counties_available=boundary_result.available,
        county_name=params.county_name,
    )

    with map_slot:
        _render_current_map(st, counties_geojson, feature, params, names)

    _render_temporal_explorer(st, params, analysis_can_start)

    if search_images:
        if validation_warnings:
            st.error("Corecteaza parametrii invalizi inainte de cautarea imaginilor.")
        elif not analysis_can_start:
            st.error(GEE_NOT_READY_MESSAGE)
        else:
            gee_status = initialize_earth_engine(interactive=False)
            st.session_state.gee_available = gee_status.available
            if not gee_status.available:
                st.error(gee_status.message)
                st.code("\n".join(AUTH_COMMANDS), language="powershell")
            else:
                _search_sar_scenes(st, params, gee_status.ee)
                st.rerun()

    if run_analysis:
        if validation_warnings:
            st.error("Corecteaza parametrii invalizi inainte de analiza.")
        elif not analysis_can_start:
            st.error(GEE_NOT_READY_MESSAGE)
        else:
            gee_status = initialize_earth_engine(interactive=False)
            st.session_state.gee_available = gee_status.available
            if not gee_status.available:
                st.error(gee_status.message)
                st.code("\n".join(AUTH_COMMANDS), language="powershell")
            else:
                _run_analysis(st, params, counties_geojson, gee_status.ee)

    with st.expander("Informatii secundare despre aplicatie", expanded=False):
        _render_service_status(
            st,
            counties_available=boundary_result.available,
            gee_available=bool(st.session_state.get("gee_available", gee_available)),
            project_configured=bool(settings.gee_project_id),
            last_analysis_available="last_analysis_result" in st.session_state,
            last_analysis=st.session_state.get("last_analysis_result"),
        )
        _render_usage(st)
        render_progress(st, st.session_state.get("analysis_logger", startup_logger), key_prefix="main_progress")

    if "last_analysis_result" in st.session_state:
        _render_secondary_analysis_result(st, st.session_state.last_analysis_result)


def _selected_county(st: Any, names: list[str]) -> str:
    if "selected_county" not in st.session_state:
        st.session_state.selected_county = "Galati" if "Galati" in names else (names[0] if names else "")
    if st.session_state.selected_county not in names and names:
        st.session_state.selected_county = "Galati" if "Galati" in names else names[0]
    return st.session_state.selected_county


def _render_service_status(
    st: Any,
    counties_available: bool,
    gee_available: bool,
    project_configured: bool,
    last_analysis_available: bool,
    last_analysis: dict[str, Any] | None = None,
) -> None:
    st.subheader("Status servicii")
    cols = st.columns(3)
    metrics = (last_analysis or {}).get("metrics", {})
    statuses = [
        ("Interfata Streamlit", "disponibila", "success"),
        ("GeoJSON judete", "disponibil" if counties_available else "lipsa", "success" if counties_available else "error"),
        ("Google Earth Engine", "initializat" if gee_available else "neinitializat", "success" if gee_available else "warning"),
        ("GEE_PROJECT_ID", "configurat" if project_configured else "lipsa", "success" if project_configured else "warning"),
        ("Sentinel-1", "disponibil" if metrics.get("scene_count_before") or metrics.get("scene_count_after") else "disponibil dupa analiza", "success" if last_analysis_available else "warning"),
        ("Sentinel-2", "disponibil" if metrics.get("sentinel2_scene_count_before") or metrics.get("sentinel2_scene_count_after") else "indisponibil pana la analiza", "success" if metrics.get("sentinel2_scene_count_before") or metrics.get("sentinel2_scene_count_after") else "warning"),
        ("Dynamic World", "disponibil" if last_analysis_available else "disponibil dupa analiza", "success" if last_analysis_available else "warning"),
        ("JRC water", "disponibil" if last_analysis_available else "disponibil dupa analiza", "success" if last_analysis_available else "warning"),
        ("Cache local", "disponibil", "success"),
        ("Ultima analiza", "disponibila" if last_analysis_available else "indisponibila", "success" if last_analysis_available else "warning"),
    ]
    for index, (label, value, status) in enumerate(statuses):
        with cols[index % 3].container(border=True):
            st.markdown(f"**{label}**")
            if status == "success":
                st.success(value)
            elif status == "error":
                st.error(value)
            else:
                st.warning(value)


def _render_usage(st: Any) -> None:
    with st.expander("Cum se foloseste aplicatia", expanded=True):
        st.markdown(
            """
1. Selecteaza judetul direct din harta sau din lista laterala.
2. Verifica perioadele inainte si dupa eveniment.
3. Ajusteaza parametrii doar daca este necesar.
4. Apasa `Ruleaza analiza SAR`.
5. Urmareste jurnalul live.
6. Exploreaza si compara layerele direct din harta.
7. Descarca raportul.
"""
        )


def _render_top_status_and_workflow(
    st: Any,
    gee_available: bool,
    counties_available: bool,
    county_name: str,
) -> None:
    scenes = st.session_state.get("sar_scene_results", {}).get("scenes") or []
    pair_status = st.session_state.get("sar_pair_status") or {}
    last_analysis = st.session_state.get("last_analysis_result")
    status_cols = st.columns(6)
    items = [
        ("Google Earth Engine", "ok" if gee_available else "lipsa"),
        ("Limite judete", "ok" if counties_available else "lipsa"),
        ("Judet selectat", county_name or "neselectat"),
        ("Scene Sentinel-1", str(len(scenes))),
        ("Pereche BEFORE/AFTER", "confirmata" if st.session_state.get("sar_pair_confirmed") else ("compatibila" if pair_status.get("compatible") else "incompleta")),
        ("Ultima analiza", "disponibila" if last_analysis else "indisponibila"),
    ]
    for col, (label, value) in zip(status_cols, items, strict=False):
        col.metric(label, value)

    steps = [
        ("Selecteaza judetul", bool(county_name)),
        ("Cauta imagini", bool(scenes)),
        ("Exploreaza si compara scene", bool(st.session_state.get("sar_candidate_compare") or st.session_state.get("sar_preview"))),
        ("Confirma BEFORE / AFTER", bool(st.session_state.get("sar_pair_confirmed"))),
        ("Ruleaza analiza finala", bool(last_analysis)),
        ("Interpreteaza si exporta", bool(last_analysis)),
    ]
    current_index = next((index for index, (_, done) in enumerate(steps) if not done), len(steps) - 1)
    labels = []
    for index, (label, done) in enumerate(steps):
        marker = "[x]" if done else ("[>]" if index == current_index else "[ ]")
        labels.append(f"{marker} {index + 1}. {label}")
    st.caption("  |  ".join(labels))


def _render_current_map(
    st: Any,
    counties_geojson: dict[str, Any] | None,
    selected_feature: dict[str, Any] | None,
    params: Any,
    available_counties: list[str],
) -> None:
    st_folium = __import__("streamlit_folium").st_folium
    last_result = st.session_state.get("last_analysis_result")
    candidate_compare = st.session_state.get("sar_candidate_compare")
    preview = st.session_state.get("sar_preview")
    returned_objects = [
        "last_active_drawing",
        "last_object_clicked",
        "last_object_clicked_popup",
        "last_object_clicked_tooltip",
    ]
    if last_result and last_result.get("layer_registry") and last_result.get("analysis_params", {}).get("county_name") == params.county_name:
        result_map = build_result_map_from_registry_payload(
            last_result["layer_registry"],
            params,
            counties_geojson,
            selected_feature,
            osm_layers=last_result.get("osm_layers"),
        )
        map_data = st_folium(
            result_map.main_map,
            use_container_width=True,
            height=760,
            returned_objects=returned_objects,
            key=f"primary-analysis-map-{st.session_state.get('map_generation', 0)}-{params.county_name}-{_selected_pair_key(st)}",
        )
        _handle_county_click(st, map_data, available_counties)
        return
    if candidate_compare and candidate_compare.get("county_name") == params.county_name:
        compare_map = build_sar_candidate_compare_map(
            candidate_compare["before_tile_url"],
            candidate_compare["after_tile_url"],
            candidate_compare["before_scene"],
            candidate_compare["after_scene"],
            params,
            counties_geojson,
            selected_feature,
        )
        map_data = st_folium(
            compare_map.main_map,
            use_container_width=True,
            height=760,
            returned_objects=returned_objects,
            key=f"primary-sar-candidate-compare-{candidate_compare.get('compare_key')}",
        )
        _handle_county_click(st, map_data, available_counties)
        return
    if preview and preview.get("tile_url") and preview.get("county_name") == params.county_name:
        preview_map = build_sar_preview_map(
            preview["tile_url"],
            preview["scene"],
            params,
            counties_geojson,
            selected_feature,
        )
        map_data = st_folium(
            preview_map.main_map,
            use_container_width=True,
            height=760,
            returned_objects=returned_objects,
            key=f"primary-sar-preview-{preview.get('scene', {}).get('ee_id')}",
        )
        _handle_county_click(st, map_data, available_counties)
        return
    overview_map = build_county_overview_map(
        counties_geojson,
        params.county_name,
        params.bbox,
        selected_feature=selected_feature,
        zoom_to_selected=bool(st.session_state.get("county_focus_requested", False)),
    )
    map_data = st_folium(
        overview_map.main_map,
        use_container_width=True,
        height=760,
        returned_objects=returned_objects,
        key=f"primary-overview-map-{params.county_name}",
    )
    _handle_county_click(st, map_data, available_counties)


def _handle_county_click(st: Any, map_data: dict[str, Any] | None, available_counties: list[str]) -> None:
    clicked_county = _clicked_county_name(map_data, available_counties)
    if not clicked_county or clicked_county == st.session_state.get("selected_county"):
        return
    st.session_state.selected_county = clicked_county
    st.session_state.county_focus_requested = True
    reset_county_dependent_state(st.session_state)
    st.rerun()


def _clicked_county_name(map_data: dict[str, Any] | None, available_counties: list[str]) -> str | None:
    if not map_data:
        return None
    valid_counties = set(available_counties)
    candidates: list[str] = []

    def collect(value: Any) -> None:
        if isinstance(value, dict):
            properties = value.get("properties")
            if isinstance(properties, dict):
                for key in ("NAME_LATN", "NUTS_NAME", "NAME"):
                    collect(properties.get(key))
            for item in value.values():
                collect(item)
        elif isinstance(value, list):
            for item in value:
                collect(item)
        elif isinstance(value, str):
            candidates.append(value.strip())

    for key in (
        "last_active_drawing",
        "last_object_clicked",
        "last_object_clicked_popup",
        "last_object_clicked_tooltip",
    ):
        collect(map_data.get(key))

    for candidate in candidates:
        normalized = normalize_county_name(candidate)
        if normalized in valid_counties:
            return normalized
        for county in available_counties:
            if county and county in candidate:
                return county
    return None


def _search_sar_scenes(st: Any, params: Any, ee: Any) -> None:
    logger = ProgressLogger()
    st.session_state.analysis_logger = logger
    progress = st.progress(0)
    status = st.empty()

    def step(percent: int, message: str, level: str = "info") -> None:
        logger.log(percent, message, level)
        progress.progress(percent)
        getattr(status, level if level in {"info", "success", "warning", "error"} else "info")(message)

    step(10, "Se cauta scene Sentinel-1 in intervalul selectat.")
    aoi = build_aoi_from_geometry(ee, params.county_geometry, params.bbox)
    step(30, "Se extrag metadatele orbitale.")
    search_result = search_sentinel1_scenes_result(
        ee,
        aoi,
        params.before_start_date,
        params.after_end_date,
        params.polarization,
        params.orbit_pass,
    )
    for warning in search_result.get("warnings", []):
        logger.warn(warning)
        status.warning(warning)
    for error in search_result.get("errors", []):
        logger.error(error.get("message", "Eroare Google Earth Engine."))
        status.error(error.get("message", "Eroare Google Earth Engine."))
    scenes = search_result.get("scenes", [])
    scenes = _attach_sar_thumbnails(ee, aoi, scenes)
    if search_result.get("errors"):
        step(55, "Cautarea scenelor s-a oprit din cauza unei erori GEE.", "error")
    elif not scenes:
        step(55, "Cautarea a reusit, dar nu exista scene pentru parametrii curenti.", "warning")
    else:
        step(55, f"Au fost gasite {len(scenes)} scene.")
    step(70, "Se calculeaza acoperirea judetului.")
    st.session_state.sar_scene_results = {
        "county_name": params.county_name,
        "search_key": _sar_search_key(params),
        "scenes": scenes,
        "warnings": search_result.get("warnings", []),
        "errors": search_result.get("errors", []),
        "query_duration": search_result.get("query_duration", 0),
        "query_parameters": search_result.get("query_parameters", {}),
    }
    st.session_state.sar_timeline_index = 0
    st.session_state.pop("sar_preview", None)
    st.session_state.pop("last_analysis_result", None)
    if search_result.get("errors"):
        return
    step(90, "Se genereaza previzualizarile.")
    if scenes:
        step(100, "Exploratorul temporal este pregatit.", "success")
    else:
        step(100, "Cautarea s-a finalizat fara scene disponibile.", "warning")


def _render_temporal_explorer(st: Any, params: Any, gee_available: bool) -> None:
    st.subheader("Explorator temporal Sentinel-1 SAR")
    results = st.session_state.get("sar_scene_results") or {}
    scenes = results.get("scenes") or []
    if results.get("search_key") != _sar_search_key(params):
        st.info("Apasa `Cauta imagini disponibile` pentru parametrii curenti.")
        _render_selected_pair_card(st, [])
        return
    for error in results.get("errors", []):
        st.error(error.get("message", "Eroare Google Earth Engine."))
        if error.get("details"):
            with st.expander("Detalii eroare GEE", expanded=False):
                st.code(error["details"])
    if results.get("errors"):
        _render_selected_pair_card(st, [])
        return
    for warning in results.get("warnings", []):
        st.warning(warning)
    if not scenes:
        st.info("Cautarea a reusit, dar nu exista scene Sentinel-1 pentru parametrii curenti.")
        _render_selected_pair_card(st, [])
        return

    index = st.slider(
        "Cronologie imagini Sentinel-1",
        min_value=0,
        max_value=len(scenes) - 1,
        value=min(int(st.session_state.get("sar_timeline_index", 0)), len(scenes) - 1),
        format="%d",
        help="Schimba scena curenta fara a rula analiza finala.",
    )
    st.session_state.sar_timeline_index = index
    scene = scenes[index]
    selected_before = st.session_state.get("sar_before_scene")
    selected_after = st.session_state.get("sar_after_scene")
    labels = scene_recommendation_labels(scene, scenes, selected_before, selected_after, params.event_date)
    if labels:
        st.caption(" | ".join(labels))
    preview_type = st.radio(
        "Tip preview SAR",
        ["Radar brut grayscale", "Doar apa SAR"],
        horizontal=True,
        key="sar_preview_type",
        help="Compara scena radar bruta sau doar pixelii candidati apa SAR.",
    )

    cols = st.columns([2, 1])
    with cols[0]:
        st.markdown(f"**Scena curenta:** `{scene['display_id']}`")
        st.write(
            {
                "data_ora_utc": scene["acquisition_time"],
                "satelit": scene["platform"],
                "polarizare": scene["polarization"],
                "orbit_pass": scene["orbit_pass"],
                "orbita_relativa": scene["relative_orbit"],
                "instrument_mode": scene["instrument_mode"],
                "rezolutie_m": scene["resolution_meters"],
                "acoperire_judet_%": scene["coverage_percent"],
            }
        )
        if scene.get("thumbnail_url"):
            st.image(scene["thumbnail_url"], caption="Thumbnail SAR", width=220)
        for warning in scene.get("warnings") or []:
            st.warning(warning)
    with cols[1]:
        if st.button("Selecteaza ca BEFORE", use_container_width=True):
            st.session_state.sar_before_scene = scene
            st.session_state.sar_pair_confirmed = False
            st.session_state.pop("sar_candidate_compare", None)
            _update_pair_status(st)
            _log_selection(st, f"Scena {scene['display_id']} a fost selectata ca BEFORE.")
            st.rerun()
        if st.button("Selecteaza ca AFTER", use_container_width=True):
            st.session_state.sar_after_scene = scene
            st.session_state.sar_pair_confirmed = False
            st.session_state.pop("sar_candidate_compare", None)
            _update_pair_status(st)
            _log_selection(st, f"Scena {scene['display_id']} a fost selectata ca AFTER.")
            st.rerun()
        if st.button("Afiseaza pe harta", use_container_width=True, disabled=not gee_available):
            gee_status = initialize_earth_engine(interactive=False)
            if not gee_status.available:
                st.error(gee_status.message)
            else:
                _show_scene_preview(st, params, scene, gee_status.ee, preview_type)
                st.rerun()

    _render_selected_pair_card(st, scenes)


def _render_selected_pair_card(st: Any, scenes: list[dict[str, Any]]) -> None:
    before = st.session_state.get("sar_before_scene")
    after = st.session_state.get("sar_after_scene")
    _update_pair_status(st)
    status = st.session_state.get("sar_pair_status") or {}
    with st.container(border=True):
        st.markdown("**Pereche SAR selectata**")
        cols = st.columns(2)
        _render_scene_summary(cols[0], "BEFORE", before)
        _render_scene_summary(cols[1], "AFTER", after)
        if status.get("errors"):
            for error in status["errors"]:
                st.error(error)
        if status.get("warnings"):
            for warning in status["warnings"]:
                st.warning(warning)
            st.checkbox(
                "Confirm folosirea perechii cu orbita relativa diferita",
                key="confirm_relative_orbit_mismatch",
            )
        if status.get("compatible"):
            st.success("Compatibilitatea perechii a fost verificata.")
            action_cols = st.columns(4)
            if action_cols[0].button("Compara candidatii", use_container_width=True):
                gee_status = initialize_earth_engine(interactive=False)
                if not gee_status.available:
                    st.error(gee_status.message)
                else:
                    _show_candidate_compare(st, gee_status.ee)
                    st.rerun()
            if action_cols[1].button("Confirma perechea pentru analiza", use_container_width=True):
                st.session_state.sar_pair_confirmed = True
                _log_selection(st, "Perechea BEFORE/AFTER a fost confirmata pentru analiza.")
                st.rerun()
            if action_cols[2].button("Iesi din comparatie", use_container_width=True):
                st.session_state.pop("sar_candidate_compare", None)
                st.rerun()
            if action_cols[3].button("Curata selectia BEFORE/AFTER", use_container_width=True):
                st.session_state.pop("sar_before_scene", None)
                st.session_state.pop("sar_after_scene", None)
                st.session_state.pop("sar_candidate_compare", None)
                st.session_state.sar_pair_confirmed = False
                st.rerun()
            if st.session_state.get("sar_pair_confirmed"):
                st.success("Pereche confirmata. Analiza finala este disponibila in sidebar.")
        elif scenes:
            _render_pair_recommendations(st, scenes)


def _render_scene_summary(container: Any, role: str, scene: dict[str, Any] | None) -> None:
    with container:
        container.markdown(f"**{role}**")
        if not scene:
            container.caption("Neselectat")
            return
        container.caption(scene["display_id"])
        container.write(
            {
                "data_ora_utc": scene["acquisition_time"],
                "polarizare": scene["polarization"],
                "orbit_pass": scene["orbit_pass"],
                "orbita_relativa": scene["relative_orbit"],
            }
        )


def _render_pair_recommendations(st: Any, scenes: list[dict[str, Any]]) -> None:
    st.info("Recomandare: alege scene cu aceeasi polarizare, directie de orbita si acoperire cat mai mare.")
    recommended = [
        scene
        for scene in scenes
        if "Recomandat BEFORE" in scene_recommendation_labels(scene, scenes, None, None, None)
        or "Recomandat AFTER" in scene_recommendation_labels(scene, scenes, None, None, None)
    ]
    if recommended:
        st.caption("Scene recomandate: " + ", ".join(scene["display_id"] for scene in recommended[:4]))


def _show_scene_preview(st: Any, params: Any, scene: dict[str, Any], ee: Any, preview_type: str) -> None:
    aoi = build_aoi_from_geometry(ee, params.county_geometry, params.bbox)
    image = selected_scene_image(ee, scene, aoi, params.smoothing_radius)
    layer_name = "Sentinel-1 SAR before"
    if preview_type == "Doar apa SAR":
        threshold = sar_water_threshold_for_mode(params.polarization, params.sar_water_mode, params.sar_water_threshold)
        image = sar_water_mask(image, threshold, aoi, params.minimum_connected_pixels)
        layer_name = "SAR water BEFORE"
    tile_url = ee_tile_url(image, layer_name)
    if not tile_url:
        st.error("Nu s-a putut genera tile URL pentru scena curenta.")
        return
    st.session_state.sar_preview = {
        "county_name": params.county_name,
        "scene": scene,
        "tile_url": tile_url,
    }


def _show_candidate_compare(st: Any, ee: Any) -> None:
    before = st.session_state.get("sar_before_scene")
    after = st.session_state.get("sar_after_scene")
    if not before or not after:
        st.error("Selecteaza mai intai candidatul BEFORE si candidatul AFTER.")
        return
    params = st.session_state.get("_current_params_for_compare")
    if params is None:
        st.error("Parametrii curenti nu sunt disponibili pentru comparatie.")
        return
    aoi = build_aoi_from_geometry(ee, params.county_geometry, params.bbox)
    before_image = selected_scene_image(ee, before, aoi, params.smoothing_radius)
    after_image = selected_scene_image(ee, after, aoi, params.smoothing_radius)
    before_layer_name = "Sentinel-1 SAR before"
    after_layer_name = "Sentinel-1 SAR after"
    if st.session_state.get("sar_preview_type") == "Doar apa SAR":
        threshold = sar_water_threshold_for_mode(params.polarization, params.sar_water_mode, params.sar_water_threshold)
        before_image = sar_water_mask(before_image, threshold, aoi, params.minimum_connected_pixels)
        after_image = sar_water_mask(after_image, threshold, aoi, params.minimum_connected_pixels)
        before_layer_name = "SAR water BEFORE"
        after_layer_name = "SAR water AFTER"
    before_tile = ee_tile_url(before_image, before_layer_name)
    after_tile = ee_tile_url(after_image, after_layer_name)
    if not before_tile or not after_tile:
        st.error("Nu s-au putut genera tile URL-urile pentru comparatia candidata.")
        return
    st.session_state.pop("sar_preview", None)
    st.session_state.sar_candidate_compare = {
        "county_name": params.county_name,
        "before_scene": before,
        "after_scene": after,
        "before_tile_url": before_tile,
        "after_tile_url": after_tile,
        "compare_key": f"{before.get('display_id')}-{after.get('display_id')}",
    }


def _attach_sar_thumbnails(ee: Any, aoi: Any, scenes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    enriched: list[dict[str, Any]] = []
    for scene in scenes:
        updated = dict(scene)
        try:
            image = selected_scene_image(ee, scene, aoi, 0)
            updated["thumbnail_url"] = image.getThumbURL(
                {
                    "region": aoi,
                    "dimensions": 180,
                    "min": -25,
                    "max": 0,
                    "palette": ["111827", "e5e7eb"],
                }
            )
        except Exception:
            updated["thumbnail_url"] = None
        enriched.append(updated)
    return enriched


def _update_pair_status(st: Any) -> None:
    status = validate_scene_pair(st.session_state.get("sar_before_scene"), st.session_state.get("sar_after_scene"))
    st.session_state.sar_pair_status = status


def _log_selection(st: Any, message: str) -> None:
    logger = st.session_state.get("analysis_logger") or ProgressLogger()
    logger.log(100, message, "success")
    logger.log(100, "Compatibilitatea perechii a fost verificata.")
    st.session_state.analysis_logger = logger


def _sar_search_key(params: Any) -> tuple[Any, ...]:
    return (
        params.county_name,
        str(params.before_start_date),
        str(params.after_end_date),
        params.polarization,
        params.orbit_pass,
    )


def _selected_pair_key(st: Any) -> str:
    before = st.session_state.get("sar_before_scene") or {}
    after = st.session_state.get("sar_after_scene") or {}
    before_id = str(before.get("display_id") or "before").replace(" ", "_")
    after_id = str(after.get("display_id") or "after").replace(" ", "_")
    return f"{before_id}-{after_id}"


def _short_window_around_scene(scene: dict[str, Any], days: int = 2) -> tuple[str, str]:
    acquisition_time = scene.get("acquisition_time")
    if not acquisition_time:
        raise RuntimeError("Scena AFTER selectata nu are acquisition_time pentru fereastra scurta.")
    center = datetime.fromisoformat(str(acquisition_time).replace("Z", "+00:00")).date()
    start = center - timedelta(days=days)
    end = center + timedelta(days=days + 1)
    return start.isoformat(), end.isoformat()


def _run_analysis(st: Any, params: Any, counties_geojson: dict[str, Any] | None, ee: Any) -> None:
    ensure_output_dirs()
    logger = ProgressLogger()
    st.session_state.analysis_logger = logger
    status_text = st.empty()
    progress_bar = st.progress(0)

    def ui_log(percent: int, message: str) -> None:
        logger.log(percent, message)
        progress_bar.progress(min(max(percent, 0), 100))
        status_text.info(message)

    ui_log(2, f"Analiza pornita pentru judetul selectat: {params.county_name}.")

    try:
        ui_log(8, "Se construieste AOI-ul judetului.")
        aoi = build_aoi_from_geometry(ee, params.county_geometry, params.bbox)

        before_scene = st.session_state.get("sar_before_scene")
        after_scene = st.session_state.get("sar_after_scene")
        pair_status = validate_scene_pair(before_scene, after_scene)
        if not pair_status.get("compatible"):
            raise RuntimeError("Perechea SAR selectata nu este compatibila pentru analiza finala.")
        if not st.session_state.get("sar_pair_confirmed"):
            raise RuntimeError("Confirma perechea BEFORE/AFTER inainte de analiza finala.")
        if pair_status.get("requires_confirmation") and not st.session_state.get("confirm_relative_orbit_mismatch"):
            raise RuntimeError("Confirma explicit folosirea perechii cu orbita relativa diferita.")

        if params.before_sar_method == "Compozit median din scene compatibile":
            ui_log(15, "Se cauta scene Sentinel-1 pentru metoda BEFORE median.")
            before_collection = get_sentinel1_collection(
                ee,
                aoi,
                params.before_start_date,
                params.before_end_date,
                params.polarization,
                params.orbit_pass,
            )
            before_count = count_scenes(before_collection)
            s1_before_dates = collection_scene_dates(before_collection)
            if before_count == 0:
                raise RuntimeError("Lipsesc scene Sentinel-1 pentru metoda BEFORE median.")
            ui_log(42, "Se creeaza compozitul median BEFORE.")
            before_image = smooth_sar(median_composite(before_collection), ee, params.smoothing_radius).clip(aoi)
        else:
            ui_log(15, "Se incarca scena BEFORE selectata.")
            before_image = selected_scene_image(ee, before_scene, aoi, params.smoothing_radius)
            before_count = 1
            s1_before_dates = [before_scene["acquisition_time"]]

        if params.after_sar_method == "Scena individuala selectata manual":
            ui_log(28, "Se incarca scena AFTER selectata.")
            after_image = selected_scene_image(ee, after_scene, aoi, params.smoothing_radius)
            after_count = 1
            s1_after_dates = [after_scene["acquisition_time"]]
        else:
            after_start, after_end = _short_window_around_scene(after_scene, days=2)
            method_label = (
                "minimum SAR exploratoriu"
                if params.after_sar_method == "Minimum SAR / percentila joasa exploratorie"
                else "compozitul median AFTER pe interval scurt"
            )
            ui_log(28, f"Se cauta scene Sentinel-1 pentru {method_label}.")
            after_collection = get_sentinel1_collection(
                ee,
                aoi,
                after_start,
                after_end,
                params.polarization,
                params.orbit_pass,
            )
            after_count = count_scenes(after_collection)
            s1_after_dates = collection_scene_dates(after_collection)
            if after_count == 0:
                raise RuntimeError("Lipsesc scene Sentinel-1 pentru metoda AFTER selectata.")
            ui_log(48, f"Se creeaza {method_label}.")
            if params.after_sar_method == "Minimum SAR / percentila joasa exploratorie":
                after_image = smooth_sar(minimum_composite(after_collection), ee, params.smoothing_radius).clip(aoi)
                logger.warn("Metoda AFTER minimum SAR / percentila joasa este exploratorie si necesita interpretare prudenta.")
            else:
                after_image = smooth_sar(median_composite(after_collection), ee, params.smoothing_radius).clip(aoi)

        ui_log(52, "Se aplica crop dupa geometria judetului.")
        sar_water_threshold = sar_water_threshold_for_mode(
            params.polarization,
            params.sar_water_mode,
            params.sar_water_threshold,
        )
        ui_log(54, "Se clasifica apa SAR in scena BEFORE.")
        sar_water_before = sar_water_mask(
            before_image,
            sar_water_threshold,
            aoi,
            params.minimum_connected_pixels,
        )
        ui_log(56, "Se clasifica apa SAR in scena AFTER.")
        sar_water_after = sar_water_mask(
            after_image,
            sar_water_threshold,
            aoi,
            params.minimum_connected_pixels,
        )
        ui_log(57, "Se calculeaza apa noua, apa persistenta si pierderea de apa SAR.")
        sar_water_changes = sar_water_change_masks(sar_water_before, sar_water_after, aoi)
        sar_water_masks = {
            "sar_water_before": sar_water_before,
            "sar_water_after": sar_water_after,
            **sar_water_changes,
        }
        sar_water_metrics = sar_water_area_metrics(ee, sar_water_masks, aoi, params.scale)

        ui_log(58, "Se calculeaza diferenta SAR.")
        ui_log(62, "Se aplica pragul SAR.")
        permanent_water = None
        if params.mask_permanent_water:
            ui_log(66, "Se elimina apa permanenta si recurenta JRC.")
            permanent_water = permanent_water_mask(ee, aoi, params.jrc_water_mode)
        else:
            logger.warn("Masca de apa permanenta este dezactivata.")

        ui_log(70, "Se elimina pixelii izolati.")
        detection = detect_flood_extent(
            ee=ee,
            before_image=before_image,
            after_image=after_image,
            aoi=aoi,
            threshold=params.threshold,
            minimum_connected_pixels=params.minimum_connected_pixels,
            scale=params.scale,
            permanent_water=permanent_water,
        )
        logger.log(76, "Se calculeaza suprafata preliminara detectata.")

        ui_log(78, "Se cauta imagini Sentinel-2.")
        ui_log(80, "Se aplica masca de nori Sentinel-2.")
        ui_log(82, "Se genereaza RGB, NDWI, MNDWI, NDVI si NDMI.")
        s2_products = build_sentinel2_products(
            ee,
            aoi,
            str(params.before_start_date),
            str(params.before_end_date),
            str(params.after_start_date),
            str(params.after_end_date),
        )
        s2_before_dates = collection_scene_dates(s2_products.before_collection)
        s2_after_dates = collection_scene_dates(s2_products.after_collection)
        for warning in s2_products.warnings:
            logger.warn(warning)

        ui_log(84, "Se proceseaza Dynamic World.")
        dw_after_start = str(params.after_start_date)
        dw_after_end = str(params.after_end_date)
        dw_after_mode_used = params.dynamic_world_after_mode
        if params.dynamic_world_after_mode == "Fereastra apropiata de scena SAR AFTER":
            dw_after_start, dw_after_end = _short_window_around_scene(after_scene, days=2)
        land_cover_before = dynamic_world_mode(
            ee,
            aoi,
            str(params.before_start_date),
            str(params.before_end_date),
        )
        dw_before_collection = (
            ee.ImageCollection(COLLECTIONS.dynamic_world)
            .filterBounds(aoi)
            .filterDate(str(params.before_start_date), str(params.before_end_date))
        )
        dw_after_collection = (
            ee.ImageCollection(COLLECTIONS.dynamic_world)
            .filterBounds(aoi)
            .filterDate(dw_after_start, dw_after_end)
        )
        dw_before_dates = collection_scene_dates(dw_before_collection)
        dw_after_dates = collection_scene_dates(dw_after_collection)
        if params.dynamic_world_after_mode == "Fereastra apropiata de scena SAR AFTER" and not dw_after_dates:
            logger.warn("Nu exista Dynamic World in fereastra apropiata de scena SAR AFTER. Se foloseste intervalul complet AFTER.")
            dw_after_start = str(params.after_start_date)
            dw_after_end = str(params.after_end_date)
            dw_after_mode_used = "Interval complet"
            dw_after_collection = (
                ee.ImageCollection(COLLECTIONS.dynamic_world)
                .filterBounds(aoi)
                .filterDate(dw_after_start, dw_after_end)
            )
            dw_after_dates = collection_scene_dates(dw_after_collection)
        land_cover_after = dynamic_world_mode(
            ee,
            aoi,
            dw_after_start,
            dw_after_end,
        )
        land_cover_changes = dynamic_world_change_map(ee, land_cover_before, land_cover_after, aoi)
        water_change_masks = dynamic_world_water_change_masks(
            land_cover_before,
            land_cover_after,
            detection.flood_mask,
            aoi,
        )
        sar_dw_overlap_masks = sar_dynamic_world_overlap(
            sar_water_changes["sar_new_water"],
            water_change_masks["dynamic_world_new_water"],
            aoi,
        )
        dynamic_world_new_water_km2 = mask_area_km2(ee, water_change_masks["dynamic_world_new_water"], aoi, params.scale)
        dynamic_world_water_loss_km2 = mask_area_km2(ee, water_change_masks["dynamic_world_water_loss"], aoi, params.scale)
        sar_dw_overlap_metrics = sar_water_area_metrics(ee, sar_dw_overlap_masks, aoi, params.scale)
        sar_dw_intersection_km2 = sar_dw_overlap_metrics["sar_dynamic_world_new_water_overlap_area_km2"]
        sar_dw_overlap_percent = overlap_percent(
            sar_dw_intersection_km2,
            sar_water_metrics["sar_new_water_area_km2"],
        )
        land_cover_stats = land_cover_intersection_stats(
            ee,
            land_cover_after,
            detection.flood_mask,
            aoi,
            params.scale,
        )
        land_cover_summary = summarize_land_cover(land_cover_stats)

        dem_products = None
        if params.load_optional_layers:
            ui_log(86, "Se genereaza DEM, hillshade si slope.")
            dem_products = build_dem_products(ee, aoi)

        ui_log(88, "Se aplica crop dupa geometria judetului pentru toate layerele.")
        ui_log(90, "Se genereaza tile layers GEE.")
        registry = LayerRegistry()
        layer_metadata = _layer_metadata(
            s1_before_dates=s1_before_dates,
            s1_after_dates=s1_after_dates,
            s2_before_dates=s2_before_dates,
            s2_after_dates=s2_after_dates,
            dw_before_dates=dw_before_dates,
            dw_after_dates=dw_after_dates,
            jrc_water_mode=params.jrc_water_mode,
        )
        layer_images = _layer_images(
            params,
            before_image,
            after_image,
            detection,
            permanent_water,
            land_cover_before,
            land_cover_after,
            land_cover_changes,
            water_change_masks,
            sar_water_masks,
            sar_dw_overlap_masks,
            s2_products,
            dem_products,
            layer_metadata,
        )
        osm_metrics: dict[str, Any] = {}
        osm_layers: dict[str, dict[str, Any]] = {}
        if params.show_osm_impact:
            ui_log(91, "Se interogheaza OpenStreetMap pentru expunere operationala estimata.")
            try:
                osm_payload = fetch_osm_operational_impact_payload(
                    params.bbox,
                    buffer_meters=params.osm_buffer_meters,
                    limit=params.osm_query_limit,
                    county_geometry=params.county_geometry,
                )
                osm_metrics = osm_payload["metrics"]
                osm_layers = osm_payload["layers"]
                if osm_metrics.get("osm_query_errors"):
                    logger.warn(
                        "Unele categorii OSM nu au raspuns la timp: "
                        + "; ".join(str(item) for item in osm_metrics["osm_query_errors"])
                    )
            except Exception as exc:
                logger.warn(f"Impactul operational OSM nu a putut fi calculat: {exc}")
                osm_metrics = {
                    "osm_buildings_potentially_affected": 0,
                    "osm_roads_intersected_km": 0.0,
                    "osm_critical_assets": 0,
                    "osm_railways_intersected_km": 0.0,
                    "osm_bridges": 0,
                    "osm_query_buffer_m": params.osm_buffer_meters,
                    "osm_query_limit": params.osm_query_limit,
                    "osm_elements_returned": 0,
                    "osm_query_errors": [str(exc)],
                }
        selected_feature = selected_county_feature(counties_geojson, params.county_name) if counties_geojson else None
        maps = build_maps(layer_images, params, counties_geojson, selected_feature, registry, osm_layers=osm_layers)
        layer_registry_payload = maps.registry.report_payload() if maps.registry else {"available": [], "unavailable": []}
        ui_log(92, "Se actualizeaza harta interactiva.")

        metrics = {
            "aoi": params.aoi_name,
            "county_name": params.county_name,
            "before_period": f"{params.before_start_date} - {params.before_end_date}",
            "after_period": f"{params.after_start_date} - {params.after_end_date}",
            "scene_count_before": before_count,
            "scene_count_after": after_count,
            "sar_before_scene_id": (before_scene or {}).get("display_id"),
            "sar_after_scene_id": (after_scene or {}).get("display_id"),
            "before_sar_method": params.before_sar_method,
            "after_sar_method": params.after_sar_method,
            "sar_before_acquisition_time": (before_scene or {}).get("acquisition_time"),
            "sar_after_acquisition_time": (after_scene or {}).get("acquisition_time"),
            "sar_before_relative_orbit": (before_scene or {}).get("relative_orbit"),
            "sar_after_relative_orbit": (after_scene or {}).get("relative_orbit"),
            "sar_before_coverage_percent": (before_scene or {}).get("coverage_percent"),
            "sar_after_coverage_percent": (after_scene or {}).get("coverage_percent"),
            "sentinel2_scene_count_before": s2_products.scene_count_before,
            "sentinel2_scene_count_after": s2_products.scene_count_after,
            "sar_detected_extent_km2": detection.detected_extent_km2,
            "sar_water_threshold": sar_water_threshold,
            "sar_water_mode": params.sar_water_mode,
            "sar_water_before_area_km2": sar_water_metrics["sar_water_before_area_km2"],
            "sar_water_after_area_km2": sar_water_metrics["sar_water_after_area_km2"],
            "sar_new_water_area_km2": sar_water_metrics["sar_new_water_area_km2"],
            "sar_persistent_water_area_km2": sar_water_metrics["sar_persistent_water_area_km2"],
            "sar_water_loss_area_km2": sar_water_metrics["sar_water_loss_area_km2"],
            "permanent_water_removed_km2": detection.permanent_water_removed_km2,
            "dynamic_world_new_water_km2": round(dynamic_world_new_water_km2, 4),
            "dynamic_world_water_loss_km2": round(dynamic_world_water_loss_km2, 4),
            "dynamic_world_after_mode": dw_after_mode_used,
            "dynamic_world_after_period": f"{dw_after_start} - {dw_after_end}",
            "sar_dynamic_world_new_water_intersection_km2": round(sar_dw_intersection_km2, 4),
            "new_water_only_sar_area_km2": sar_dw_overlap_metrics["new_water_only_sar_area_km2"],
            "new_water_only_dynamic_world_area_km2": sar_dw_overlap_metrics["new_water_only_dynamic_world_area_km2"],
            "sar_dynamic_world_overlap_percent": sar_dw_overlap_percent,
            "dominant_land_cover_class": land_cover_summary["dominant_class"],
            "crops_intersected_km2": land_cover_summary["crops_intersected_km2"],
            "built_up_intersected_km2": land_cover_summary["built_up_intersected_km2"],
            "vegetation_intersected_km2": land_cover_summary["vegetation_intersected_km2"],
            "processing_time": f"{logger.duration_seconds()} s",
            "jrc_water_mode": params.jrc_water_mode,
        }
        metrics.update(osm_metrics)

        ui_log(94, "Se calculeaza statisticile.")
        ui_log(97, "Se genereaza raportul.")
        report_paths = generate_reports(
            output_dir=REPORTS_DIR,
            analysis_parameters=params.as_dict(),
            metrics=metrics,
            land_cover_statistics=land_cover_stats,
            processing_log=[entry["message"] for entry in logger.entries],
            warnings=logger.warnings + detection.warnings,
            layer_registry=layer_registry_payload,
            processing_log_json=logger.as_json(),
            osm_layers=osm_layers,
        )
        logger.log(100, "Analiza a fost finalizata.", "success")
        progress_bar.progress(100)
        status_text.success("Analiza a fost finalizata. Harta se actualizeaza.")
        st.session_state.last_analysis_result = {
            "metrics": metrics,
            "land_cover_stats": land_cover_stats,
            "layer_registry": layer_registry_payload,
            "analysis_params": params.as_dict(),
            "logger": logger,
            "report_paths": report_paths,
            "osm_layers": osm_layers,
        }
        st.session_state.pop("sar_preview", None)
        st.session_state.map_generation = st.session_state.get("map_generation", 0) + 1
        st.rerun()
    except Exception as exc:
        logger.error(str(exc))
        _render_friendly_error(
            st,
            "Analiza nu a putut fi finalizata.",
            "Fluxul a fost oprit controlat, fara sa blocheze interfata.",
            "Verifica autentificarea GEE, intervalele de date si orbit pass. Pentru lipsa scenelor, largeste intervalele.",
            repr(exc),
        )


def _layer_images(
    params: Any,
    before_image: Any,
    after_image: Any,
    detection: Any,
    permanent_water: Any,
    land_cover_before: Any,
    land_cover_after: Any,
    land_cover_changes: Any,
    water_change_masks: dict[str, Any],
    sar_water_masks: dict[str, Any],
    sar_dw_overlap_masks: dict[str, Any],
    s2_products: Any,
    dem_products: Any,
    layer_metadata: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    layer_images: dict[str, dict[str, Any]] = {}
    def add(layer_id: str, display_name: str, category: str, layer_type: str, image: Any, shown: bool = False) -> None:
        if image is not None:
            style = layer_style(layer_id)
            metadata = layer_metadata.get(layer_id) or {}
            if style.get("description") and not metadata.get("details"):
                metadata = {**metadata, "details": style["description"]}
            layer_images[layer_id] = {
                "display_name": style.get("display_name", display_name),
                "category": style.get("category", category),
                "layer_type": layer_type,
                "image": image,
                "shown": shown,
                "comparable": True,
                "metadata": metadata,
            }

    if params.show_sar_before:
        add("sar_before", "Sentinel-1 SAR before", "Sentinel-1 SAR", "before", before_image, True)
    if params.show_sar_after:
        add("sar_after", "Sentinel-1 SAR after", "Sentinel-1 SAR", "after", after_image, True)
    if params.show_sar_water_layers:
        add("sar_water_before", "SAR water BEFORE", "Apa observata prin SAR", "before", sar_water_masks.get("sar_water_before"))
        add("sar_water_after", "SAR water AFTER", "Apa observata prin SAR", "after", sar_water_masks.get("sar_water_after"))
        add("sar_new_water", "SAR new water", "Apa observata prin SAR", "result", sar_water_masks.get("sar_new_water"), True)
        if params.load_optional_layers:
            add("sar_persistent_water", "SAR persistent water", "Apa observata prin SAR", "result", sar_water_masks.get("sar_persistent_water"))
            add("sar_water_loss", "SAR water loss", "Apa observata prin SAR", "delta", sar_water_masks.get("sar_water_loss"))
    if params.show_sar_change:
        add("sar_difference", "SAR difference", "Sentinel-1 SAR", "delta", detection.change_image.select("sar_difference"))
        add("sar_ratio", "SAR ratio", "Sentinel-1 SAR", "delta", detection.change_image.select("sar_ratio"))
    if params.show_detected_flood_extent:
        add("flood_extent", "SAR flood extent filtrat", "Apa observata prin SAR", "result", detection.flood_mask)
    if params.show_permanent_water and permanent_water is not None:
        add("permanent_water", "permanent water", "Date auxiliare", "static", permanent_water)
    if params.show_land_cover:
        add("dynamic_world_before", "Dynamic World before", "Land cover", "before", land_cover_before)
        add("dynamic_world_after", "Dynamic World after", "Land cover", "after", land_cover_after)
        add("dynamic_world_new_water", "Dynamic World - apa noua", "Cresterea apei - Dynamic World", "result", water_change_masks.get("dynamic_world_new_water"), True)
        if params.load_optional_layers:
            add("land_cover_changes", "Land cover changes", "Land cover", "delta", land_cover_changes)
            add("dynamic_world_water_loss", "Dynamic World - pierdere apa", "Cresterea apei - Dynamic World", "delta", water_change_masks.get("dynamic_world_water_loss"))
            add("dynamic_world_other_change", "Dynamic World - alte diferente", "Cresterea apei - Dynamic World", "delta", water_change_masks.get("dynamic_world_other_change"))
        if params.show_sar_dynamic_world_correlation:
            add("sar_dynamic_world_new_water_overlap", "SAR x Dynamic World new water overlap", "Corelare SAR x Dynamic World", "result", sar_dw_overlap_masks.get("sar_dynamic_world_new_water_overlap"), True)
            if params.load_optional_layers:
                add("new_water_only_sar", "New water only SAR", "Corelare SAR x Dynamic World", "result", sar_dw_overlap_masks.get("new_water_only_sar"))
                add("new_water_only_dynamic_world", "New water only Dynamic World", "Corelare SAR x Dynamic World", "result", sar_dw_overlap_masks.get("new_water_only_dynamic_world"))
        if params.load_optional_layers:
            add("intersected_land_cover", "land cover", "Land cover", "result", land_cover_after.updateMask(detection.flood_mask))
    if params.load_optional_layers and s2_products.rgb_before is not None:
        add("rgb_before", "RGB before", "Sentinel-2 optic", "before", s2_products.rgb_before)
    if params.load_optional_layers and s2_products.rgb_after is not None:
        add("rgb_after", "RGB after", "Sentinel-2 optic", "after", s2_products.rgb_after)
    index_names = {
        "ndwi_before": ("NDWI before", "before"),
        "ndwi_after": ("NDWI after", "after"),
        "delta_ndwi": ("Delta NDWI", "delta"),
        "mndwi_before": ("MNDWI before", "before"),
        "mndwi_after": ("MNDWI after", "after"),
        "delta_mndwi": ("Delta MNDWI", "delta"),
        "ndvi_before": ("NDVI before", "before"),
        "ndvi_after": ("NDVI after", "after"),
        "delta_ndvi": ("Delta NDVI", "delta"),
        "ndmi_before": ("NDMI before", "before"),
        "ndmi_after": ("NDMI after", "after"),
        "delta_ndmi": ("Delta NDMI", "delta"),
    }
    if params.load_optional_layers:
        for key, (display, layer_type) in index_names.items():
            add(key, display, "Sentinel-2 optic", layer_type, s2_products.indices.get(key))
    if params.load_optional_layers and dem_products is not None:
        add("dem", "DEM", "Date auxiliare", "static", dem_products.dem)
        add("hillshade", "Hillshade", "Date auxiliare", "static", dem_products.hillshade)
        add("slope", "Slope", "Date auxiliare", "static", dem_products.slope)
    return layer_images


def _layer_metadata(
    s1_before_dates: list[str],
    s1_after_dates: list[str],
    s2_before_dates: list[str],
    s2_after_dates: list[str],
    dw_before_dates: list[str],
    dw_after_dates: list[str],
    jrc_water_mode: str,
) -> dict[str, dict[str, Any]]:
    s1_before = dates_metadata("COPERNICUS/S1_GRD", s1_before_dates, "Compozit median SAR before.")
    s1_after = dates_metadata("COPERNICUS/S1_GRD", s1_after_dates, "Compozit median SAR after.")
    s2_before = dates_metadata("COPERNICUS/S2_SR_HARMONIZED", s2_before_dates, "Compozit median optic before, cu masca nori.")
    s2_after = dates_metadata("COPERNICUS/S2_SR_HARMONIZED", s2_after_dates, "Compozit median optic after, cu masca nori.")
    dw_before = dates_metadata("GOOGLE/DYNAMICWORLD/V1", dw_before_dates, "Clasa modala Dynamic World before.")
    dw_after = dates_metadata("GOOGLE/DYNAMICWORLD/V1", dw_after_dates, "Clasa modala Dynamic World after.")
    dw_change = dates_metadata(
        "GOOGLE/DYNAMICWORLD/V1",
        sorted(set(dw_before_dates + dw_after_dates)),
        "Categorii: neschimbat, alta schimbare, apa pierduta, apa noua.",
    )
    static_jrc = dates_metadata(
        "JRC/GSW1_4/GlobalSurfaceWater",
        ["1984-2021"],
        f"Mod masca JRC: {jrc_water_mode}. Conservator >=90, Echilibrat >=75, Extins >=50 sau seasonality >=10.",
    )
    static_srtm = dates_metadata("USGS/SRTMGL1_003", ["2000-02"], "Date statice DEM SRTM.")
    metadata = {
        "sar_before": s1_before,
        "sar_after": s1_after,
        "sar_water_before": dates_metadata("COPERNICUS/S1_GRD", s1_before_dates, "Pixeli SAR compatibili cu apa in scena BEFORE."),
        "sar_water_after": dates_metadata("COPERNICUS/S1_GRD", s1_after_dates, "Pixeli SAR compatibili cu apa in scena AFTER."),
        "sar_new_water": dates_metadata("COPERNICUS/S1_GRD", sorted(set(s1_before_dates + s1_after_dates)), "Apa observata prin SAR in AFTER, absenta in BEFORE."),
        "sar_persistent_water": dates_metadata("COPERNICUS/S1_GRD", sorted(set(s1_before_dates + s1_after_dates)), "Apa observata prin SAR atat in BEFORE, cat si in AFTER."),
        "sar_water_loss": dates_metadata("COPERNICUS/S1_GRD", sorted(set(s1_before_dates + s1_after_dates)), "Apa observata prin SAR in BEFORE, absenta in AFTER."),
        "sar_difference": dates_metadata("COPERNICUS/S1_GRD", sorted(set(s1_before_dates + s1_after_dates)), "Diferenta before - after."),
        "sar_ratio": dates_metadata("COPERNICUS/S1_GRD", sorted(set(s1_before_dates + s1_after_dates)), "Raport before / after."),
        "flood_extent": dates_metadata("COPERNICUS/S1_GRD + JRC GSW", sorted(set(s1_before_dates + s1_after_dates)), "SAR flood extent filtrat: change detection, filtrare spatiala si masca JRC configurabila."),
        "permanent_water": static_jrc,
        "dynamic_world_before": dw_before,
        "dynamic_world_after": dw_after,
        "land_cover_changes": dw_change,
        "dynamic_world_new_water": dates_metadata("GOOGLE/DYNAMICWORLD/V1", sorted(set(dw_before_dates + dw_after_dates)), "Apa noua evidentiata prin Dynamic World: non-apa BEFORE -> apa AFTER."),
        "dynamic_world_water_loss": dates_metadata("GOOGLE/DYNAMICWORLD/V1", sorted(set(dw_before_dates + dw_after_dates)), "Pierdere apa evidentiata prin Dynamic World: apa BEFORE -> non-apa AFTER."),
        "dynamic_world_other_change": dates_metadata("GOOGLE/DYNAMICWORLD/V1", sorted(set(dw_before_dates + dw_after_dates)), "Diferente observate intre clasificari, excluzand apa noua si pierderea de apa."),
        "sar_dynamic_world_new_water_overlap": dates_metadata("COPERNICUS/S1_GRD + GOOGLE/DYNAMICWORLD/V1", sorted(set(s1_before_dates + s1_after_dates + dw_before_dates + dw_after_dates)), "Zone de apa noua identificate de SAR water si Dynamic World."),
        "new_water_only_sar": dates_metadata("COPERNICUS/S1_GRD + GOOGLE/DYNAMICWORLD/V1", sorted(set(s1_before_dates + s1_after_dates + dw_before_dates + dw_after_dates)), "Apa noua observata prin SAR, fara corespondent Dynamic World."),
        "new_water_only_dynamic_world": dates_metadata("COPERNICUS/S1_GRD + GOOGLE/DYNAMICWORLD/V1", sorted(set(s1_before_dates + s1_after_dates + dw_before_dates + dw_after_dates)), "Apa noua Dynamic World, fara corespondent SAR water."),
        "intersected_land_cover": dates_metadata("GOOGLE/DYNAMICWORLD/V1 + flood mask", dw_after_dates, "Terenuri after intersectate cu extinderea detectata."),
        "rgb_before": s2_before,
        "rgb_after": s2_after,
        "dem": static_srtm,
        "hillshade": static_srtm,
        "slope": static_srtm,
    }
    for index_name in ("ndwi", "mndwi", "ndvi", "ndmi"):
        metadata[f"{index_name}_before"] = s2_before
        metadata[f"{index_name}_after"] = s2_after
        metadata[f"delta_{index_name}"] = dates_metadata(
            "COPERNICUS/S2_SR_HARMONIZED",
            sorted(set(s2_before_dates + s2_after_dates)),
            f"Diferenta {index_name.upper()} after - before.",
        )
    return metadata


def _render_secondary_analysis_result(st: Any, result: dict[str, Any]) -> None:
    with st.expander("Rezultate si rapoarte", expanded=True):
        tabs = st.tabs(["Rezumat", "Cronologie", "Impact asupra mediului", "Validare", "Jurnal tehnic", "Export"])
        with tabs[0]:
            render_metric_cards(st, result["metrics"])
            st.write(
                {
                    "BEFORE": result["metrics"].get("sar_before_scene_id"),
                    "AFTER": result["metrics"].get("sar_after_scene_id"),
                    "Interpretare": "Rezultate GEOINT preliminare; nu reprezinta confirmare oficiala din teren.",
                }
            )
        with tabs[1]:
            scenes = st.session_state.get("sar_scene_results", {}).get("scenes") or []
            if scenes:
                st.dataframe(scenes, use_container_width=True, hide_index=True)
            else:
                st.info("Cronologia SAR va fi disponibila dupa cautarea scenelor.")
        with tabs[2]:
            render_land_cover(st, result["land_cover_stats"])
        with tabs[3]:
            _render_ems_validation(st, result)
        with tabs[4]:
            logger = result.get("logger")
            if logger:
                render_progress(st, logger, key_prefix="results_progress")
                st.download_button(
                    "Descarca jurnal JSON",
                    data=logger.as_json(),
                    file_name="analysis_log.json",
                    mime="application/json",
                    key="results_analysis_log_json",
                )
        with tabs[5]:
            st.json({key: str(value) for key, value in result["report_paths"].items()})
            st.download_button(
                "Descarca raport JSON",
                data=json.dumps(
                    {
                        "metrics": result["metrics"],
                        "land_cover_statistics": result["land_cover_stats"],
                        "methodological_note": METHODOLOGICAL_NOTE,
                    },
                    indent=2,
                    ensure_ascii=False,
                ),
                file_name="flood_impact_report.json",
                mime="application/json",
                key="results_flood_impact_report_json",
            )


def _render_ems_validation(st: Any, result: dict[str, Any]) -> None:
    st.caption("EMS este tratat ca produs operational de referinta, nu ca adevar absolut.")
    upload = st.file_uploader(
        "Incarca produs Copernicus EMS",
        type=["geojson", "json", "gpkg", "zip"],
        help="GeoJSON este calculat local. GPKG si Shapefile ZIP necesita suport geospatial suplimentar.",
    )
    if upload is None:
        st.info("Incarca un GeoJSON EMS pentru calcularea ariei produsului de referinta.")
        return
    suffix = upload.name.lower().rsplit(".", 1)[-1]
    if suffix not in {"geojson", "json"}:
        st.warning("Format acceptat pentru upload, dar calculul local este disponibil acum doar pentru GeoJSON.")
        return
    try:
        ems_area = geojson_area_km2(upload.getvalue())
    except Exception as exc:
        st.error("Produsul EMS nu a putut fi citit ca GeoJSON valid.")
        st.code(str(exc))
        return
    sar_area = float(result["metrics"].get("sar_detected_extent_km2", 0.0) or 0.0)
    st.warning(
        "Intersectia spatiala SAR-EMS necesita o geometrie vectoriala SAR. In acest ecran, "
        "seteaza manual aria de intersectie daca ai calculat-o extern."
    )
    intersection = st.number_input(
        "Arie intersectie SAR x EMS km2",
        min_value=0.0,
        max_value=float(max(sar_area, ems_area)),
        value=0.0,
        step=0.1,
    )
    metrics = validation_metrics(sar_area, ems_area, intersection)
    st.dataframe(
        [{"indicator": key, "valoare": value} for key, value in metrics.items()],
        hide_index=True,
        use_container_width=True,
    )


def _render_friendly_error(
    st: Any,
    title: str,
    explanation: str,
    next_step: str,
    technical_detail: str,
) -> None:
    st.error(title)
    st.write(explanation)
    st.info(next_step)
    with st.expander("Detalii tehnice scurte", expanded=False):
        st.code(technical_detail)


if __name__ == "__main__":
    main()
