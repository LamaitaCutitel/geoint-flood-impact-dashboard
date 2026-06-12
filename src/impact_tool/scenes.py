from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib.request import urlopen

from src.gee.gee_tile_layers import ee_tile_url
from src.gee.sar_water_masks import sar_water_mask
from src.gee.sentinel1_scene_explorer import selected_scene_image, validate_scene_pair
from src.impact_tool.cache import PersistentCache, scene_cache_key


THUMBNAIL_TTL_SECONDS = 7 * 24 * 60 * 60
THUMBNAIL_BATCH_SIZE = 8


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


def scene_thumbnail_url(
    *,
    cache: PersistentCache,
    ee: Any,
    aoi: Any,
    aoi_hash: str,
    scene: dict[str, Any],
    dimensions: int = 320,
) -> tuple[str, bool]:
    key = cache.key(
        "thumbnails",
        aoi_hash,
        scene.get("ee_id"),
        scene.get("polarization"),
        dimensions,
    )
    cached = cache.get("thumbnails", key, ttl_seconds=THUMBNAIL_TTL_SECONDS)
    cached_path = (
        Path(cached.value.get("path", ""))
        if cached.hit and isinstance(cached.value, dict)
        else None
    )
    if cached_path and cached_path.is_file():
        return str(cached_path), True
    image = selected_scene_image(ee, scene, aoi)
    url = image.getThumbURL(
        {
            "region": aoi,
            "dimensions": dimensions,
            "min": -25,
            "max": 0,
            "palette": ["111827", "f8fafc"],
            "format": "png",
        }
    )
    thumbnail_path = cache.root / "thumbnails" / f"{key}.png"
    thumbnail_path.parent.mkdir(parents=True, exist_ok=True)
    with urlopen(url, timeout=30) as response:
        thumbnail_path.write_bytes(response.read())
    cache.set(
        "thumbnails",
        key,
        {
            "path": str(thumbnail_path),
            "source_url": url,
            "scene_id": scene.get("ee_id"),
            "dimensions": dimensions,
        },
    )
    return str(thumbnail_path), False


def hydrate_scene_thumbnails(
    *,
    cache: PersistentCache,
    ee: Any,
    aoi: Any,
    aoi_hash: str,
    scenes: list[dict[str, Any]],
    max_thumbnails: int = THUMBNAIL_BATCH_SIZE,
) -> tuple[list[dict[str, Any]], int]:
    hydrated = []
    cache_hits = 0
    for index, scene in enumerate(scenes):
        item = dict(scene)
        if index >= max_thumbnails:
            item["thumbnail_url"] = item.get("thumbnail_url")
            hydrated.append(item)
            continue
        try:
            item["thumbnail_url"], hit = scene_thumbnail_url(
                cache=cache,
                ee=ee,
                aoi=aoi,
                aoi_hash=aoi_hash,
                scene=scene,
            )
            cache_hits += int(hit)
        except Exception as exc:
            item["thumbnail_url"] = None
            item.setdefault("warnings", []).append(
                f"Thumbnail indisponibil: {exc}"
            )
        hydrated.append(item)
    return hydrated, cache_hits


def timeline_entries(scenes: list[dict[str, Any]]) -> list[dict[str, str]]:
    return [
        {
            "scene_id": str(scene.get("ee_id", "")),
            "date": str(scene.get("acquisition_time", ""))[:10],
            "orbit_pass": str(scene.get("orbit_pass", "necunoscut")),
        }
        for scene in sorted(
            scenes,
            key=lambda item: str(item.get("acquisition_time", "")),
        )
    ]


def preview_tile_for_scene(ee: Any, aoi: Any, scene: dict[str, Any]) -> str:
    image = selected_scene_image(ee, scene, aoi)
    return ee_tile_url(image, "Sentinel-1 SAR before") or ""


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
    smoothing_meters: int = 0,
    minimum_connected_pixels: int = 8,
) -> dict[str, str]:
    before_image = selected_scene_image(
        ee,
        before,
        aoi,
        smoothing_radius=smoothing_meters,
    )
    after_image = selected_scene_image(
        ee,
        after,
        aoi,
        smoothing_radius=smoothing_meters,
    )
    if mode == "Doar apă observată prin SAR":
        before_image = sar_water_mask(
            before_image,
            threshold,
            aoi,
            minimum_connected_pixels,
        )
        after_image = sar_water_mask(
            after_image,
            threshold,
            aoi,
            minimum_connected_pixels,
        )
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
