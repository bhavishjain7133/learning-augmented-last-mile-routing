from __future__ import annotations

from collections import Counter
from statistics import median
from typing import Iterable

from .splits import RouteSplit
from .types import Route


def profile_routes(routes: Iterable[Route], split: RouteSplit | None = None) -> dict[str, object]:
    route_list = list(routes)
    route_ids = [route.route_id for route in route_list]
    stop_counts = [len(route.stops) for route in route_list]
    profile: dict[str, object] = {
        "route_count": len(route_list),
        "duplicate_route_id_count": len(route_ids) - len(set(route_ids)),
        "station_count": len({route.station_code for route in route_list}),
        "date_min": min(route.route_date for route in route_list).isoformat(),
        "date_max": max(route.route_date for route in route_list).isoformat(),
        "observed_sequence_coverage": sum(
            route.actual_sequence is not None for route in route_list
        ) / len(route_list),
        "invalid_station_count": sum(
            sum(stop.is_station for stop in route.stops.values()) != 1 for route in route_list
        ),
        "sequence_stop_mismatch_count": sum(
            route.actual_sequence is not None and set(route.actual_sequence) != set(route.stops)
            for route in route_list
        ),
        "missing_dropoff_zone_count": sum(
            stop.zone_id is None
            for route in route_list
            for stop in route.stops.values()
            if not stop.is_station
        ),
        "route_score_counts": dict(sorted(Counter(route.route_score for route in route_list).items())),
        "station_route_counts": dict(
            sorted(Counter(route.station_code for route in route_list).items())
        ),
        "stops_per_route": {
            "minimum": min(stop_counts),
            "median": median(stop_counts),
            "maximum": max(stop_counts),
        },
    }
    if split is not None:
        profile["split_route_counts"] = {
            "train": len(split.train),
            "validation": len(split.validation),
            "test": len(split.test),
        }
        profile["split_station_counts"] = {
            "train": len({route.station_code for route in split.train}),
            "validation": len({route.station_code for route in split.validation}),
            "test": len({route.station_code for route in split.test}),
        }
    return profile

