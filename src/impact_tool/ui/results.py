from __future__ import annotations

from typing import Any

from src.impact_tool.models import TAB_NAMES, ImpactToolState
from src.impact_tool.state import reset_analysis_results, reset_scene_selection


def render_result_tabs(st: Any, state: ImpactToolState) -> None:
    tabs = st.tabs(list(TAB_NAMES))
    with tabs[0]:
        st.info("Harta principală rămâne spațiul central de lucru.")
        _render_map_tools(st, state)
        if state.cache_events:
            with st.expander("Jurnal procesare și cache", expanded=False):
                for event in state.cache_events[-12:]:
                    st.caption(f"✓ {event}")
                if state.timings:
                    st.json(state.timings, expanded=False)
    with tabs[1]:
        _render_sar_summary(st, state)
    with tabs[2]:
        _render_dynamic_world(st, state)
    with tabs[3]:
        _render_osm(st, state)
    with tabs[4]:
        st.info("Raportul final devine disponibil după finalizarea analizei.")


def _render_sar_summary(st: Any, state: ImpactToolState) -> None:
    sar = state.analysis_results.get("sar")
    if not sar:
        st.info("Indicatorii de impact vor fi disponibili după analiză.")
        return
    metrics = sar.get("metrics", {})
    columns = st.columns(3)
    columns[0].metric("Apă BEFORE", f"{metrics.get('sar_water_before_area_km2', 0):.3f} km²")
    columns[1].metric("Apă AFTER", f"{metrics.get('sar_water_after_area_km2', 0):.3f} km²")
    columns[2].metric("Apă nouă SAR", f"{metrics.get('sar_new_water_area_km2', 0):.3f} km²")
    st.caption(f"Durata procesării SAR: {sar.get('duration_seconds', 0):.2f} s")


def _render_dynamic_world(st: Any, state: ImpactToolState) -> None:
    if st.button(
        "Rulează / Reîncearcă Dynamic World",
        disabled=not bool(state.analysis_results.get("sar")),
        key="run_dynamic_world",
    ):
        state.dynamic_world_requested = True
        st.rerun()
    result = state.analysis_results.get("dynamic_world")
    if not result:
        message = state.analysis_results.get(
            "dynamic_world_error",
            "Rezultatele Dynamic World vor fi disponibile după analiză.",
        )
        st.info(message)
        return
    status = result.get("status", "indisponibil")
    if status == "reușit":
        st.success("Dynamic World: reușit")
    elif status == "tile indisponibil":
        st.warning(result.get("error") or "Dynamic World: tile indisponibil")
    else:
        st.error(result.get("error") or f"Dynamic World: {status}")
    periods = result.get("periods", {})
    dates = result.get("acquisition_dates", {})
    product_types = result.get("product_types", {})
    coverage = result.get("coverage", {})
    st.caption(
        "BEFORE: "
        f"căutare {periods.get('before')} · data efectivă {dates.get('before')} · "
        f"acoperire {float(coverage.get('before') or 0) * 100:.1f}% · "
        f"{product_types.get('before') or 'produs indisponibil'}"
    )
    st.caption(
        "AFTER: "
        f"căutare {periods.get('after')} · data efectivă {dates.get('after')} · "
        f"acoperire {float(coverage.get('after') or 0) * 100:.1f}% · "
        f"{product_types.get('after') or 'produs indisponibil'}"
    )
    tile_errors = {
        key: value
        for key, value in result.get("tiles", {}).items()
        if isinstance(value, dict) and value.get("status") != "reușit"
    }
    if tile_errors:
        with st.expander("Diagnostic tile-uri Dynamic World", expanded=False):
            st.json(tile_errors, expanded=False)
    st.subheader("Diferențe observate Dynamic World")
    st.bar_chart(result.get("transition_values", {}))
    st.json(result.get("metrics", {}), expanded=False)


def _render_osm(st: Any, state: ImpactToolState) -> None:
    if not state.analysis_complete:
        st.info("Elementele OSM pot fi încărcate numai după analiza SAR.")
        return
    if not state.osm_status:
        st.caption("Datele OSM sunt încărcate automat în timpul analizei.")
        return
    state.presentation_mode = st.toggle(
        "Mod prezentare",
        value=state.presentation_mode,
        help="Păstrează pe hartă infrastructura esențială și importantă.",
        key="osm_presentation_mode",
    )
    st.markdown("#### Filtre OSM")
    columns = st.columns(6)
    labels = {
        "buildings": "Clădiri",
        "roads": "Drumuri",
        "railways": "Căi ferate",
        "bridges": "Poduri",
        "critical": "Obiective critice",
        "reference_buildings": "Clădiri de referință",
    }
    for column, (key, label) in zip(columns, labels.items()):
        state.osm_filters[key] = column.checkbox(
            label,
            value=state.osm_filters.get(key, True),
            key=f"osm_filter_{key}",
        )
    state.critical_mode = st.toggle(
        "Afișează doar impactul critic",
        value=state.critical_mode,
        help="Păstrează apa nouă SAR, bufferul, drumurile, podurile și obiectivele critice.",
    )
    for category, status in state.osm_status.items():
        if status.get("ok"):
            st.caption(
                f"Sursa: {status.get('source', 'necunoscută')} | "
                f"data cache: {status.get('cache_date', 'indisponibilă')} | "
                f"completitudine: {status.get('completeness', 'necunoscută')}"
            )
            st.success(
                f"{category}: {status.get('count', 0)} obiecte · {status.get('source')}"
            )
            for warning in status.get("warnings", []):
                st.warning(warning)
        else:
            st.warning(f"{category}: {status.get('error', 'eroare necunoscută')}")
            if st.button(f"Reîncearcă {category}", key=f"retry_osm_{category}"):
                state.osm_retry_category = category
                state.osm_load_requested = True
                st.rerun()
    impact = state.analysis_results.get("osm_impact")
    if impact:
        _render_priority_table(st, state, impact)
        with st.expander("Mod QA", expanded=False):
            st.caption("Informații tehnice pentru verificarea implementării.")
            st.json(
                {
                    "counts": impact.get("metrics", {}).get("status_counts", {}),
                    "cache": state.osm_status,
                    "events": state.cache_events[-10:],
                    "relations_omise": sum(
                        len(status.get("warnings", []))
                        for status in state.osm_status.values()
                    ),
                },
                expanded=False,
            )
    else:
        st.warning(
            "Impactul geometric necesită geometria vectorială a apei noi SAR; "
            "datele OSM brute rămân disponibile."
        )


def _render_priority_table(st: Any, state: ImpactToolState, impact: dict[str, Any]) -> None:
    rows = []
    category_names = {
        "osm_buildings": "Clădire",
        "osm_roads": "Drum",
        "osm_railways": "Cale ferată",
        "osm_bridges": "Pod",
        "osm_critical": "Obiectiv critic",
    }
    for layer_id, layer in impact.get("layers", {}).items():
        for feature in layer.get("features", []):
            properties = feature.get("properties", {})
            if properties.get("status") == "Neexpus":
                continue
            point = _feature_center(feature.get("geometry") or {})
            rows.append(
                {
                    "name": properties.get("name") or "Fără nume",
                    "category": category_names.get(layer_id, layer_id),
                    "status": properties.get("status", "Necunoscut"),
                    "distance": properties.get("distance_to_water_m", 0),
                    "level": properties.get("infrastructure_level", "context tehnic"),
                    "coordinates": point,
                }
            )
    priority = {"esențial": 0, "important": 1, "context tehnic": 2}
    rows.sort(key=lambda row: (priority.get(row["level"], 3), row["distance"]))
    st.markdown("#### Elemente prioritare")
    for index, row in enumerate(rows[:25]):
        columns = st.columns([2.2, 1.4, 1.5, 1.1, 0.7])
        columns[0].write(row["name"])
        columns[1].write(row["category"])
        columns[2].write(row["status"])
        columns[3].write(f'{row["distance"]} m')
        if columns[4].button("Zoom", key=f"osm_zoom_{index}"):
            state.map_focus = row["coordinates"]
            st.rerun()


def _feature_center(geometry: dict[str, Any]) -> list[float]:
    from shapely.geometry import shape

    point = shape(geometry).representative_point()
    return [point.y, point.x]


def _render_map_tools(st: Any, state: ImpactToolState) -> None:
    with st.expander("Instrumente și resetare", expanded=False):
        st.caption(
            "Harta include identificarea coordonatelor, măsurarea distanței și suprafeței, "
            "revenire la România, centrare pe județ și ecran complet."
        )
        columns = st.columns(3)
        if columns[0].button("Curăță scenele", key="clear_scene_pair"):
            reset_scene_selection(state)
            st.rerun()
        if columns[1].button("Curăță rezultatele", key="clear_analysis_results"):
            reset_analysis_results(state)
            st.rerun()
        if columns[2].button(
            "Reia analiza",
            disabled=not state.scenes_confirmed,
            key="rerun_analysis",
        ):
            state.run_requested = True
            st.rerun()
