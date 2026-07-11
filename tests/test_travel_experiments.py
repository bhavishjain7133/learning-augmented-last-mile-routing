import pandas as pd

from lastmile.travel_experiments import (
    select_travel_preference_weight,
    travel_validation_summary,
)


def test_travel_summary_and_selection_use_travel_time_guardrail() -> None:
    results = pd.DataFrame(
        [
            {"route_id": "r1", "method": "nearest_neighbor", "preference_weight": None,
             "travel_time_seconds": 100.0, "pairwise_disagreement": 0.5,
             "adjacent_edge_recall": 0.2, "zone_reentries": 2, "runtime_ms": 1.0},
            {"route_id": "r2", "method": "nearest_neighbor", "preference_weight": None,
             "travel_time_seconds": 200.0, "pairwise_disagreement": 0.5,
             "adjacent_edge_recall": 0.2, "zone_reentries": 2, "runtime_ms": 1.0},
            {"route_id": "r1", "method": "pairwise_zone", "preference_weight": 0.5,
             "travel_time_seconds": 104.0, "pairwise_disagreement": 0.3,
             "adjacent_edge_recall": 0.4, "zone_reentries": 0, "runtime_ms": 2.0},
            {"route_id": "r2", "method": "pairwise_zone", "preference_weight": 0.5,
             "travel_time_seconds": 208.0, "pairwise_disagreement": 0.3,
             "adjacent_edge_recall": 0.4, "zone_reentries": 0, "runtime_ms": 2.0},
            {"route_id": "r1", "method": "pairwise_zone", "preference_weight": 1.0,
             "travel_time_seconds": 120.0, "pairwise_disagreement": 0.2,
             "adjacent_edge_recall": 0.5, "zone_reentries": 0, "runtime_ms": 2.0},
            {"route_id": "r2", "method": "pairwise_zone", "preference_weight": 1.0,
             "travel_time_seconds": 240.0, "pairwise_disagreement": 0.2,
             "adjacent_edge_recall": 0.5, "zone_reentries": 0, "runtime_ms": 2.0},
        ]
    )
    summary = travel_validation_summary(results)
    assert select_travel_preference_weight(summary, 0.05) == 0.5

