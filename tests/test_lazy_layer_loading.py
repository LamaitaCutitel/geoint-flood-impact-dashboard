from types import SimpleNamespace

from app import _layer_images


class _FakeImage:
    def select(self, name):
        return _FakeImage()

    def updateMask(self, mask):
        return _FakeImage()


def _params(load_optional_layers=False):
    return SimpleNamespace(
        show_sar_before=True,
        show_sar_after=True,
        show_sar_water_layers=True,
        show_sar_change=load_optional_layers,
        show_detected_flood_extent=True,
        show_permanent_water=True,
        show_land_cover=True,
        show_sar_dynamic_world_correlation=True,
        show_sentinel2_rgb=load_optional_layers,
        load_optional_layers=load_optional_layers,
    )


def _layer_images_for(load_optional_layers=False):
    image = _FakeImage()
    return _layer_images(
        _params(load_optional_layers),
        image,
        image,
        SimpleNamespace(change_image=image, flood_mask=image),
        image,
        image,
        image,
        image,
        {
            "dynamic_world_new_water": image,
            "dynamic_world_water_loss": image,
            "dynamic_world_other_change": image,
        },
        {
            "sar_water_before": image,
            "sar_water_after": image,
            "sar_new_water": image,
            "sar_persistent_water": image,
            "sar_water_loss": image,
        },
        {
            "sar_dynamic_world_new_water_overlap": image,
            "new_water_only_sar": image,
            "new_water_only_dynamic_world": image,
        },
        SimpleNamespace(rgb_before=image, rgb_after=image, indices={"ndwi_before": image}),
        SimpleNamespace(dem=image, hillshade=image, slope=image),
        {},
    )


def test_default_layers_skip_optional_outputs():
    layers = _layer_images_for(False)

    assert "sar_new_water" in layers
    assert "dynamic_world_new_water" in layers
    assert "sar_dynamic_world_new_water_overlap" in layers
    assert "sar_difference" not in layers
    assert "sar_persistent_water" not in layers
    assert "dynamic_world_other_change" not in layers
    assert "rgb_before" not in layers
    assert "dem" not in layers


def test_optional_layers_are_added_on_request():
    layers = _layer_images_for(True)

    assert "sar_difference" in layers
    assert "sar_persistent_water" in layers
    assert "dynamic_world_other_change" in layers
    assert "rgb_before" in layers
    assert "dem" in layers
