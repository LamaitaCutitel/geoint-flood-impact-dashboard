from __future__ import annotations

import json
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
from src.app.layer_registry import LayerRegistry
from src.app.layout import configure_page, sidebar_parameters
from src.app.map_builder import build_county_overview_map, build_maps, build_result_map_from_registry_payload, build_sar_preview_map
from src.app.progress_logger import ProgressLogger, bootstrap_startup_logger, render_progress
from src.app.results_panel import render_land_cover, render_metric_cards
from src.gee.dynamic_world import (
    dynamic_world_change_map,
    dynamic_world_mode,
    land_cover_intersection_stats,
    summarize_land_cover,
)
from src.gee.collection_metadata import collection_scene_dates, dates_metadata
from src.gee.gee_config import COLLECTIONS
from src.gee.dem_layers import build_dem_products
from src.gee.gee_auth import AUTH_COMMANDS, initialize_earth_engine, local_earthengine_status
from src.gee.permanent_water import permanent_water_mask
from src.gee.sar_flood_detection import detect_flood_extent
from src.gee.sar_preprocessing import build_before_after_composites
from src.gee.gee_tile_layers import ee_tile_url
from src.gee.sentinel1_collection import (
    build_aoi_from_geometry,
    count_scenes,
    get_sentinel1_collection,
)
from src.gee.sentinel1_scene_explorer import (
    scene_recommendation_labels,
    search_sentinel1_scenes,
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
        render_progress(st, st.session_state.get("analysis_logger", startup_logger))

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


def _render_current_map(
    st: Any,
    counties_geojson: dict[str, Any] | None,
    selected_feature: dict[str, Any] | None,
    params: Any,
    available_counties: list[str],
) -> None:
    st_folium = __import__("streamlit_folium").st_folium
    last_result = st.session_state.get("last_analysis_result")
    preview = st.session_state.get("sar_preview")
    returned_objects = [
        "last_active_drawing",
        "last_object_clicked",
        "last_object_clicked_popup",
        "last_object_clicked_tooltip",
    ]
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
    if last_result and last_result.get("layer_registry") and last_result.get("analysis_params", {}).get("county_name") == params.county_name:
        result_map = build_result_map_from_registry_payload(
            last_result["layer_registry"],
            params,
            counties_geojson,
            selected_feature,
        )
        map_data = st_folium(
            result_map.main_map,
            use_container_width=True,
            height=760,
            returned_objects=returned_objects,
            key=f"primary-analysis-map-{st.session_state.get('map_generation', 0)}-{params.county_name}",
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
    st.session_state.pop("last_analysis_result", None)
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
    scenes = search_sentinel1_scenes(
        ee,
        aoi,
        params.before_start_date,
        params.after_end_date,
        params.polarization,
        params.orbit_pass,
    )
    step(55, f"Au fost gasite {len(scenes)} scene.")
    step(70, "Se calculeaza acoperirea judetului.")
    st.session_state.sar_scene_results = {
        "county_name": params.county_name,
        "search_key": _sar_search_key(params),
        "scenes": scenes,
    }
    st.session_state.sar_timeline_index = 0
    st.session_state.pop("sar_preview", None)
    st.session_state.pop("last_analysis_result", None)
    step(90, "Se genereaza previzualizarile.")
    step(100, "Exploratorul temporal este pregatit.", "success")


def _render_temporal_explorer(st: Any, params: Any, gee_available: bool) -> None:
    st.subheader("Explorator temporal Sentinel-1 SAR")
    results = st.session_state.get("sar_scene_results") or {}
    scenes = results.get("scenes") or []
    if results.get("search_key") != _sar_search_key(params):
        st.info("Apasa `Cauta imagini disponibile` pentru parametrii curenti.")
        _render_selected_pair_card(st, [])
        return
    if not scenes:
        st.info("Nu exista scene cautate pentru parametrii curenti.")
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
    labels = scene_recommendation_labels(scene, scenes, selected_before, selected_after)
    if labels:
        st.caption(" | ".join(labels))

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
        for warning in scene.get("warnings") or []:
            st.warning(warning)
    with cols[1]:
        if st.button("Selecteaza ca BEFORE", use_container_width=True):
            st.session_state.sar_before_scene = scene
            _update_pair_status(st)
            _log_selection(st, f"Scena {scene['display_id']} a fost selectata ca BEFORE.")
            st.rerun()
        if st.button("Selecteaza ca AFTER", use_container_width=True):
            st.session_state.sar_after_scene = scene
            _update_pair_status(st)
            _log_selection(st, f"Scena {scene['display_id']} a fost selectata ca AFTER.")
            st.rerun()
        if st.button("Afiseaza pe harta", use_container_width=True, disabled=not gee_available):
            gee_status = initialize_earth_engine(interactive=False)
            if not gee_status.available:
                st.error(gee_status.message)
            else:
                _show_scene_preview(st, params, scene, gee_status.ee)
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
        if "Recomandat pentru BEFORE" in scene_recommendation_labels(scene, scenes, None, None)
        or "Recomandat pentru AFTER" in scene_recommendation_labels(scene, scenes, None, None)
    ]
    if recommended:
        st.caption("Scene recomandate: " + ", ".join(scene["display_id"] for scene in recommended[:4]))


def _show_scene_preview(st: Any, params: Any, scene: dict[str, Any], ee: Any) -> None:
    aoi = build_aoi_from_geometry(ee, params.county_geometry, params.bbox)
    image = selected_scene_image(ee, scene, aoi, params.smoothing_radius)
    tile_url = ee_tile_url(image, "Sentinel-1 SAR before")
    if not tile_url:
        st.error("Nu s-a putut genera tile URL pentru scena curenta.")
        return
    st.session_state.sar_preview = {
        "county_name": params.county_name,
        "scene": scene,
        "tile_url": tile_url,
    }


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
        if pair_status.get("requires_confirmation") and not st.session_state.get("confirm_relative_orbit_mismatch"):
            raise RuntimeError("Confirma explicit folosirea perechii cu orbita relativa diferita.")

        if params.use_median_composite:
            ui_log(15, "Se cauta scene Sentinel-1 pentru compozitul median before.")
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
            ui_log(28, "Se cauta scene Sentinel-1 pentru compozitul median after.")
            after_collection = get_sentinel1_collection(
                ee,
                aoi,
                params.after_start_date,
                params.after_end_date,
                params.polarization,
                params.orbit_pass,
            )
            after_count = count_scenes(after_collection)
            s1_after_dates = collection_scene_dates(after_collection)
            if before_count == 0 or after_count == 0:
                raise RuntimeError("Lipsesc scene Sentinel-1 pentru compozitul median.")
            ui_log(42, "Se creeaza compozitul median before.")
            ui_log(48, "Se creeaza compozitul median after.")
            before_image, after_image = build_before_after_composites(
                before_collection,
                after_collection,
                ee,
                params.smoothing_radius,
                aoi,
            )
        else:
            ui_log(15, "Se incarca scena BEFORE selectata.")
            before_image = selected_scene_image(ee, before_scene, aoi, params.smoothing_radius)
            ui_log(28, "Se incarca scena AFTER selectata.")
            after_image = selected_scene_image(ee, after_scene, aoi, params.smoothing_radius)
            before_count = 1
            after_count = 1
            s1_before_dates = [before_scene["acquisition_time"]]
            s1_after_dates = [after_scene["acquisition_time"]]

        ui_log(52, "Se aplica crop dupa geometria judetului.")

        ui_log(58, "Se calculeaza diferenta SAR.")
        ui_log(62, "Se aplica pragul SAR.")
        permanent_water = None
        if params.mask_permanent_water:
            ui_log(66, "Se elimina apa permanenta si recurenta JRC.")
            permanent_water = permanent_water_mask(ee, aoi)
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
        land_cover_before = dynamic_world_mode(
            ee,
            aoi,
            str(params.before_start_date),
            str(params.before_end_date),
        )
        land_cover_after = dynamic_world_mode(
            ee,
            aoi,
            str(params.after_start_date),
            str(params.after_end_date),
        )
        dw_before_collection = (
            ee.ImageCollection(COLLECTIONS.dynamic_world)
            .filterBounds(aoi)
            .filterDate(str(params.before_start_date), str(params.before_end_date))
        )
        dw_after_collection = (
            ee.ImageCollection(COLLECTIONS.dynamic_world)
            .filterBounds(aoi)
            .filterDate(str(params.after_start_date), str(params.after_end_date))
        )
        dw_before_dates = collection_scene_dates(dw_before_collection)
        dw_after_dates = collection_scene_dates(dw_after_collection)
        land_cover_changes = dynamic_world_change_map(ee, land_cover_before, land_cover_after, aoi)
        land_cover_stats = land_cover_intersection_stats(
            ee,
            land_cover_after,
            detection.flood_mask,
            aoi,
            params.scale,
        )
        land_cover_summary = summarize_land_cover(land_cover_stats)

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
            s2_products,
            dem_products,
            layer_metadata,
        )
        selected_feature = selected_county_feature(counties_geojson, params.county_name) if counties_geojson else None
        maps = build_maps(layer_images, params, counties_geojson, selected_feature, registry)
        layer_registry_payload = maps.registry.report_payload() if maps.registry else {"available": [], "unavailable": []}
        ui_log(92, "Se actualizeaza harta interactiva.")

        metrics = {
            "aoi": params.aoi_name,
            "county_name": params.county_name,
            "before_period": f"{params.before_start_date} - {params.before_end_date}",
            "after_period": f"{params.after_start_date} - {params.after_end_date}",
            "scene_count_before": before_count,
            "scene_count_after": after_count,
            "sentinel2_scene_count_before": s2_products.scene_count_before,
            "sentinel2_scene_count_after": s2_products.scene_count_after,
            "sar_detected_extent_km2": detection.detected_extent_km2,
            "permanent_water_removed_km2": detection.permanent_water_removed_km2,
            "dominant_land_cover_class": land_cover_summary["dominant_class"],
            "crops_intersected_km2": land_cover_summary["crops_intersected_km2"],
            "built_up_intersected_km2": land_cover_summary["built_up_intersected_km2"],
            "vegetation_intersected_km2": land_cover_summary["vegetation_intersected_km2"],
            "processing_time": f"{logger.duration_seconds()} s",
        }

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
        }
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
    s2_products: Any,
    dem_products: Any,
    layer_metadata: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    layer_images: dict[str, dict[str, Any]] = {}
    def add(layer_id: str, display_name: str, category: str, layer_type: str, image: Any, shown: bool = False) -> None:
        if image is not None:
            layer_images[layer_id] = {
                "display_name": display_name,
                "category": category,
                "layer_type": layer_type,
                "image": image,
                "shown": shown,
                "comparable": True,
                "metadata": layer_metadata.get(layer_id),
            }

    if params.show_sar_before:
        add("sar_before", "Sentinel-1 SAR before", "Sentinel-1 SAR", "before", before_image, True)
    if params.show_sar_after:
        add("sar_after", "Sentinel-1 SAR after", "Sentinel-1 SAR", "after", after_image, True)
    if params.show_sar_change:
        add("sar_difference", "SAR difference", "Sentinel-1 SAR", "delta", detection.change_image.select("sar_difference"))
        add("sar_ratio", "SAR ratio", "Sentinel-1 SAR", "delta", detection.change_image.select("sar_ratio"))
    if params.show_detected_flood_extent:
        add("flood_extent", "detected flood extent", "Sentinel-1 SAR", "result", detection.flood_mask, True)
    if params.show_permanent_water and permanent_water is not None:
        add("permanent_water", "permanent water", "Date auxiliare", "static", permanent_water)
    if params.show_land_cover:
        add("dynamic_world_before", "Dynamic World before", "Land cover", "before", land_cover_before)
        add("dynamic_world_after", "Dynamic World after", "Land cover", "after", land_cover_after)
        add("land_cover_changes", "Land cover changes", "Land cover", "delta", land_cover_changes)
        add("intersected_land_cover", "land cover", "Land cover", "result", land_cover_after.updateMask(detection.flood_mask))
    if s2_products.rgb_before is not None:
        add("rgb_before", "RGB before", "Sentinel-2 optic", "before", s2_products.rgb_before)
    if s2_products.rgb_after is not None:
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
    for key, (display, layer_type) in index_names.items():
        add(key, display, "Sentinel-2 optic", layer_type, s2_products.indices.get(key))
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
        "Masca alternativa mai completa: occurrence >= 50% sau seasonality >= 10 luni/an.",
    )
    static_srtm = dates_metadata("USGS/SRTMGL1_003", ["2000-02"], "Date statice DEM SRTM.")
    metadata = {
        "sar_before": s1_before,
        "sar_after": s1_after,
        "sar_difference": dates_metadata("COPERNICUS/S1_GRD", sorted(set(s1_before_dates + s1_after_dates)), "Diferenta before - after."),
        "sar_ratio": dates_metadata("COPERNICUS/S1_GRD", sorted(set(s1_before_dates + s1_after_dates)), "Raport before / after."),
        "flood_extent": dates_metadata("COPERNICUS/S1_GRD + JRC GSW", sorted(set(s1_before_dates + s1_after_dates)), "Extindere preliminara detectata dupa prag SAR si masca apei recurente/permanente."),
        "permanent_water": static_jrc,
        "dynamic_world_before": dw_before,
        "dynamic_world_after": dw_after,
        "land_cover_changes": dw_change,
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
    with st.expander("Rezultate si rapoarte", expanded=False):
        render_metric_cards(st, result["metrics"])
        render_land_cover(st, result["land_cover_stats"])
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
