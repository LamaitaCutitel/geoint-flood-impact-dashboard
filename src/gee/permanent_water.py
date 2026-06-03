from __future__ import annotations

from typing import Any

from src.gee.gee_config import COLLECTIONS


def permanent_water_mask(ee: Any, aoi: Any) -> Any:
    water = ee.Image(COLLECTIONS.permanent_water).clip(aoi)
    occurrence = water.select("occurrence").gte(50)
    seasonality = water.select("seasonality").gte(10)
    return occurrence.Or(seasonality).selfMask().clip(aoi)


def mask_permanent_water(flood_mask: Any, permanent_water: Any) -> Any:
    return flood_mask.updateMask(permanent_water.Not())
