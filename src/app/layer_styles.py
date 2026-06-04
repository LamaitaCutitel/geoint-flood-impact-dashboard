from __future__ import annotations

from typing import Any


LAYER_STYLES: dict[str, dict[str, Any]] = {
    "sar_before": {
        "display_name": "Sentinel-1 SAR before",
        "vis_params": {"min": -25, "max": 0, "palette": ["111827", "e5e7eb"]},
        "legend_color": "#94a3b8",
        "description": "Scena sau compozit SAR BEFORE in tonuri gri.",
        "category": "Sentinel-1 SAR",
    },
    "sar_after": {
        "display_name": "Sentinel-1 SAR after",
        "vis_params": {"min": -25, "max": 0, "palette": ["111827", "e5e7eb"]},
        "legend_color": "#64748b",
        "description": "Scena sau compozit SAR AFTER in tonuri gri.",
        "category": "Sentinel-1 SAR",
    },
    "sar_difference": {
        "display_name": "SAR difference",
        "vis_params": {"bands": ["sar_difference"], "min": -5, "max": 5, "palette": ["2563eb", "f8fafc", "dc2626"]},
        "legend_color": "#dc2626",
        "description": "Diferenta observata intre imaginile SAR BEFORE si AFTER.",
        "category": "Sentinel-1 SAR",
    },
    "sar_ratio": {
        "display_name": "SAR ratio",
        "vis_params": {"bands": ["sar_ratio"], "min": 0.8, "max": 2.0, "palette": ["2563eb", "facc15", "dc2626"]},
        "legend_color": "#facc15",
        "description": "Raport SAR pentru change detection.",
        "category": "Sentinel-1 SAR",
    },
    "sar_water_before": {
        "display_name": "SAR water BEFORE",
        "vis_params": {"palette": ["7dd3fc"]},
        "legend_color": "#7dd3fc",
        "description": "Pixeli SAR compatibili cu apa in scena BEFORE.",
        "category": "Apa observata prin SAR",
    },
    "sar_water_after": {
        "display_name": "SAR water AFTER",
        "vis_params": {"palette": ["2563eb"]},
        "legend_color": "#2563eb",
        "description": "Pixeli SAR compatibili cu apa in scena AFTER.",
        "category": "Apa observata prin SAR",
    },
    "sar_new_water": {
        "display_name": "SAR new water",
        "vis_params": {"palette": ["22d3ee"]},
        "legend_color": "#22d3ee",
        "description": "Apa observata automat prin SAR in AFTER, absenta in BEFORE.",
        "category": "Apa observata prin SAR",
    },
    "sar_persistent_water": {
        "display_name": "SAR persistent water",
        "vis_params": {"palette": ["1e3a8a"]},
        "legend_color": "#1e3a8a",
        "description": "Apa observata automat prin SAR in ambele scene.",
        "category": "Apa observata prin SAR",
    },
    "sar_water_loss": {
        "display_name": "SAR water loss",
        "vis_params": {"palette": ["f97316"]},
        "legend_color": "#f97316",
        "description": "Apa observata automat prin SAR in BEFORE, absenta in AFTER.",
        "category": "Apa observata prin SAR",
    },
    "flood_extent": {
        "display_name": "SAR flood extent filtrat",
        "vis_params": {"palette": ["be185d"]},
        "legend_color": "#be185d",
        "description": "Extindere preliminara SAR filtrata prin change detection si filtre auxiliare.",
        "category": "Apa observata prin SAR",
    },
    "permanent_water": {
        "display_name": "permanent water",
        "vis_params": {"palette": ["0f172a"]},
        "legend_color": "#0f172a",
        "description": "Apa permanenta sau recurenta JRC.",
        "category": "Apa permanenta JRC",
    },
    "dynamic_world_before": {
        "display_name": "Dynamic World before",
        "vis_params": {
            "min": 0,
            "max": 8,
            "palette": ["419bdf", "397d49", "88b053", "7a87c6", "e49635", "dfc35a", "c4281b", "a59b8f", "b39fe1"],
        },
        "legend_color": "#419bdf",
        "description": "Clasa modala Dynamic World BEFORE.",
        "category": "Land cover",
    },
    "dynamic_world_after": {
        "display_name": "Dynamic World after",
        "vis_params": {
            "min": 0,
            "max": 8,
            "palette": ["419bdf", "397d49", "88b053", "7a87c6", "e49635", "dfc35a", "c4281b", "a59b8f", "b39fe1"],
        },
        "legend_color": "#397d49",
        "description": "Clasa modala Dynamic World AFTER.",
        "category": "Land cover",
    },
    "dynamic_world_changes": {
        "display_name": "Land cover changes",
        "vis_params": {"min": 1, "max": 4, "palette": ["e5e7eb", "facc15", "fb7185", "0284c7"]},
        "legend_color": "#a78bfa",
        "description": "Diferente observate Dynamic World intre BEFORE si AFTER.",
        "category": "Land cover",
    },
    "dynamic_world_new_water": {
        "display_name": "Dynamic World - apa noua",
        "vis_params": {"palette": ["818cf8"]},
        "legend_color": "#818cf8",
        "description": "Diferente observate Dynamic World: non-apa BEFORE reclasificata ca apa AFTER.",
        "category": "Cresterea apei - Dynamic World",
    },
    "dynamic_world_water_loss": {
        "display_name": "Dynamic World - pierdere apa",
        "vis_params": {"palette": ["f59e0b"]},
        "legend_color": "#f59e0b",
        "description": "Diferente observate Dynamic World: apa BEFORE reclasificata non-apa AFTER.",
        "category": "Cresterea apei - Dynamic World",
    },
    "dynamic_world_other_change": {
        "display_name": "Dynamic World - alte diferente",
        "vis_params": {"palette": ["a78bfa"]},
        "legend_color": "#a78bfa",
        "description": "Alte diferente observate Dynamic World.",
        "category": "Cresterea apei - Dynamic World",
    },
    "sar_dynamic_world_new_water_overlap": {
        "display_name": "SAR x Dynamic World new water overlap",
        "vis_params": {"palette": ["16a34a"]},
        "legend_color": "#16a34a",
        "description": "Apa noua observata atat prin SAR, cat si prin Dynamic World.",
        "category": "Corelare SAR x Dynamic World",
    },
    "new_water_only_sar": {
        "display_name": "New water only SAR",
        "vis_params": {"palette": ["67e8f9"]},
        "legend_color": "#67e8f9",
        "description": "Apa noua observata prin SAR fara corespondent Dynamic World.",
        "category": "Corelare SAR x Dynamic World",
    },
    "new_water_only_dynamic_world": {
        "display_name": "New water only Dynamic World",
        "vis_params": {"palette": ["9333ea"]},
        "legend_color": "#9333ea",
        "description": "Apa noua Dynamic World fara corespondent SAR.",
        "category": "Corelare SAR x Dynamic World",
    },
}


def layer_style(layer_id: str) -> dict[str, Any]:
    return LAYER_STYLES.get(layer_id, {})


def vis_params_by_display_name() -> dict[str, dict[str, Any]]:
    return {
        str(style["display_name"]): dict(style.get("vis_params") or {})
        for style in LAYER_STYLES.values()
        if style.get("display_name")
    }
