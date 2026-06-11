from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from math import cos, radians
from typing import Any


LARGE_AOI_RATIO = 0.75


@dataclass(frozen=True)
class AreaMetadata:
    geometry: dict[str, Any]
    bbox: list[float]
    centroid: list[float]
    area_km2: float
    area_hash: str
    warnings: list[str]


@dataclass(frozen=True)
class AoiValidation:
    valid: bool
    geometry: dict[str, Any] | None
    warnings: list[str]
    errors: list[str]


def geometry_from_drawing(drawing: dict[str, Any] | None) -> dict[str, Any] | None:
    if not drawing:
        return None
    if drawing.get("type") == "Feature":
        return drawing.get("geometry")
    if drawing.get("type") in {"Polygon", "MultiPolygon"}:
        return drawing
    geometry = drawing.get("geometry")
    return geometry if isinstance(geometry, dict) else None


def validate_aoi(
    geometry: dict[str, Any] | None,
    county_geometry: dict[str, Any] | None,
) -> AoiValidation:
    if not geometry:
        return AoiValidation(False, None, [], ["AOI-ul este gol."])
    if geometry.get("type") not in {"Polygon", "MultiPolygon"}:
        return AoiValidation(False, None, [], ["AOI-ul trebuie să fie un poligon."])

    rings = _outer_rings(geometry)
    if not rings or any(len(ring) < 4 for ring in rings):
        return AoiValidation(False, None, [], ["Geometria AOI nu conține un poligon valid."])
    if any(ring[0] != ring[-1] for ring in rings):
        return AoiValidation(False, None, [], ["Conturul AOI nu este închis."])
    if area_km2(geometry) <= 0:
        return AoiValidation(False, None, [], ["Suprafața AOI este nulă."])

    warnings: list[str] = []
    if county_geometry:
        inside_flags = [
            _point_in_geometry((float(point[0]), float(point[1])), county_geometry)
            for ring in rings
            for point in ring[:-1]
        ]
        if not any(inside_flags):
            return AoiValidation(
                False,
                None,
                [],
                ["AOI-ul nu intersectează județul selectat."],
            )
        if not all(inside_flags):
            clipped = _intersection_with_shapely(geometry, county_geometry)
            if clipped:
                geometry = clipped
                warnings.append(
                    "AOI-ul depășea limita județului și a fost decupat la intersecția controlată."
                )
            else:
                return AoiValidation(
                    False,
                    None,
                    [],
                    [
                        "AOI-ul depășește limita județului. Desenează poligonul în interiorul județului."
                    ],
                )

        county_area = area_km2(county_geometry)
        if county_area and area_km2(geometry) / county_area >= LARGE_AOI_RATIO:
            warnings.append(
                "AOI-ul acoperă o mare parte din județ; analiza poate necesita mai mult timp."
            )
    return AoiValidation(True, geometry, warnings, [])


def area_metadata(
    geometry: dict[str, Any],
    warnings: list[str] | None = None,
) -> AreaMetadata:
    return AreaMetadata(
        geometry=geometry,
        bbox=geometry_bbox(geometry),
        centroid=[round(value, 8) for value in geometry_centroid(geometry)],
        area_km2=round(area_km2(geometry), 4),
        area_hash=geometry_hash(geometry),
        warnings=list(warnings or []),
    )


def geometry_bbox(geometry: dict[str, Any]) -> list[float]:
    points = _all_points(geometry)
    if not points:
        return []
    xs = [point[0] for point in points]
    ys = [point[1] for point in points]
    return [min(xs), min(ys), max(xs), max(ys)]


def geometry_centroid(geometry: dict[str, Any]) -> list[float]:
    rings = _outer_rings(geometry)
    if not rings:
        return []
    weighted_x = 0.0
    weighted_y = 0.0
    total_area = 0.0
    for ring in rings:
        centroid_x, centroid_y, signed_area = _ring_centroid(ring)
        weight = abs(signed_area)
        weighted_x += centroid_x * weight
        weighted_y += centroid_y * weight
        total_area += weight
    if not total_area:
        points = _all_points(geometry)
        return [
            sum(point[0] for point in points) / len(points),
            sum(point[1] for point in points) / len(points),
        ]
    return [weighted_x / total_area, weighted_y / total_area]


def area_km2(geometry: dict[str, Any]) -> float:
    rings = _outer_rings(geometry)
    if not rings:
        return 0.0
    center_lat = geometry_centroid(geometry)[1]
    meters_per_degree_lat = 111_320.0
    meters_per_degree_lon = 111_320.0 * cos(radians(center_lat))
    total_square_meters = 0.0
    for ring in rings:
        projected = [
            (float(point[0]) * meters_per_degree_lon, float(point[1]) * meters_per_degree_lat)
            for point in ring
        ]
        total_square_meters += abs(_signed_ring_area(projected))
    return total_square_meters / 1_000_000.0


def geometry_hash(geometry: dict[str, Any]) -> str:
    serialized = json.dumps(geometry, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]


def _intersection_with_shapely(
    geometry: dict[str, Any],
    county_geometry: dict[str, Any],
) -> dict[str, Any] | None:
    try:
        from shapely.geometry import mapping, shape

        intersection = shape(geometry).intersection(shape(county_geometry))
        if intersection.is_empty or intersection.geom_type not in {"Polygon", "MultiPolygon"}:
            return None
        return mapping(intersection)
    except (ImportError, ValueError, TypeError):
        return None


def _outer_rings(geometry: dict[str, Any]) -> list[list[list[float]]]:
    coordinates = geometry.get("coordinates") or []
    if geometry.get("type") == "Polygon":
        return [coordinates[0]] if coordinates else []
    if geometry.get("type") == "MultiPolygon":
        return [polygon[0] for polygon in coordinates if polygon]
    return []


def _all_points(geometry: dict[str, Any]) -> list[tuple[float, float]]:
    return [
        (float(point[0]), float(point[1]))
        for ring in _outer_rings(geometry)
        for point in ring
        if len(point) >= 2
    ]


def _signed_ring_area(points: list[tuple[float, float]]) -> float:
    return 0.5 * sum(
        start[0] * end[1] - end[0] * start[1]
        for start, end in zip(points, points[1:])
    )


def _ring_centroid(ring: list[list[float]]) -> tuple[float, float, float]:
    signed_area = _signed_ring_area([(float(point[0]), float(point[1])) for point in ring])
    if not signed_area:
        points = ring[:-1] or ring
        return (
            sum(float(point[0]) for point in points) / len(points),
            sum(float(point[1]) for point in points) / len(points),
            0.0,
        )
    factor = 1 / (6 * signed_area)
    centroid_x = factor * sum(
        (float(start[0]) + float(end[0]))
        * (float(start[0]) * float(end[1]) - float(end[0]) * float(start[1]))
        for start, end in zip(ring, ring[1:])
    )
    centroid_y = factor * sum(
        (float(start[1]) + float(end[1]))
        * (float(start[0]) * float(end[1]) - float(end[0]) * float(start[1]))
        for start, end in zip(ring, ring[1:])
    )
    return centroid_x, centroid_y, signed_area


def _point_in_geometry(point: tuple[float, float], geometry: dict[str, Any]) -> bool:
    return any(_point_in_ring(point, ring) for ring in _outer_rings(geometry))


def _point_in_ring(point: tuple[float, float], ring: list[list[float]]) -> bool:
    x, y = point
    inside = False
    previous_x, previous_y = float(ring[-1][0]), float(ring[-1][1])
    for raw_current in ring:
        current_x, current_y = float(raw_current[0]), float(raw_current[1])
        if _point_on_segment(point, (previous_x, previous_y), (current_x, current_y)):
            return True
        if (current_y > y) != (previous_y > y):
            intersection_x = (
                (previous_x - current_x) * (y - current_y) / (previous_y - current_y)
                + current_x
            )
            if x <= intersection_x:
                inside = not inside
        previous_x, previous_y = current_x, current_y
    return inside


def _point_on_segment(
    point: tuple[float, float],
    start: tuple[float, float],
    end: tuple[float, float],
    tolerance: float = 1e-10,
) -> bool:
    x, y = point
    x1, y1 = start
    x2, y2 = end
    cross = (x - x1) * (y2 - y1) - (y - y1) * (x2 - x1)
    if abs(cross) > tolerance:
        return False
    return (
        min(x1, x2) - tolerance <= x <= max(x1, x2) + tolerance
        and min(y1, y2) - tolerance <= y <= max(y1, y2) + tolerance
    )
