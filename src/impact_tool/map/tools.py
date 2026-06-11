from __future__ import annotations

from branca.element import MacroElement
from jinja2 import Template


class NavigationControl(MacroElement):
    _template = Template(
        """
        {% macro html(this, kwargs) %}
        <style>
          .impact-nav button { width:30px; height:30px; border:0; background:#fff; cursor:pointer; }
        </style>
        {% endmacro %}
        {% macro script(this, kwargs) %}
        (function () {
          var map = {{ this._parent.get_name() }};
          var control = L.control({position:'topleft'});
          control.onAdd = function () {
            var box = L.DomUtil.create('div', 'leaflet-bar impact-nav');
            var home = L.DomUtil.create('button', '', box);
            home.type = 'button'; home.title = 'Revino la România'; home.innerHTML = '⌂';
            home.onclick = function () { map.setView([45.9432, 24.9668], 6); };
            var county = L.DomUtil.create('button', '', box);
            county.type = 'button'; county.title = 'Centrează pe județ'; county.innerHTML = '◎';
            county.onclick = function () { map.fitBounds({{ this.bounds }}); };
            L.DomEvent.disableClickPropagation(box);
            return box;
          };
          control.addTo(map);
        })();
        {% endmacro %}
        """
    )

    def __init__(self, bounds: list[list[float]]) -> None:
        super().__init__()
        self._name = "NavigationControl"
        self.bounds = bounds
