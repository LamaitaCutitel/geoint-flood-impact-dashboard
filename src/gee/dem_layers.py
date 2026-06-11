from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class DemProducts:
    dem: Any
    hillshade: Any
    slope: Any


def build_dem_products(ee: Any, aoi: Any) -> DemProducts:
    dem = ee.Image("USGS/SRTMGL1_003").clip(aoi)
    terrain = ee.Algorithms.Terrain(dem)
    return DemProducts(
        dem=dem.rename("dem").clip(aoi),
        hillshade=terrain.select("hillshade").rename("hillshade").clip(aoi),
        slope=terrain.select("slope").rename("slope").clip(aoi),
    )
