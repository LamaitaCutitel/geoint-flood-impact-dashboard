import json

from src.app.ems_validation import geojson_area_km2, validation_metrics


def test_validation_metrics_compute_iou_precision_recall_and_f1():
    metrics = validation_metrics(sar_area_km2=10, ems_area_km2=8, intersection_km2=5)

    assert metrics["intersection_km2"] == 5
    assert metrics["union_km2"] == 13
    assert metrics["iou"] == round(5 / 13, 4)
    assert metrics["precision"] == 0.5
    assert metrics["recall"] == 0.625
    assert metrics["f1"] == 0.5556
    assert metrics["false_positive_area_km2"] == 5
    assert metrics["false_negative_area_km2"] == 3


def test_validation_metrics_clamps_intersection_to_available_areas():
    metrics = validation_metrics(sar_area_km2=3, ems_area_km2=2, intersection_km2=5)

    assert metrics["intersection_km2"] == 2
    assert metrics["false_negative_area_km2"] == 0


def test_geojson_area_km2_reads_polygon():
    geojson = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {},
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [
                        [
                            [27.0, 45.0],
                            [27.01, 45.0],
                            [27.01, 45.01],
                            [27.0, 45.01],
                            [27.0, 45.0],
                        ]
                    ],
                },
            }
        ],
    }

    assert geojson_area_km2(json.dumps(geojson)) > 0
