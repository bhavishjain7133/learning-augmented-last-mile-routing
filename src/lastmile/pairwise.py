from __future__ import annotations

from collections import Counter, defaultdict
from statistics import median
from typing import Iterable, Mapping

from .geometry import build_haversine_matrix
from .model import MISSING_ZONE, parent_zone
from .types import Route


def compress_route_zones(route: Route) -> tuple[str, ...]:
    if route.actual_sequence is None:
        raise ValueError("Observed sequence is required to learn zone preferences")
    zones: list[str] = []
    for stop_id in route.actual_sequence[1:]:
        zone = route.stops[stop_id].zone_id or MISSING_ZONE
        if not zones or zone != zones[-1]:
            zones.append(zone)
    return tuple(zones)


class PairwiseZonePreferenceModel:
    """Hierarchical pairwise zone-order model with neutral unseen-pair fallback."""

    def __init__(self, smoothing: float = 1.0, minimum_support: int = 3) -> None:
        if smoothing <= 0:
            raise ValueError("smoothing must be positive")
        if minimum_support < 1:
            raise ValueError("minimum_support must be at least one")
        self.smoothing = smoothing
        self.minimum_support = minimum_support
        self._exact: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
        self._parent: dict[str, Counter[tuple[str, str]]] = defaultdict(Counter)
        self._global_parent: Counter[tuple[str, str]] = Counter()

    def fit(self, routes: Iterable[Route]) -> "PairwiseZonePreferenceModel":
        observed_routes = 0
        for route in routes:
            if route.actual_sequence is None:
                continue
            zones = compress_route_zones(route)
            observed_routes += 1
            for first_index, first_zone in enumerate(zones):
                for second_zone in zones[first_index + 1 :]:
                    if first_zone == second_zone:
                        continue
                    self._exact[route.station_code][(first_zone, second_zone)] += 1
                    first_parent = parent_zone(first_zone)
                    second_parent = parent_zone(second_zone)
                    if first_parent != second_parent:
                        self._parent[route.station_code][(first_parent, second_parent)] += 1
                        self._global_parent[(first_parent, second_parent)] += 1
        if observed_routes == 0:
            raise ValueError("No observed sequences were available for fitting")
        return self

    def _smoothed_probability(
        self, counter: Counter[tuple[str, str]], first: str, second: str
    ) -> tuple[float, int]:
        wins = counter[(first, second)]
        losses = counter[(second, first)]
        support = wins + losses
        probability = (wins + self.smoothing) / (support + 2 * self.smoothing)
        return probability, support

    def probability_before(
        self, station_code: str, first_zone: str, second_zone: str
    ) -> tuple[float, str, int]:
        if first_zone == second_zone:
            return 0.5, "same_zone", 0

        probability, support = self._smoothed_probability(
            self._exact[station_code], first_zone, second_zone
        )
        if support >= self.minimum_support:
            return probability, "station_exact", support

        first_parent = parent_zone(first_zone)
        second_parent = parent_zone(second_zone)
        if first_parent != second_parent:
            probability, support = self._smoothed_probability(
                self._parent[station_code], first_parent, second_parent
            )
            if support >= self.minimum_support:
                return probability, "station_parent", support

            probability, support = self._smoothed_probability(
                self._global_parent, first_parent, second_parent
            )
            if support >= self.minimum_support:
                return probability, "global_parent", support

        return 0.5, "neutral", 0


def pairwise_preference_zone_route(
    route: Route,
    model: PairwiseZonePreferenceModel,
    preference_weight: float,
    matrix: Mapping[str, Mapping[str, float]] | None = None,
) -> tuple[str, ...]:
    """Order zones using pairwise Borda preference blended with nearest travel."""
    if preference_weight < 0:
        raise ValueError("preference_weight must be non-negative")
    matrix = matrix or build_haversine_matrix(route.stops)
    station_id = route.station_stop_id
    zone_to_stops: dict[str, set[str]] = defaultdict(set)
    for stop_id, stop in route.stops.items():
        if stop_id != station_id:
            zone_to_stops[stop.zone_id or MISSING_ZONE].add(stop_id)

    sequence = [station_id]
    current = station_id
    remaining_zones = set(zone_to_stops)
    while remaining_zones:
        nearest_by_zone = {
            zone: min(float(matrix[current][stop_id]) for stop_id in zone_to_stops[zone])
            for zone in remaining_zones
        }
        distance_scale = median(nearest_by_zone.values()) or 1.0

        def zone_score(zone: str) -> tuple[float, str]:
            others = remaining_zones - {zone}
            if others:
                preference_strength = sum(
                    model.probability_before(route.station_code, zone, other)[0]
                    for other in others
                ) / len(others)
            else:
                preference_strength = 1.0
            travel_component = nearest_by_zone[zone] / distance_scale
            preference_penalty = 1.0 - preference_strength
            return travel_component + preference_weight * preference_penalty, zone

        selected_zone = min(remaining_zones, key=zone_score)
        unvisited = set(zone_to_stops[selected_zone])
        while unvisited:
            next_stop = min(unvisited, key=lambda stop_id: (matrix[current][stop_id], stop_id))
            sequence.append(next_stop)
            unvisited.remove(next_stop)
            current = next_stop
        remaining_zones.remove(selected_zone)

    result = tuple(sequence)
    route.validate_sequence(result)
    return result

