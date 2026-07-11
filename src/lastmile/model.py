from __future__ import annotations

from collections import Counter, defaultdict
from math import log
from statistics import median
from typing import Iterable, Mapping

from .geometry import build_haversine_matrix
from .types import Route

START_ZONE = "__START__"
MISSING_ZONE = "__MISSING__"


def parent_zone(zone_id: str | None) -> str:
    return MISSING_ZONE if not zone_id else zone_id.split("-")[0]


class ZoneTransitionModel:
    """Smoothed station-conditioned Markov model over zone transitions."""

    def __init__(self, smoothing: float = 1.0, use_parent_zones: bool = False) -> None:
        if smoothing <= 0:
            raise ValueError("smoothing must be positive")
        self.smoothing = smoothing
        self.use_parent_zones = use_parent_zones
        self._counts: dict[tuple[str, str], Counter[str]] = defaultdict(Counter)
        self._global_counts: dict[str, Counter[str]] = defaultdict(Counter)
        self._vocabulary: set[str] = set()

    def zone_token(self, zone_id: str | None) -> str:
        return parent_zone(zone_id) if self.use_parent_zones else (zone_id or MISSING_ZONE)

    def fit(self, routes: Iterable[Route]) -> "ZoneTransitionModel":
        for route in routes:
            if route.actual_sequence is None:
                continue
            previous = START_ZONE
            previous_stop_zone: str | None = None
            for stop_id in route.actual_sequence[1:]:
                zone = self.zone_token(route.stops[stop_id].zone_id)
                if zone == previous_stop_zone:
                    continue
                self._counts[(route.station_code, previous)][zone] += 1
                self._global_counts[previous][zone] += 1
                self._vocabulary.add(zone)
                previous = zone
                previous_stop_zone = zone
        if not self._vocabulary:
            raise ValueError("No observed zone transitions were available for fitting")
        return self

    def probability(self, station_code: str, previous_zone: str, next_zone: str) -> float:
        station_counter = self._counts.get((station_code, previous_zone))
        counter = station_counter if station_counter else self._global_counts.get(previous_zone, Counter())
        vocabulary_size = len(self._vocabulary) + int(next_zone not in self._vocabulary)
        numerator = counter.get(next_zone, 0) + self.smoothing
        denominator = sum(counter.values()) + self.smoothing * vocabulary_size
        return numerator / denominator


def hybrid_greedy_route(
    route: Route,
    model: ZoneTransitionModel,
    preference_weight: float,
    matrix: Mapping[str, Mapping[str, float]] | None = None,
) -> tuple[str, ...]:
    """Construct a route using normalized edge cost plus learned zone surprise."""
    if preference_weight < 0:
        raise ValueError("preference_weight must be non-negative")
    matrix = matrix or build_haversine_matrix(route.stops)
    current = route.station_stop_id
    previous_zone = START_ZONE
    unvisited = set(route.stops) - {current}
    sequence = [current]
    while unvisited:
        candidate_distances = [float(matrix[current][candidate]) for candidate in unvisited]
        distance_scale = median(candidate_distances) or 1.0
        zone_penalties: dict[str, float] = {}

        def score(stop_id: str) -> tuple[float, str]:
            next_zone = model.zone_token(route.stops[stop_id].zone_id)
            travel_component = float(matrix[current][stop_id]) / distance_scale
            # The fitted model operates on *compressed* zone sequences. Remaining
            # within the current zone is therefore not a transition and must not
            # be assigned an unseen-transition penalty.
            if next_zone not in zone_penalties:
                zone_penalties[next_zone] = (
                    0.0
                    if next_zone == previous_zone
                    else -log(model.probability(route.station_code, previous_zone, next_zone))
                )
            preference_component = zone_penalties[next_zone]
            return travel_component + preference_weight * preference_component, stop_id

        next_stop = min(unvisited, key=score)
        next_zone = model.zone_token(route.stops[next_stop].zone_id)
        if next_zone != previous_zone:
            previous_zone = next_zone
        sequence.append(next_stop)
        unvisited.remove(next_stop)
        current = next_stop
    result = tuple(sequence)
    route.validate_sequence(result)
    return result


def hybrid_zone_route(
    route: Route,
    model: ZoneTransitionModel,
    preference_weight: float,
    matrix: Mapping[str, Mapping[str, float]] | None = None,
) -> tuple[str, ...]:
    """Choose a learned zone order, then exhaust each zone by nearest neighbour."""
    if preference_weight < 0:
        raise ValueError("preference_weight must be non-negative")
    matrix = matrix or build_haversine_matrix(route.stops)
    station_id = route.station_stop_id
    zone_to_stops: dict[str, set[str]] = defaultdict(set)
    for stop_id, stop in route.stops.items():
        if stop_id != station_id:
            zone_to_stops[model.zone_token(stop.zone_id)].add(stop_id)

    sequence = [station_id]
    current = station_id
    previous_zone = START_ZONE
    remaining_zones = set(zone_to_stops)
    while remaining_zones:
        nearest_by_zone = {
            zone: min(float(matrix[current][stop_id]) for stop_id in zone_to_stops[zone])
            for zone in remaining_zones
        }
        distance_scale = median(nearest_by_zone.values()) or 1.0

        def zone_score(zone: str) -> tuple[float, str]:
            travel_component = nearest_by_zone[zone] / distance_scale
            preference_component = -log(
                model.probability(route.station_code, previous_zone, zone)
            )
            return travel_component + preference_weight * preference_component, zone

        selected_zone = min(remaining_zones, key=zone_score)
        unvisited = set(zone_to_stops[selected_zone])
        while unvisited:
            next_stop = min(unvisited, key=lambda stop_id: (matrix[current][stop_id], stop_id))
            sequence.append(next_stop)
            unvisited.remove(next_stop)
            current = next_stop
        previous_zone = selected_zone
        remaining_zones.remove(selected_zone)

    result = tuple(sequence)
    route.validate_sequence(result)
    return result
