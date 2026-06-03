from __future__ import annotations

import pandas as pd
import plotly.express as px

from config.settings import METHODOLOGICAL_NOTE


def render_metric_cards(st, metrics: dict[str, object]) -> None:
    labels = [
        ("AOI", metrics.get("aoi", "n/a")),
        ("before period", metrics.get("before_period", "n/a")),
        ("after period", metrics.get("after_period", "n/a")),
        ("scene count before", metrics.get("scene_count_before", 0)),
        ("scene count after", metrics.get("scene_count_after", 0)),
        ("SAR detected extent km2", metrics.get("sar_detected_extent_km2", 0.0)),
        ("permanent water removed km2", metrics.get("permanent_water_removed_km2", 0.0)),
        ("crops intersected km2", metrics.get("crops_intersected_km2", 0.0)),
        ("built-up intersected km2", metrics.get("built_up_intersected_km2", 0.0)),
        ("vegetation intersected km2", metrics.get("vegetation_intersected_km2", 0.0)),
        ("dominant land cover class", metrics.get("dominant_land_cover_class", "n/a")),
        ("processing time", metrics.get("processing_time", "n/a")),
    ]
    columns = st.columns(4)
    for index, (label, value) in enumerate(labels):
        columns[index % 4].metric(label, value)


def render_land_cover(st, land_cover_stats: dict[str, float]) -> None:
    df = pd.DataFrame(
        [{"class": name, "area_km2": area} for name, area in land_cover_stats.items()]
    )
    st.subheader("Terenuri intersectate de extinderea preliminara detectata")
    st.dataframe(df, use_container_width=True, hide_index=True)
    if not df.empty:
        fig = px.bar(df, x="class", y="area_km2", color="class")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="km2")
        st.plotly_chart(fig, use_container_width=True)


def render_methodological_note(st) -> None:
    st.warning(METHODOLOGICAL_NOTE)
