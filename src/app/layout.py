from __future__ import annotations

from config.settings import GALATI_PRESET, PROFILE_SCALES
from src.app.state import AnalysisParameters


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
) -> tuple[AnalysisParameters, bool]:
    with st.sidebar:
        st.header("Configurare analiza")

        with st.expander("A. Zona de analiza", expanded=True):
            if selected_county not in county_names and county_names:
                selected_county = county_names[0]
            county_index = county_names.index(selected_county) if selected_county in county_names else 0
            county_name = st.selectbox(
                "Selecteaza judetul",
                county_names or ["GeoJSON indisponibil"],
                index=county_index,
                help="Judetul selectat este folosit ca AOI pentru analiza SAR.",
            )
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

            with st.expander("C. Parametri Sentinel-1 SAR", expanded=True):
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
                    "Prag SAR",
                    0.5,
                    3.0,
                    1.25,
                    0.05,
                    help="Controleaza sensibilitatea detectiei. Un prag mai permisiv poate detecta mai multe zone, dar poate creste numarul de rezultate false pozitive.",
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

            with st.expander("D. Performanta", expanded=True):
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

            with st.expander("E. Layere", expanded=False):
                show_before = st.checkbox("SAR before", True)
                show_after = st.checkbox("SAR after", True)
                show_change = st.checkbox("SAR change", True)
                show_flood = st.checkbox("Extindere detectata", True)
                show_permanent = st.checkbox("Apa permanenta", True)
                show_land = st.checkbox("Dynamic World", True)
                show_s2 = st.checkbox("Sentinel-2 RGB auxiliar", False)

            with st.expander("Comparatie vizuala", expanded=False):
                comparison = st.selectbox("Comparatie vizuala", list(COMPARISON_PRESETS))
                left_default, right_default = COMPARISON_PRESETS[comparison]
                left_layer = st.selectbox(
                    "Layer stanga",
                    LAYER_OPTIONS,
                    index=LAYER_OPTIONS.index(left_default),
                )
                right_layer = st.selectbox(
                    "Layer dreapta",
                    LAYER_OPTIONS,
                    index=LAYER_OPTIONS.index(right_default),
                )

            run_analysis = st.form_submit_button(
                "Ruleaza analiza SAR",
                type="primary",
                use_container_width=True,
                disabled=not gee_available or not county_geometry,
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
        before_start_date=before_start,
        before_end_date=before_end,
        after_start_date=after_start,
        after_end_date=after_end,
        polarization=polarization,
        orbit_pass=orbit_pass,
        smoothing_radius=smoothing_radius,
        threshold=threshold,
        minimum_connected_pixels=minimum_connected,
        mask_permanent_water=mask_permanent,
        analysis_profile=profile,
        scale=scale,
        show_permanent_water=show_permanent,
        show_land_cover=show_land,
        show_sentinel2_rgb=show_s2,
        show_sar_before=show_before,
        show_sar_after=show_after,
        show_sar_change=show_change,
        show_detected_flood_extent=show_flood,
        comparison_preset=comparison,
        left_layer=left_layer,
        right_layer=right_layer,
    )
    if run_analysis:
        st.session_state.last_analysis_params = params.as_dict()
    return params, run_analysis
