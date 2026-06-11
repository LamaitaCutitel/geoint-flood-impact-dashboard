from __future__ import annotations

import json

from branca.element import MacroElement
from jinja2 import Template


SWIPE_CONTROL_STATUS = "indisponibil până la selectarea scenelor"


def swipe_ready(before_scene: dict | None, after_scene: dict | None) -> bool:
    return bool(before_scene and after_scene)


class SarSwipeControl(MacroElement):
    _template = Template(
        """
        {% macro script(this, kwargs) %}
        (function () {
          var map = {{ this._parent.get_name() }};
          var config = {{ this.config_json }};
          var left = L.tileLayer(config.before, {attribution: 'Google Earth Engine'}).addTo(map);
          var right = L.tileLayer(config.after, {attribution: 'Google Earth Engine'}).addTo(map);
          var fallback = L.control({position: 'topright'});
          fallback.onAdd = function () {
            var box = L.DomUtil.create('div', 'impact-swipe-fallback');
            box.innerHTML = '<strong>SAR BEFORE ↔ SAR AFTER</strong><br><small>Se încarcă separatorul vertical…</small>';
            return box;
          };
          fallback.addTo(map);

          function start() {
            if (window.L && L.control && L.control.sideBySide) {
              L.control.sideBySide(left, right).addTo(map);
              map.removeControl(fallback);
              return true;
            }
            return false;
          }
          if (start()) { return; }
          var script = document.createElement('script');
          script.src = 'https://cdn.jsdelivr.net/npm/leaflet-side-by-side@2.2.0/leaflet-side-by-side.min.js';
          script.onload = start;
          script.onerror = function () {
            var small = document.querySelector('.impact-swipe-fallback small');
            if (small) { small.textContent = 'Separator indisponibil; ambele imagini rămân în hartă.'; }
          };
          document.head.appendChild(script);
        })();
        {% endmacro %}
        """
    )

    def __init__(self, before_tile: str, after_tile: str) -> None:
        super().__init__()
        self._name = "SarSwipeControl"
        self.config_json = json.dumps({"before": before_tile, "after": after_tile})
