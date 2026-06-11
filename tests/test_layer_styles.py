from src.app.layer_styles import LAYER_STYLES, layer_style, vis_params_by_display_name
from src.app.leaflet_compare_control import _sar_first


def test_layer_styles_expose_visual_metadata_for_sar_new_water():
    style = layer_style("sar_new_water")

    assert style["display_name"] == "Apa noua evidentiata prin SAR"
    assert style["legend_color"] == "#22d3ee"
    assert style["vis_params"]["palette"] == ["22d3ee"]
    assert style["category"] == "Analiza apei prin SAR"
    assert style["source"] == "COPERNICUS/S1_GRD"
    assert style["legend_items"]


def test_vis_params_are_derived_from_layer_styles():
    vis_params = vis_params_by_display_name()

    assert vis_params["Suprapunere SAR x Dynamic World"] == (
        LAYER_STYLES["sar_dynamic_world_new_water_overlap"]["vis_params"]
    )


def test_all_layer_styles_have_required_metadata():
    required = {
        "display_name",
        "category",
        "vis_params",
        "legend_items",
        "description",
        "source",
        "date_or_period",
        "layer_type",
    }

    for layer_id in [
        "sar_new_water",
        "dynamic_world_before",
        "dynamic_world_changes",
        "osm_buildings",
        "osm_roads",
        "osm_critical",
        "rgb_before",
        "dem",
    ]:
        assert required <= set(layer_style(layer_id)), layer_id


def test_dynamic_world_palette_matches_expected_classes():
    items = dict(layer_style("dynamic_world_before")["legend_items"])

    assert items["#419bdf"] == "apa"
    assert items["#397d49"] == "arbori"
    assert items["#c4281b"] == "construit"


def test_compare_control_prioritizes_sar_water_layers():
    layers = [
        {"id": "sar_before", "display_name": "Sentinel-1 SAR before", "tile_url": "a"},
        {"id": "sar_after", "display_name": "Sentinel-1 SAR after", "tile_url": "b"},
        {"id": "sar_water_after", "display_name": "SAR water AFTER", "tile_url": "c"},
        {"id": "sar_water_before", "display_name": "SAR water BEFORE", "tile_url": "d"},
    ]

    ordered = _sar_first(layers)

    assert ordered[0]["id"] == "sar_water_before"
    assert ordered[1]["id"] == "sar_water_after"
