from types import SimpleNamespace

from src.app.layer_registry import LayerRegistry
from src.app.map_builder import _osm_exposure_color, build_maps


class _FakeEeImage:
    def getMapId(self, vis_params):
        return {"tile_fetcher": SimpleNamespace(url_format="https://tiles.example/{z}/{x}/{y}")}


def test_build_maps_adds_osm_vector_layers_to_registry():
    registry = LayerRegistry()
    params = SimpleNamespace(bbox=[27.0, 45.0, 28.0, 46.0], county_name="Galati")
    osm_layers = {
        "osm_roads": {
            "type": "FeatureCollection",
            "display_name": "Drumuri potential afectate OSM",
            "color": "#f97316",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {"type": "LineString", "coordinates": [[27.0, 45.0], [27.1, 45.1]]},
                    "properties": {
                        "exposure_label": "drum potential afectat",
                        "name": "test road",
                        "exposure_level": "medium",
                    },
                }
            ],
        }
    }

    bundle = build_maps(
        {"sar_new_water": {"display_name": "SAR new water", "category": "Apa observata prin SAR", "layer_type": "result", "image": _FakeEeImage()}},
        params,
        registry=registry,
        osm_layers=osm_layers,
    )
    payload = bundle.registry.report_payload()

    osm = [layer for layer in payload["available"] if layer["id"] == "osm_roads"][0]
    assert osm["category"] == "Impact operational OSM"
    assert osm["comparable"] is False


def test_osm_exposure_color_uses_level_before_fallback():
    assert _osm_exposure_color({"properties": {"exposure_level": "high"}}, "#0ea5e9") == "#dc2626"
    assert _osm_exposure_color({"properties": {"exposure_level": "medium"}}, "#0ea5e9") == "#f97316"
    assert _osm_exposure_color({"properties": {}}, "#0ea5e9") == "#0ea5e9"
