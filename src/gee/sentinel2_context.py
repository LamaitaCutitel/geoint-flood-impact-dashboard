from __future__ import annotations

from typing import Any

from src.gee.gee_config import COLLECTIONS


def sentinel2_rgb_context(ee: Any, aoi: Any, start_date: str, end_date: str) -> Any:
    collection = (
        ee.ImageCollection(COLLECTIONS.sentinel2)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 60))
        .select(["B4", "B3", "B2"])
    )
    return collection.median().clip(aoi)
