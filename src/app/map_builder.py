from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import folium
from branca.element import MacroElement
from jinja2 import Template

from src.app.county_boundaries import bbox_center, county_display_name, zoom_for_bbox
from src.app.layer_registry import LayerEntry, LayerRegistry
from src.app.leaflet_compare_control import DynamicCompareControl
from src.gee.gee_tile_layers import ee_tile_url


ROMANIA_CENTER = [45.9432, 24.9668]
ROMANIA_ZOOM = 6


@dataclass
class MapBundle:
    main_map: folium.Map
    registry: LayerRegistry | None = None
    fallback_reason: str | None = None


def _base_map(center: list[float] | None = None, zoom: int | None = None) -> folium.Map:
    return folium.Map(
        location=center or ROMANIA_CENTER,
        zoom_start=zoom or ROMANIA_ZOOM,
        tiles="OpenStreetMap",
        control_scale=True,
    )


def add_counties_layer(
    folium_map: folium.Map,
    counties_geojson: dict[str, Any] | None,
    selected_county: str,
) -> None:
    if not counties_geojson:
        return

    def style_function(feature: dict[str, Any]) -> dict[str, Any]:
        is_selected = county_display_name(feature) == selected_county
        return {
            "color": "#dc2626" if is_selected else "#334155",
            "weight": 3 if is_selected else 1,
            "fillColor": "#ffffff" if is_selected else "#38bdf8",
            "fillOpacity": 0 if is_selected else 0.13,
        }

    def highlight_function(_: dict[str, Any]) -> dict[str, Any]:
        return {"weight": 3, "color": "#0f172a", "fillOpacity": 0.18}

    folium.GeoJson(
        counties_geojson,
        name="Administrativ - toate judetele",
        style_function=style_function,
        highlight_function=highlight_function,
        tooltip=folium.GeoJsonTooltip(fields=["NAME_LATN"], aliases=["Judet"], localize=True, sticky=True),
        popup=folium.GeoJsonPopup(fields=["NAME_LATN"], aliases=["Judet"]),
        show=True,
    ).add_to(folium_map)


def add_selected_county_layer(
    folium_map: folium.Map,
    selected_feature: dict[str, Any] | None,
) -> None:
    if not selected_feature:
        return
    folium.GeoJson(
        selected_feature,
        name="Administrativ - judet selectat",
        style_function=lambda _: {
            "color": "#b91c1c",
            "weight": 4,
            "fillColor": "#ffffff",
            "fillOpacity": 0,
        },
        tooltip=folium.GeoJsonTooltip(fields=["NAME_LATN"], aliases=["Judet"]),
        popup=folium.GeoJsonPopup(fields=["NAME_LATN"], aliases=["Judet selectat"]),
        show=True,
    ).add_to(folium_map)


def build_county_overview_map(
    counties_geojson: dict[str, Any] | None,
    selected_county: str,
    selected_bbox: list[float] | None = None,
    selected_feature: dict[str, Any] | None = None,
    zoom_to_selected: bool = False,
) -> MapBundle:
    center = bbox_center(selected_bbox) if selected_bbox and zoom_to_selected else ROMANIA_CENTER
    zoom = zoom_for_bbox(selected_bbox) if selected_bbox and zoom_to_selected else ROMANIA_ZOOM
    folium_map = _base_map(center, zoom)
    add_counties_layer(folium_map, counties_geojson, selected_county)
    add_selected_county_layer(folium_map, selected_feature)
    if selected_bbox and zoom_to_selected:
        folium_map.fit_bounds([[selected_bbox[1], selected_bbox[0]], [selected_bbox[3], selected_bbox[2]]])
    add_map_legend(folium_map, params=None, has_analysis_layers=False)
    folium.LayerControl(collapsed=False).add_to(folium_map)
    return MapBundle(main_map=folium_map)


def build_sar_preview_map(
    tile_url: str,
    scene: dict[str, Any],
    params: Any,
    counties_geojson: dict[str, Any] | None = None,
    selected_feature: dict[str, Any] | None = None,
) -> MapBundle:
    center = bbox_center(params.bbox)
    zoom = zoom_for_bbox(params.bbox)
    folium_map = _base_map(center, zoom)
    add_counties_layer(folium_map, counties_geojson, params.county_name)
    add_selected_county_layer(folium_map, selected_feature)
    folium.TileLayer(
        tiles=tile_url,
        attr="Google Earth Engine",
        name=f"Preview SAR - {scene.get('display_id', 'scena curenta')}",
        overlay=True,
        control=True,
        show=True,
    ).add_to(folium_map)
    folium_map.fit_bounds([[params.bbox[1], params.bbox[0]], [params.bbox[3], params.bbox[2]]])
    add_preview_legend(folium_map, scene)
    folium.LayerControl(collapsed=False).add_to(folium_map)
    return MapBundle(main_map=folium_map)


def add_preview_legend(folium_map: folium.Map, scene: dict[str, Any]) -> None:
    _PreviewLegend(scene).add_to(folium_map)


class _PreviewLegend(MacroElement):
    _template = Template(
        """
        {% macro html(this, kwargs) %}
        <div class="map-data-legend">
          <div class="legend-title">Preview Sentinel-1 SAR</div>
          <div><strong>{{ this.display_id }}</strong></div>
          <div>Sursa: COPERNICUS/S1_GRD</div>
          <div>Data UTC: {{ this.acquisition_time }}</div>
          <div>Tip: PREVIEW</div>
          <div>Simbolizare: tonuri gri SAR</div>
        </div>
        <style>
          .map-data-legend {
            position: fixed;
            left: 18px;
            bottom: 24px;
            z-index: 9999;
            max-width: 330px;
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(15, 23, 42, 0.18);
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.18);
            color: #0f172a;
            font: 12px/1.35 Arial, sans-serif;
            padding: 10px 12px;
          }
          .legend-title {
            font-weight: 700;
            margin-bottom: 6px;
          }
        </style>
        {% endmacro %}
        """
    )

    def __init__(self, scene: dict[str, Any]) -> None:
        super().__init__()
        self._name = "PreviewLegend"
        self.display_id = scene.get("display_id", "scena")
        self.acquisition_time = scene.get("acquisition_time", "necunoscut")


def build_maps(
    layer_images: dict[str, dict[str, Any]],
    params: Any,
    counties_geojson: dict[str, Any] | None = None,
    selected_feature: dict[str, Any] | None = None,
    registry: LayerRegistry | None = None,
) -> MapBundle:
    registry = registry or LayerRegistry()
    center = bbox_center(params.bbox)
    zoom = zoom_for_bbox(params.bbox)
    main_map = _base_map(center, zoom)
    add_counties_layer(main_map, counties_geojson, params.county_name)
    add_selected_county_layer(main_map, selected_feature)
    main_map.fit_bounds([[params.bbox[1], params.bbox[0]], [params.bbox[3], params.bbox[2]]])

    for layer_id, meta in layer_images.items():
        display_name = meta["display_name"]
        tile_url = ee_tile_url(meta["image"], display_name)
        if not tile_url:
            registry.unavailable(
                layer_id=layer_id,
                display_name=display_name,
                category=meta["category"],
                layer_type=meta["layer_type"],
                warning=f"Nu s-a putut genera tile URL pentru {display_name}.",
                metadata=meta.get("metadata"),
            )
            continue
        layer = folium.TileLayer(
            tiles=tile_url,
            attr="Google Earth Engine",
            name=f"{meta['category']} - {display_name}",
            overlay=True,
            control=True,
            show=meta.get("shown", False),
        )
        layer.add_to(main_map)
        registry.add(
            LayerEntry(
                id=layer_id,
                display_name=display_name,
                category=meta["category"],
                layer_type=meta["layer_type"],
                available=True,
                comparable=meta.get("comparable", True),
                shown=meta.get("shown", False),
                tile_url=tile_url,
                folium_layer=layer,
                metadata=meta.get("metadata"),
            )
        )

    DynamicCompareControl(registry, auto_start=True).add_to(main_map)
    add_map_legend(main_map, params=params, has_analysis_layers=True, layer_payload=registry.report_payload())
    folium.LayerControl(collapsed=False).add_to(main_map)
    return MapBundle(main_map=main_map, registry=registry)


def add_map_legend(
    folium_map: folium.Map,
    params: Any | None,
    has_analysis_layers: bool,
    layer_payload: dict[str, Any] | None = None,
) -> None:
    _MapLegend(params=params, has_analysis_layers=has_analysis_layers, layer_payload=layer_payload).add_to(folium_map)


class _MapLegend(MacroElement):
    _template = Template(
        """
        {% macro html(this, kwargs) %}
        <div class="map-data-legend">
          <div class="legend-title">Legenda dinamica</div>
          <div class="legend-row"><span class="legend-line county"></span><span>Judet selectat: contur AOI</span></div>
          <div class="legend-row"><span class="legend-swatch counties"></span><span>Judete Romania NUTS 2024</span></div>
          {% if this.has_analysis_layers %}
          {{ this.layer_details }}
          {% endif %}
          <div class="legend-dates">{{ this.date_text }}</div>
        </div>
        <style>
          .map-data-legend {
            position: fixed;
            left: 18px;
            bottom: 24px;
            z-index: 9999;
            max-width: 330px;
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(15, 23, 42, 0.18);
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.18);
            color: #0f172a;
            font: 12px/1.35 Arial, sans-serif;
            padding: 10px 12px;
          }
          .legend-title {
            font-weight: 700;
            margin-bottom: 6px;
          }
          .legend-row {
            align-items: center;
            display: flex;
            gap: 7px;
            margin: 4px 0;
          }
          .legend-swatch {
            border: 1px solid rgba(15, 23, 42, 0.25);
            display: inline-block;
            flex: 0 0 14px;
            height: 14px;
            width: 14px;
          }
          .legend-line {
            border-top: 3px solid #b91c1c;
            display: inline-block;
            flex: 0 0 22px;
            width: 22px;
          }
          .legend-swatch.counties { background: rgba(56, 189, 248, 0.35); }
          .legend-swatch.sar { background: linear-gradient(90deg, #111827, #cbd5e1); }
          .legend-swatch.flood { background: #ef4444; }
          .legend-swatch.water { background: #2563eb; }
          .legend-swatch.land { background: linear-gradient(90deg, #16a34a, #facc15, #a855f7); }
          .legend-swatch.dem { background: linear-gradient(90deg, #365314, #d9f99d); }
          .legend-dates {
            border-top: 1px solid rgba(15, 23, 42, 0.12);
            margin-top: 7px;
            padding-top: 7px;
            white-space: pre-line;
          }
          .legend-detail {
            border-top: 1px solid rgba(15, 23, 42, 0.08);
            margin-top: 5px;
            padding-top: 5px;
          }
          .legend-detail summary {
            cursor: pointer;
            font-weight: 700;
          }
          .legend-detail ul {
            margin: 5px 0 0 18px;
            padding: 0;
          }
          .legend-detail li {
            margin: 6px 0;
          }
        </style>
        {% endmacro %}
        """
    )

    def __init__(self, params: Any | None, has_analysis_layers: bool, layer_payload: dict[str, Any] | None = None) -> None:
        super().__init__()
        self._name = "MapLegend"
        self.has_analysis_layers = has_analysis_layers
        self.date_text = _legend_date_text(params, has_analysis_layers)
        self.layer_details = _legend_layer_details(layer_payload)


def _legend_date_text(params: Any | None, has_analysis_layers: bool) -> str:
    if not params or not has_analysis_layers:
        return "Limite administrative: Eurostat GISCO NUTS 2024."
    return (
        "Deschide fiecare categorie pentru zilele scenelor folosite.\n"
        "Daca apar mai multe zile, layerul este compozit median din acele scene."
    )


def _legend_layer_details(layer_payload: dict[str, Any] | None) -> str:
    if not layer_payload:
        return ""
    grouped: dict[str, list[dict[str, Any]]] = {}
    for layer in layer_payload.get("available", []):
        grouped.setdefault(layer.get("category") or "Alte date", []).append(layer)
    for layer in layer_payload.get("unavailable", []):
        grouped.setdefault(layer.get("category") or "Alte date", []).append(layer)

    parts: list[str] = []
    for category, layers in grouped.items():
        rows = []
        for layer in layers:
            metadata = layer.get("metadata") or {}
            dates = metadata.get("dates") or metadata.get("date") or "data exacta indisponibila"
            if isinstance(dates, list):
                dates_text = ", ".join(str(item) for item in dates) if dates else "data exacta indisponibila"
            else:
                dates_text = str(dates)
            source = metadata.get("source") or "sursa nespecificata"
            details = metadata.get("details") or layer.get("warning") or ""
            status = "disponibil" if layer.get("available", True) else "indisponibil"
            rows.append(
                "<li>"
                f"<strong>{layer.get('display_name')}</strong> ({status})<br>"
                f"Sursa: {source}<br>"
                f"Zi/scene: {dates_text}"
                f"{'<br>' + details if details else ''}"
                "</li>"
            )
        parts.append(
            "<details class=\"legend-detail\">"
            f"<summary>{category}</summary>"
            f"<ul>{''.join(rows)}</ul>"
            "</details>"
        )
    return "".join(parts)


def build_result_map_from_registry_payload(
    layer_payload: dict[str, list[dict[str, Any]]],
    params: Any,
    counties_geojson: dict[str, Any] | None = None,
    selected_feature: dict[str, Any] | None = None,
) -> MapBundle:
    registry = LayerRegistry()
    center = bbox_center(params.bbox)
    zoom = zoom_for_bbox(params.bbox)
    main_map = _base_map(center, zoom)
    add_counties_layer(main_map, counties_geojson, params.county_name)
    add_selected_county_layer(main_map, selected_feature)
    main_map.fit_bounds([[params.bbox[1], params.bbox[0]], [params.bbox[3], params.bbox[2]]])

    for layer_meta in layer_payload.get("available", []):
        tile_url = layer_meta.get("tile_url")
        if not tile_url:
            continue
        layer = folium.TileLayer(
            tiles=tile_url,
            attr="Google Earth Engine",
            name=f"{layer_meta.get('category')} - {layer_meta.get('display_name')}",
            overlay=True,
            control=True,
            show=bool(layer_meta.get("shown")),
        )
        layer.add_to(main_map)
        registry.add(
            LayerEntry(
                id=layer_meta["id"],
                display_name=layer_meta["display_name"],
                category=layer_meta["category"],
                layer_type=layer_meta["layer_type"],
                available=True,
                comparable=bool(layer_meta.get("comparable", True)),
                shown=bool(layer_meta.get("shown")),
                tile_url=tile_url,
                folium_layer=layer,
                metadata=layer_meta.get("metadata"),
            )
        )

    for layer_meta in layer_payload.get("unavailable", []):
        registry.unavailable(
            layer_id=layer_meta["id"],
            display_name=layer_meta["display_name"],
            category=layer_meta["category"],
            layer_type=layer_meta["layer_type"],
            warning=layer_meta.get("warning") or "Layer indisponibil.",
            comparable=bool(layer_meta.get("comparable", False)),
            metadata=layer_meta.get("metadata"),
        )

    DynamicCompareControl(registry, auto_start=True).add_to(main_map)
    add_map_legend(main_map, params=params, has_analysis_layers=True, layer_payload=registry.report_payload())
    folium.LayerControl(collapsed=False).add_to(main_map)
    return MapBundle(main_map=main_map, registry=registry)
