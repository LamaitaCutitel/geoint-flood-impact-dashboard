from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.gee.permanent_water import mask_permanent_water
from src.utils.area_utils import square_meters_to_square_kilometers


@dataclass
class FloodDetectionResult:
    flood_mask: Any
    change_image: Any
    detected_extent_km2: float
    permanent_water_removed_km2: float
    warnings: list[str]


def detect_flood_extent(
    ee: Any,
    before_image: Any,
    after_image: Any,
    aoi: Any,
    threshold: float,
    minimum_connected_pixels: int,
    scale: int,
    permanent_water: Any | None = None,
) -> FloodDetectionResult:
    warnings: list[str] = []
    change = before_image.divide(after_image).rename("sar_ratio")
    flood_mask = change.gt(threshold).selfMask()

    if minimum_connected_pixels > 0:
        connected = flood_mask.connectedPixelCount(100, True)
        flood_mask = flood_mask.updateMask(connected.gte(minimum_connected_pixels))

    extent_before_water_mask = _area_km2(ee, flood_mask, aoi, scale)
    permanent_removed = 0.0
    if permanent_water is not None:
        flood_mask_without_permanent = mask_permanent_water(flood_mask, permanent_water)
        extent_after_water_mask = _area_km2(ee, flood_mask_without_permanent, aoi, scale)
        permanent_removed = max(extent_before_water_mask - extent_after_water_mask, 0.0)
        flood_mask = flood_mask_without_permanent
    else:
        warnings.append("Masca de apa permanenta nu a fost aplicata.")
        extent_after_water_mask = extent_before_water_mask

    return FloodDetectionResult(
        flood_mask=flood_mask,
        change_image=change,
        detected_extent_km2=extent_after_water_mask,
        permanent_water_removed_km2=round(permanent_removed, 4),
        warnings=warnings,
    )


def _area_km2(ee: Any, mask: Any, aoi: Any, scale: int) -> float:
    try:
        area_image = mask.multiply(ee.Image.pixelArea())
        stats = area_image.reduceRegion(
            reducer=ee.Reducer.sum(),
            geometry=aoi,
            scale=scale,
            maxPixels=1e9,
            bestEffort=True,
        ).getInfo()
        area_sqm = next(iter(stats.values()), 0) if stats else 0
        return square_meters_to_square_kilometers(area_sqm)
    except Exception:
        return 0.0
