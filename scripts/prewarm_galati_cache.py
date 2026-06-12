from __future__ import annotations

from pathlib import Path
import sys
from time import perf_counter


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.app.county_boundaries import (
    county_geometry,
    load_or_download_counties,
    selected_county_feature,
)
from src.impact_tool.cache import PersistentCache
from src.impact_tool.osm import inspect_osm_cache, load_osm_categories
from src.impact_tool.osm_impact import buffered_geometry


def main() -> None:
    started = perf_counter()
    boundary_result = load_or_download_counties()
    feature = selected_county_feature(boundary_result.geojson, "Galati")
    if not feature:
        raise RuntimeError("Limita judetului Galati nu este disponibila.")

    query_geometry, query_bbox = buffered_geometry(county_geometry(feature), 1000)
    cache = PersistentCache()
    print(f"cache_root={cache.root}")
    result = load_osm_categories(
        analysis_complete=True,
        aoi_hash="galati-county-plus-1000m",
        bbox=query_bbox,
        geometry=query_geometry,
        cache=cache,
        analysis_mode="detaliat",
    )
    rapid_critical = load_osm_categories(
        analysis_complete=True,
        aoi_hash="galati-county-plus-1000m",
        bbox=query_bbox,
        geometry=query_geometry,
        cache=cache,
        categories=("critical",),
        analysis_mode="rapid",
    )
    cache_status = inspect_osm_cache(cache, query_geometry)
    rapid_status = inspect_osm_cache(
        cache,
        query_geometry,
        categories=("critical",),
        analysis_mode="rapid",
    )
    failures = []
    for category, status in result["status"].items():
        metadata = cache_status.get(category, {})
        print(
            f"{category}: status={metadata.get('status', 'lipsa')}, "
            f"count={status.get('count', 0)}, "
            f"source={status.get('source', 'necunoscuta')}, "
            f"completeness={status.get('completeness', 'necunoscuta')}, "
            f"tile-uri={status.get('tile_count', 0)}, "
            f"duplicate={status.get('duplicate_count', 0)}, "
            f"relatii={status.get('relation_count', 0)}, "
            f"erori={status.get('errors') or status.get('error') or []}"
        )
        if (
            not status.get("ok")
            or status.get("completeness") != "complet"
            or metadata.get("status") != "valid"
        ):
            failures.append(category)
    rapid_metadata = rapid_status["critical"]
    rapid_result = rapid_critical["status"]["critical"]
    print(
        "critical_rapid: "
        f"status={rapid_metadata.get('status', 'lipsa')}, "
        f"count={rapid_result.get('count', 0)}, "
        f"source={rapid_result.get('source', 'necunoscuta')}, "
        f"completeness={rapid_result.get('completeness', 'necunoscuta')}, "
        f"tile-uri={rapid_result.get('tile_count', 0)}, "
        f"duplicate={rapid_result.get('duplicate_count', 0)}, "
        f"relatii={rapid_result.get('relation_count', 0)}, "
        f"erori={rapid_result.get('errors') or rapid_result.get('error') or []}"
    )
    if (
        not rapid_result.get("ok")
        or rapid_result.get("completeness") != "complet"
        or rapid_metadata.get("status") != "valid"
    ):
        failures.append("critical_rapid")
    if failures:
        raise RuntimeError(
            "Prewarm incomplet pentru categoriile: " + ", ".join(failures)
        )
    print(f"duration_seconds={perf_counter() - started:.3f}")


if __name__ == "__main__":
    main()
