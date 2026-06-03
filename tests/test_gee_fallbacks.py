import sys

from src.gee.gee_auth import initialize_earth_engine
from src.gee.sentinel1_collection import count_scenes


def test_initialize_earth_engine_without_project_id(monkeypatch):
    monkeypatch.delenv("GEE_PROJECT_ID", raising=False)
    result = initialize_earth_engine(interactive=False)
    assert result.available is False
    assert "GEE_PROJECT_ID" in result.message


def test_initialize_earth_engine_without_package(monkeypatch):
    monkeypatch.setenv("GEE_PROJECT_ID", "demo-project")
    monkeypatch.setitem(sys.modules, "ee", None)
    result = initialize_earth_engine(interactive=False)
    assert result.available is False
    assert "earthengine-api" in result.message


class _BrokenCollection:
    def size(self):
        raise RuntimeError("No scenes")


def test_count_scenes_fallback_for_missing_sentinel1_scenes():
    assert count_scenes(_BrokenCollection()) == 0
