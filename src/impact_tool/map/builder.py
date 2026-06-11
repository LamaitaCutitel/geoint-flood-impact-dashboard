from __future__ import annotations

from typing import Any

import folium
from folium.plugins import Draw, Fullscreen, MeasureControl

from src.app.county_boundaries import bbox_center, feature_bbox, selected_county_feature
from src.impact_tool.map.layers import (
    add_aoi_layer,
    add_buffer_layer,
    add_county_outlines,
    add_osm_layers,
    add_tile_layers,
)
from src.impact_tool.map.legend import ImpactLegend, legend_entries
from src.impact_tool.map.swipe import SarSwipeControl
from src.impact_tool.map.tools import NavigationControl


ROMANIA_CENTER = [45.9432, 24.9668]


def build_shell_map(
    counties_geojson: dict[str, Any] | None,
    selected_county: str,
    aoi_geometry: dict[str, Any] | None = None,
    draw_enabled: bool = True,
    preview_tiles: dict[str, str] | None = None,
    analysis_layers: list[dict[str, Any]] | None = None,
    buffer_geometry: dict[str, Any] | None = None,
    osm_layers: dict[str, dict[str, Any]] | None = None,
) -> folium.Map:
    selected_feature = (
        selected_county_feature(counties_geojson, selected_county)
        if counties_geojson
        else None
    )
    selected_bbox = feature_bbox(selected_feature) if selected_feature else None
    center = bbox_center(selected_bbox) if selected_bbox else ROMANIA_CENTER

    folium_map = folium.Map(
        location=center,
        zoom_start=8 if selected_feature else 6,
        tiles="CartoDB dark_matter",
        control_scale=True,
        zoom_control=True,
    )
    add_county_outlines(folium_map, counties_geojson, selected_county)
    add_aoi_layer(folium_map, aoi_geometry)
    add_tile_layers(folium_map, analysis_layers or [])
    add_buffer_layer(folium_map, buffer_geometry)
    add_osm_layers(folium_map, osm_layers or {})
    if draw_enabled:
        Draw(
            export=False,
            position="topleft",
            draw_options={
                "polyline": False,
                "polygon": {
                    "allowIntersection": False,
                    "showArea": True,
                    "shapeOptions": {
                        "color": "#16a34a",
                        "weight": 3,
                        "fillColor": "#22c55e",
                        "fillOpacity": 0.08,
                    },
                },
                "rectangle": {
                    "shapeOptions": {
                        "color": "#16a34a",
                        "weight": 3,
                        "fillColor": "#22c55e",
                        "fillOpacity": 0.08,
                    },
                },
                "circle": False,
                "marker": False,
                "circlemarker": False,
            },
            edit_options={"edit": False, "remove": False},
        ).add_to(folium_map)
    if selected_bbox:
        folium_map.fit_bounds(
            [[selected_bbox[1], selected_bbox[0]], [selected_bbox[3], selected_bbox[2]]]
        )
        NavigationControl(
            [[selected_bbox[1], selected_bbox[0]], [selected_bbox[3], selected_bbox[2]]]
        ).add_to(folium_map)
    MeasureControl(
        position="topleft",
        primary_length_unit="meters",
        primary_area_unit="sqmeters",
    ).add_to(folium_map)
    Fullscreen(
        position="topleft",
        title="Ecran complet",
        title_cancel="Ieși din ecran complet",
    ).add_to(folium_map)
    folium.LatLngPopup().add_to(folium_map)
    ImpactLegend(
        legend_entries(
            analysis_layers,
            bool(buffer_geometry),
            osm_layers,
        )
    ).add_to(folium_map)
    if preview_tiles and preview_tiles.get("before") and preview_tiles.get("after"):
        SarSwipeControl(preview_tiles["before"], preview_tiles["after"]).add_to(folium_map)
    if analysis_layers or osm_layers or buffer_geometry:
        folium.LayerControl(collapsed=True, position="topright").add_to(folium_map)
    return folium_map
