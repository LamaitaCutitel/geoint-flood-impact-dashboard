from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from src.gee.dynamic_world import (
    dynamic_world_change_map,
    dynamic_world_mode,
    dynamic_world_water_change_masks,
    mask_area_km2,
)
from src.gee.gee_tile_layers import ee_tile_url
from src.gee.sar_water_masks import sar_dynamic_world_overlap, sar_water_area_metrics


TRANSITION_CLASSES = {
    4: "crops",
    2: "grass",
    6: "built",
    1: "trees",
    3: "flooded vegetation",
    5: "shrub and scrub",
    7: "bare",
}


def scene_day_period(scene: dict[str, Any]) -> tuple[str, str]:
    acquired = datetime.fromisoformat(str(scene["acquisition_time"]).replace("Z", "+00:00"))
    return acquired.date().isoformat(), (acquired.date() + timedelta(days=1)).isoformat()


def run_dynamic_world_analysis(
    ee: Any,
    aoi: Any,
    before_scene: dict[str, Any],
    after_scene: dict[str, Any],
    sar_new_water: Any,
    scale_meters: int = 10,
) -> dict[str, Any]:
    before_period = scene_day_period(before_scene)
    after_period = scene_day_period(after_scene)
    before = dynamic_world_mode(ee, aoi, *before_period)
    after = dynamic_world_mode(ee, aoi, *after_period)
    change = dynamic_world_change_map(ee, before, after, aoi)
    water_masks = dynamic_world_water_change_masks(before, after, sar_new_water, aoi)
    correlation = sar_dynamic_world_overlap(
        sar_new_water,
        water_masks["dynamic_world_new_water"],
        aoi,
    )
    areas = sar_water_area_metrics(
        ee,
        {
            "dynamic_world_new_water": water_masks["dynamic_world_new_water"],
            **correlation,
        },
        aoi,
        scale_meters,
    )
    transitions = {}
    for class_id, class_name in TRANSITION_CLASSES.items():
        mask = before.eq(class_id).And(after.eq(0)).selfMask().clip(aoi)
        transitions[class_name] = round(mask_area_km2(ee, mask, aoi, scale_meters), 4)
    tiles = {
        "dynamic_world_before": ee_tile_url(before, "Dynamic World before"),
        "dynamic_world_after": ee_tile_url(after, "Dynamic World after"),
        "dynamic_world_changes": ee_tile_url(change, "Land cover changes"),
        "dynamic_world_new_water": ee_tile_url(
            water_masks["dynamic_world_new_water"],
            "Dynamic World - apa noua",
        ),
        "both_methods": ee_tile_url(
            correlation["sar_dynamic_world_new_water_overlap"],
            "SAR x Dynamic World new water overlap",
        ),
        "only_sar": ee_tile_url(correlation["new_water_only_sar"], "New water only SAR"),
        "only_dynamic_world": ee_tile_url(
            correlation["new_water_only_dynamic_world"],
            "New water only Dynamic World",
        ),
    }
    return {
        "products": {
            "before": before,
            "after": after,
            "changes": change,
            **water_masks,
            **correlation,
        },
        "periods": {"before": before_period, "after": after_period},
        "metrics": areas,
        "transitions": transitions,
        "tiles": tiles,
        "charts": {
            "water_areas": {
                "Apă nouă SAR": areas.get("new_water_only_sar_area_km2", 0)
                + areas.get("sar_dynamic_world_new_water_overlap_area_km2", 0),
                "Apă nouă Dynamic World": areas.get(
                    "new_water_only_dynamic_world_area_km2", 0
                )
                + areas.get("sar_dynamic_world_new_water_overlap_area_km2", 0),
                "Suprapunere": areas.get(
                    "sar_dynamic_world_new_water_overlap_area_km2", 0
                ),
            },
            "transitions": transitions,
        },
    }


def dynamic_world_layer_definitions(result: dict[str, Any]) -> list[dict[str, Any]]:
    tiles = result.get("tiles", {})
    specifications = (
        ("dynamic_world_before", "Dynamic World BEFORE", "#419bdf", False),
        ("dynamic_world_after", "Dynamic World AFTER", "#397d49", False),
        ("dynamic_world_changes", "Modificări observate Dynamic World", "#facc15", False),
        ("dynamic_world_new_water", "Apă nouă evidențiată prin Dynamic World", "#0284c7", False),
        ("both_methods", "Apă nouă prin ambele metode", "#16a34a", False),
        ("only_sar", "Apă nouă doar SAR", "#22d3ee", False),
        ("only_dynamic_world", "Apă nouă doar Dynamic World", "#9333ea", False),
    )
    return [
        {"id": key, "name": name, "tile_url": tiles.get(key), "color": color, "shown": shown}
        for key, name, color, shown in specifications
    ]
