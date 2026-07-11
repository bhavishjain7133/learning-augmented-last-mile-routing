from lastmile.geometry import build_haversine_matrix
from lastmile.metrics import zone_reentries
from lastmile.pairwise import (
    PairwiseZonePreferenceModel,
    compress_route_zones,
    pairwise_preference_zone_route,
)
from lastmile.synthetic import make_synthetic_route


def test_pairwise_model_learns_observed_zone_order() -> None:
    routes = [make_synthetic_route(route_id=f"train-{index}") for index in range(4)]
    model = PairwiseZonePreferenceModel(smoothing=1.0, minimum_support=2).fit(routes)
    probability, level, support = model.probability_before("SYN1", "A-1", "B-1")
    assert probability > 0.5
    assert level == "station_exact"
    assert support == 4


def test_pairwise_route_is_valid_and_zone_contiguous() -> None:
    routes = [make_synthetic_route(route_id=f"train-{index}") for index in range(4)]
    route = make_synthetic_route(route_id="test")
    matrix = build_haversine_matrix(route.stops)
    model = PairwiseZonePreferenceModel(smoothing=1.0, minimum_support=2).fit(routes)
    sequence = pairwise_preference_zone_route(route, model, preference_weight=1.0, matrix=matrix)
    route.validate_sequence(sequence)
    assert zone_reentries(route, sequence) == 0


def test_compressed_zones_remove_consecutive_duplicates() -> None:
    route = make_synthetic_route()
    assert compress_route_zones(route) == ("A-1", "B-1", "C-1")


def test_unseen_pair_has_neutral_probability() -> None:
    model = PairwiseZonePreferenceModel().fit([make_synthetic_route()])
    probability, level, support = model.probability_before("UNKNOWN", "X-1", "Y-1")
    assert probability == 0.5
    assert level == "neutral"
    assert support == 0

