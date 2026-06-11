from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from src.gee.gee_tile_layers import ee_tile_url
from src.gee.sar_water_masks import sar_water_mask
from src.gee.sentinel1_scene_explorer import selected_scene_image, validate_scene_pair
from src.impact_tool.cache import PersistentCache, scene_cache_key


@dataclass(frozen=True)
class SceneSearchResult:
    scenes: list[dict[str, Any]]
    warnings: list[str]
    errors: list[str]
    from_cache: bool = False


def search_scenes(
    *,
    cache: PersistentCache,
    aoi_hash: str,
    start_date: str,
    end_date: str,
    polarization: str,
    orbit_pass: str,
    searcher: Callable[..., dict[str, Any]],
    search_args: tuple[Any, ...] = (),
) -> SceneSearchResult:
    key = scene_cache_key(
        cache,
        aoi_hash,
        (start_date, end_date),
        polarization,
        orbit_pass,
    )
    cached = cache.get("scenes", key)
    if cached.hit:
        payload = cached.value or {}
        return SceneSearchResult(
            scenes=payload.get("scenes", []),
            warnings=payload.get("warnings", []),
            errors=_error_messages(payload.get("errors", [])),
            from_cache=True,
        )
    payload = searcher(
        *search_args,
        start_date,
        end_date,
        polarization,
        orbit_pass,
    )
    cache.set("scenes", key, payload)
    return SceneSearchResult(
        scenes=payload.get("scenes", []),
        warnings=payload.get("warnings", []),
        errors=_error_messages(payload.get("errors", [])),
    )


def scene_label(scene: dict[str, Any]) -> str:
    acquired = str(scene.get("acquisition_time", "")).replace("T", " ")[:16]
    return (
        f"{acquired} · {scene.get('orbit_pass', '?')} · "
        f"orbita {scene.get('relative_orbit', '?')} · "
        f"{float(scene.get('coverage_percent') or 0):.1f}%"
    )


def select_scene_pair(
    scenes: list[dict[str, Any]],
    before_id: str,
    after_id: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    by_id = {scene.get("ee_id"): scene for scene in scenes}
    return by_id.get(before_id), by_id.get(after_id)


def confirm_scene_pair(
    before: dict[str, Any] | None,
    after: dict[str, Any] | None,
    warnings_accepted: bool = False,
) -> dict[str, Any]:
    validation = validate_scene_pair(before, after)
    confirmed = validation["compatible"] and (
        not validation["requires_confirmation"] or warnings_accepted
    )
    return {**validation, "confirmed": confirmed}


def preview_tiles_for_pair(
    ee: Any,
    aoi: Any,
    before: dict[str, Any],
    after: dict[str, Any],
    mode: str,
    threshold: float = -18.0,
) -> dict[str, str]:
    before_image = selected_scene_image(ee, before, aoi)
    after_image = selected_scene_image(ee, after, aoi)
    if mode == "Doar apă observată prin SAR":
        before_image = sar_water_mask(before_image, threshold, aoi, 0)
        after_image = sar_water_mask(after_image, threshold, aoi, 0)
        before_name = "SAR water BEFORE"
        after_name = "SAR water AFTER"
    else:
        before_name = "Sentinel-1 SAR before"
        after_name = "Sentinel-1 SAR after"
    return {
        "before": ee_tile_url(before_image, before_name) or "",
        "after": ee_tile_url(after_image, after_name) or "",
    }


def _error_messages(errors: list[Any]) -> list[str]:
    messages = []
    for error in errors:
        if isinstance(error, dict):
            messages.append(str(error.get("message") or error.get("code") or error))
        else:
            messages.append(str(error))
    return messages
