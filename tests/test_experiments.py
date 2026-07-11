import pandas as pd

from lastmile.experiments import select_preference_weight, validation_summary


def test_validation_summary_and_selection_respect_cost_tolerance() -> None:
    results = pd.DataFrame(
        [
            {"route_id": "r1", "method": "nearest_neighbor", "preference_weight": None,
             "geodesic_cost_km": 10.0, "pairwise_disagreement": 0.5,
             "adjacent_edge_recall": 0.2, "zone_reentries": 2, "runtime_ms": 1.0},
            {"route_id": "r2", "method": "nearest_neighbor", "preference_weight": None,
             "geodesic_cost_km": 20.0, "pairwise_disagreement": 0.5,
             "adjacent_edge_recall": 0.2, "zone_reentries": 2, "runtime_ms": 1.0},
            {"route_id": "r1", "method": "hybrid_zone", "preference_weight": 0.5,
             "geodesic_cost_km": 10.4, "pairwise_disagreement": 0.3,
             "adjacent_edge_recall": 0.4, "zone_reentries": 1, "runtime_ms": 2.0},
            {"route_id": "r2", "method": "hybrid_zone", "preference_weight": 0.5,
             "geodesic_cost_km": 20.8, "pairwise_disagreement": 0.3,
             "adjacent_edge_recall": 0.4, "zone_reentries": 1, "runtime_ms": 2.0},
            {"route_id": "r1", "method": "hybrid_zone", "preference_weight": 1.0,
             "geodesic_cost_km": 12.0, "pairwise_disagreement": 0.2,
             "adjacent_edge_recall": 0.5, "zone_reentries": 0, "runtime_ms": 2.0},
            {"route_id": "r2", "method": "hybrid_zone", "preference_weight": 1.0,
             "geodesic_cost_km": 24.0, "pairwise_disagreement": 0.2,
             "adjacent_edge_recall": 0.5, "zone_reentries": 0, "runtime_ms": 2.0},
        ]
    )
    summary = validation_summary(results)
    assert select_preference_weight(summary, median_cost_tolerance=0.05) == 0.5
