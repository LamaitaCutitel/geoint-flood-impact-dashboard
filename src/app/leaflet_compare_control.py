from __future__ import annotations

import json

from branca.element import MacroElement
from jinja2 import Template

from src.app.layer_registry import LayerRegistry


class DynamicCompareControl(MacroElement):
    _template = Template(
        """
        {% macro script(this, kwargs) %}
        (function() {
          var map = {{ this._parent.get_name() }};
          var layers = {{ this.layers_json }};
          if (!layers.length) { return; }

          if (!document.getElementById('dynamic-compare-style')) {
            var style = document.createElement('style');
            style.id = 'dynamic-compare-style';
            style.textContent = [
              '.leaflet-sbs-divider {',
              '  background: #f8fafc !important;',
              '  box-shadow: 0 0 0 2px rgba(15,23,42,.65), 0 0 10px rgba(15,23,42,.45) !important;',
              '  width: 4px !important;',
              '  z-index: 999 !important;',
              '}',
              '.leaflet-sbs-range {',
              '  z-index: 1000 !important;',
              '  pointer-events: auto !important;',
              '  cursor: ew-resize !important;',
              '}'
            ].join('');
            document.head.appendChild(style);
          }

          if (!window.__leafletSideBySideLoading && !window.L.control.sideBySide) {
            window.__leafletSideBySideLoading = true;
            var script = document.createElement('script');
            script.src = 'https://cdn.jsdelivr.net/npm/leaflet-side-by-side@2.2.0/leaflet-side-by-side.min.js';
            script.onload = function() { window.__leafletSideBySideLoading = false; };
            script.onerror = function() { window.__leafletSideBySideLoading = false; };
            document.head.appendChild(script);
          }

          var compareControl = null;
          var leftLayer = null;
          var rightLayer = null;

          function makeLayer(item) {
            return L.tileLayer(item.tile_url, {
              attribution: 'Google Earth Engine',
              opacity: 1
            });
          }

          function renderControl(container) {
            container.innerHTML = '';
            var title = L.DomUtil.create('div', 'compare-title', container);
            title.innerHTML = '<strong>Compara doua layere</strong>';
            var left = L.DomUtil.create('select', '', container);
            var right = L.DomUtil.create('select', '', container);
            layers.forEach(function(item, idx) {
              var optLeft = document.createElement('option');
              optLeft.value = idx;
              optLeft.text = item.display_name;
              left.appendChild(optLeft);
              var optRight = document.createElement('option');
              optRight.value = idx;
              optRight.text = item.display_name;
              right.appendChild(optRight);
            });
            right.value = layers.length > 1 ? 1 : 0;
            var start = L.DomUtil.create('button', '', container);
            start.innerText = 'Porneste comparatia';
            var swap = L.DomUtil.create('button', '', container);
            swap.innerText = 'Schimba layerele';
            var stop = L.DomUtil.create('button', '', container);
            stop.innerText = 'Iesi din comparatie';

            function clearCompare() {
              if (compareControl) {
                map.removeControl(compareControl);
                compareControl = null;
              }
              if (leftLayer) { map.removeLayer(leftLayer); leftLayer = null; }
              if (rightLayer) { map.removeLayer(rightLayer); rightLayer = null; }
            }

            function startCompare() {
              clearCompare();
              var leftItem = layers[parseInt(left.value)];
              var rightItem = layers[parseInt(right.value)];
              if (!leftItem || !rightItem) { return; }
              leftLayer = makeLayer(leftItem).addTo(map);
              rightLayer = makeLayer(rightItem).addTo(map);
              var waitForPlugin = function() {
                if (window.L.control.sideBySide) {
                  compareControl = L.control.sideBySide(leftLayer, rightLayer).addTo(map);
                  setTimeout(function() {
                    var range = document.querySelector('.leaflet-sbs-range');
                    if (range) {
                      range.style.zIndex = 1000;
                      range.style.pointerEvents = 'auto';
                    }
                  }, 50);
                } else {
                  setTimeout(waitForPlugin, 150);
                }
              };
              waitForPlugin();
            }

            start.onclick = startCompare;
            swap.onclick = startCompare;
            stop.onclick = clearCompare;
            L.DomEvent.disableClickPropagation(container);
            {% if this.auto_start %}
            setTimeout(startCompare, 300);
            {% endif %}
          }

          var control = L.control({position: 'topright'});
          control.onAdd = function() {
            var div = L.DomUtil.create('div', 'leaflet-bar dynamic-compare-control');
            div.style.background = 'white';
            div.style.padding = '8px';
            div.style.maxWidth = '260px';
            div.style.fontSize = '12px';
            div.style.boxShadow = '0 1px 6px rgba(0,0,0,.25)';
            div.style.lineHeight = '1.35';
            div.querySelectorAll = div.querySelectorAll || function(){ return []; };
            renderControl(div);
            return div;
          };
          control.addTo(map);
        })();
        {% endmacro %}
        """
    )

    def __init__(self, registry: LayerRegistry, auto_start: bool = False) -> None:
        super().__init__()
        self._name = "DynamicCompareControl"
        layers = [
                {
                    "id": layer.id,
                    "display_name": layer.display_name,
                    "tile_url": layer.tile_url,
                }
                for layer in registry.comparable_layers()
            ]
        if auto_start:
            layers = _sar_first(layers)
        self.layers_json = json.dumps(
            layers,
            ensure_ascii=False,
        )
        self.auto_start = auto_start


def _sar_first(layers: list[dict[str, str | None]]) -> list[dict[str, str | None]]:
    by_id = {layer["id"]: layer for layer in layers}
    before = by_id.get("sar_before")
    after = by_id.get("sar_after")
    if not before or not after:
        return layers
    rest = [layer for layer in layers if layer["id"] not in {"sar_before", "sar_after"}]
    return [before, after, *rest]
