from __future__ import annotations

from config.settings import GALATI_PRESET, PROFILE_SCALES
from src.app.state import AnalysisParameters, county_dependent_parameter_key, reset_county_dependent_state
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
    st.warning(
        "Mod exploratoriu / experimental. Pentru fluxul metodologic al disertatiei "
        "ruleaza impact_tool.py."
    )
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
        presentation_mode = st.toggle(
            "Mod prezentare",
            value=False,
            help=(
                "Simplifica panoul lateral si lasa harta ca element principal. "
                "Activeaza-l pentru prezentare; dezactiveaza-l cand ajustezi parametri avansati."
            ),
        )
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
                reset_county_dependent_state(st.session_state)
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
                    "Data inceput perioada de referinta (BEFORE)",
                    GALATI_PRESET["before_start_date"],
                    help=(
                        "Prima zi cautata pentru imaginea sau compozitul de referinta. "
                        "Un interval prea scurt poate sa nu gaseasca scene compatibile; implicit este recomandat pentru evenimentul presetat."
                    ),
                )
                before_end = st.date_input(
                    "Data sfarsit perioada de referinta (BEFORE)",
                    GALATI_PRESET["before_end_date"],
                    help=(
                        "Ultima zi cautata pentru perioada de referinta. Ajusteaza doar daca nu exista scene Sentinel-1 compatibile."
                    ),
                )
                after_start = st.date_input(
                    "Data inceput perioada dupa eveniment (AFTER)",
                    GALATI_PRESET["after_start_date"],
                    help=(
                        "Prima zi cautata dupa eveniment. Controleaza scenele folosite pentru apa observata automat prin SAR."
                    ),
                )
                after_end = st.date_input(
                    "Data sfarsit perioada dupa eveniment (AFTER)",
                    GALATI_PRESET["after_end_date"],
                    help=(
                        "Ultima zi cautata dupa eveniment. Un interval prea larg poate amesteca stari diferite ale apei."
                    ),
                )
                event_date = st.date_input(
                    "Data evenimentului",
                    GALATI_PRESET["event_date"],
                    help=(
                        "Data de referinta a evenimentului. Este folosita pentru ordonarea scenelor candidate BEFORE/AFTER; "
                        "seteaz-o la data principala a fenomenului analizat."
                    ),
                )

            with st.expander("Setari avansate SAR", expanded=not presentation_mode):
                polarization = st.radio(
                    "Polarizare",
                    ["VH", "VV"],
                    horizontal=True,
                    help=(
                        "Alege banda radar Sentinel-1 folosita. VH este recomandata implicit pentru evidentierea apei; "
                        "VV poate fi testata comparativ, dar poate raspunde diferit pe zone urbane sau vegetatie."
                    ),
                )
                orbit_pass = st.selectbox(
                    "Directia orbitei",
                    ["BOTH", "ASCENDING", "DESCENDING"],
                    help=(
                        "Selecteaza directia orbitei Sentinel-1. Pentru comparatii robuste, scenele BEFORE si AFTER trebuie "
                        "sa fie compatibile; BOTH este util la cautare, dar poate cere confirmare suplimentara."
                    ),
                )
                threshold = st.slider(
                    "Prag schimbare SAR",
                    0.5,
                    3.0,
                    1.25,
                    0.05,
                    help=(
                        "Controleaza sensibilitatea schimbarii dintre BEFORE si AFTER. Valoarea implicita este echilibrata; "
                        "un prag prea mic poate include zgomot, iar unul prea mare poate omite apa observata automat prin SAR."
                    ),
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
                    "Prag apa SAR",
                    value=float(default_water_threshold),
                    step=0.5,
                    disabled=sar_water_mode != "Manual",
                    help=(
                        "Controleaza identificarea pixelilor radar cu semnal compatibil cu apa. Se modifica manual doar "
                        "cand presetul nu se potriveste; o valoare prea sensibila poate include umbre radar sau sol umed."
                    ),
                )
                smoothing_radius = st.slider(
                    "Raza netezire speckle",
                    0,
                    100,
                    30,
                    5,
                    help=(
                        "Reduce zgomotul speckle specific imaginilor radar. Valoarea implicita pastreaza un compromis; "
                        "o raza prea mare poate sterge detalii locale sau canale inguste."
                    ),
                )
                minimum_connected = st.slider(
                    "Numar minim pixeli conectati",
                    0,
                    50,
                    8,
                    1,
                    help=(
                        "Elimina grupurile mici de pixeli izolati. Creste valoarea pentru rezultate mai curate; "
                        "scade-o daca vrei sa pastrezi extinderi mici, cu risc mai mare de zgomot."
                    ),
                )
                mask_permanent = st.toggle(
                    "Masca apa permanenta",
                    value=True,
                    help=(
                        "Elimina corpurile de apa permanente folosind JRC Global Surface Water. Este recomandata implicit "
                        "pentru evidentierea apei temporare; dezactivarea poate include lacuri si rauri permanente."
                    ),
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
                    "Profil de performanta",
                    ["Previzualizare rapida", "Standard", "Export detaliat"],
                    index=1,
                    help=(
                        "Controleaza viteza si nivelul de detaliu. Standard este recomandat; Previzualizare rapida raspunde mai repede, "
                        "iar Export detaliat poate dura mai mult."
                    ),
                )
                profile_key = {
                    "Previzualizare rapida": "Rapid preview",
                    "Standard": "Standard",
                    "Export detaliat": "Detailed",
                }[profile]
                scale_key = "Detailed export" if profile_key == "Detailed" else profile_key
                scale = st.select_slider(
                    "Scara analiza",
                    options=[10, 20, 30, 40, 50],
                    value=PROFILE_SCALES[scale_key],
                    help=(
                        "Rezolutia de calcul trimisa catre Google Earth Engine, in metri. Valoarea implicita Standard este recomandata; "
                        "o scara prea fina poate creste timpul de procesare."
                    ),
                )
                before_sar_method = st.selectbox(
                    "Metoda BEFORE",
                    ["Compozit median din scene compatibile", "Scena individuala"],
                    help=(
                        "Default recomandat: compozit median din scene compatibile pentru o "
                        "linie de baza mai stabila inainte de eveniment."
                    ),
                )
                after_sar_method = st.selectbox(
                    "Metoda AFTER",
                    [
                        "Scena individuala selectata manual",
                        "Compozit median pe interval scurt",
                        "Minimum SAR / percentila joasa exploratorie",
                    ],
                    help=(
                        "Default recomandat: scena individuala selectata manual. Produsul minimum "
                        "SAR / percentila joasa este exploratoriu si poate include zgomot radar."
                    ),
                )
                dynamic_world_after_mode = st.selectbox(
                    "Fereastra Dynamic World dupa eveniment",
                    ["Fereastra apropiata de scena SAR AFTER", "Interval complet"],
                    help=(
                        "Default: foloseste o fereastra scurta in jurul scenei SAR AFTER. "
                        "Daca nu exista imagini Dynamic World in fereastra, analiza revine la intervalul complet."
                    ),
                )

            with st.expander("Layere optionale", expanded=False):
                show_before = st.checkbox(
                    "Imagine de referinta SAR (BEFORE)",
                    True,
                    help="Afiseaza scena sau compozitul SAR de referinta pe harta. Dezactiveaza pentru o harta mai simpla.",
                )
                show_after = st.checkbox(
                    "Imagine dupa eveniment SAR (AFTER)",
                    True,
                    help="Afiseaza scena sau compozitul SAR dupa eveniment. Este utila pentru comparatia vizuala.",
                )
                load_optional_layers = st.checkbox(
                    "Incarca layere suplimentare",
                    False,
                    help=(
                        "Adauga SAR difference/ratio, SAR persistent/loss, alte diferente Dynamic World, "
                        "Sentinel-2, indici si DEM. Poate creste timpul de incarcare a hartii."
                    ),
                )
                show_change = load_optional_layers
                show_flood = st.checkbox(
                    "Extindere preliminara filtrata",
                    True,
                    help="Afiseaza rezultatul principal al analizei SAR filtrate.",
                )
                show_sar_water = st.checkbox(
                    "Afiseaza layere apa SAR",
                    True,
                    help="Include apa observata prin SAR inainte, dupa eveniment si apa noua evidentiata prin SAR.",
                )
                show_sar_dw = st.checkbox(
                    "Afiseaza corelare SAR x Dynamic World",
                    True,
                    help="Afiseaza suprapunerea multisursa si diferentele dintre SAR si Dynamic World.",
                )
                show_permanent = st.checkbox(
                    "Apa permanenta JRC",
                    True,
                    help="Afiseaza masca de apa permanenta folosita ca referinta.",
                )
                show_land = st.checkbox(
                    "Dynamic World",
                    True,
                    help="Afiseaza clasele Dynamic World BEFORE/AFTER si diferentele observate.",
                )
                show_s2 = load_optional_layers
                show_osm_impact = st.checkbox(
                    "Calculeaza impact operational OSM",
                    False,
                    help=(
                        "Interogheaza Overpass API la cerere pentru cladiri, drumuri, obiective "
                        "critice, cai ferate si poduri. Interogarea foloseste bbox-ul AOI pentru viteza, "
                        "dar rezultatele afisate si raportate sunt filtrate la interiorul judetului."
                    ),
                )
                osm_buffer = st.slider(
                    "Buffer OSM metri",
                    0,
                    2000,
                    500,
                    100,
                    help=(
                        "Distanta suplimentara folosita pentru a cauta elemente OSM in jurul extinderii preliminare. "
                        "500 m este recomandat; valori mari pot incetini interogarea Overpass."
                    ),
                )
                osm_limit = st.selectbox(
                    "Limita elemente OSM",
                    [500, 1000, 2500, 5000],
                    index=0,
                    help=(
                        "Numarul maxim de elemente cerute pe categorie OSM. Pastreaza 500 pentru stabilitate; creste doar daca zona este mare "
                        "si conexiunea Overpass raspunde bine."
                    ),
                )

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
        analysis_profile=profile_key,
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
        before_sar_method=before_sar_method,
        after_sar_method=after_sar_method,
        dynamic_world_after_mode=dynamic_world_after_mode,
        load_optional_layers=load_optional_layers,
        show_osm_impact=show_osm_impact,
        osm_buffer_meters=osm_buffer,
        osm_query_limit=osm_limit,
        use_median_composite=before_sar_method == "Compozit median din scene compatibile"
        and after_sar_method != "Scena individuala selectata manual",
        comparison_preset="Compara doua layere in harta",
        left_layer="Sentinel-1 SAR before",
        right_layer="Sentinel-1 SAR after",
    )
    current_dependent_key = county_dependent_parameter_key(params)
    previous_dependent_key = st.session_state.get("county_dependent_parameter_key")
    if previous_dependent_key and previous_dependent_key != current_dependent_key:
        reset_county_dependent_state(st.session_state)
    st.session_state.county_dependent_parameter_key = current_dependent_key
    if run_analysis:
        st.session_state.last_analysis_params = params.as_dict()
    return params, search_images, run_analysis
