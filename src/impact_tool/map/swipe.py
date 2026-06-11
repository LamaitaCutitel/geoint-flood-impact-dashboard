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
        {% macro html(this, kwargs) %}
        <style>
          .impact-swipe-control {
            background:rgba(15,23,42,.92); border:1px solid #64748b;
            border-radius:6px; color:#fff; padding:8px 10px; width:220px;
          }
          .impact-swipe-control strong { display:block; font-size:12px; margin-bottom:5px; }
          .impact-swipe-control input { cursor:ew-resize; margin:0; width:100%; }
          .impact-swipe-divider {
            background:#fff; box-shadow:0 0 0 1px #0f172a;
            pointer-events:none; position:absolute; top:0; bottom:0; width:3px;
            z-index:650;
          }
        </style>
        {% endmacro %}
        {% macro script(this, kwargs) %}
        (function () {
          var map = {{ this._parent.get_name() }};
          var config = {{ this.config_json }};
          map.createPane('impactSwipeBefore');
          map.createPane('impactSwipeAfter');
          var beforePane = map.getPane('impactSwipeBefore');
          var afterPane = map.getPane('impactSwipeAfter');
          beforePane.style.zIndex = 410;
          afterPane.style.zIndex = 420;

          L.tileLayer(config.before, {
            attribution:'Google Earth Engine', pane:'impactSwipeBefore'
          }).addTo(map);
          L.tileLayer(config.after, {
            attribution:'Google Earth Engine', pane:'impactSwipeAfter'
          }).addTo(map);

          var divider = L.DomUtil.create('div', 'impact-swipe-divider', map.getContainer());
          var control = L.control({position:'topright'});
          control.onAdd = function () {
            var box = L.DomUtil.create('div', 'impact-swipe-control');
            box.innerHTML = '<strong>BEFORE ↔ AFTER</strong>';
            var slider = L.DomUtil.create('input', '', box);
            slider.type = 'range';
            slider.min = '0'; slider.max = '100'; slider.value = '50';
            slider.setAttribute('aria-label', 'Comparație BEFORE AFTER');
            function update() {
              var percent = Number(slider.value);
              afterPane.style.clipPath = 'inset(0 0 0 ' + percent + '%)';
              divider.style.left = percent + '%';
            }
            slider.addEventListener('input', update);
            L.DomEvent.disableClickPropagation(box);
            L.DomEvent.disableScrollPropagation(box);
            update();
            return box;
          };
          control.addTo(map);
        })();
        {% endmacro %}
        """
    )

    def __init__(self, before_tile: str, after_tile: str) -> None:
        super().__init__()
        self._name = "SarSwipeControl"
        self.config_json = json.dumps({"before": before_tile, "after": after_tile})
