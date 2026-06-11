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
    result = state.analysis_results.get("dynamic_world")
    if not result:
        message = state.analysis_results.get(
            "dynamic_world_error",
            "Rezultatele Dynamic World vor fi disponibile după analiză.",
        )
        st.info(message)
        return
    st.subheader("Diferențe observate Dynamic World")
    st.bar_chart(result.get("transitions", {}))
    st.json(result.get("metrics", {}), expanded=False)


def _render_osm(st: Any, state: ImpactToolState) -> None:
    if not state.analysis_complete:
        st.info("Elementele OSM pot fi încărcate numai după analiza SAR.")
        return
    if not state.osm_status:
        st.caption("Datele OSM sunt încărcate automat în timpul analizei.")
        return
    st.markdown("#### Filtre OSM")
    columns = st.columns(5)
    labels = {
        "buildings": "Clădiri",
        "roads": "Drumuri",
        "railways": "Căi ferate",
        "bridges": "Poduri",
        "critical": "Obiective critice",
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
            st.success(
                f"{category}: {status.get('count', 0)} obiecte · {status.get('source')}"
            )
        else:
            st.warning(f"{category}: {status.get('error', 'eroare necunoscută')}")
            if st.button(
                f"Reîncearcă {category}",
                key=f"retry_osm_{category}",
            ):
                state.osm_retry_category = category
                state.osm_load_requested = True
                st.rerun()
    impact = state.analysis_results.get("osm_impact")
    if impact:
        st.json(impact.get("metrics", {}), expanded=False)
    else:
        st.warning(
            "Impactul geometric necesită geometria vectorială a apei noi SAR; "
            "datele OSM brute rămân disponibile."
        )


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
