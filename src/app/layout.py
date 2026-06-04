from __future__ import annotations

from config.settings import GALATI_PRESET, PROFILE_SCALES
from src.app.state import AnalysisParameters
from src.gee.sar_water_masks import sar_water_threshold_for_mode


LAYER_OPTIONS = [
    "Sentinel-1 SAR before",
    "Sentinel-1 SAR after",
    "SAR change",
    "permanent water",
    "detected flood extent",
    "land cover",
    "Sentinel-2 RGB",
]

COMPARISON_PRESETS = {
    "Before SAR vs After SAR": ("Sentinel-1 SAR before", "Sentinel-1 SAR after"),
    "After SAR vs Extindere detectata": (
        "Sentinel-1 SAR after",
        "detected flood extent",
    ),
    "Apa permanenta vs Extindere temporara": (
        "permanent water",
        "detected flood extent",
    ),
    "Land cover vs Extindere detectata": ("land cover", "detected flood extent"),
    "Sentinel-2 RGB vs Extindere detectata": (
        "Sentinel-2 RGB",
        "detected flood extent",
    ),
}


def configure_page(st) -> None:
    st.set_page_config(
        page_title="Dashboard GEOINT pentru inundatii",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("Dashboard GEOINT pentru analiza preliminara a inundatiilor")
    st.caption(
        "Analiza Sentinel-1 SAR, procesare cloud in Google Earth Engine si evaluarea "
        "tipurilor de teren intersectate."
    )


def render_usage(st) -> None:
    with st.expander("Cum se foloseste aplicatia", expanded=True):
        st.markdown(
            """
1. Selecteaza judetul.
2. Verifica perioadele inainte si dupa eveniment.
3. Ajusteaza parametrii doar daca este necesar.
4. Apasa `Ruleaza analiza SAR`.
5. Urmareste jurnalul live si exploreaza layerele rezultate.
"""
        )


def sidebar_parameters(
    st,
    county_names: list[str],
    selected_county: str,
    county_geometry: dict | None,
    county_bbox: list[float],
    gee_available: bool,
) -> tuple[AnalysisParameters, bool, bool]:
    with st.sidebar:
        st.header("Configurare analiza")
        presentation_mode = st.toggle("Mod prezentare", value=False)
        st.session_state.presentation_mode = presentation_mode

        with st.expander("Mod simplu", expanded=True):
            if selected_county not in county_names and county_names:
                selected_county = county_names[0]
            county_index = county_names.index(selected_county) if selected_county in county_names else 0
            county_name = st.selectbox(
                "Selecteaza judetul",
                county_names or ["GeoJSON indisponibil"],
                index=county_index,
                help="Judetul selectat este folosit ca AOI pentru analiza SAR.",
            )
            previous_county = st.session_state.get("selected_county")
            if previous_county and previous_county != county_name:
                st.session_state.county_focus_requested = True
                st.session_state.pop("last_analysis_result", None)
            st.session_state.selected_county = county_name
            st.selectbox(
                "Preset eveniment",
                ["Galati - inundatii septembrie 2024"],
                help="Preset academic pentru evenimentul din septembrie 2024.",
            )
            st.info(f"AOI curent: {county_name}. Harta se actualizeaza fara a porni analiza.")

        with st.form("analysis_parameters_form"):
            with st.expander("B. Perioade analizate", expanded=True):
                before_start = st.date_input(
                    "Data inceput before",
                    GALATI_PRESET["before_start_date"],
                    help="Perioada before reprezinta intervalul de referinta anterior evenimentului.",
                )
                before_end = st.date_input(
                    "Data sfarsit before",
                    GALATI_PRESET["before_end_date"],
                    help="Perioada before reprezinta intervalul de referinta anterior evenimentului.",
                )
                after_start = st.date_input(
                    "Data inceput after",
                    GALATI_PRESET["after_start_date"],
                    help="Perioada after reprezinta intervalul in care este analizata extinderea preliminara a apei.",
                )
                after_end = st.date_input(
                    "Data sfarsit after",
                    GALATI_PRESET["after_end_date"],
                    help="Perioada after reprezinta intervalul in care este analizata extinderea preliminara a apei.",
                )
                event_date = st.date_input(
                    "Data evenimentului",
                    GALATI_PRESET["event_date"],
                    help="Data folosita pentru recomandarea automata a scenelor BEFORE si AFTER.",
                )

            with st.expander("Setari avansate SAR", expanded=not presentation_mode):
                polarization = st.radio(
                    "Polarizare",
                    ["VH", "VV"],
                    horizontal=True,
                    help="VH este recomandata implicit pentru evidentierea schimbarilor asociate apei. VV poate fi testata comparativ.",
                )
                orbit_pass = st.selectbox(
                    "Orbit pass",
                    ["BOTH", "ASCENDING", "DESCENDING"],
                    help="Selecteaza directia orbitei Sentinel-1. Pentru comparatii robuste, imaginile before si after trebuie sa fie compatibile. Foloseste BOTH doar pentru explorare.",
                )
                threshold = st.slider(
                    "SAR change threshold",
                    0.5,
                    3.0,
                    1.25,
                    0.05,
                    help="Controleaza sensibilitatea detectiei. Un prag mai permisiv poate detecta mai multe zone, dar poate creste numarul de rezultate false pozitive.",
                )
                sar_water_mode = st.selectbox(
                    "Mod detectie apa SAR",
                    ["Echilibrat", "Conservator", "Sensibil", "Manual"],
                    help=(
                        "Conservator detecteaza mai putini pixeli si reduce fals pozitivele. "
                        "Echilibrat este recomandat implicit. Sensibil detecteaza mai multe zone, "
                        "dar poate include suprafete netede, sol umed sau umbre radar."
                    ),
                )
                default_water_threshold = sar_water_threshold_for_mode(polarization, sar_water_mode, -18.0)
                sar_water_threshold = st.number_input(
                    "SAR water threshold",
                    value=float(default_water_threshold),
                    step=0.5,
                    disabled=sar_water_mode != "Manual",
                    help=(
                        "Pragul SAR water threshold este utilizat pentru identificarea pixelilor radar cu "
                        "comportament compatibil cu apa. Este diferit de pragul change detection, care "
                        "masoara schimbarea dintre imaginile BEFORE si AFTER."
                    ),
                )
                smoothing_radius = st.slider(
                    "Smoothing radius",
                    0,
                    100,
                    30,
                    5,
                    help="Reduce zgomotul speckle specific imaginilor radar. O valoare prea mare poate elimina detalii locale.",
                )
                minimum_connected = st.slider(
                    "Minimum connected pixels",
                    0,
                    50,
                    8,
                    1,
                    help="Elimina grupurile foarte mici de pixeli izolati pentru a reduce zgomotul.",
                )
                mask_permanent = st.toggle(
                    "Permanent water masking",
                    value=True,
                    help="Elimina corpurile de apa permanente folosind JRC Global Surface Water, astfel incat rezultatul sa evidentieze mai bine apa temporara.",
                )
                jrc_mode = st.selectbox(
                    "Mod masca JRC",
                    ["Echilibrat", "Conservator", "Extins"],
                    help=(
                        "Conservator: occurrence >= 90. Echilibrat: occurrence >= 75. "
                        "Extins: occurrence >= 50 sau seasonality >= 10 luni/an."
                    ),
                )

            with st.expander("Performanta si compozit", expanded=not presentation_mode):
                profile = st.selectbox(
                    "Profil analiza",
                    ["Rapid preview", "Standard", "Detailed"],
                    index=1,
                    help="Rapid preview foloseste o scara mai redusa pentru rezultate rapide. Standard este recomandat pentru majoritatea analizelor. Detailed este destinat exporturilor si poate necesita mai mult timp.",
                )
                scale_key = "Detailed export" if profile == "Detailed" else profile
                scale = st.select_slider(
                    "Scara",
                    options=[10, 20, 30, 40, 50],
                    value=PROFILE_SCALES[scale_key],
                    help="Rezolutia de calcul trimisa catre Google Earth Engine.",
                )
                use_median = st.checkbox(
                    "Foloseste compozit median in locul scenelor individuale",
                    value=False,
                    help=(
                        "Optiune avansata. Cand este dezactivata, analiza finala foloseste scena "
                        "BEFORE si scena AFTER selectate manual in exploratorul temporal."
                    ),
                )

            with st.expander("Layere optionale", expanded=False):
                show_before = st.checkbox("SAR before", True)
                show_after = st.checkbox("SAR after", True)
                show_change = st.checkbox("SAR change", True)
                show_flood = st.checkbox("Extindere detectata", True)
                show_sar_water = st.checkbox("Afiseaza layere apa SAR", True)
                show_sar_dw = st.checkbox("Afiseaza corelare SAR x Dynamic World", True)
                show_permanent = st.checkbox("Apa permanenta", True)
                show_land = st.checkbox("Dynamic World", True)
                show_s2 = st.checkbox("Sentinel-2 RGB auxiliar", False)

            pair_status = st.session_state.get("sar_pair_status") or {}
            final_disabled = (
                not gee_available
                or not county_geometry
                or not pair_status.get("compatible")
                or not st.session_state.get("sar_pair_confirmed")
                or (pair_status.get("requires_confirmation") and not st.session_state.get("confirm_relative_orbit_mismatch"))
            )
            search_images = st.form_submit_button(
                "Cauta imagini disponibile",
                use_container_width=True,
                disabled=not gee_available or not county_geometry,
            )
            run_analysis = st.form_submit_button(
                "Ruleaza analiza finala pe imaginile selectate",
                type="primary",
                use_container_width=True,
                disabled=final_disabled,
            )
            if not gee_available:
                st.warning(
                    "Google Earth Engine nu este initializat. Ruleaza o singura data: "
                    "python -m src.gee.gee_auth, apoi reporneste aplicatia. Verifica si "
                    "GEE_PROJECT_ID in fisierul .env."
                )

    params = AnalysisParameters(
        aoi_name=county_name,
        county_name=county_name,
        county_geometry=county_geometry,
        bbox=county_bbox,
        event_date=event_date,
        before_start_date=before_start,
        before_end_date=before_end,
        after_start_date=after_start,
        after_end_date=after_end,
        polarization=polarization,
        orbit_pass=orbit_pass,
        smoothing_radius=smoothing_radius,
        threshold=threshold,
        sar_water_mode=sar_water_mode,
        sar_water_threshold=sar_water_threshold,
        minimum_connected_pixels=minimum_connected,
        mask_permanent_water=mask_permanent,
        jrc_water_mode=jrc_mode,
        analysis_profile=profile,
        scale=scale,
        show_permanent_water=show_permanent,
        show_land_cover=show_land,
        show_sentinel2_rgb=show_s2,
        show_sar_before=show_before,
        show_sar_after=show_after,
        show_sar_change=show_change,
        show_detected_flood_extent=show_flood,
        show_sar_water_layers=show_sar_water,
        show_sar_dynamic_world_correlation=show_sar_dw,
        use_median_composite=use_median,
        comparison_preset="Compara doua layere in harta",
        left_layer="Sentinel-1 SAR before",
        right_layer="Sentinel-1 SAR after",
    )
    if run_analysis:
        st.session_state.last_analysis_params = params.as_dict()
    return params, search_images, run_analysis
