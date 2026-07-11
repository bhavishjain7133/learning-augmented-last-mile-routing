from __future__ import annotations

from datetime import date, timedelta

from .types import Route, Stop


def make_synthetic_route(
    route_id: str = "synthetic-001",
    station_code: str = "SYN1",
    day_offset: int = 0,
) -> Route:
    stops = {
        "ST": Stop("ST", 0.0, 0.0, "Station", None),
        "A1": Stop("A1", 0.0, 0.01, "Dropoff", "A-1"),
        "A2": Stop("A2", 0.0, 0.02, "Dropoff", "A-1"),
        "B1": Stop("B1", 0.01, 0.02, "Dropoff", "B-1"),
        "B2": Stop("B2", 0.02, 0.02, "Dropoff", "B-1"),
        "C1": Stop("C1", 0.02, 0.0, "Dropoff", "C-1"),
    }
    return Route(
        route_id=route_id,
        station_code=station_code,
        route_date=date(2018, 1, 1) + timedelta(days=day_offset),
        departure_time_utc="08:00:00",
        executor_capacity_cm3=1_000_000,
        route_score="High",
        stops=stops,
        actual_sequence=("ST", "A1", "A2", "B1", "B2", "C1"),
    )

