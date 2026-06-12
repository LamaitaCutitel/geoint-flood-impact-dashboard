from __future__ import annotations

from datetime import date, timedelta
from time import perf_counter
from typing import Any

from src.app.county_boundaries import (
    county_geometry,
    county_names,
    feature_bbox,
    load_or_download_counties,
    selected_county_feature,
)
from src.gee.gee_auth import initialize_earth_engine
from src.gee.sentinel1_collection import build_aoi_from_geometry
from src.gee.sentinel1_scene_explorer import search_sentinel1_scenes_result
from src.impact_tool.cache import PersistentCache
from src.impact_tool.models import BUFFER_MAX_METERS, BUFFER_MIN_METERS, ImpactToolState
from src.impact_tool.presets import GALATI_PRESET_NAME, apply_galati_preset
from src.impact_tool.scenes import (
    confirm_scene_pair,
    hydrate_scene_thumbnails,
    preview_tile_for_scene,
    preview_tiles_for_pair,
    scene_label,
    search_scenes,
    select_scene_pair,
    timeline_entries,
)
from src.impact_tool.state import (
    apply_scene_pair,
    clear_aoi,
    record_timing,
    set_county,
    update_buffer,
)
from src.impact_tool.workflow import workflow_steps


def render_sidebar(st: Any, state: ImpactToolState) -> tuple[dict | None, list[str]]:
    boundary_result = load_or_download_counties()
    counties = county_names(boundary_result.geojson) if boundary_result.geojson else []

    with st.sidebar:
        st.markdown('<div class="impact-sidebar-title">Pașii analizei</div>', unsafe_allow_html=True)
        for step in workflow_steps(state):
            status_class = "done" if step.complete else ("active" if step.active else "waiting")
            st.markdown(
                f'<div class="workflow-step {status_class}">'
                f'<span>{step.number}</span><p>{step.label}</p></div>',
                unsafe_allow_html=True,
            )

        st.divider()
        galati_feature = (
            selected_county_feature(boundary_result.geojson, "Galati")
            if boundary_result.geojson
            else None
        )
        if st.button(
            GALATI_PRESET_NAME,
            use_container_width=True,
            key="apply_galati_preset",
        ):
            apply_galati_preset(
                state,
                st.session_state,
                county_geometry(galati_feature),
                feature_bbox(galati_feature),
            )
            st.rerun()
        if state.preset_name == GALATI_PRESET_NAME:
            cache_states = {
                item.get("status", "lipsă")
                for item in state.preset_cache_status.values()
            }
            if cache_states == {"valid"}:
                st.success("Cache Galați pregătit pentru rulare rapidă")
            else:
                st.warning(
                    "Cache Galați: "
                    + ", ".join(sorted(cache_states or {"lipsă"}))
                )
        selected_index = counties.index(state.county_name) if state.county_name in counties else 0
        selected_county = st.selectbox(
            "Județ",
            counties or [state.county_name],
            index=selected_index,
            help="Selectează județul folosit ca arie implicită a analizei.",
        )
        selected_feature = (
            selected_county_feature(boundary_result.geojson, selected_county)
            if boundary_result.geojson
            else None
        )
        if set_county(
            state,
            selected_county,
            county_geometry(selected_feature),
            feature_bbox(selected_feature),
        ):
            st.rerun()

        area_label = "Zonă focală desenată manual" if state.aoi_active else "Județ complet"
        st.markdown(
            f'<div class="active-area"><strong>Aria activă</strong><span>{area_label}</span></div>',
            unsafe_allow_html=True,
        )
        st.radio(
            "Aria activă",
            ["Județ complet", "Zonă focală desenată manual"],
            index=1 if state.aoi_active else 0,
            disabled=True,
            help="Zona focală devine activă după desenarea și validarea unui poligon pe hartă.",
            label_visibility="collapsed",
        )
        if st.button(
            "Desenează zonă focală",
            use_container_width=True,
            help="Folosește apoi instrumentul poligon sau dreptunghi din colțul stâng al hărții.",
        ):
            state.draw_requested = True
        if state.draw_requested and not state.aoi_active:
            st.info("Desenează un singur poligon pe hartă. Acesta va fi validat automat.")
        if state.aoi_active:
            st.caption(
                f"Suprafață: {state.active_area_km2:.2f} km² · "
                f"Hash: {state.active_area_hash}"
            )
            if st.button(
                "Șterge AOI și revino la județ",
                use_container_width=True,
                type="secondary",
            ):
                clear_aoi(state)
                st.rerun()
        for warning in state.area_warnings:
            st.warning(warning)
        for error in state.area_errors:
            st.error(error)

        _render_scene_selection(st, state)

        selected_buffer = st.slider(
            "Buffer în jurul apei noi",
            min_value=BUFFER_MIN_METERS,
            max_value=BUFFER_MAX_METERS,
            value=state.buffer_meters,
            step=1,
            help="Distanța de avertizare pentru evaluarea elementelor potențial expuse.",
        )
        update_buffer(state, selected_buffer)

        rapid_column, detailed_column = st.columns(2)
        run_rapid = rapid_column.button(
            "Rulează analiza rapidă",
            type="primary",
            use_container_width=True,
            disabled=not state.can_run_analysis,
            help="Rulează SAR și categoriile OSM operaționale, fără Dynamic World.",
            key="run_rapid_analysis",
        )
        run_detailed = detailed_column.button(
            "Rulează analiza detaliată",
            use_container_width=True,
            disabled=not state.can_run_analysis,
            help="Rulează SAR, Dynamic World, corelarea multisursă și toate categoriile OSM.",
            key="run_detailed_analysis",
        )
        if run_rapid or run_detailed:
            state.analysis_mode = "detaliat" if run_detailed else "rapid"
            state.run_requested = True

        with st.expander("Parametri SAR avansați", expanded=False):
            state.analysis_parameters["water_threshold"] = st.number_input(
                "Prag apă SAR (dB)",
                min_value=-30.0,
                max_value=-5.0,
                value=float(state.analysis_parameters["water_threshold"]),
                step=0.5,
                help="Pixelii cu retroîmprăștiere sub prag sunt considerați apă observată automat prin SAR.",
            )
            state.analysis_parameters["smoothing_meters"] = st.slider(
                "Smoothing SAR (m)",
                0,
                100,
                int(state.analysis_parameters["smoothing_meters"]),
                step=10,
            )
            state.analysis_parameters["minimum_connected_pixels"] = st.slider(
                "Minimum connected pixels",
                0,
                50,
                int(state.analysis_parameters["minimum_connected_pixels"]),
                step=1,
            )

        if state.comparison_ready:
            swipe_enabled = st.toggle(
                "Activează bara BEFORE / AFTER",
                value=state.swipe_enabled,
                help="Încarcă imaginile selectate și afișează separatorul vertical pe hartă.",
            )
            if swipe_enabled != state.swipe_enabled:
                state.swipe_enabled = swipe_enabled
                if swipe_enabled and not state.preview_tiles:
                    _refresh_preview_tiles(state)
                st.rerun()
            selected_preview_mode = st.radio(
                "Mod comparație",
                ["Radar brut în tonuri de gri", "Doar apă observată prin SAR"],
                index=0 if state.preview_mode == "Radar brut în tonuri de gri" else 1,
                disabled=not state.swipe_enabled,
                help="Schimbă reprezentarea comparatorului fără a porni analiza finală.",
            )
            if selected_preview_mode != state.preview_mode:
                state.preview_mode = selected_preview_mode
                _refresh_preview_tiles(state)
                st.rerun()
            if state.swipe_enabled:
                st.caption("Comparatorul vertical este activ pe hartă.")
        else:
            st.markdown(
                '<div class="swipe-placeholder">Comparație BEFORE / AFTER</div>',
                unsafe_allow_html=True,
            )
            st.caption("Comparatorul glisant va fi disponibil după selectarea celor două scene.")

    return boundary_result.geojson, boundary_result.warnings


def _render_scene_selection(st: Any, state: ImpactToolState) -> None:
    st.markdown("#### Scene Sentinel-1")
    today = date.today()
    preset_suffix = "_preset" if state.preset_name == GALATI_PRESET_NAME else ""
    start_key = f"impact_scene_start{preset_suffix}"
    start_value = st.session_state.pop(
        start_key,
        today - timedelta(days=60),
    )
    start_date = st.date_input(
        "Început interval",
        value=start_value,
        key=start_key,
    )
    end_key = f"impact_scene_end{preset_suffix}"
    end_value = st.session_state.pop(end_key, today)
    end_date = st.date_input(
        "Sfârșit interval",
        value=end_value,
        key=end_key,
    )
    polarization_options = ["VH", "VV"]
    polarization_key = f"impact_scene_polarization{preset_suffix}"
    polarization_value = st.session_state.pop(polarization_key, "VH")
    polarization = st.selectbox(
        "Polarizare",
        polarization_options,
        index=polarization_options.index(polarization_value),
        key=polarization_key,
        help="Polarizarea radar utilizată pentru ambele scene.",
    )
    orbit_pass = st.selectbox(
        "Orbit pass",
        ["BOTH", "ASCENDING", "DESCENDING"],
        help="Direcția orbitei Sentinel-1.",
    )
    if st.button("Caută scene Sentinel-1", use_container_width=True):
        gee = initialize_earth_engine()
        if not gee.available or gee.ee is None:
            state.scene_errors = [gee.message]
        else:
            aoi = build_aoi_from_geometry(gee.ee, state.active_geometry, state.active_area_bbox)
            scenes_started = perf_counter()
            result = search_scenes(
                cache=PersistentCache(),
                aoi_hash=state.active_area_hash,
                start_date=str(start_date),
                end_date=str(end_date),
                polarization=polarization,
                orbit_pass=orbit_pass,
                searcher=search_sentinel1_scenes_result,
                search_args=(gee.ee, aoi),
            )
            record_timing(state, "scene", perf_counter() - scenes_started)
            thumbnails_started = perf_counter()
            state.scene_candidates, thumbnail_hits = hydrate_scene_thumbnails(
                cache=PersistentCache(),
                ee=gee.ee,
                aoi=aoi,
                aoi_hash=state.active_area_hash,
                scenes=result.scenes,
                max_thumbnails=state.scene_gallery_limit,
            )
            record_timing(
                state,
                "thumbnail-uri",
                perf_counter() - thumbnails_started,
            )
            state.scene_warnings = result.warnings
            state.scene_errors = result.errors
            state.scene_query = {
                "start_date": str(start_date),
                "end_date": str(end_date),
                "polarization": polarization,
                "orbit_pass": orbit_pass,
            }
            state.cache_events.append(
                "Scene Sentinel-1 disponibile în cache."
                if result.from_cache
                else "Scene Sentinel-1 încărcate din Google Earth Engine."
            )
            state.cache_events.append(
                f"Thumbnail-uri Sentinel-1 din cache: {thumbnail_hits}/"
                f"{len(state.scene_candidates)}."
            )

    for error in state.scene_errors:
        st.error(error)
    for warning in state.scene_warnings:
        st.warning(warning)
    if not state.scene_candidates:
        st.selectbox(
            "Imagine de referință (BEFORE)",
            ["Nicio imagine selectată"],
            disabled=True,
        )
        st.selectbox(
            "Imagine după eveniment (AFTER)",
            ["Nicio imagine selectată"],
            disabled=True,
        )
        return

    _render_scene_timeline(st, state.scene_candidates)
    _render_scene_gallery(st, state)

    scene_ids = [scene["ee_id"] for scene in state.scene_candidates]
    labels = {scene["ee_id"]: scene_label(scene) for scene in state.scene_candidates}
    before_id = st.selectbox(
        "Imagine de referință (BEFORE)",
        scene_ids,
        index=_selected_scene_index(scene_ids, state.before_scene, 0),
        format_func=lambda scene_id: labels[scene_id],
        key="impact_before_scene_select",
    )
    after_id = st.selectbox(
        "Imagine după eveniment (AFTER)",
        scene_ids,
        index=_selected_scene_index(
            scene_ids,
            state.after_scene,
            max(0, len(scene_ids) - 1),
        ),
        format_func=lambda scene_id: labels[scene_id],
        key="impact_after_scene_select",
    )
    before, after = select_scene_pair(state.scene_candidates, before_id, after_id)
    validation = confirm_scene_pair(before, after)
    for error in validation["errors"]:
        st.error(error)
    for warning in validation["warnings"]:
        st.warning(warning)
    accept_warnings = False
    if st.button(
        "Compară imaginile",
        use_container_width=True,
        disabled=not validation["compatible"],
        key="compare_scene_pair",
    ):
        apply_scene_pair(state, before, after, False)
        state.swipe_enabled = True
        _refresh_preview_tiles(state)
        st.rerun()
    if state.swipe_enabled:
        st.caption("Trage direct bara verticală din hartă pentru comparație.")
    if validation["requires_confirmation"]:
        accept_warnings = st.checkbox("Accept avertismentele perechii selectate")
    if st.button(
        "Confirmă imaginile",
        use_container_width=True,
        disabled=not validation["compatible"],
    ):
        confirmation = confirm_scene_pair(before, after, accept_warnings)
        apply_scene_pair(state, before, after, confirmation["confirmed"])
        if confirmation["confirmed"]:
            state.preview_scene_id = ""
            state.preview_scene_tile = ""
            st.rerun()


def _render_scene_timeline(st: Any, scenes: list[dict[str, Any]]) -> None:
    entries = timeline_entries(scenes)
    labels = " → ".join(
        f"{entry['date']} ({entry['orbit_pass']})"
        for entry in entries
    )
    st.caption(f"Timeline: {labels}")


def _render_scene_gallery(st: Any, state: ImpactToolState) -> None:
    st.markdown("##### Galerie scene")
    visible_scenes = state.scene_candidates[: state.scene_gallery_limit]
    for row_start in range(0, len(visible_scenes), 2):
        columns = st.columns(2)
        for column, scene in zip(
            columns,
            visible_scenes[row_start : row_start + 2],
        ):
            with column:
                thumbnail = scene.get("thumbnail_url")
                if thumbnail:
                    st.image(thumbnail, use_container_width=True)
                else:
                    st.caption("Thumbnail indisponibil")
                st.caption(
                    f"{str(scene.get('acquisition_time', ''))[:16].replace('T', ' ')}\n\n"
                    f"{scene.get('orbit_pass', '?')} · orbita "
                    f"{scene.get('relative_orbit', '?')} · "
                    f"{scene.get('polarization', '?')} · "
                    f"{float(scene.get('coverage_percent') or 0):.1f}% AOI"
                )
                scene_id = str(scene.get("ee_id"))
                if st.button(
                    "Previzualizează",
                    key=f"preview-scene-{scene_id}",
                    use_container_width=True,
                ):
                    _preview_scene(state, scene)
                    st.rerun()
                before_col, after_col = st.columns(2)
                if before_col.button(
                    "Alege BEFORE",
                    key=f"choose-before-{scene_id}",
                    use_container_width=True,
                ):
                    state.before_scene = scene
                    st.session_state["impact_before_scene_select"] = scene_id
                    st.rerun()
                if after_col.button(
                    "Alege AFTER",
                    key=f"choose-after-{scene_id}",
                    use_container_width=True,
                ):
                    state.after_scene = scene
                    st.session_state["impact_after_scene_select"] = scene_id
                    st.rerun()
    if state.scene_gallery_limit < len(state.scene_candidates):
        if st.button(
            "Afișează mai multe",
            use_container_width=True,
            key="show_more_scene_thumbnails",
        ):
            _load_more_thumbnails(state)
            st.rerun()


def _preview_scene(state: ImpactToolState, scene: dict[str, Any]) -> None:
    gee = initialize_earth_engine()
    if not gee.available or gee.ee is None:
        state.scene_errors = [gee.message]
        return
    aoi = build_aoi_from_geometry(gee.ee, state.active_geometry, state.active_area_bbox)
    state.preview_scene_id = str(scene.get("ee_id"))
    state.preview_scene_tile = preview_tile_for_scene(gee.ee, aoi, scene)


def _selected_scene_index(
    scene_ids: list[str],
    selected: dict[str, Any] | None,
    fallback: int,
) -> int:
    selected_id = (selected or {}).get("ee_id")
    return scene_ids.index(selected_id) if selected_id in scene_ids else fallback


def _refresh_preview_tiles(state: ImpactToolState) -> None:
    if not state.before_scene or not state.after_scene:
        return
    gee = initialize_earth_engine()
    if not gee.available or gee.ee is None:
        state.scene_errors = [gee.message]
        return
    aoi = build_aoi_from_geometry(gee.ee, state.active_geometry, state.active_area_bbox)
    state.preview_tiles = preview_tiles_for_pair(
        gee.ee,
        aoi,
        state.before_scene,
        state.after_scene,
        state.preview_mode,
        threshold=float(state.analysis_parameters["water_threshold"]),
        smoothing_meters=int(state.analysis_parameters["smoothing_meters"]),
        minimum_connected_pixels=int(
            state.analysis_parameters["minimum_connected_pixels"]
        ),
    )


def _load_more_thumbnails(state: ImpactToolState) -> None:
    gee = initialize_earth_engine()
    if not gee.available or gee.ee is None:
        state.scene_errors = [gee.message]
        return
    state.scene_gallery_limit = min(
        len(state.scene_candidates),
        state.scene_gallery_limit + 8,
    )
    aoi = build_aoi_from_geometry(gee.ee, state.active_geometry, state.active_area_bbox)
    state.scene_candidates, _ = hydrate_scene_thumbnails(
        cache=PersistentCache(),
        ee=gee.ee,
        aoi=aoi,
        aoi_hash=state.active_area_hash,
        scenes=state.scene_candidates,
        max_thumbnails=state.scene_gallery_limit,
    )
