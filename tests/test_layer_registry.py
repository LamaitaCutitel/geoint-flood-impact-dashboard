from src.app.layer_registry import LayerEntry, LayerRegistry


def test_layer_registry_tracks_available_and_unavailable_layers():
    registry = LayerRegistry()
    registry.add(
        LayerEntry(
            id="sar_before",
            display_name="Sentinel-1 SAR before",
            category="Sentinel-1 SAR",
            layer_type="before",
            tile_url="https://tiles.example/{z}/{x}/{y}",
        )
    )
    registry.unavailable(
        "s2_after",
        "RGB after",
        "Sentinel-2 optic",
        "after",
        "clouds",
    )

    assert len(registry.available_layers()) == 1
    assert len(registry.unavailable_layers()) == 1
    assert registry.comparable_layers()[0].id == "sar_before"
    payload = registry.report_payload()
    assert payload["available"][0]["display_name"] == "Sentinel-1 SAR before"
    assert payload["unavailable"][0]["warning"] == "clouds"
