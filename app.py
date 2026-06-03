from __future__ import annotations

import json

from config.settings import (
    METHODOLOGICAL_NOTE,
    REPORTS_DIR,
    ensure_output_dirs,
    validate_analysis_parameters,
)
from src.app.layout import configure_page, sidebar_parameters
from src.app.map_builder import build_maps, build_placeholder_map
from src.app.progress_logger import ProgressLogger, render_progress
from src.app.results_panel import render_land_cover, render_methodological_note, render_metric_cards
from src.gee.dynamic_world import (
    dynamic_world_mode,
    land_cover_intersection_stats,
    summarize_land_cover,
)
from src.gee.gee_auth import AUTH_COMMANDS, initialize_earth_engine
from src.gee.permanent_water import permanent_water_mask
from src.gee.sar_flood_detection import detect_flood_extent
from src.gee.sar_preprocessing import build_before_after_composites
from src.gee.sentinel1_collection import build_aoi, count_scenes, get_sentinel1_collection
from src.gee.sentinel2_context import sentinel2_rgb_context
from src.reports.report_generator import generate_reports


def main() -> None:
    import streamlit as st
    from streamlit_folium import st_folium

    configure_page(st)
    params, run_analysis = sidebar_parameters(st)
    validation_warnings = validate_analysis_parameters(params.as_dict())

    st.write(
        "Dashboard pentru cartografierea unei extinderi preliminare detectate automat prin SAR "
        "si pentru tipuri de teren intersectate de extinderea detectata."
    )

    if validation_warnings:
        for warning in validation_warnings:
            st.warning(warning)

    if not run_analysis:
        maps = build_placeholder_map(params)
        st_folium(maps.main_map, use_container_width=True, height=520)
        render_methodological_note(st)
        return

    ensure_output_dirs()
    logger = ProgressLogger()
    logger.log(0, "Initializare analiza.")
    render_progress(st, logger)

    gee = initialize_earth_engine(interactive=False)
    if not gee.available:
        logger.warn(gee.message)
        st.error(gee.message)
        st.code("\n".join(AUTH_COMMANDS), language="powershell")
        st.info(
            "Autentificarea se face o singura data pe fiecare PC sau VM. "
            "Aplicatia nu ruleaza procesare raster locala si nu descarca automat GeoTIFF-uri."
        )
        maps = build_placeholder_map(params)
        st_folium(maps.main_map, use_container_width=True, height=520)
        render_progress(st, logger)
        render_methodological_note(st)
        return

    ee = gee.ee
    logger.log(10, "AOI incarcat.")
    aoi = build_aoi(ee, params.bbox)

    logger.log(20, "Cautare scene Sentinel-1.")
    before_collection = get_sentinel1_collection(
        ee,
        aoi,
        params.before_start_date,
        params.before_end_date,
        params.polarization,
        params.orbit_pass,
    )
    after_collection = get_sentinel1_collection(
        ee,
        aoi,
        params.after_start_date,
        params.after_end_date,
        params.polarization,
        params.orbit_pass,
    )
    before_count = count_scenes(before_collection)
    after_count = count_scenes(after_collection)
    logger.log(20, f"Au fost gasite {before_count} scene Sentinel-1 pentru perioada before.")
    logger.log(20, f"Au fost gasite {after_count} scene Sentinel-1 pentru perioada after.")

    if before_count == 0 or after_count == 0:
        message = (
            "Nu exista suficiente scene Sentinel-1 pentru intervalele selectate. "
            "Largeste perioada sau schimba orbit pass."
        )
        logger.warn(message)
        st.error(message)
        render_progress(st, logger)
        render_methodological_note(st)
        return

    logger.log(35, "S-a creat compozitul median SAR.")
    before_image, after_image = build_before_after_composites(
        before_collection,
        after_collection,
        ee,
        params.smoothing_radius,
    )

    logger.log(50, "Change detection SAR in cloud.")
    permanent_water = permanent_water_mask(ee, aoi) if params.mask_permanent_water else None
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
    logger.log(60, "A fost aplicata masca de apa permanenta.")
    logger.log(70, f"Suprafata preliminara detectata: {detection.detected_extent_km2} km2.")

    logger.log(80, "Analiza Dynamic World.")
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
    logger.log(80, "Analiza land cover a fost finalizata.")

    logger.log(90, "Generare harta.")
    layer_images = {
        "Sentinel-1 SAR before": before_image,
        "Sentinel-1 SAR after": after_image,
        "SAR change": detection.change_image,
        "permanent water": permanent_water,
        "detected flood extent": detection.flood_mask,
        "land cover": land_cover,
    }
    if params.show_sentinel2_rgb:
        layer_images["Sentinel-2 RGB"] = sentinel2_rgb_context(
            ee, aoi, str(params.before_start_date), str(params.after_end_date)
        )
    layer_images = {key: value for key, value in layer_images.items() if value is not None}
    maps = build_maps(layer_images, params)

    metrics = {
        "aoi": params.aoi_name,
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

    logger.log(97, "Raport generat.")
    report_paths = generate_reports(
        output_dir=REPORTS_DIR,
        analysis_parameters=params.as_dict(),
        metrics=metrics,
        land_cover_statistics=land_cover_stats,
        processing_log=[entry["message"] for entry in logger.entries],
        warnings=logger.warnings + detection.warnings,
    )
    logger.log(100, "Finalizat.")

    render_metric_cards(st, metrics)
    st.subheader("Harta principala")
    st_folium(maps.main_map, use_container_width=True, height=560)
    st.subheader("Slider vertical before / after")
    if maps.fallback_reason:
        st.info(maps.fallback_reason)
    st_folium(maps.comparison_map, use_container_width=True, height=560)
    render_land_cover(st, land_cover_stats)
    render_methodological_note(st)
    render_progress(st, logger)
    with st.expander("Rapoarte generate"):
        st.json({key: str(value) for key, value in report_paths.items()})
        st.download_button(
            "Descarca raport JSON",
            data=json.dumps(
                {
                    "metrics": metrics,
                    "land_cover_statistics": land_cover_stats,
                    "methodological_note": METHODOLOGICAL_NOTE,
                },
                indent=2,
                ensure_ascii=False,
            ),
            file_name="flood_impact_report.json",
            mime="application/json",
        )


if __name__ == "__main__":
    main()
