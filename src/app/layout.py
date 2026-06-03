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
    "Before vs After SAR": ("Sentinel-1 SAR before", "Sentinel-1 SAR after"),
    "After SAR vs Detected Flood Extent": (
        "Sentinel-1 SAR after",
        "detected flood extent",
    ),
    "Permanent Water vs Temporary Flood Extent": (
        "permanent water",
        "detected flood extent",
    ),
    "Land Cover vs Detected Flood Extent": ("land cover", "detected flood extent"),
    "Sentinel-2 RGB vs Detected Flood Extent": (
        "Sentinel-2 RGB",
        "detected flood extent",
    ),
}


def configure_page(st) -> None:
    st.set_page_config(
        page_title="GEOINT Flood Impact Dashboard",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.title("GEOINT Flood Impact Dashboard")
    st.caption("produs GEOINT preliminar de suport decizional")


def sidebar_parameters(st) -> AnalysisParameters:
    with st.sidebar:
        st.header("Zona analizata")
        preset = st.selectbox("Preset", [GALATI_PRESET["name"], "Custom bounding box"])
        bbox = list(GALATI_PRESET["bbox"])
        if preset == "Custom bounding box":
            west = st.number_input("West", value=float(bbox[0]), format="%.5f")
            south = st.number_input("South", value=float(bbox[1]), format="%.5f")
            east = st.number_input("East", value=float(bbox[2]), format="%.5f")
            north = st.number_input("North", value=float(bbox[3]), format="%.5f")
            bbox = [west, south, east, north]

        st.header("Perioade")
        before_start = st.date_input("before_start_date", GALATI_PRESET["before_start_date"])
        before_end = st.date_input("before_end_date", GALATI_PRESET["before_end_date"])
        after_start = st.date_input("after_start_date", GALATI_PRESET["after_start_date"])
        after_end = st.date_input("after_end_date", GALATI_PRESET["after_end_date"])

        st.header("Sentinel-1")
        polarization = st.radio("Polarization", ["VH", "VV"], horizontal=True)
        orbit_pass = st.selectbox("Orbit pass", ["BOTH", "ASCENDING", "DESCENDING"])
        smoothing_radius = st.slider("Smoothing radius", 0, 100, 30, 5)
        threshold = st.slider("SAR threshold", 0.5, 3.0, 1.25, 0.05)
        minimum_connected = st.slider("Minimum connected pixels", 0, 50, 8, 1)
        mask_permanent = st.toggle("Permanent water masking", value=True)

        st.header("Performanta")
        profile = st.selectbox(
            "Analysis profile", ["Rapid preview", "Standard", "Detailed export"], index=1
        )
        default_scale = PROFILE_SCALES[profile]
        scale = st.select_slider(
            "Scale",
            options=[10, 20, 30, 40, 50],
            value=default_scale,
        )

        st.header("Layere auxiliare")
        show_permanent = st.checkbox("show permanent water", True)
        show_land = st.checkbox("show land cover", True)
        show_s2 = st.checkbox("show Sentinel-2 RGB", False)
        show_before = st.checkbox("show SAR before", True)
        show_after = st.checkbox("show SAR after", True)
        show_change = st.checkbox("show SAR change", True)
        show_flood = st.checkbox("show detected flood extent", True)

        st.header("Comparatie")
        comparison = st.selectbox("Preset comparatie", list(COMPARISON_PRESETS))
        left_default, right_default = COMPARISON_PRESETS[comparison]
        left_layer = st.selectbox("Layer stanga", LAYER_OPTIONS, index=LAYER_OPTIONS.index(left_default))
        right_layer = st.selectbox("Layer dreapta", LAYER_OPTIONS, index=LAYER_OPTIONS.index(right_default))

        run_analysis = st.button("Run SAR Flood Analysis", type="primary", use_container_width=True)

    params = AnalysisParameters(
        aoi_name=GALATI_PRESET["name"] if preset == GALATI_PRESET["name"] else "custom AOI",
        bbox=bbox,
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
    return params, run_analysis
