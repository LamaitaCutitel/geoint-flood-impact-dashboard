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
    "SAR water BEFORE": "Zone cu semnal radar compatibil cu apa in scena BEFORE.",
    "SAR water AFTER": "Zone cu semnal radar compatibil cu apa in scena AFTER.",
    "SAR new water": "Zone compatibile cu apa in AFTER, absente ca apa in BEFORE.",
    "SAR persistent water": "Zone compatibile cu apa in ambele scene SAR.",
    "SAR water loss": "Zone compatibile cu apa in BEFORE, absente in AFTER.",
    "Apa noua Dynamic World": "Apa noua evidentiata prin Dynamic World: non-apa BEFORE -> apa AFTER.",
    "Intersectie SAR x DW": "Intersectie cu extinderea preliminara SAR si apa noua evidentiata prin Dynamic World.",
    "Suprapunere SAR x DW": "Procent din extinderea SAR intersectat cu apa noua Dynamic World.",
    "Apa permanenta eliminata": "Suprafata eliminata folosind JRC Global Surface Water.",
    "Teren agricol intersectat": "Suprafata clasei crops intersectata de extinderea preliminara detectata.",
    "Zona construita intersectata": "Suprafata clasei built intersectata de extinderea preliminara detectata.",
    "Vegetatie intersectata": "Suma claselor de vegetatie intersectate de extinderea preliminara.",
    "Clasa dominanta": "Clasa Dynamic World cu cea mai mare suprafata intersectata.",
    "Cladiri potential afectate OSM": "Numar estimativ de cladiri OSM in zona de interogare extinsa cu buffer.",
    "Drumuri intersectate OSM": "Lungime estimativa de drumuri OSM intersectate de zona de interogare.",
    "Obiective critice OSM": "Numar estimativ de obiective critice OSM in zona de interogare.",
    "Cai ferate intersectate OSM": "Lungime estimativa de cai ferate OSM intersectate.",
    "Poduri OSM": "Numar estimativ de elemente OSM marcate ca poduri.",
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
        ("SAR water BEFORE", f"{metrics.get('sar_water_before_area_km2', 0.0)} km2"),
        ("SAR water AFTER", f"{metrics.get('sar_water_after_area_km2', 0.0)} km2"),
        ("SAR new water", f"{metrics.get('sar_new_water_area_km2', 0.0)} km2"),
        ("SAR persistent water", f"{metrics.get('sar_persistent_water_area_km2', 0.0)} km2"),
        ("SAR water loss", f"{metrics.get('sar_water_loss_area_km2', 0.0)} km2"),
        ("Apa noua Dynamic World", f"{metrics.get('dynamic_world_new_water_km2', 0.0)} km2"),
        ("Intersectie SAR x DW", f"{metrics.get('sar_dynamic_world_new_water_intersection_km2', 0.0)} km2"),
        ("Suprapunere SAR x DW", f"{metrics.get('sar_dynamic_world_overlap_percent', 0.0)}%"),
        ("Apa permanenta eliminata", f"{metrics.get('permanent_water_removed_km2', 0.0)} km2"),
        ("Teren agricol intersectat", f"{metrics.get('crops_intersected_km2', 0.0)} km2"),
        ("Zona construita intersectata", f"{metrics.get('built_up_intersected_km2', 0.0)} km2"),
        ("Vegetatie intersectata", f"{metrics.get('vegetation_intersected_km2', 0.0)} km2"),
        ("Clasa dominanta", metrics.get("dominant_land_cover_class", "n/a")),
        ("Cladiri potential afectate OSM", metrics.get("osm_buildings_potentially_affected", 0)),
        ("Drumuri intersectate OSM", f"{metrics.get('osm_roads_intersected_km', 0.0)} km"),
        ("Obiective critice OSM", metrics.get("osm_critical_assets", 0)),
        ("Cai ferate intersectate OSM", f"{metrics.get('osm_railways_intersected_km', 0.0)} km"),
        ("Poduri OSM", metrics.get("osm_bridges", 0)),
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
