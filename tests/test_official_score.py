from lastmile.geometry import build_haversine_matrix
from lastmile.official_score import official_route_score, sequence_deviation
from lastmile.synthetic import make_synthetic_route


def test_official_score_is_zero_for_exact_match() -> None:
    route = make_synthetic_route()
    actual = route.actual_sequence
    assert actual is not None
    matrix = build_haversine_matrix(route.stops)
    assert official_route_score(actual, actual, matrix) == 0.0


def test_official_score_is_positive_for_nontrivial_valid_permutation() -> None:
    route = make_synthetic_route()
    actual = route.actual_sequence
    assert actual is not None
    proposed = ("ST", "A2", "B2", "A1", "C1", "B1")
    matrix = build_haversine_matrix(route.stops)
    assert official_route_score(actual, proposed, matrix) > 0


def test_official_sequence_deviation_preserves_reverse_path_edge_case() -> None:
    """The MIT reference formula assigns zero SD to an exact reverse traversal."""
    route = make_synthetic_route()
    actual = route.actual_sequence
    assert actual is not None
    reversed_path = (actual[0],) + tuple(reversed(actual[1:]))
    actual_closed = actual + (actual[0],)
    reversed_closed = reversed_path + (reversed_path[0],)
    assert sequence_deviation(actual_closed, reversed_closed) == 0.0


def test_sequence_deviation_matches_perfect_route() -> None:
    route = make_synthetic_route()
    actual = route.actual_sequence
    assert actual is not None
    closed = actual + (actual[0],)
    assert sequence_deviation(closed, closed) == 0.0

