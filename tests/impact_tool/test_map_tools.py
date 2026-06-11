from __future__ import annotations

from src.impact_tool.map.builder import build_shell_map
from src.impact_tool.map.layers import add_osm_layers
from src.impact_tool.models import ImpactToolState
from src.impact_tool.osm_impact import visible_impact_layers
from src.impact_tool.ui.shell import _analysis_layers
import folium


def test_map_contains_identify_measure_navigation_and_fullscreen() -> None:
    html = build_shell_map(None, "Galati").get_root().render()
    assert "LatLngPopup" in html or "latlng" in html.lower()
    assert "L.Control.Measure" in html
    assert "fullscreen" in html.lower()


def test_layer_control_contains_only_two_basemaps() -> None:
    html = build_shell_map(
        None,
        "Galati",
        analysis_layers=[
            {
                "id": "sar_new_water",
                "name": "Apa noua SAR",
                "tile_url": "https://tiles.test/{z}/{x}/{y}",
                "shown": True,
            }
        ],
    ).get_root().render()
    assert html.count("L.control.layers(") == 1
    assert "OSM Light / CartoDB Positron" in html
    assert "Satelit / Esri World Imagery" in html
    control_config = html.split("L.control.layers(", 1)[1].split(");", 1)[0]
    assert "Apa noua SAR" not in control_config


def test_navigation_control_can_center_aoi() -> None:
    counties = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {"NAME_LATN": "Galati"},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [[27, 45], [28, 45], [28, 46], [27, 46], [27, 45]]
                    ],
                },
            }
        ],
    }
    aoi = {
        "type": "Polygon",
        "coordinates": [
            [[27.2, 45.2], [27.4, 45.2], [27.4, 45.4], [27.2, 45.4], [27.2, 45.2]]
        ],
    }
    html = build_shell_map(counties, "Galati", aoi_geometry=aoi).get_root().render()
    assert "Centrează pe AOI" in html


def test_critical_mode_filters_secondary_layers() -> None:
    impact = {
        "layers": {
            key: {"type": "FeatureCollection", "features": []}
            for key in (
                "osm_buildings",
                "osm_roads",
                "osm_railways",
                "osm_bridges",
                "osm_critical",
            )
        }
    }
    visible = visible_impact_layers(
        impact,
        {key: True for key in ("buildings", "roads", "railways", "bridges", "critical")},
        critical_only=True,
    )
    assert set(visible) == {"osm_roads", "osm_bridges", "osm_critical"}


def test_osm_filters_can_disable_category() -> None:
    impact = {
        "layers": {
            "osm_roads": {"type": "FeatureCollection", "features": []},
            "osm_critical": {"type": "FeatureCollection", "features": []},
        }
    }
    visible = visible_impact_layers(
        impact,
        {"roads": False, "critical": True},
        critical_only=False,
    )
    assert set(visible) == {"osm_critical"}


def test_empty_osm_layer_does_not_build_invalid_tooltip() -> None:
    folium_map = folium.Map(location=[45.5, 27.5])
    add_osm_layers(
        folium_map,
        {
            "osm_roads": {
                "type": "FeatureCollection",
                "display_name": "Drumuri",
                "features": [],
            }
        },
    )
    assert "Drumuri" not in folium_map.get_root().render()


def test_osm_tooltip_uses_only_fields_available_on_all_features() -> None:
    folium_map = folium.Map(location=[45.5, 27.5])
    add_osm_layers(
        folium_map,
        {
            "osm_roads": {
                "type": "FeatureCollection",
                "display_name": "Drumuri",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[27.4, 45.4], [27.5, 45.5]],
                        },
                        "properties": {"status": "Intersectat direct"},
                    },
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[27.5, 45.5], [27.6, 45.6]],
                        },
                        "properties": {
                            "name": "DN test",
                            "status": "În buffer de avertizare",
                        },
                    },
                ],
            }
        },
    )
    html = folium_map.get_root().render()
    assert "Status" in html
    assert "Distanță până la apă" not in html


def test_only_selected_analysis_layers_are_sent_to_map() -> None:
    state = ImpactToolState(
        active_layers=["sar_new_water"],
        analysis_results={
            "sar": {
                "tiles": {
                    "sar_water_before": "https://tiles/before",
                    "sar_water_after": "https://tiles/after",
                    "sar_new_water": "https://tiles/new-water",
                }
            }
        },
    )
    layers = _analysis_layers(state)
    assert [layer["id"] for layer in layers] == ["sar_new_water"]


def test_no_analysis_tiles_are_sent_when_all_layers_are_disabled() -> None:
    state = ImpactToolState(
        active_layers=[],
        analysis_results={
            "sar": {
                "tiles": {
                    "sar_water_before": "https://tiles/before",
                    "sar_water_after": "https://tiles/after",
                    "sar_new_water": "https://tiles/new-water",
                }
            },
            "dynamic_world": {
                "tiles": {
                    "dynamic_world_before": "https://tiles/dw-before",
                }
            },
        },
    )
    assert _analysis_layers(state) == []


def test_critical_asset_has_one_clustered_svg_marker() -> None:
    folium_map = folium.Map(location=[45.5, 27.5])
    add_osm_layers(
        folium_map,
        {
            "osm_critical": {
                "type": "FeatureCollection",
                "display_name": "Obiective",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [27.5, 45.5]},
                        "properties": {
                            "name": "Spital",
                            "amenity": "hospital",
                            "status": "Intersectat direct",
                        },
                    }
                ],
            }
        },
    )
    html = folium_map.get_root().render()
    assert html.count("L.marker(") == 1
    assert "markerClusterGroup" in html
    assert "svg xmlns=" in html


def test_bridge_has_line_and_centroid_icon() -> None:
    folium_map = folium.Map(location=[45.5, 27.5])
    add_osm_layers(
        folium_map,
        {
            "osm_bridges": {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": {
                            "type": "LineString",
                            "coordinates": [[27.4, 45.4], [27.6, 45.6]],
                        },
                        "properties": {"status": "În buffer de avertizare"},
                    }
                ],
            }
        },
    )
    html = folium_map.get_root().render()
    assert "LineString" in html
    assert html.count("L.marker(") == 1
    assert "pod" in html


def test_reference_filter_and_presentation_mode() -> None:
    from src.impact_tool.ui.shell import _visible_osm_layers

    state = ImpactToolState(
        active_layers=["osm_buildings", "osm_critical"],
        presentation_mode=True,
        osm_filters={
            "buildings": True,
            "critical": True,
            "reference_buildings": False,
        },
        analysis_results={
            "osm_impact": {
                "layers": {
                    "osm_buildings": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "properties": {
                                    "status": "Referință",
                                    "infrastructure_level": "context tehnic",
                                }
                            }
                        ],
                    },
                    "osm_critical": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "properties": {
                                    "status": "Intersectat direct",
                                    "infrastructure_level": "esențial",
                                }
                            }
                        ],
                    },
                }
            }
        },
    )
    visible = _visible_osm_layers(state)
    assert visible["osm_buildings"]["features"] == []
    assert len(visible["osm_critical"]["features"]) == 1


def test_osm_ui_contains_zoom_completeness_and_hidden_qa() -> None:
    from pathlib import Path

    source = Path("src/impact_tool/ui/results.py").read_text(encoding="utf-8")
    assert "Mod prezentare" in source
    assert "Clădiri de referință" in source
    assert 'button("Zoom"' in source
    assert "completitudine" in source
    assert 'expander("Mod QA", expanded=False)' in source
