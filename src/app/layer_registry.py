from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


@dataclass
class LayerEntry:
    id: str
    display_name: str
    category: str
    layer_type: str
    available: bool = True
    comparable: bool = True
    shown: bool = False
    warning: str | None = None
    tile_url: str | None = None
    folium_layer: Any | None = None

    def to_report_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data.pop("folium_layer", None)
        return data


class LayerRegistry:
    def __init__(self) -> None:
        self._layers: dict[str, LayerEntry] = {}

    def add(self, entry: LayerEntry) -> None:
        self._layers[entry.id] = entry

    def unavailable(
        self,
        layer_id: str,
        display_name: str,
        category: str,
        layer_type: str,
        warning: str,
        comparable: bool = False,
    ) -> None:
        self.add(
            LayerEntry(
                id=layer_id,
                display_name=display_name,
                category=category,
                layer_type=layer_type,
                available=False,
                comparable=comparable,
                warning=warning,
            )
        )

    def available_layers(self) -> list[LayerEntry]:
        return [layer for layer in self._layers.values() if layer.available]

    def unavailable_layers(self) -> list[LayerEntry]:
        return [layer for layer in self._layers.values() if not layer.available]

    def comparable_layers(self) -> list[LayerEntry]:
        return [layer for layer in self.available_layers() if layer.comparable and layer.tile_url]

    def report_payload(self) -> dict[str, list[dict[str, Any]]]:
        return {
            "available": [layer.to_report_dict() for layer in self.available_layers()],
            "unavailable": [layer.to_report_dict() for layer in self.unavailable_layers()],
        }

    def __iter__(self):
        return iter(self._layers.values())
