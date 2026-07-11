from __future__ import annotations

from math import atan2
from typing import Mapping, Sequence

from .geometry import build_haversine_matrix
from .metrics import route_cost
from .types import Route

DistanceMatrix = Mapping[str, Mapping[str, float]]


def nearest_neighbor_route(route: Route, matrix: DistanceMatrix | None = None) -> tuple[str, ...]:
    matrix = matrix or build_haversine_matrix(route.stops)
    current = route.station_stop_id
    unvisited = set(route.stops) - {current}
    sequence = [current]
    while unvisited:
        next_stop = min(unvisited, key=lambda stop_id: (matrix[current][stop_id], stop_id))
        sequence.append(next_stop)
        unvisited.remove(next_stop)
        current = next_stop
    result = tuple(sequence)
    route.validate_sequence(result)
    return result


def angular_zone_route(route: Route, matrix: DistanceMatrix | None = None) -> tuple[str, ...]:
    """Order zones by polar angle around the station, then use NN within each zone."""
    matrix = matrix or build_haversine_matrix(route.stops)
    station_id = route.station_stop_id
    station = route.stops[station_id]
    zone_to_stops: dict[str, list[str]] = {}
    for stop_id, stop in route.stops.items():
        if stop_id == station_id:
            continue
        zone = stop.zone_id or f"__MISSING__:{stop_id}"
        zone_to_stops.setdefault(zone, []).append(stop_id)

    def zone_angle(zone: str) -> tuple[float, str]:
        members = zone_to_stops[zone]
        mean_latitude = sum(route.stops[item].latitude for item in members) / len(members)
        mean_longitude = sum(route.stops[item].longitude for item in members) / len(members)
        return (atan2(mean_latitude - station.latitude, mean_longitude - station.longitude), zone)

    sequence = [station_id]
    current = station_id
    for zone in sorted(zone_to_stops, key=zone_angle):
        unvisited = set(zone_to_stops[zone])
        while unvisited:
            next_stop = min(unvisited, key=lambda stop_id: (matrix[current][stop_id], stop_id))
            sequence.append(next_stop)
            unvisited.remove(next_stop)
            current = next_stop
    result = tuple(sequence)
    route.validate_sequence(result)
    return result


def two_opt(
    route: Route,
    initial_sequence: Sequence[str],
    matrix: DistanceMatrix | None = None,
    max_passes: int = 50,
) -> tuple[str, ...]:
    """Deterministic open-path 2-opt with the station fixed at position zero."""
    matrix = matrix or build_haversine_matrix(route.stops)
    best = list(initial_sequence)
    route.validate_sequence(best)
    best_cost = route_cost(best, matrix)
    for _ in range(max_passes):
        improved = False
        for first in range(1, len(best) - 1):
            for second in range(first + 1, len(best)):
                candidate = best[:first] + list(reversed(best[first : second + 1])) + best[second + 1 :]
                candidate_cost = route_cost(candidate, matrix)
                if candidate_cost + 1e-12 < best_cost:
                    best = candidate
                    best_cost = candidate_cost
                    improved = True
        if not improved:
            break
    result = tuple(best)
    route.validate_sequence(result)
    return result

