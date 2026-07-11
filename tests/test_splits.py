from lastmile.splits import chronological_station_split
from lastmile.synthetic import make_synthetic_route


def test_chronological_station_split_is_disjoint_and_ordered() -> None:
    routes = [make_synthetic_route(route_id=f"r-{index}", day_offset=index) for index in range(20)]
    split = chronological_station_split(routes)
    split.validate()
    assert max(route.route_date for route in split.train) <= min(
        route.route_date for route in split.validation
    )
    assert max(route.route_date for route in split.validation) <= min(
        route.route_date for route in split.test
    )

