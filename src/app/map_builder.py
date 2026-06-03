from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import folium

from src.app.county_boundaries import bbox_center, county_display_name, zoom_for_bbox
from src.app.layer_registry import LayerEntry, LayerRegistry
from src.app.leaflet_compare_control import DynamicCompareControl
from src.gee.gee_tile_layers import ee_tile_url


ROMANIA_CENTER = [45.9432, 24.9668]
ROMANIA_ZOOM = 6


@dataclass
class MapBundle:
    main_map: folium.Map
    registry: LayerRegistry | None = None
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
        name="Administrativ - toate judetele",
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(fields=["NAME_LATN"], aliases=["Judet"], localize=True, sticky=True),
        popup=folium.GeoJsonPopup(fields=["NAME_LATN"], aliases=["Judet"]),
        show=True,
    ).add_to(folium_map)


def add_selected_county_layer(
    folium_map: folium.Map,
    selected_feature: dict[str, Any] | None,
) -> None:
    if not selected_feature:
        return
    folium.GeoJson(
        selected_feature,
        name="Administrativ - judet selectat",
        style_function=lambda _: {
            "color": "#b91c1c",
            "weight": 4,
            "fillColor": "#f97316",
            "fillOpacity": 0.18,
        },
        tooltip=folium.GeoJsonTooltip(fields=["NAME_LATN"], aliases=["Judet"]),
        popup=folium.GeoJsonPopup(fields=["NAME_LATN"], aliases=["Judet selectat"]),
        show=True,
    ).add_to(folium_map)


def build_county_overview_map(
    counties_geojson: dict[str, Any] | None,
    selected_county: str,
    selected_bbox: list[float] | None = None,
    selected_feature: dict[str, Any] | None = None,
) -> MapBundle:
    center = bbox_center(selected_bbox) if selected_bbox else ROMANIA_CENTER
    zoom = zoom_for_bbox(selected_bbox) if selected_bbox else ROMANIA_ZOOM
    folium_map = _base_map(center, zoom)
    add_counties_layer(folium_map, counties_geojson, selected_county)
    add_selected_county_layer(folium_map, selected_feature)
    if selected_bbox:
        folium_map.fit_bounds([[selected_bbox[1], selected_bbox[0]], [selected_bbox[3], selected_bbox[2]]])
    folium.LayerControl(collapsed=False).add_to(folium_map)
    return MapBundle(main_map=folium_map)


def build_maps(
    layer_images: dict[str, dict[str, Any]],
    params: Any,
    counties_geojson: dict[str, Any] | None = None,
    selected_feature: dict[str, Any] | None = None,
    registry: LayerRegistry | None = None,
) -> MapBundle:
    registry = registry or LayerRegistry()
    center = bbox_center(params.bbox)
    zoom = zoom_for_bbox(params.bbox)
    main_map = _base_map(center, zoom)
    add_counties_layer(main_map, counties_geojson, params.county_name)
    add_selected_county_layer(main_map, selected_feature)
    main_map.fit_bounds([[params.bbox[1], params.bbox[0]], [params.bbox[3], params.bbox[2]]])

    for layer_id, meta in layer_images.items():
        display_name = meta["display_name"]
        tile_url = ee_tile_url(meta["image"], display_name)
        if not tile_url:
            registry.unavailable(
                layer_id=layer_id,
                display_name=display_name,
                category=meta["category"],
                layer_type=meta["layer_type"],
                warning=f"Nu s-a putut genera tile URL pentru {display_name}.",
            )
            continue
        layer = folium.TileLayer(
            tiles=tile_url,
            attr="Google Earth Engine",
            name=f"{meta['category']} - {display_name}",
            overlay=True,
            control=True,
            show=meta.get("shown", False),
        )
        layer.add_to(main_map)
        registry.add(
            LayerEntry(
                id=layer_id,
                display_name=display_name,
                category=meta["category"],
                layer_type=meta["layer_type"],
                available=True,
                comparable=meta.get("comparable", True),
                shown=meta.get("shown", False),
                tile_url=tile_url,
                folium_layer=layer,
            )
        )

    DynamicCompareControl(registry).add_to(main_map)
    folium.LayerControl(collapsed=False).add_to(main_map)
    return MapBundle(main_map=main_map, registry=registry)
