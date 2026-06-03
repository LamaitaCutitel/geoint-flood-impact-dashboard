from __future__ import annotations

from typing import Any

import folium


VIS_PARAMS = {
    "Sentinel-1 SAR before": {"min": -25, "max": 0, "palette": ["111827", "e5e7eb"]},
    "Sentinel-1 SAR after": {"min": -25, "max": 0, "palette": ["111827", "e5e7eb"]},
    "SAR change": {"min": 0.8, "max": 2.0, "palette": ["2563eb", "facc15", "dc2626"]},
    "permanent water": {"palette": ["2563eb"]},
    "detected flood extent": {"palette": ["ef4444"]},
    "land cover": {
        "min": 0,
        "max": 8,
        "palette": [
            "419bdf",
            "397d49",
            "88b053",
            "7a87c6",
            "e49635",
            "dfc35a",
            "c4281b",
            "a59b8f",
            "b39fe1",
        ],
    },
    "Sentinel-2 RGB": {"min": 0, "max": 3000, "bands": ["B4", "B3", "B2"]},
}


def add_ee_tile_layer(
    folium_map: folium.Map,
    ee_image: Any,
    name: str,
    shown: bool = False,
) -> folium.raster_layers.TileLayer | None:
    try:
        tile = ee_image.getMapId(VIS_PARAMS.get(name, {}))
        layer = folium.TileLayer(
            tiles=tile["tile_fetcher"].url_format,
            attr="Google Earth Engine",
            name=name,
            overlay=True,
            control=True,
            show=shown,
        )
        layer.add_to(folium_map)
        return layer
    except Exception:
        return None
