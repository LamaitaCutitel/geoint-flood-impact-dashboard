from __future__ import annotations

from dataclasses import dataclass

from config.settings import (
    GEE_DYNAMIC_WORLD_COLLECTION,
    GEE_PERMANENT_WATER_COLLECTION,
    GEE_S1_COLLECTION,
    GEE_SENTINEL2_COLLECTION,
)


@dataclass(frozen=True)
class GeeCollections:
    sentinel1: str = GEE_S1_COLLECTION
    permanent_water: str = GEE_PERMANENT_WATER_COLLECTION
    dynamic_world: str = GEE_DYNAMIC_WORLD_COLLECTION
    sentinel2: str = GEE_SENTINEL2_COLLECTION


COLLECTIONS = GeeCollections()
