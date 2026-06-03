from __future__ import annotations

from typing import Any

from config.settings import LAND_COVER_CLASSES
from src.gee.gee_config import COLLECTIONS
from src.utils.area_utils import dominant_class, square_meters_to_square_kilometers


def dynamic_world_mode(ee: Any, aoi: Any, start_date: str, end_date: str) -> Any:
    return (
        ee.ImageCollection(COLLECTIONS.dynamic_world)
        .filterBounds(aoi)
        .filterDate(start_date, end_date)
        .select("label")
        .mode()
        .clip(aoi)
    )


def dynamic_world_change_map(ee: Any, before: Any, after: Any, aoi: Any) -> Any:
    water_class = 0
    no_change = before.eq(after)
    new_water = after.eq(water_class).And(before.neq(water_class))
    water_loss = before.eq(water_class).And(after.neq(water_class))
    other_change = before.neq(after).And(new_water.Not()).And(water_loss.Not())
    return (
        ee.Image(0)
        .where(no_change, 1)
        .where(other_change, 2)
        .where(water_loss, 3)
        .where(new_water, 4)
        .rename("land_cover_changes")
        .clip(aoi)
    )


def land_cover_intersection_stats(
    ee: Any,
    land_cover: Any,
    flood_mask: Any,
    aoi: Any,
    scale: int,
) -> dict[str, float]:
    stats: dict[str, float] = {name: 0.0 for name in LAND_COVER_CLASSES.values()}
    try:
        pixel_area = ee.Image.pixelArea().addBands(land_cover.rename("label"))
        grouped = pixel_area.updateMask(flood_mask).reduceRegion(
            reducer=ee.Reducer.sum().group(groupField=1, groupName="label"),
            geometry=aoi,
            scale=scale,
            maxPixels=1e9,
            bestEffort=True,
        ).getInfo()
    except Exception:
        return stats

    for item in grouped.get("groups", []):
        label = int(item.get("label"))
        class_name = LAND_COVER_CLASSES.get(label, f"class_{label}")
        stats[class_name] = square_meters_to_square_kilometers(item.get("sum", 0))
    return stats


def summarize_land_cover(stats: dict[str, float]) -> dict[str, str | float]:
    return {
        "dominant_class": dominant_class(stats),
        "crops_intersected_km2": round(stats.get("crops", 0.0), 4),
        "built_up_intersected_km2": round(stats.get("built", 0.0), 4),
        "vegetation_intersected_km2": round(
            stats.get("trees", 0.0)
            + stats.get("grass", 0.0)
            + stats.get("flooded vegetation", 0.0)
            + stats.get("shrub and scrub", 0.0),
            4,
        ),
    }
