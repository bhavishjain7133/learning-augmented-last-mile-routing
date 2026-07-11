from __future__ import annotations

from dataclasses import asdict, dataclass
from time import perf_counter
from typing import Iterable, Sequence

import pandas as pd

from .baselines import angular_zone_route, nearest_neighbor_route
from .geometry import build_haversine_matrix
from .metrics import adjacent_edge_recall, normalized_pairwise_disagreement, route_cost, zone_reentries
from .model import ZoneTransitionModel, hybrid_zone_route
from .pairwise import PairwiseZonePreferenceModel, pairwise_preference_zone_route
from .types import Route


@dataclass(frozen=True)
class EvaluationRecord:
    route_id: str
    station_code: str
    route_date: str
    route_score: str | None
    stop_count: int
    method: str
    preference_weight: float | None
    geodesic_cost_km: float
    pairwise_disagreement: float
    adjacent_edge_recall: float
    zone_reentries: int
    runtime_ms: float


def _record(
    route: Route,
    method: str,
    sequence: Sequence[str],
    matrix: dict[str, dict[str, float]],
    elapsed_seconds: float,
    preference_weight: float | None = None,
) -> EvaluationRecord:
    if route.actual_sequence is None:
        raise ValueError("Evaluation requires an observed sequence")
    return EvaluationRecord(
        route_id=route.route_id,
        station_code=route.station_code,
        route_date=route.route_date.isoformat(),
        route_score=route.route_score,
        stop_count=len(route.stops),
        method=method,
        preference_weight=preference_weight,
        geodesic_cost_km=route_cost(sequence, matrix),
        pairwise_disagreement=normalized_pairwise_disagreement(sequence, route.actual_sequence),
        adjacent_edge_recall=adjacent_edge_recall(sequence, route.actual_sequence),
        zone_reentries=zone_reentries(route, sequence),
        runtime_ms=elapsed_seconds * 1000,
    )


def evaluate_geodesic_screen(
    routes: Iterable[Route],
    model: ZoneTransitionModel,
    preference_weights: Sequence[float],
) -> pd.DataFrame:
    """Evaluate transparent geodesic baselines and hybrid weights route by route."""
    records: list[EvaluationRecord] = []
    for route in routes:
        matrix = build_haversine_matrix(route.stops)

        start = perf_counter()
        nearest = nearest_neighbor_route(route, matrix)
        records.append(_record(route, "nearest_neighbor", nearest, matrix, perf_counter() - start))

        start = perf_counter()
        angular = angular_zone_route(route, matrix)
        records.append(_record(route, "angular_zone", angular, matrix, perf_counter() - start))

        for weight in preference_weights:
            start = perf_counter()
            hybrid = hybrid_zone_route(route, model, weight, matrix)
            records.append(
                _record(
                    route,
                    "hybrid_zone",
                    hybrid,
                    matrix,
                    perf_counter() - start,
                    preference_weight=float(weight),
                )
            )
    return pd.DataFrame(asdict(record) for record in records)


def evaluate_pairwise_screen(
    routes: Iterable[Route],
    model: PairwiseZonePreferenceModel,
    preference_weights: Sequence[float],
) -> pd.DataFrame:
    """Evaluate baselines and hierarchical pairwise zone-ranking weights."""
    records: list[EvaluationRecord] = []
    for route in routes:
        matrix = build_haversine_matrix(route.stops)

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
    return pd.DataFrame(asdict(record) for record in records)


def validation_summary(
    results: pd.DataFrame, candidate_method: str = "hybrid_zone"
) -> pd.DataFrame:
    nearest = (
        results.loc[results["method"] == "nearest_neighbor", ["route_id", "geodesic_cost_km"]]
        .rename(columns={"geodesic_cost_km": "nearest_cost_km"})
        .set_index("route_id")
    )
    hybrid = results.loc[results["method"] == candidate_method].copy()
    hybrid = hybrid.join(nearest, on="route_id", validate="many_to_one")
    hybrid["cost_increase_fraction"] = (
        hybrid["geodesic_cost_km"] / hybrid["nearest_cost_km"] - 1
    )
    return (
        hybrid.groupby("preference_weight", as_index=False)
        .agg(
            routes=("route_id", "nunique"),
            median_pairwise_disagreement=("pairwise_disagreement", "median"),
            mean_pairwise_disagreement=("pairwise_disagreement", "mean"),
            median_cost_increase_fraction=("cost_increase_fraction", "median"),
            mean_cost_increase_fraction=("cost_increase_fraction", "mean"),
            median_edge_recall=("adjacent_edge_recall", "median"),
            median_zone_reentries=("zone_reentries", "median"),
            median_runtime_ms=("runtime_ms", "median"),
        )
        .sort_values("preference_weight")
        .reset_index(drop=True)
    )


def select_preference_weight(
    summary: pd.DataFrame, median_cost_tolerance: float = 0.05
) -> float:
    """Select on validation only: best disagreement under a fixed cost tolerance."""
    eligible = summary.loc[
        summary["median_cost_increase_fraction"] <= median_cost_tolerance
    ].copy()
    if eligible.empty:
        return 0.0
    selected = eligible.sort_values(
        ["median_pairwise_disagreement", "median_cost_increase_fraction", "preference_weight"]
    ).iloc[0]
    return float(selected["preference_weight"])
