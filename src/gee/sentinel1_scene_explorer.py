from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import UTC, datetime
from typing import Any

from src.gee.sentinel1_collection import get_sentinel1_collection


@dataclass(frozen=True)
class Sentinel1Scene:
    ee_id: str
    display_id: str
    acquisition_time: str
    platform: str
    polarization: str
    orbit_pass: str
    relative_orbit: int | None
    instrument_mode: str
    resolution_meters: float | None
    coverage_percent: float
    warnings: list[str]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


def search_sentinel1_scenes(
    ee: Any,
    aoi: Any,
    start_date: Any,
    end_date: Any,
    polarization: str,
    orbit_pass: str,
    limit: int = 60,
) -> list[dict[str, Any]]:
    collection = get_sentinel1_collection(ee, aoi, start_date, end_date, polarization, orbit_pass)
    aoi_area = aoi.area(1)

    def annotate(image: Any) -> Any:
        footprint_area = image.geometry().intersection(aoi, 1).area(1)
        coverage = footprint_area.divide(aoi_area).multiply(100)
        return image.set("aoi_coverage_percent", coverage)

    try:
        features = collection.map(annotate).sort("system:time_start").toList(limit).getInfo()
    except Exception:
        return []

    scenes: list[dict[str, Any]] = []
    for feature in features:
        scene = _scene_from_feature(feature, polarization)
        if scene:
            scenes.append(scene.as_dict())
    return scenes


def selected_scene_image(ee: Any, scene: dict[str, Any], aoi: Any, smoothing_radius: int = 0) -> Any:
    image = ee.Image(scene["ee_id"]).select(scene["polarization"]).clip(aoi)
    if smoothing_radius <= 0:
        return image
    kernel = ee.Kernel.circle(radius=smoothing_radius, units="meters", normalize=True)
    return image.focal_mean(kernel=kernel, iterations=1).clip(aoi)


def validate_scene_pair(before: dict[str, Any] | None, after: dict[str, Any] | None) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not before or not after:
        return {
            "compatible": False,
            "requires_confirmation": False,
            "errors": ["Selecteaza o scena BEFORE si o scena AFTER."],
            "warnings": [],
        }
    if before["acquisition_time"] >= after["acquisition_time"]:
        errors.append("Scena BEFORE trebuie sa fie anterioara scenei AFTER.")
    for key, label in (
        ("polarization", "polarizare"),
        ("instrument_mode", "instrument mode"),
        ("orbit_pass", "directie orbita"),
    ):
        if before.get(key) != after.get(key):
            errors.append(f"Pereche incompatibila: {label} diferit.")
    if before.get("relative_orbit") != after.get("relative_orbit"):
        warnings.append("Orbita relativa difera; comparatia poate produce diferente geometrice.")
    for role, scene in (("BEFORE", before), ("AFTER", after)):
        if float(scene.get("coverage_percent") or 0) < 90:
            errors.append(f"Scena {role} are acoperire insuficienta a judetului.")
    return {
        "compatible": not errors,
        "requires_confirmation": not errors and bool(warnings),
        "errors": errors,
        "warnings": warnings,
    }


def scene_recommendation_labels(
    scene: dict[str, Any],
    scenes: list[dict[str, Any]],
    selected_before: dict[str, Any] | None,
    selected_after: dict[str, Any] | None,
) -> list[str]:
    labels: list[str] = []
    if float(scene.get("coverage_percent") or 0) < 90:
        labels.append("Acoperire incompleta")
    if selected_before and scene["acquisition_time"] > selected_before["acquisition_time"]:
        if _soft_compatible(selected_before, scene):
            labels.append("Compatibil cu scena selectata")
        else:
            labels.append("Orbita incompatibila")
    if selected_after and scene["acquisition_time"] < selected_after["acquisition_time"]:
        if _soft_compatible(scene, selected_after):
            labels.append("Compatibil cu scena selectata")
        else:
            labels.append("Orbita incompatibila")
    before_candidate = _best_before(scenes)
    after_candidate = _best_after(scenes)
    if before_candidate and before_candidate["ee_id"] == scene["ee_id"]:
        labels.append("Recomandat pentru BEFORE")
    if after_candidate and after_candidate["ee_id"] == scene["ee_id"]:
        labels.append("Recomandat pentru AFTER")
    return labels


def _scene_from_feature(feature: dict[str, Any], polarization: str) -> Sentinel1Scene | None:
    props = feature.get("properties") or {}
    ee_id = feature.get("id") or props.get("system:id")
    timestamp = props.get("system:time_start")
    if not ee_id or timestamp is None:
        return None
    acquisition_time = _timestamp_to_iso(timestamp)
    coverage = round(float(props.get("aoi_coverage_percent") or 0), 1)
    warnings = []
    if coverage < 90:
        warnings.append("Acoperire incompleta a judetului.")
    return Sentinel1Scene(
        ee_id=ee_id,
        display_id=ee_id.split("/")[-1],
        acquisition_time=acquisition_time,
        platform=props.get("platform_number") or props.get("SPACECRAFT_NAME") or "Sentinel-1",
        polarization=polarization,
        orbit_pass=props.get("orbitProperties_pass") or "necunoscut",
        relative_orbit=_safe_int(props.get("relativeOrbitNumber_start")),
        instrument_mode=props.get("instrumentMode") or "necunoscut",
        resolution_meters=_safe_float(props.get("resolution_meters") or props.get("resolution")),
        coverage_percent=coverage,
        warnings=warnings,
    )


def _timestamp_to_iso(timestamp_ms: int | float) -> str:
    return datetime.fromtimestamp(int(timestamp_ms) / 1000, tz=UTC).replace(microsecond=0).isoformat()


def _safe_int(value: Any) -> int | None:
    try:
        return int(value)
    except Exception:
        return None


def _safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except Exception:
        return None


def _soft_compatible(before: dict[str, Any], after: dict[str, Any]) -> bool:
    return (
        before.get("polarization") == after.get("polarization")
        and before.get("instrument_mode") == after.get("instrument_mode")
        and before.get("orbit_pass") == after.get("orbit_pass")
    )


def _best_before(scenes: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not scenes:
        return None
    midpoint = len(scenes) // 2
    candidates = scenes[:midpoint] or scenes[:1]
    return max(candidates, key=_recommendation_score)


def _best_after(scenes: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not scenes:
        return None
    midpoint = len(scenes) // 2
    candidates = scenes[midpoint:] or scenes[-1:]
    return max(candidates, key=_recommendation_score)


def _recommendation_score(scene: dict[str, Any]) -> tuple[float, int]:
    coverage = float(scene.get("coverage_percent") or 0)
    relative_orbit = int(scene.get("relative_orbit") or 0)
    return coverage, relative_orbit
