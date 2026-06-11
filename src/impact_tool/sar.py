from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Any

from src.gee.gee_tile_layers import ee_tile_url
from src.gee.sar_water_masks import (
    sar_water_area_metrics,
    sar_water_change_masks,
    sar_water_mask,
)
from src.gee.sentinel1_scene_explorer import selected_scene_image


@dataclass(frozen=True)
class SarParameters:
    water_threshold: float = -18.0
    smoothing_meters: int = 0
    minimum_connected_pixels: int = 8
    scale_meters: int = 10


def run_sar_analysis(
    ee: Any,
    aoi: Any,
    before_scene: dict[str, Any],
    after_scene: dict[str, Any],
    parameters: SarParameters,
) -> dict[str, Any]:
    started = perf_counter()
    before_image = selected_scene_image(
        ee,
        before_scene,
        aoi,
        smoothing_radius=parameters.smoothing_meters,
    )
    after_image = selected_scene_image(
        ee,
        after_scene,
        aoi,
        smoothing_radius=parameters.smoothing_meters,
    )
    before_water = sar_water_mask(
        before_image,
        parameters.water_threshold,
        aoi,
        parameters.minimum_connected_pixels,
    )
    after_water = sar_water_mask(
        after_image,
        parameters.water_threshold,
        aoi,
        parameters.minimum_connected_pixels,
    )
    changes = sar_water_change_masks(before_water, after_water, aoi)
    masks = {
        "sar_water_before": before_water,
        "sar_water_after": after_water,
        "sar_new_water": changes["sar_new_water"],
    }
    metrics = sar_water_area_metrics(ee, masks, aoi, parameters.scale_meters)
    tiles = {
        "sar_water_before": ee_tile_url(before_water, "SAR water BEFORE"),
        "sar_water_after": ee_tile_url(after_water, "SAR water AFTER"),
        "sar_new_water": ee_tile_url(changes["sar_new_water"], "SAR new water"),
    }
    new_water_geometry = _vector_geometry(changes["sar_new_water"], aoi)
    return {
        "products": {**masks, **changes},
        "metrics": metrics,
        "tiles": tiles,
        "new_water_geometry": new_water_geometry,
        "parameters": {
            "polarization": before_scene.get("polarization"),
            "water_threshold": parameters.water_threshold,
            "smoothing_meters": parameters.smoothing_meters,
            "minimum_connected_pixels": parameters.minimum_connected_pixels,
        },
        "duration_seconds": round(perf_counter() - started, 3),
    }


def _vector_geometry(mask: Any, aoi: Any) -> dict[str, Any] | None:
    try:
        vectors = mask.reduceToVectors(
            geometry=aoi,
            scale=30,
            geometryType="polygon",
            eightConnected=True,
            maxPixels=1e8,
            bestEffort=True,
        )
        return vectors.geometry().getInfo()
    except Exception:
        return None


def sar_layer_definitions(result: dict[str, Any]) -> list[dict[str, Any]]:
    tiles = result.get("tiles", {})
    return [
        {
            "id": "sar_water_before",
            "name": "Apă observată BEFORE",
            "tile_url": tiles.get("sar_water_before"),
            "color": "#7dd3fc",
            "shown": False,
        },
        {
            "id": "sar_water_after",
            "name": "Apă observată AFTER",
            "tile_url": tiles.get("sar_water_after"),
            "color": "#2563eb",
            "shown": False,
        },
        {
            "id": "sar_new_water",
            "name": "Apă nouă evidențiată prin SAR",
            "tile_url": tiles.get("sar_new_water"),
            "color": "#22d3ee",
            "shown": True,
        },
    ]
