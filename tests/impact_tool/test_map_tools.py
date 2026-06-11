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
