from __future__ import annotations

from src.app.county_boundaries import (
    county_geometry,
    feature_bbox,
    load_or_download_counties,
    selected_county_feature,
)
from src.impact_tool.cache import PersistentCache
from src.impact_tool.osm import load_osm_categories


def main() -> None:
    boundary_result = load_or_download_counties()
    feature = selected_county_feature(boundary_result.geojson, "Galati")
    if not feature:
        raise RuntimeError("Limita judetului Galati nu este disponibila.")
    result = load_osm_categories(
        analysis_complete=True,
        aoi_hash="galati-county-prewarm",
        bbox=feature_bbox(feature),
        geometry=county_geometry(feature),
        cache=PersistentCache(),
    )
    for category, status in result["status"].items():
        print(
            f"{category}: {status.get('count', 0)} elemente, "
            f"{status.get('source', 'necunoscut')}, {status.get('completeness', '')}"
        )


if __name__ == "__main__":
    main()
