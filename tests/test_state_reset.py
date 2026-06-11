from datetime import date

from src.app.state import (
    COUNTY_DEPENDENT_STATE_KEYS,
    AnalysisParameters,
    county_dependent_parameter_key,
    reset_county_dependent_state,
)


def test_reset_county_dependent_state_removes_old_selections():
    session_state = {key: "old" for key in COUNTY_DEPENDENT_STATE_KEYS}
    session_state["unrelated"] = "kept"

    reset_county_dependent_state(session_state)

    assert all(key not in session_state for key in COUNTY_DEPENDENT_STATE_KEYS)
    assert session_state["unrelated"] == "kept"


def test_county_change_updates_reset_key():
    params = AnalysisParameters(county_name="Galati")
    changed = AnalysisParameters(county_name="Braila")

    assert county_dependent_parameter_key(params) != county_dependent_parameter_key(changed)


def test_period_change_updates_reset_key():
    params = AnalysisParameters(before_start_date=date(2024, 8, 20))
    changed = AnalysisParameters(before_start_date=date(2024, 8, 19))

    assert county_dependent_parameter_key(params) != county_dependent_parameter_key(changed)


def test_polarization_change_updates_reset_key():
    params = AnalysisParameters(polarization="VH")
    changed = AnalysisParameters(polarization="VV")

    assert county_dependent_parameter_key(params) != county_dependent_parameter_key(changed)


def test_orbit_pass_change_updates_reset_key():
    params = AnalysisParameters(orbit_pass="BOTH")
    changed = AnalysisParameters(orbit_pass="ASCENDING")

    assert county_dependent_parameter_key(params) != county_dependent_parameter_key(changed)


def test_hybrid_sar_strategy_defaults_to_before_median_after_individual():
    params = AnalysisParameters()

    assert params.before_sar_method == "Compozit median din scene compatibile"
    assert params.after_sar_method == "Scena individuala selectata manual"


def test_dynamic_world_and_lazy_loading_defaults():
    params = AnalysisParameters()

    assert params.dynamic_world_after_mode == "Fereastra apropiata de scena SAR AFTER"
    assert params.load_optional_layers is False
