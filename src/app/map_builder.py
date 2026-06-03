from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import folium
from folium.plugins import SideBySideLayers

from config.settings import GALATI_PRESET
from src.gee.gee_tile_layers import add_ee_tile_layer


@dataclass
class MapBundle:
    main_map: folium.Map
    comparison_map: folium.Map
    fallback_reason: str | None = None


def _base_map(center: list[float] | None = None, zoom: int | None = None) -> folium.Map:
    return folium.Map(
        location=center or GALATI_PRESET["center"],
        zoom_start=zoom or GALATI_PRESET["zoom"],
        tiles="CartoDB positron",
        control_scale=True,
    )


def build_maps(
    layer_images: dict[str, Any],
    params: Any,
    center: list[float] | None = None,
    zoom: int | None = None,
) -> MapBundle:
    main_map = _base_map(center, zoom)
    comparison_map = _base_map(center, zoom)

    for layer_name, image in layer_images.items():
        add_ee_tile_layer(
            main_map,
            image,
            layer_name,
            shown=layer_name in {
                "detected flood extent",
                "permanent water",
                "Sentinel-1 SAR after",
            },
        )

    left = add_ee_tile_layer(comparison_map, layer_images.get(params.left_layer), params.left_layer, True)
    right = add_ee_tile_layer(comparison_map, layer_images.get(params.right_layer), params.right_layer, True)
    fallback_reason = None
    if left and right:
        try:
            SideBySideLayers(left, right).add_to(comparison_map)
        except Exception as exc:
            fallback_reason = f"SideBySideLayers fallback: {exc}"
    else:
        fallback_reason = "Comparația side-by-side nu are ambele layere disponibile."

    folium.LayerControl(collapsed=False).add_to(main_map)
    folium.LayerControl(collapsed=False).add_to(comparison_map)
    return MapBundle(main_map=main_map, comparison_map=comparison_map, fallback_reason=fallback_reason)


def build_placeholder_map(params: Any) -> MapBundle:
    main_map = _base_map()
    bounds = [[params.bbox[1], params.bbox[0]], [params.bbox[3], params.bbox[2]]]
    folium.Rectangle(
        bounds=bounds,
        color="#2563eb",
        weight=2,
        fill=True,
        fill_opacity=0.08,
        tooltip="AOI preset Galati",
    ).add_to(main_map)
    folium.LayerControl(collapsed=False).add_to(main_map)
    comparison_map = _base_map()
    folium.Rectangle(bounds=bounds, color="#dc2626", weight=2, fill=False).add_to(comparison_map)
    return MapBundle(
        main_map=main_map,
        comparison_map=comparison_map,
        fallback_reason="Earth Engine nu este initializat; se afiseaza doar AOI.",
    )
