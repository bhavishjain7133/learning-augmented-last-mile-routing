from __future__ import annotations

import argparse
import json

from .baselines import angular_zone_route, nearest_neighbor_route, two_opt
from .geometry import build_haversine_matrix
from .metrics import adjacent_edge_recall, normalized_pairwise_disagreement, route_cost, zone_reentries
from .model import ZoneTransitionModel, hybrid_greedy_route
from .synthetic import make_synthetic_route


def run_synthetic_demo() -> dict[str, dict[str, float | int]]:
    train_routes = [
        make_synthetic_route(route_id=f"train-{index}", day_offset=index) for index in range(5)
    ]
    test_route = make_synthetic_route(route_id="test", day_offset=10)
    matrix = build_haversine_matrix(test_route.stops)
    model = ZoneTransitionModel(smoothing=1.0).fit(train_routes)
    methods = {
        "nearest_neighbor": nearest_neighbor_route(test_route, matrix),
        "angular_zone": angular_zone_route(test_route, matrix),
    }
    methods["two_opt"] = two_opt(test_route, methods["nearest_neighbor"], matrix)
    methods["hybrid"] = hybrid_greedy_route(
        test_route, model, preference_weight=0.5, matrix=matrix
    )
    results: dict[str, dict[str, float | int]] = {}
    for name, sequence in methods.items():
        actual = test_route.actual_sequence or sequence
        results[name] = {
            "geodesic_cost_km": route_cost(sequence, matrix),
            "pairwise_disagreement": normalized_pairwise_disagreement(sequence, actual),
            "adjacent_edge_recall": adjacent_edge_recall(sequence, actual),
            "zone_reentries": zone_reentries(test_route, sequence),
        }
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("synthetic-demo", help="Run the deterministic end-to-end smoke test")
    args = parser.parse_args()
    if args.command == "synthetic-demo":
        print(json.dumps(run_synthetic_demo(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

