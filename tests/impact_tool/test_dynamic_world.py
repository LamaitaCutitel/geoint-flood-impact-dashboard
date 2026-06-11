from __future__ import annotations

from src.impact_tool.dynamic_world import (
    TRANSITION_CLASSES,
    dynamic_world_layer_definitions,
    scene_day_period,
)


def test_scene_period_uses_exact_acquisition_day() -> None:
    period = scene_day_period({"acquisition_time": "2024-09-14T16:27:00+00:00"})
    assert period == ("2024-09-14", "2024-09-15")


def test_all_relevant_transitions_are_declared() -> None:
    assert set(TRANSITION_CLASSES.values()) == {
        "crops",
        "grass",
        "built",
        "trees",
        "flooded vegetation",
        "shrub and scrub",
        "bare",
    }


def test_dynamic_world_and_correlation_layers() -> None:
    layers = dynamic_world_layer_definitions({"tiles": {}})
    names = {layer["name"] for layer in layers}
    assert "Dynamic World BEFORE" in names
    assert "Dynamic World AFTER" in names
    assert "Apă nouă prin ambele metode" in names
    assert "Apă nouă doar SAR" in names
    assert "Apă nouă doar Dynamic World" in names
