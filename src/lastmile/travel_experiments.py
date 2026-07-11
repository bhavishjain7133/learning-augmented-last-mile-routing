from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Iterable, Mapping, Sequence

import pandas as pd

from .baselines import angular_zone_route, nearest_neighbor_route
from .data import iter_travel_time_matrices
from .metrics import adjacent_edge_recall, normalized_pairwise_disagreement, route_cost, zone_reentries
from .official_score import official_route_score
from .pairwise import PairwiseZonePreferenceModel, pairwise_preference_zone_route
from .types import Route


@dataclass(frozen=True)
class TravelEvaluationRecord:
    route_id: str
    station_code: str
    route_date: str
    route_score: str | None
    stop_count: int
    method: str
    preference_weight: float | None
    travel_time_seconds: float
    pairwise_disagreement: float
    official_route_score: float
    adjacent_edge_recall: float
    zone_reentries: int
    runtime_ms: float


def _record(
    route: Route,
    method: str,
    sequence: Sequence[str],
    matrix: Mapping[str, Mapping[str, float]],
    elapsed_seconds: float,
    preference_weight: float | None = None,
) -> TravelEvaluationRecord:
    if route.actual_sequence is None:
        raise ValueError("Evaluation requires an observed sequence")
    return TravelEvaluationRecord(
        route_id=route.route_id,
        station_code=route.station_code,
        route_date=route.route_date.isoformat(),
        route_score=route.route_score,
        stop_count=len(route.stops),
        method=method,
        preference_weight=preference_weight,
        travel_time_seconds=route_cost(sequence, matrix),
        pairwise_disagreement=normalized_pairwise_disagreement(sequence, route.actual_sequence),
        official_route_score=official_route_score(route.actual_sequence, sequence, matrix),
        adjacent_edge_recall=adjacent_edge_recall(sequence, route.actual_sequence),
        zone_reentries=zone_reentries(route, sequence),
        runtime_ms=elapsed_seconds * 1000,
    )


def evaluate_travel_time_stream(
    routes: Iterable[Route],
    model: PairwiseZonePreferenceModel,
    preference_weights: Sequence[float],
    travel_times_path: str,
) -> pd.DataFrame:
    """Stream the monolithic matrix file and evaluate only requested routes."""
    route_lookup = {route.route_id: route for route in routes}
    records: list[TravelEvaluationRecord] = []
    found: set[str] = set()
    for route_id, matrix in iter_travel_time_matrices(travel_times_path):
        route = route_lookup.get(route_id)
        if route is None:
            continue
        if set(matrix) != set(route.stops):
            raise ValueError(f"Travel-time origin keys do not match route stops: {route_id}")
        if any(set(row) != set(route.stops) for row in matrix.values()):
            raise ValueError(f"Travel-time destination keys do not match route stops: {route_id}")
        found.add(route_id)

        actual = route.actual_sequence
        if actual is None:
            raise ValueError(f"Observed sequence missing for route {route_id}")
        records.append(_record(route, "observed_driver", actual, matrix, 0.0))

        start = perf_counter()
        nearest = nearest_neighbor_route(route, matrix)
        records.append(_record(route, "nearest_neighbor", nearest, matrix, perf_counter() - start))

        start = perf_counter()
        angular = angular_zone_route(route, matrix)
        records.append(_record(route, "angular_zone", angular, matrix, perf_counter() - start))

        for weight in preference_weights:
            start = perf_counter()
            pairwise = pairwise_preference_zone_route(route, model, weight, matrix)
            records.append(
                _record(
                    route,
                    "pairwise_zone",
                    pairwise,
                    matrix,
                    perf_counter() - start,
                    preference_weight=float(weight),
                )
            )
        if len(found) == len(route_lookup):
            break

    missing = set(route_lookup) - found
    if missing:
        raise KeyError(f"Travel-time matrices missing for {len(missing)} requested routes")
    return pd.DataFrame(asdict(record) for record in records)


def travel_validation_summary(
    results: pd.DataFrame, candidate_method: str = "pairwise_zone"
) -> pd.DataFrame:
    nearest = (
        results.loc[results["method"] == "nearest_neighbor", ["route_id", "travel_time_seconds"]]
        .rename(columns={"travel_time_seconds": "nearest_travel_time_seconds"})
        .set_index("route_id")
    )
    candidate = results.loc[results["method"] == candidate_method].copy()
    candidate = candidate.join(nearest, on="route_id", validate="many_to_one")
    candidate["travel_time_increase_fraction"] = (
        candidate["travel_time_seconds"] / candidate["nearest_travel_time_seconds"] - 1
    )
    return (
        candidate.groupby("preference_weight", as_index=False)
        .agg(
            routes=("route_id", "nunique"),
            median_pairwise_disagreement=("pairwise_disagreement", "median"),
            mean_pairwise_disagreement=("pairwise_disagreement", "mean"),
            median_travel_time_increase_fraction=("travel_time_increase_fraction", "median"),
            mean_travel_time_increase_fraction=("travel_time_increase_fraction", "mean"),
            median_edge_recall=("adjacent_edge_recall", "median"),
            median_zone_reentries=("zone_reentries", "median"),
            median_runtime_ms=("runtime_ms", "median"),
        )
        .sort_values("preference_weight")
        .reset_index(drop=True)
    )


def select_travel_preference_weight(
    summary: pd.DataFrame, median_travel_time_tolerance: float = 0.05
) -> float:
    eligible = summary.loc[
        summary["median_travel_time_increase_fraction"] <= median_travel_time_tolerance
    ].copy()
    if eligible.empty:
        return 0.0
    selected = eligible.sort_values(
        [
            "median_pairwise_disagreement",
            "median_travel_time_increase_fraction",
            "preference_weight",
        ]
    ).iloc[0]
    return float(selected["preference_weight"])




