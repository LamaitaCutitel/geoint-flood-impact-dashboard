from src.gee.sentinel1_scene_explorer import validate_scene_pair


def _scene(**overrides):
    scene = {
        "ee_id": "COPERNICUS/S1_GRD/S1A_TEST",
        "display_id": "S1A_TEST",
        "acquisition_time": "2024-09-01T16:27:00+00:00",
        "platform": "A",
        "polarization": "VH",
        "orbit_pass": "ASCENDING",
        "relative_orbit": 80,
        "instrument_mode": "IW",
        "resolution_meters": 10,
        "coverage_percent": 100,
        "warnings": [],
    }
    scene.update(overrides)
    return scene


def test_validate_scene_pair_accepts_matching_scenes():
    before = _scene(acquisition_time="2024-09-01T16:27:00+00:00")
    after = _scene(acquisition_time="2024-09-14T16:27:00+00:00")

    status = validate_scene_pair(before, after)

    assert status["compatible"] is True
    assert status["requires_confirmation"] is False


def test_validate_scene_pair_blocks_reversed_dates():
    before = _scene(acquisition_time="2024-09-20T16:27:00+00:00")
    after = _scene(acquisition_time="2024-09-14T16:27:00+00:00")

    status = validate_scene_pair(before, after)

    assert status["compatible"] is False
    assert "BEFORE trebuie sa fie anterioara" in status["errors"][0]


def test_validate_scene_pair_warns_on_relative_orbit_only():
    before = _scene(acquisition_time="2024-09-01T16:27:00+00:00", relative_orbit=80)
    after = _scene(acquisition_time="2024-09-14T16:27:00+00:00", relative_orbit=81)

    status = validate_scene_pair(before, after)

    assert status["compatible"] is True
    assert status["requires_confirmation"] is True
