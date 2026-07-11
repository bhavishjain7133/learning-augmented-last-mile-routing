from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from .types import Route


@dataclass(frozen=True)
class RouteSplit:
    train: tuple[Route, ...]
    validation: tuple[Route, ...]
    test: tuple[Route, ...]

    def validate(self) -> None:
        train_ids = {route.route_id for route in self.train}
        validation_ids = {route.route_id for route in self.validation}
        test_ids = {route.route_id for route in self.test}
        if train_ids & validation_ids or train_ids & test_ids or validation_ids & test_ids:
            raise ValueError("Route splits overlap")


def chronological_station_split(
    routes: list[Route] | tuple[Route, ...],
    train_fraction: float = 0.70,
    validation_fraction: float = 0.15,
) -> RouteSplit:
    if not 0 < train_fraction < 1:
        raise ValueError("train_fraction must lie in (0, 1)")
    if not 0 <= validation_fraction < 1:
        raise ValueError("validation_fraction must lie in [0, 1)")
    if train_fraction + validation_fraction >= 1:
        raise ValueError("Train and validation fractions must sum to less than one")

    by_station: dict[str, list[Route]] = defaultdict(list)
    for route in routes:
        by_station[route.station_code].append(route)
    train: list[Route] = []
    validation: list[Route] = []
    test: list[Route] = []
    for station_routes in by_station.values():
        ordered = sorted(station_routes, key=lambda route: (route.route_date, route.route_id))
        count = len(ordered)
        if count < 3:
            train.extend(ordered)
            continue
        train_end = max(1, int(count * train_fraction))
        validation_end = max(train_end + 1, int(count * (train_fraction + validation_fraction)))
        validation_end = min(validation_end, count - 1)
        train.extend(ordered[:train_end])
        validation.extend(ordered[train_end:validation_end])
        test.extend(ordered[validation_end:])
    split = RouteSplit(tuple(train), tuple(validation), tuple(test))
    split.validate()
    return split

