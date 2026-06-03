from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import folium
from folium.plugins import SideBySideLayers

from src.app.county_boundaries import bbox_center, county_display_name, zoom_for_bbox
from src.gee.gee_tile_layers import add_ee_tile_layer


ROMANIA_CENTER = [45.9432, 24.9668]
ROMANIA_ZOOM = 6


@dataclass
class MapBundle:
    main_map: folium.Map
    comparison_map: folium.Map | None = None
    fallback_reason: str | None = None


def _base_map(center: list[float] | None = None, zoom: int | None = None) -> folium.Map:
    return folium.Map(
        location=center or ROMANIA_CENTER,
        zoom_start=zoom or ROMANIA_ZOOM,
        tiles="CartoDB positron",
        control_scale=True,
    )


def add_counties_layer(
    folium_map: folium.Map,
    counties_geojson: dict[str, Any] | None,
    selected_county: str,
) -> None:
    if not counties_geojson:
        return

    def style_function(feature: dict[str, Any]) -> dict[str, Any]:
        is_selected = county_display_name(feature) == selected_county
        return {
            "color": "#dc2626" if is_selected else "#334155",
            "weight": 3 if is_selected else 1,
            "fillColor": "#f97316" if is_selected else "#38bdf8",
            "fillOpacity": 0.32 if is_selected else 0.13,
        }

    def highlight_function(_: dict[str, Any]) -> dict[str, Any]:
        return {"weight": 3, "color": "#0f172a", "fillOpacity": 0.35}

    folium.GeoJson(
        counties_geojson,
        name="Judetele Romaniei",
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(
            fields=["NAME_LATN"],
            aliases=["Judet"],
            localize=True,
            sticky=True,
        ),
        popup=folium.GeoJsonPopup(fields=["NAME_LATN"], aliases=["Judet"]),
    ).add_to(folium_map)


def build_county_overview_map(
    counties_geojson: dict[str, Any] | None,
    selected_county: str,
    selected_bbox: list[float] | None = None,
) -> folium.Map:
    center = bbox_center(selected_bbox) if selected_bbox else ROMANIA_CENTER
    zoom = zoom_for_bbox(selected_bbox) if selected_bbox else ROMANIA_ZOOM
    folium_map = _base_map(center, zoom)
    add_counties_layer(folium_map, counties_geojson, selected_county)
    if selected_bbox:
        folium_map.fit_bounds(
            [[selected_bbox[1], selected_bbox[0]], [selected_bbox[3], selected_bbox[2]]]
        )
    folium.LayerControl(collapsed=False).add_to(folium_map)
    return folium_map


def build_maps(
    layer_images: dict[str, Any],
    params: Any,
    counties_geojson: dict[str, Any] | None = None,
) -> MapBundle:
    center = bbox_center(params.bbox)
    zoom = zoom_for_bbox(params.bbox)
    main_map = _base_map(center, zoom)
    add_counties_layer(main_map, counties_geojson, params.county_name)
    main_map.fit_bounds([[params.bbox[1], params.bbox[0]], [params.bbox[3], params.bbox[2]]])

    shown_layers = {
        "detected flood extent",
        "Sentinel-1 SAR after",
    }
    if params.show_permanent_water:
        shown_layers.add("permanent water")

    for layer_name, image in layer_images.items():
        add_ee_tile_layer(main_map, image, layer_name, shown=layer_name in shown_layers)

    folium.LayerControl(collapsed=False).add_to(main_map)

    comparison_map = _base_map(center, zoom)
    comparison_map.fit_bounds([[params.bbox[1], params.bbox[0]], [params.bbox[3], params.bbox[2]]])
    left = add_ee_tile_layer(
        comparison_map, layer_images.get(params.left_layer), params.left_layer, True
    )
    right = add_ee_tile_layer(
        comparison_map, layer_images.get(params.right_layer), params.right_layer, True
    )
    fallback_reason = None
    if left and right:
        try:
            SideBySideLayers(left, right).add_to(comparison_map)
        except Exception as exc:
            fallback_reason = f"Fallback comparatie side-by-side: {exc}"
    else:
        fallback_reason = "Comparația side-by-side nu are ambele layere disponibile."

    folium.LayerControl(collapsed=False).add_to(comparison_map)
    return MapBundle(
        main_map=main_map,
        comparison_map=comparison_map,
        fallback_reason=fallback_reason,
    )
