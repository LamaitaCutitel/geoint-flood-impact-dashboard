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
    selected_county_feature,
)
from src.app.layout import configure_page, sidebar_parameters
from src.app.map_builder import build_county_overview_map, build_maps
from src.app.progress_logger import ProgressLogger
from src.app.results_panel import render_land_cover, render_metric_cards
from src.gee.dynamic_world import (
    dynamic_world_mode,
    land_cover_intersection_stats,
    summarize_land_cover,
)
from src.gee.gee_auth import AUTH_COMMANDS, initialize_earth_engine, local_earthengine_status
from src.gee.permanent_water import permanent_water_mask
from src.gee.sar_flood_detection import detect_flood_extent
from src.gee.sar_preprocessing import build_before_after_composites
from src.gee.sentinel1_collection import (
    build_aoi_from_geometry,
    count_scenes,
    get_sentinel1_collection,
)
from src.gee.sentinel2_context import sentinel2_rgb_context
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

    params, run_analysis = sidebar_parameters(
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

    if SHOW_DEBUG_PANELS:
        _render_service_status(
            st,
            counties_available=boundary_result.available,
            gee_available=gee_available,
            project_configured=bool(settings.gee_project_id),
            last_analysis_available="last_analysis_result" in st.session_state,
        )

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

    overview_map = build_county_overview_map(counties_geojson, params.county_name, params.bbox)
    st_folium(overview_map, use_container_width=True, height=650)

    validation_warnings = validate_analysis_parameters(params.as_dict())
    for warning in validation_warnings:
        st.warning(warning)

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

    if "last_analysis_result" in st.session_state:
        _render_analysis_result(st, st.session_state.last_analysis_result)


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
) -> None:
    st.subheader("Status servicii")
    cols = st.columns(3)
    statuses = [
        ("Interfata Streamlit", "disponibila", "success"),
        ("GeoJSON judete", "disponibil" if counties_available else "lipsa", "success" if counties_available else "error"),
        ("Google Earth Engine", "initializat" if gee_available else "neinitializat", "success" if gee_available else "warning"),
        ("GEE_PROJECT_ID", "configurat" if project_configured else "lipsa", "success" if project_configured else "warning"),
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


def _run_analysis(st: Any, params: Any, counties_geojson: dict[str, Any] | None, ee: Any) -> None:
    ensure_output_dirs()
    logger = ProgressLogger()
    st.session_state.analysis_logger = logger
    logger.log(2, f"Analiza pornita pentru judetul selectat: {params.county_name}.")

    try:
        logger.log(8, "Se construieste AOI-ul judetului.")
        aoi = build_aoi_from_geometry(ee, params.county_geometry, params.bbox)

        logger.log(15, "Se cauta scene Sentinel-1 pentru perioada before.")
        before_collection = get_sentinel1_collection(
            ee,
            aoi,
            params.before_start_date,
            params.before_end_date,
            params.polarization,
            params.orbit_pass,
        )
        before_count = count_scenes(before_collection)
        logger.log(22, f"Au fost gasite {before_count} scene before.")

        logger.log(28, "Se cauta scene Sentinel-1 pentru perioada after.")
        after_collection = get_sentinel1_collection(
            ee,
            aoi,
            params.after_start_date,
            params.after_end_date,
            params.polarization,
            params.orbit_pass,
        )
        after_count = count_scenes(after_collection)
        logger.log(35, f"Au fost gasite {after_count} scene after.")

        if before_count == 0:
            raise RuntimeError("Lipsesc scene Sentinel-1 pentru perioada before.")
        if after_count == 0:
            raise RuntimeError("Lipsesc scene Sentinel-1 pentru perioada after.")

        logger.log(42, "Se creeaza compozitul median before.")
        logger.log(48, "Se creeaza compozitul median after.")
        logger.log(52, "Se aplica filtrul pentru reducerea zgomotului speckle.")
        before_image, after_image = build_before_after_composites(
            before_collection,
            after_collection,
            ee,
            params.smoothing_radius,
        )

        logger.log(58, "Se calculeaza diferenta SAR.")
        logger.log(62, "Se aplica pragul SAR.")
        permanent_water = None
        if params.mask_permanent_water:
            logger.log(66, "Se elimina apa permanenta.")
            permanent_water = permanent_water_mask(ee, aoi)
        else:
            logger.warn("Masca de apa permanenta este dezactivata.")

        logger.log(70, "Se elimina pixelii izolati.")
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

        logger.log(82, "Se analizeaza tipurile de teren cu Dynamic World.")
        land_cover = dynamic_world_mode(
            ee,
            aoi,
            str(params.before_start_date),
            str(params.after_end_date),
        )
        land_cover_stats = land_cover_intersection_stats(
            ee,
            land_cover,
            detection.flood_mask,
            aoi,
            params.scale,
        )
        land_cover_summary = summarize_land_cover(land_cover_stats)

        logger.log(88, "Se genereaza layerele hartii.")
        layer_images = _layer_images(params, before_image, after_image, detection, permanent_water, land_cover, ee, aoi)
        maps = build_maps(layer_images, params, counties_geojson)

        metrics = {
            "aoi": params.aoi_name,
            "county_name": params.county_name,
            "before_period": f"{params.before_start_date} - {params.before_end_date}",
            "after_period": f"{params.after_start_date} - {params.after_end_date}",
            "scene_count_before": before_count,
            "scene_count_after": after_count,
            "sar_detected_extent_km2": detection.detected_extent_km2,
            "permanent_water_removed_km2": detection.permanent_water_removed_km2,
            "dominant_land_cover_class": land_cover_summary["dominant_class"],
            "crops_intersected_km2": land_cover_summary["crops_intersected_km2"],
            "built_up_intersected_km2": land_cover_summary["built_up_intersected_km2"],
            "vegetation_intersected_km2": land_cover_summary["vegetation_intersected_km2"],
            "processing_time": f"{logger.duration_seconds()} s",
        }

        logger.log(94, "Se genereaza raportul.")
        report_paths = generate_reports(
            output_dir=REPORTS_DIR,
            analysis_parameters=params.as_dict(),
            metrics=metrics,
            land_cover_statistics=land_cover_stats,
            processing_log=[entry["message"] for entry in logger.entries],
            warnings=logger.warnings + detection.warnings,
        )
        logger.log(100, "Analiza a fost finalizata.", "success")
        st.session_state.last_analysis_result = {
            "metrics": metrics,
            "land_cover_stats": land_cover_stats,
            "maps": maps,
            "logger": logger,
            "report_paths": report_paths,
        }
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
    land_cover: Any,
    ee: Any,
    aoi: Any,
) -> dict[str, Any]:
    layer_images = {}
    if params.show_sar_before:
        layer_images["Sentinel-1 SAR before"] = before_image
    if params.show_sar_after:
        layer_images["Sentinel-1 SAR after"] = after_image
    if params.show_sar_change:
        layer_images["SAR change"] = detection.change_image
    if params.show_detected_flood_extent:
        layer_images["detected flood extent"] = detection.flood_mask
    if params.show_permanent_water and permanent_water is not None:
        layer_images["permanent water"] = permanent_water
    if params.show_land_cover:
        layer_images["land cover"] = land_cover
    if params.show_sentinel2_rgb:
        layer_images["Sentinel-2 RGB"] = sentinel2_rgb_context(
            ee, aoi, str(params.before_start_date), str(params.after_end_date)
        )
    return layer_images


def _render_analysis_result(st: Any, result: dict[str, Any]) -> None:
    if SHOW_DEBUG_PANELS:
        render_metric_cards(st, result["metrics"])
    st_folium = __import__("streamlit_folium").st_folium
    st_folium(result["maps"].main_map, use_container_width=True, height=650)
    if result["maps"].comparison_map:
        if result["maps"].fallback_reason:
            st.info(result["maps"].fallback_reason)
        st_folium(result["maps"].comparison_map, use_container_width=True, height=650)
    if SHOW_DEBUG_PANELS:
        render_land_cover(st, result["land_cover_stats"])
        with st.expander("Rapoarte generate", expanded=False):
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
