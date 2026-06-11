from __future__ import annotations

from typing import Any
from html import escape

import folium

from src.app.county_boundaries import county_display_name


def add_county_outlines(
    folium_map: folium.Map,
    counties_geojson: dict[str, Any] | None,
    selected_county: str,
) -> None:
    if not counties_geojson:
        return

    def style(feature: dict[str, Any]) -> dict[str, Any]:
        selected = county_display_name(feature) == selected_county
        return {
            "color": "#2563eb" if selected else "#64748b",
            "weight": 3 if selected else 1,
            "fillOpacity": 0,
        }

    folium.GeoJson(
        counties_geojson,
        name="Limite județe",
        style_function=style,
        tooltip=folium.GeoJsonTooltip(fields=["NAME_LATN"], aliases=["Județ"]),
        show=True,
    ).add_to(folium_map)


def add_aoi_layer(
    folium_map: folium.Map,
    aoi_geometry: dict[str, Any] | None,
) -> None:
    if not aoi_geometry:
        return
    folium.GeoJson(
        {
            "type": "Feature",
            "properties": {"name": "Zonă focală"},
            "geometry": aoi_geometry,
        },
        name="Zonă focală desenată",
        style_function=lambda _: {
            "color": "#16a34a",
            "weight": 3,
            "fillColor": "#22c55e",
            "fillOpacity": 0.08,
        },
        tooltip="Zonă focală activă",
        show=True,
    ).add_to(folium_map)


def add_tile_layers(folium_map: folium.Map, layers: list[dict[str, Any]]) -> None:
    for layer in layers:
        tile_url = layer.get("tile_url")
        if not tile_url:
            continue
        folium.TileLayer(
            tiles=tile_url,
            attr="Google Earth Engine",
            name=layer["name"],
            overlay=True,
            control=True,
            show=bool(layer.get("shown")),
        ).add_to(folium_map)


def add_buffer_layer(folium_map: folium.Map, geometry: dict[str, Any] | None) -> None:
    if not geometry:
        return
    folium.GeoJson(
        {"type": "Feature", "properties": {}, "geometry": geometry},
        name="Buffer de avertizare",
        style_function=lambda _: {
            "color": "#f59e0b",
            "weight": 2,
            "fillColor": "#facc15",
            "fillOpacity": 0.12,
        },
        show=True,
    ).add_to(folium_map)


def add_osm_layers(
    folium_map: folium.Map,
    layers: dict[str, dict[str, Any]],
) -> None:
    styles = {
        "osm_buildings": {"color": "#dc2626", "weight": 1, "fillOpacity": 0.35},
        "osm_roads": {"color": "#f97316", "weight": 4},
        "osm_railways": {"color": "#7c3aed", "weight": 3},
        "osm_bridges": {"color": "#0ea5e9", "weight": 4},
        "osm_critical": {"color": "#dc2626", "weight": 2},
    }
    for layer_id, collection in layers.items():
        features = collection.get("features", [])
        if not features:
            continue
        folium.GeoJson(
            collection,
            name=collection.get("display_name", layer_id),
            style_function=lambda feature, layer_style=styles.get(layer_id, {}): {
                **layer_style,
                "opacity": 1
                if feature.get("properties", {}).get("status") == "Intersectat direct"
                else 0.75,
            },
            tooltip=_osm_tooltip(features),
            show=True,
        ).add_to(folium_map)
        if layer_id == "osm_critical":
            for feature in collection.get("features", []):
                if feature.get("geometry", {}).get("type") != "Point":
                    continue
                longitude, latitude = feature["geometry"]["coordinates"]
                properties = feature.get("properties", {})
                symbol = escape(str(properties.get("symbol", "●")))
                name = escape(str(properties.get("name") or "Obiectiv critic"))
                status = escape(str(properties.get("status") or "Necunoscut"))
                distance = escape(str(properties.get("distance_to_water_m", "indisponibil")))
                folium.Marker(
                    [latitude, longitude],
                    icon=folium.DivIcon(
                        html=(
                            '<div style="width:26px;height:26px;border-radius:50%;'
                            'background:#fff;border:2px solid #dc2626;color:#991b1b;'
                            'display:flex;align-items:center;justify-content:center;'
                            f'font-weight:700">{symbol}</div>'
                        )
                    ),
                    tooltip=f"{name} · {status}",
                    popup=folium.Popup(
                        f"<strong>{name}</strong><br>Status: {status}<br>"
                        f"Distanță până la apă: {distance} m<br>"
                        "Sursă: OpenStreetMap",
                        max_width=320,
                    ),
                ).add_to(folium_map)


def _osm_tooltip(features: list[dict[str, Any]]) -> folium.GeoJsonTooltip | None:
    property_sets = [
        set((feature.get("properties") or {}).keys())
        for feature in features
    ]
    if not property_sets:
        return None
    available = set.intersection(*property_sets)
    candidates = (
        ("name", "Nume"),
        ("status", "Status"),
        ("distance_to_water_m", "Distanță până la apă (m)"),
    )
    fields = [field for field, _ in candidates if field in available]
    if not fields:
        return None
    aliases = [alias for field, alias in candidates if field in available]
    return folium.GeoJsonTooltip(fields=fields, aliases=aliases, localize=True)
