from __future__ import annotations

from src.impact_tool.sar import SarParameters, run_sar_analysis, sar_layer_definitions


class FakeImage:
    def __init__(self, expression: str):
        self.expression = expression

    def select(self, value):
        return FakeImage(f"select({self.expression},{value})")

    def clip(self, aoi):
        return FakeImage(f"clip({self.expression},{aoi})")

    def lt(self, value):
        return FakeImage(f"lt({self.expression},{value})")

    def selfMask(self):
        return FakeImage(f"mask({self.expression})")

    def connectedPixelCount(self, size, connected):
        return FakeImage(f"connected({self.expression})")

    def gte(self, value):
        return FakeImage(f"gte({self.expression},{value})")

    def updateMask(self, value):
        return FakeImage(f"update({self.expression})")

    def unmask(self, value):
        return FakeImage(f"unmask({self.expression})")

    def And(self, other):
        return FakeImage(f"and({self.expression},{other.expression})")

    def Not(self):
        return FakeImage(f"not({self.expression})")

    def getMapId(self, params):
        class Fetcher:
            url_format = "https://tiles/{z}/{x}/{y}"
        return {"tile_fetcher": Fetcher()}


class FakeEE:
    def Image(self, scene_id):
        return FakeImage(scene_id)


def _scene(scene_id, timestamp):
    return {
        "ee_id": scene_id,
        "polarization": "VH",
        "acquisition_time": timestamp,
    }


def test_strict_sar_analysis_builds_only_required_products(monkeypatch) -> None:
    monkeypatch.setattr(
        "src.impact_tool.sar.sar_water_area_metrics",
        lambda ee, masks, aoi, scale: {f"{key}_area_km2": 1.0 for key in masks},
    )
    result = run_sar_analysis(
        FakeEE(),
        "county",
        _scene("before", "2024-01-01"),
        _scene("after", "2024-01-13"),
        SarParameters(minimum_connected_pixels=0),
    )
    assert set(result["metrics"]) == {
        "sar_water_before_area_km2",
        "sar_water_after_area_km2",
        "sar_new_water_area_km2",
    }
    assert result["products"]["sar_new_water"].expression.endswith(",county)")
    assert set(result["tiles"]) == {"sar_water_before", "sar_water_after", "sar_new_water"}


def test_sar_layers_have_no_technical_products() -> None:
    layers = sar_layer_definitions({"tiles": {}})
    names = {layer["name"] for layer in layers}
    assert names == {
        "Apă observată BEFORE",
        "Apă observată AFTER",
        "Apă nouă evidențiată prin SAR",
    }
    assert all("ratio" not in name.lower() and "difference" not in name.lower() for name in names)
