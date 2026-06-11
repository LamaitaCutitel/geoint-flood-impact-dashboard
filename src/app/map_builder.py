from __future__ import annotations

from dataclasses import dataclass
import html
import json
from typing import Any

import folium
from branca.element import MacroElement
from folium.plugins import Fullscreen, MeasureControl, SideBySideLayers
from jinja2 import Template

from src.app.county_boundaries import bbox_center, county_display_name, zoom_for_bbox
from src.app.layer_registry import LayerEntry, LayerRegistry
from src.app.layer_styles import layer_style
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
    folium_map = folium.Map(
        location=center or ROMANIA_CENTER,
        zoom_start=zoom or ROMANIA_ZOOM,
        tiles="OpenStreetMap",
        control_scale=True,
    )
    Fullscreen(position="topleft").add_to(folium_map)
    MeasureControl(position="topleft", primary_length_unit="kilometers").add_to(folium_map)
    return folium_map


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
            "fillOpacity": 0,
        }

    def highlight_function(_: dict[str, Any]) -> dict[str, Any]:
        return {"weight": 3, "color": "#0f172a", "fillOpacity": 0.08}

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


def build_sar_candidate_compare_map(
    before_tile_url: str,
    after_tile_url: str,
    before_scene: dict[str, Any],
    after_scene: dict[str, Any],
    params: Any,
    counties_geojson: dict[str, Any] | None = None,
    selected_feature: dict[str, Any] | None = None,
) -> MapBundle:
    center = bbox_center(params.bbox)
    zoom = zoom_for_bbox(params.bbox)
    folium_map = _base_map(center, zoom)
    add_counties_layer(folium_map, counties_geojson, params.county_name)
    add_selected_county_layer(folium_map, selected_feature)
    before_layer = folium.TileLayer(
        tiles=before_tile_url,
        attr="Google Earth Engine",
        name=f"Explorare SAR - candidat BEFORE {before_scene.get('display_id')}",
        overlay=True,
        control=True,
        show=True,
    )
    after_layer = folium.TileLayer(
        tiles=after_tile_url,
        attr="Google Earth Engine",
        name=f"Explorare SAR - candidat AFTER {after_scene.get('display_id')}",
        overlay=True,
        control=True,
        show=True,
    )
    before_layer.add_to(folium_map)
    after_layer.add_to(folium_map)
    SideBySideLayers(before_layer, after_layer).add_to(folium_map)
    folium_map.fit_bounds([[params.bbox[1], params.bbox[0]], [params.bbox[3], params.bbox[2]]])
    add_candidate_compare_legend(folium_map, before_scene, after_scene)
    folium.LayerControl(collapsed=False).add_to(folium_map)
    return MapBundle(main_map=folium_map)


def add_candidate_compare_legend(
    folium_map: folium.Map,
    before_scene: dict[str, Any],
    after_scene: dict[str, Any],
) -> None:
    _CandidateCompareLegend(before_scene, after_scene).add_to(folium_map)


class _CandidateCompareLegend(MacroElement):
    _template = Template(
        """
        {% macro html(this, kwargs) %}
        <div class="map-data-legend">
          <div class="legend-title">Comparatie candidate SAR</div>
          <div>Stanga: Sentinel-1 - {{ this.before_time }}</div>
          <div>Dreapta: Sentinel-1 - {{ this.after_time }}</div>
          <div>Nu ruleaza analiza finala.</div>
        </div>
        <style>
          .map-data-legend {
            position: fixed;
            left: 18px;
            bottom: 24px;
            z-index: 9999;
            max-height: 360px;
            max-width: 360px;
            overflow-y: auto;
            background: rgba(255, 255, 255, 0.94);
            border: 1px solid rgba(15, 23, 42, 0.18);
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.18);
            color: #0f172a;
            font: 12px/1.35 Arial, sans-serif;
            padding: 10px 12px;
          }
          .legend-title { font-weight: 700; margin-bottom: 6px; }
          .leaflet-sbs-divider {
            background: #f8fafc !important;
            box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.7), 0 0 10px rgba(15, 23, 42, 0.45) !important;
            width: 4px !important;
            z-index: 999 !important;
          }
          .leaflet-sbs-range {
            z-index: 1000 !important;
            pointer-events: auto !important;
            cursor: ew-resize !important;
          }
        </style>
        {% endmacro %}
        """
    )

    def __init__(self, before_scene: dict[str, Any], after_scene: dict[str, Any]) -> None:
        super().__init__()
        self._name = "CandidateCompareLegend"
        self.before_time = before_scene.get("acquisition_time", "necunoscut")
        self.after_time = after_scene.get("acquisition_time", "necunoscut")


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
            max-height: 360px;
            max-width: 330px;
            overflow-y: auto;
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
          .leaflet-control-layers {
            max-height: 430px;
            max-width: 360px;
            overflow-y: auto;
          }
          .leaflet-control-layers-overlays,
          .leaflet-control-layers-base {
            max-height: 320px;
            overflow-y: auto;
          }
          .leaflet-sbs-divider {
            background: #f8fafc !important;
            box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.7), 0 0 10px rgba(15, 23, 42, 0.45) !important;
            width: 4px !important;
            z-index: 999 !important;
          }
          .leaflet-sbs-range {
            z-index: 1000 !important;
            pointer-events: auto !important;
            cursor: ew-resize !important;
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
    osm_layers: dict[str, dict[str, Any]] | None = None,
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

    add_osm_operational_layers(main_map, registry, osm_layers)
    add_default_side_by_side(registry)
    DynamicCompareControl(registry, auto_start=False).add_to(main_map)
    add_map_legend(main_map, params=params, has_analysis_layers=True, layer_payload=registry.report_payload())
    folium.LayerControl(collapsed=False).add_to(main_map)
    GroupedLayerControlEnhancer().add_to(main_map)
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
          <details open>
            <summary class="legend-title">Legenda hartii</summary>
            <div class="legend-row"><span class="legend-line county"></span><span>Judet selectat: contur AOI</span></div>
            <div class="legend-row"><span class="legend-swatch counties"></span><span>Judete Romania NUTS 2024</span></div>
            {% if this.has_analysis_layers %}
            <div class="legend-section-title">Layere active implicit</div>
            {{ this.active_layer_details }}
            <details class="legend-detail">
              <summary>Detalii pentru toate layerele</summary>
              {{ this.layer_details }}
            </details>
            {% endif %}
            <div class="legend-dates">{{ this.date_text }}</div>
          </details>
        </div>
        <script>
        (function() {
          var legend = document.currentScript.previousElementSibling;
          var layers = {{ this.layers_json }};
          if (!legend || !layers.length) { return; }
          var activeBox = legend.querySelector('[data-active-layers]');
          function esc(value) {
            return String(value || '').replace(/[&<>"']/g, function(char) {
              return ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]);
            });
          }
          function render(items) {
            if (!activeBox) { return; }
            if (!items.length) {
              activeBox.innerHTML = '<div class="legend-card">Activeaza un layer pentru detalii contextuale.</div>';
              return;
            }
            activeBox.innerHTML = items.map(function(layer) {
              var itemsHtml = (layer.legend_items || []).map(function(item) {
                return '<div class="legend-row"><span class="legend-swatch" style="background:' + esc(item[0]) + '"></span><span>' + esc(item[1]) + '</span></div>';
              }).join('');
              return '<div class="legend-card"><strong>' + esc(layer.display_name) + '</strong>' +
                '<div>Tip: ' + esc(layer.layer_type || 'layer') + '</div>' +
                '<div>Sursa: ' + esc(layer.source || 'sursa nespecificata') + '</div>' +
                '<div>Data/perioada: ' + esc(layer.date_or_period || 'indisponibil') + '</div>' +
                itemsHtml + '</div>';
            }).join('');
          }
          function checkedLayerNames() {
            return Array.from(document.querySelectorAll('.leaflet-control-layers-overlays label'))
              .filter(function(label) {
                var input = label.querySelector('input[type="checkbox"]');
                return input && input.checked;
              })
              .map(function(label) { return (label.textContent || '').trim(); });
          }
          function refresh() {
            var names = checkedLayerNames();
            var items = layers.filter(function(layer) {
              return names.indexOf(layer.display_name) >= 0 || names.indexOf((layer.category || '') + ' - ' + layer.display_name) >= 0;
            });
            if (!items.length) {
              items = layers.filter(function(layer) { return layer.shown; });
            }
            render(items.slice(0, 4));
          }
          render(layers.filter(function(layer) { return layer.shown; }).slice(0, 4));
          setTimeout(refresh, 350);
          document.addEventListener('change', function(event) {
            if (event.target && event.target.closest && event.target.closest('.leaflet-control-layers')) {
              setTimeout(refresh, 50);
            }
          });
        })();
        </script>
        <style>
          .map-data-legend {
            position: fixed;
            left: 18px;
            bottom: 24px;
            z-index: 9999;
            max-height: 360px;
            max-width: 340px;
            overflow-y: auto;
            background: rgba(255, 255, 255, 0.95);
            border: 1px solid rgba(15, 23, 42, 0.18);
            border-radius: 6px;
            box-shadow: 0 2px 10px rgba(15, 23, 42, 0.18);
            color: #0f172a;
            font: 12px/1.35 Arial, sans-serif;
            padding: 10px 12px;
          }
          .legend-title { cursor: pointer; font-weight: 700; margin-bottom: 6px; }
          .legend-section-title { font-weight: 700; margin-top: 8px; }
          .legend-card {
            border-top: 1px solid rgba(15, 23, 42, 0.12);
            margin-top: 6px;
            padding-top: 6px;
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
          .legend-detail summary { cursor: pointer; font-weight: 700; }
          .legend-detail ul { margin: 5px 0 0 18px; padding: 0; }
          .legend-detail li { margin: 6px 0; }
          .leaflet-control-layers {
            max-height: 430px;
            max-width: 380px;
            overflow-y: auto;
          }
          .leaflet-control-layers-overlays,
          .leaflet-control-layers-base {
            max-height: 320px;
            overflow-y: auto;
          }
          .leaflet-layer-group-heading {
            background: #f1f5f9;
            border-top: 1px solid #cbd5e1;
            color: #0f172a;
            font-weight: 700;
            margin: 6px -4px 3px;
            padding: 4px 6px;
          }
          .leaflet-sbs-divider {
            background: #f8fafc !important;
            box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.7), 0 0 10px rgba(15, 23, 42, 0.45) !important;
            width: 4px !important;
            z-index: 999 !important;
          }
          .leaflet-sbs-range {
            z-index: 1000 !important;
            pointer-events: auto !important;
            cursor: ew-resize !important;
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
        self.active_layer_details = _active_legend_layer_details(layer_payload)
        self.layer_details = _legend_layer_details(layer_payload)
        self.layers_json = json.dumps(_legend_payload_for_js(layer_payload), ensure_ascii=False)


class GroupedLayerControlEnhancer(MacroElement):
    _template = Template(
        """
        {% macro script(this, kwargs) %}
        (function() {
          function enhance() {
            document.querySelectorAll('.leaflet-control-layers-overlays').forEach(function(container) {
              if (container.dataset.grouped === 'true') { return; }
              container.dataset.grouped = 'true';
              var labels = Array.from(container.querySelectorAll('label'));
              var currentGroup = null;
              labels.forEach(function(label) {
                var textNode = Array.from(label.childNodes).find(function(node) { return node.nodeType === 3; });
                var text = (label.textContent || '').trim();
                var parts = text.split(' - ');
                var group = parts.length > 1 ? parts[0] : 'Alte layere';
                var itemName = parts.length > 1 ? parts.slice(1).join(' - ') : text;
                if (group !== currentGroup) {
                  currentGroup = group;
                  var heading = document.createElement('div');
                  heading.className = 'leaflet-layer-group-heading';
                  heading.textContent = group;
                  container.insertBefore(heading, label);
                }
                if (textNode) { textNode.textContent = ' ' + itemName; }
              });
            });
          }
          setTimeout(enhance, 250);
        })();
        {% endmacro %}
        """
    )

    def __init__(self) -> None:
        super().__init__()
        self._name = "GroupedLayerControlEnhancer"


class _LegacyMapLegend(MacroElement):
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
            max-height: 360px;
            max-width: 330px;
            overflow-y: auto;
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
          .leaflet-control-layers {
            max-height: 430px;
            max-width: 360px;
            overflow-y: auto;
          }
          .leaflet-control-layers-overlays,
          .leaflet-control-layers-base {
            max-height: 320px;
            overflow-y: auto;
          }
          .leaflet-sbs-divider {
            background: #f8fafc !important;
            box-shadow: 0 0 0 2px rgba(15, 23, 42, 0.7), 0 0 10px rgba(15, 23, 42, 0.45) !important;
            width: 4px !important;
            z-index: 999 !important;
          }
          .leaflet-sbs-range {
            z-index: 1000 !important;
            pointer-events: auto !important;
            cursor: ew-resize !important;
          }
        </style>
        {% endmacro %}
        """
    )

    def __init__(self, params: Any | None, has_analysis_layers: bool, layer_payload: dict[str, Any] | None = None) -> None:
        super().__init__()
        self._name = "LegacyMapLegend"
        self.has_analysis_layers = has_analysis_layers
        self.date_text = _legend_date_text(params, has_analysis_layers)
        self.layer_details = _legend_layer_details(layer_payload)


def _legend_date_text(params: Any | None, has_analysis_layers: bool) -> str:
    if not params or not has_analysis_layers:
        return "Limite administrative: Eurostat GISCO NUTS 2024."
    return (
        "Deschide fiecare categorie pentru zilele scenelor folosite.\n"
        "Daca apar mai multe zile, layerul este compozit median din acele scene.\n"
        f"Metoda BEFORE SAR: {getattr(params, 'before_sar_method', 'nespecificata')}.\n"
        f"Metoda AFTER SAR: {getattr(params, 'after_sar_method', 'nespecificata')}."
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
            style = layer_style(layer.get("id") or "")
            details = metadata.get("details") or style.get("description") or layer.get("warning") or ""
            status = "disponibil" if layer.get("available", True) else "indisponibil"
            color = _legend_color(layer.get("id") or "")
            legend_items = "".join(
                f"<br><span style=\"display:inline-block;width:10px;height:10px;background:{html.escape(str(item[0]))};border:1px solid #334155;margin-right:4px\"></span>{html.escape(str(item[1]))}"
                for item in style.get("legend_items", [])
            )
            rows.append(
                "<li>"
                f"<span style=\"display:inline-block;width:12px;height:12px;background:{color};border:1px solid #334155;margin-right:4px\"></span>"
                f"<strong>{html.escape(str(layer.get('display_name')))}</strong> ({status})<br>"
                f"Tip: {html.escape(str(style.get('layer_type', layer.get('layer_type', 'layer'))))}<br>"
                f"Sursa: {html.escape(str(style.get('source') or source))}<br>"
                f"Zi/scene: {dates_text}"
                f"{legend_items}"
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


def _active_legend_layer_details(layer_payload: dict[str, Any] | None) -> str:
    active_layers = [
        layer
        for layer in (layer_payload or {}).get("available", [])
        if layer.get("shown")
    ][:4]
    if not active_layers:
        return "<div data-active-layers><div class=\"legend-card\">Activeaza un layer pentru detalii contextuale.</div></div>"
    cards = [_legend_card(layer) for layer in active_layers]
    return f"<div data-active-layers>{''.join(cards)}</div>"


def _legend_card(layer: dict[str, Any]) -> str:
    style = layer_style(layer.get("id") or "")
    metadata = layer.get("metadata") or {}
    dates = metadata.get("dates") or metadata.get("date") or style.get("date_or_period")
    if isinstance(dates, list):
        dates_text = ", ".join(str(item) for item in dates) if dates else str(style.get("date_or_period"))
    else:
        dates_text = str(dates)
    legend_items = "".join(
        "<div class=\"legend-row\">"
        f"<span class=\"legend-swatch\" style=\"background:{html.escape(str(color))}\"></span>"
        f"<span>{html.escape(str(label))}</span>"
        "</div>"
        for color, label in style.get("legend_items", [])
    )
    return (
        "<div class=\"legend-card\">"
        f"<strong>{html.escape(str(layer.get('display_name')))}</strong>"
        f"<div>Tip: {html.escape(str(style.get('layer_type', layer.get('layer_type', 'layer'))))}</div>"
        f"<div>Sursa: {html.escape(str(style.get('source') or metadata.get('source') or 'sursa nespecificata'))}</div>"
        f"<div>Data/perioada: {html.escape(dates_text)}</div>"
        f"{legend_items}"
        f"<div>{html.escape(str(style.get('description', '')))}</div>"
        "</div>"
    )


def _legend_payload_for_js(layer_payload: dict[str, Any] | None) -> list[dict[str, Any]]:
    payload: list[dict[str, Any]] = []
    for layer in (layer_payload or {}).get("available", []):
        style = layer_style(layer.get("id") or "")
        metadata = layer.get("metadata") or {}
        dates = metadata.get("dates") or metadata.get("date") or style.get("date_or_period")
        if isinstance(dates, list):
            dates = ", ".join(str(item) for item in dates) if dates else style.get("date_or_period")
        payload.append(
            {
                "id": layer.get("id"),
                "display_name": layer.get("display_name"),
                "category": layer.get("category"),
                "shown": bool(layer.get("shown")),
                "layer_type": style.get("layer_type", layer.get("layer_type")),
                "source": style.get("source") or metadata.get("source"),
                "date_or_period": str(dates),
                "legend_items": style.get("legend_items", []),
            }
        )
    return payload


def _legend_color(layer_id: str) -> str:
    style = layer_style(layer_id)
    if style.get("legend_color"):
        return str(style["legend_color"])
    colors = {
        "sar_water_before": "#7dd3fc",
        "sar_water_after": "#2563eb",
        "sar_new_water": "#22d3ee",
        "sar_persistent_water": "#1e3a8a",
        "sar_water_loss": "#f97316",
        "flood_extent": "#be185d",
        "dynamic_world_new_water": "#818cf8",
        "dynamic_world_water_loss": "#f59e0b",
        "dynamic_world_other_change": "#a78bfa",
        "sar_dynamic_world_new_water_overlap": "#16a34a",
        "new_water_only_sar": "#67e8f9",
        "new_water_only_dynamic_world": "#9333ea",
        "permanent_water": "#0f172a",
        "osm_buildings": "#ef4444",
        "osm_roads": "#f97316",
        "osm_critical": "#7c3aed",
        "osm_railways": "#111827",
        "osm_bridges": "#0ea5e9",
    }
    return colors.get(layer_id, "#94a3b8")


def add_osm_operational_layers(
    folium_map: folium.Map,
    registry: LayerRegistry,
    osm_layers: dict[str, dict[str, Any]] | None,
) -> None:
    if not osm_layers:
        return
    for layer_id, layer_payload in osm_layers.items():
        features = layer_payload.get("features") or []
        display_name = layer_payload.get("display_name") or layer_id
        color = layer_payload.get("color") or _legend_color(layer_id)
        if not features:
            registry.unavailable(
                layer_id=layer_id,
                display_name=display_name,
                category="Impact operational OSM",
                layer_type="vector",
                warning="Nu au fost gasite elemente OSM in zona interogata.",
                metadata=_osm_metadata(display_name),
            )
            continue
        if layer_id == "osm_critical":
            geojson_layer = _critical_facilities_layer(layer_payload, display_name, color)
            geojson_layer.add_to(folium_map)
            registry.add(
                LayerEntry(
                    id=layer_id,
                    display_name=display_name,
                    category="Impact operational OSM",
                    layer_type="vector",
                    available=True,
                    comparable=False,
                    shown=False,
                    folium_layer=geojson_layer,
                    metadata=_osm_metadata(display_name),
                )
            )
            continue
        geojson_layer = folium.GeoJson(
            layer_payload,
            name=f"Impact operational OSM - {display_name}",
            style_function=lambda feature, color=color: {
                "color": _osm_exposure_color(feature, color),
                "fillColor": _osm_exposure_color(feature, color),
                "weight": 3 if feature.get("geometry", {}).get("type") != "Polygon" else 1,
                "fillOpacity": 0.35,
                "opacity": 0.9,
            },
            marker=folium.CircleMarker(radius=6, color=color, fill=True, fill_color=color, fill_opacity=0.85),
            tooltip=folium.GeoJsonTooltip(
                fields=["exposure_label", "name", "exposure_level"],
                aliases=["Expunere", "Nume", "Nivel"],
                localize=True,
                sticky=True,
            ),
            popup=folium.GeoJsonPopup(
                fields=_osm_popup_fields(layer_id),
                aliases=_osm_popup_aliases(layer_id),
                localize=True,
            ),
            show=False,
            control=True,
        )
        geojson_layer.add_to(folium_map)
        registry.add(
            LayerEntry(
                id=layer_id,
                display_name=display_name,
                category="Impact operational OSM",
                layer_type="vector",
                available=True,
                comparable=False,
                shown=False,
                folium_layer=geojson_layer,
                metadata=_osm_metadata(display_name),
            )
        )


def _critical_facilities_layer(layer_payload: dict[str, Any], display_name: str, color: str) -> folium.FeatureGroup:
    group = folium.FeatureGroup(name=f"Impact operational OSM - {display_name}", show=False, control=True)
    line_features = []
    for feature in layer_payload.get("features", []):
        geometry = feature.get("geometry") or {}
        properties = feature.get("properties") or {}
        if geometry.get("type") == "Point":
            lon, lat = geometry.get("coordinates", [None, None])[:2]
            if lat is None or lon is None:
                continue
            folium.Marker(
                location=[lat, lon],
                icon=_critical_facility_icon(properties),
                tooltip=properties.get("exposure_label", "obiectiv critic potential expus"),
                popup=folium.Popup(_osm_popup_html(properties), max_width=320),
            ).add_to(group)
        else:
            line_features.append(feature)
    if line_features:
        folium.GeoJson(
            {"type": "FeatureCollection", "features": line_features},
            style_function=lambda feature, color=color: {
                "color": _osm_exposure_color(feature, color),
                "fillColor": _osm_exposure_color(feature, color),
                "weight": 2,
                "fillOpacity": 0.35,
                "opacity": 0.9,
            },
            tooltip=folium.GeoJsonTooltip(
                fields=["exposure_label", "name", "exposure_status"],
                aliases=["Expunere", "Nume", "Status"],
                localize=True,
                sticky=True,
            ),
            popup=folium.GeoJsonPopup(
                fields=_osm_popup_fields("osm_critical"),
                aliases=_osm_popup_aliases("osm_critical"),
                localize=True,
            ),
        ).add_to(group)
    return group


def _critical_facility_icon(properties: dict[str, Any]) -> folium.Icon:
    amenity = properties.get("amenity")
    icon_name = {
        "hospital": "plus-square",
        "clinic": "plus-square",
        "doctors": "user-md",
        "fire_station": "fire",
        "police": "shield",
        "school": "graduation-cap",
        "pharmacy": "medkit",
        "fuel": "tint",
    }.get(amenity, "exclamation-triangle")
    color = "red" if amenity in {"hospital", "clinic", "doctors", "fire_station"} else "purple"
    return folium.Icon(color=color, icon=icon_name, prefix="fa")


def _osm_popup_html(properties: dict[str, Any]) -> str:
    rows = [
        ("ID OSM", properties.get("osm_id", "necunoscut")),
        ("Tip geometrie OSM", properties.get("osm_type", "necunoscut")),
        ("Tip obiectiv", properties.get("amenity", "necunoscut")),
        ("Nume", properties.get("name", "fara nume")),
        ("Cladire", properties.get("building", "nespecificat")),
        ("Operator", properties.get("operator", "nespecificat")),
        ("Adresa", _osm_address(properties)),
        ("Sursa", properties.get("osm_source", "OpenStreetMap")),
        ("Distanta fata de extindere", properties.get("distance_to_extent", "nedisponibila")),
        ("Status", properties.get("exposure_status", "within buffer")),
        ("Nivel expunere", properties.get("exposure_level", "nespecificat")),
    ]
    return "<br>".join(f"<strong>{html.escape(label)}:</strong> {html.escape(str(value))}" for label, value in rows)


def _osm_popup_fields(layer_id: str) -> list[str]:
    base = ["osm_id", "name", "exposure_label", "exposure_level", "osm_source", "distance_to_extent", "exposure_status"]
    by_layer = {
        "osm_buildings": ["building", "addr_city", "addr_street", "addr_housenumber"],
        "osm_roads": ["highway"],
        "osm_critical": ["amenity", "building", "operator", "addr_city", "addr_street", "addr_housenumber", "emergency", "healthcare"],
        "osm_railways": ["railway"],
        "osm_bridges": ["bridge", "highway", "railway"],
    }
    return base + by_layer.get(layer_id, [])


def _osm_popup_aliases(layer_id: str) -> list[str]:
    aliases = {
        "osm_id": "ID OSM",
        "name": "Nume",
        "exposure_label": "Expunere",
        "exposure_level": "Nivel",
        "osm_source": "Sursa",
        "distance_to_extent": "Distanta fata de extindere",
        "exposure_status": "Status",
        "building": "Cladire",
        "addr_city": "Localitate",
        "addr_street": "Strada",
        "addr_housenumber": "Numar",
        "highway": "Tip drum",
        "amenity": "Tip obiectiv",
        "operator": "Operator",
        "emergency": "Serviciu urgenta",
        "healthcare": "Serviciu medical",
        "railway": "Tip cale ferata",
        "bridge": "Pod",
    }
    return [aliases[field] for field in _osm_popup_fields(layer_id)]


def _osm_address(properties: dict[str, Any]) -> str:
    parts = [
        properties.get("addr_street"),
        properties.get("addr_housenumber"),
        properties.get("addr_city"),
    ]
    address = ", ".join(str(part) for part in parts if part)
    return address or "nespecificata"


def _osm_metadata(display_name: str) -> dict[str, Any]:
    return {
        "source": "OpenStreetMap via Overpass API",
        "date": "interogare la rularea analizei",
        "details": (
            f"{display_name}. Expunere estimata operational, raportata la zona analizata "
            "dupa rularea rasterului SAR flood extent filtrat. Culori expunere: high rosu, "
            "medium portocaliu, low galben."
        ),
    }


def _osm_exposure_color(feature: dict[str, Any], fallback: str) -> str:
    level = (feature.get("properties") or {}).get("exposure_level")
    return {
        "high": "#dc2626",
        "medium": "#f97316",
        "low": "#eab308",
    }.get(level, fallback)


def build_result_map_from_registry_payload(
    layer_payload: dict[str, list[dict[str, Any]]],
    params: Any,
    counties_geojson: dict[str, Any] | None = None,
    selected_feature: dict[str, Any] | None = None,
    osm_layers: dict[str, dict[str, Any]] | None = None,
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

    add_osm_operational_layers(main_map, registry, osm_layers)
    add_default_side_by_side(registry)
    DynamicCompareControl(registry, auto_start=False).add_to(main_map)
    add_map_legend(main_map, params=params, has_analysis_layers=True, layer_payload=registry.report_payload())
    folium.LayerControl(collapsed=False).add_to(main_map)
    GroupedLayerControlEnhancer().add_to(main_map)
    return MapBundle(main_map=main_map, registry=registry)


def add_default_side_by_side(registry: LayerRegistry) -> None:
    layers_by_id = {layer.id: layer for layer in registry.available_layers()}
    before = layers_by_id.get("sar_water_before") or layers_by_id.get("sar_before")
    after = layers_by_id.get("sar_water_after") or layers_by_id.get("sar_after")
    if not before or not after:
        return
    if not before.folium_layer or not after.folium_layer:
        return
    parent_map = before.folium_layer._parent
    if parent_map is None:
        return
    SideBySideLayers(before.folium_layer, after.folium_layer).add_to(parent_map)
