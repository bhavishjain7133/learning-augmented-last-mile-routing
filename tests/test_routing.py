from lastmile.baselines import angular_zone_route, nearest_neighbor_route, two_opt
from lastmile.geometry import build_haversine_matrix
from lastmile.metrics import (
    adjacent_edge_recall,
    normalized_pairwise_disagreement,
    route_cost,
    zone_reentries,
)
from lastmile.model import ZoneTransitionModel, hybrid_greedy_route, hybrid_zone_route, parent_zone
from lastmile.synthetic import make_synthetic_route


def test_baselines_return_valid_routes() -> None:
    route = make_synthetic_route()
    matrix = build_haversine_matrix(route.stops)
    route.validate_sequence(nearest_neighbor_route(route, matrix))
    route.validate_sequence(angular_zone_route(route, matrix))


def test_two_opt_never_worsens_initial_route() -> None:
    route = make_synthetic_route()
    matrix = build_haversine_matrix(route.stops)
    actual = route.actual_sequence or ()
    initial = (route.station_stop_id,) + tuple(
        stop for stop in reversed(actual) if stop != route.station_stop_id
    )
    improved = two_opt(route, initial, matrix)
    assert route_cost(improved, matrix) <= route_cost(initial, matrix) + 1e-12


def test_sequence_metrics_have_expected_bounds() -> None:
    route = make_synthetic_route()
    actual = route.actual_sequence
    assert actual is not None
    assert normalized_pairwise_disagreement(actual, actual) == 0.0
    assert adjacent_edge_recall(actual, actual) == 1.0
    reversed_tail = (actual[0],) + tuple(reversed(actual[1:]))
    assert normalized_pairwise_disagreement(reversed_tail, actual) == 1.0


def test_zone_reentries_detect_backtracking() -> None:
    route = make_synthetic_route()
    assert zone_reentries(route, ("ST", "A1", "B1", "A2", "B2", "C1")) == 2


def test_hybrid_model_returns_valid_route() -> None:
    routes = [make_synthetic_route(route_id=f"train-{index}") for index in range(4)]
    test_route = make_synthetic_route(route_id="test")
    matrix = build_haversine_matrix(test_route.stops)
    model = ZoneTransitionModel(smoothing=1.0).fit(routes)
    sequence = hybrid_greedy_route(test_route, model, preference_weight=0.5, matrix=matrix)
    test_route.validate_sequence(sequence)
    assert zone_reentries(test_route, sequence) == 0
    grouped = hybrid_zone_route(test_route, model, preference_weight=0.5, matrix=matrix)
    test_route.validate_sequence(grouped)
    assert zone_reentries(test_route, grouped) == 0


def test_parent_zone_is_stable() -> None:
    assert parent_zone("E-20.2H") == "E"
    assert parent_zone(None) == "__MISSING__"
