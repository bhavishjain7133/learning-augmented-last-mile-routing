from __future__ import annotations

from collections import Counter
from typing import Mapping, Sequence

from .types import Route


def route_cost(sequence: Sequence[str], matrix: Mapping[str, Mapping[str, float]]) -> float:
    return sum(float(matrix[first][second]) for first, second in zip(sequence, sequence[1:]))


def normalized_pairwise_disagreement(
    predicted: Sequence[str], actual: Sequence[str], exclude_first: bool = True
) -> float:
    """Kendall-style disagreement normalized to [0, 1]."""
    if set(predicted) != set(actual):
        raise ValueError("Predicted and actual sequences must contain the same stops")
    predicted_items = list(predicted[1:] if exclude_first else predicted)
    actual_items = list(actual[1:] if exclude_first else actual)
    if len(predicted_items) < 2:
        return 0.0
    actual_position = {stop_id: position for position, stop_id in enumerate(actual_items)}
    inversions = 0
    comparisons = 0
    for first_index, first_stop in enumerate(predicted_items):
        for second_stop in predicted_items[first_index + 1 :]:
            comparisons += 1
            if actual_position[first_stop] > actual_position[second_stop]:
                inversions += 1
    return inversions / comparisons


def adjacent_edge_recall(
    predicted: Sequence[str], actual: Sequence[str], undirected: bool = True
) -> float:
    if len(actual) < 2:
        return 1.0
    def edge(first: str, second: str):
        return frozenset((first, second)) if undirected else (first, second)
    predicted_edges = {edge(first, second) for first, second in zip(predicted, predicted[1:])}
    actual_edges = {edge(first, second) for first, second in zip(actual, actual[1:])}
    return len(predicted_edges & actual_edges) / len(actual_edges)


def zone_reentries(route: Route, sequence: Sequence[str]) -> int:
    """Count returns to a zone after the route has previously left it."""
    zones = [route.stops[stop_id].zone_id for stop_id in sequence if route.stops[stop_id].zone_id]
    compressed = [zone for index, zone in enumerate(zones) if index == 0 or zone != zones[index - 1]]
    counts = Counter(compressed)
    return sum(max(0, count - 1) for count in counts.values())

