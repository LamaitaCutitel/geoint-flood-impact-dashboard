from __future__ import annotations

import pandas as pd
import plotly.express as px

from config.settings import METHODOLOGICAL_NOTE


METRIC_HELP = {
    "Judet analizat": "Unitatea administrativa folosita ca AOI pentru analiza SAR.",
    "Scene Sentinel-1 before": "Numarul imaginilor SAR disponibile in perioada de referinta.",
    "Scene Sentinel-1 after": "Numarul imaginilor SAR disponibile dupa eveniment.",
    "Scene Sentinel-2 before": "Numarul imaginilor optice disponibile in perioada de referinta.",
    "Scene Sentinel-2 after": "Numarul imaginilor optice disponibile dupa eveniment.",
    "Suprafata preliminara detectata": "Suprafata estimata automat prin analiza schimbarii semnalului SAR, dupa aplicarea filtrelor.",
    "Apa permanenta eliminata": "Suprafata eliminata folosind JRC Global Surface Water.",
    "Teren agricol intersectat": "Suprafata clasei crops intersectata de extinderea preliminara detectata.",
    "Zona construita intersectata": "Suprafata clasei built intersectata de extinderea preliminara detectata.",
    "Vegetatie intersectata": "Suma claselor de vegetatie intersectate de extinderea preliminara.",
    "Clasa dominanta": "Clasa Dynamic World cu cea mai mare suprafata intersectata.",
    "Durata procesarii": "Durata masurata local pentru fluxul declansat de utilizator.",
}


def render_metric_cards(st, metrics: dict[str, object]) -> None:
    cards = [
        ("Judet analizat", metrics.get("county_name", metrics.get("aoi", "n/a"))),
        ("Scene Sentinel-1 before", metrics.get("scene_count_before", 0)),
        ("Scene Sentinel-1 after", metrics.get("scene_count_after", 0)),
        ("Scene Sentinel-2 before", metrics.get("sentinel2_scene_count_before", 0)),
        ("Scene Sentinel-2 after", metrics.get("sentinel2_scene_count_after", 0)),
        ("Suprafata preliminara detectata", f"{metrics.get('sar_detected_extent_km2', 0.0)} km2"),
        ("Apa permanenta eliminata", f"{metrics.get('permanent_water_removed_km2', 0.0)} km2"),
        ("Teren agricol intersectat", f"{metrics.get('crops_intersected_km2', 0.0)} km2"),
        ("Zona construita intersectata", f"{metrics.get('built_up_intersected_km2', 0.0)} km2"),
        ("Vegetatie intersectata", f"{metrics.get('vegetation_intersected_km2', 0.0)} km2"),
        ("Clasa dominanta", metrics.get("dominant_land_cover_class", "n/a")),
        ("Durata procesarii", metrics.get("processing_time", "n/a")),
    ]
    st.subheader("Rezultatele analizei")
    columns = st.columns(3)
    for index, (label, value) in enumerate(cards):
        with columns[index % 3].container(border=True):
            st.metric(label, value)
            st.caption(METRIC_HELP[label])


def render_land_cover(st, land_cover_stats: dict[str, float]) -> None:
    df = pd.DataFrame(
        [{"clasa": name, "suprafata_km2": area} for name, area in land_cover_stats.items()]
    )
    st.subheader("Terenuri intersectate de extinderea preliminara detectata")
    st.dataframe(df, use_container_width=True, hide_index=True)
    if not df.empty:
        fig = px.bar(df, x="clasa", y="suprafata_km2", color="clasa")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="km2")
        st.plotly_chart(fig, use_container_width=True)


def render_methodological_note(st) -> None:
    st.warning(METHODOLOGICAL_NOTE)
