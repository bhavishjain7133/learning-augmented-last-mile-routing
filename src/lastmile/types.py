from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Mapping


@dataclass(frozen=True)
class Stop:
    stop_id: str
    latitude: float
    longitude: float
    stop_type: str
    zone_id: str | None

    @property
    def is_station(self) -> bool:
        return self.stop_type.lower() == "station"


@dataclass(frozen=True)
class Route:
    route_id: str
    station_code: str
    route_date: date
    departure_time_utc: str
    executor_capacity_cm3: int
    route_score: str | None
    stops: Mapping[str, Stop]
    actual_sequence: tuple[str, ...] | None = None

    @property
    def station_stop_id(self) -> str:
        stations = [stop_id for stop_id, stop in self.stops.items() if stop.is_station]
        if len(stations) != 1:
            raise ValueError(
                f"Route {self.route_id} must have exactly one station stop; found {len(stations)}"
            )
        return stations[0]

    def validate_sequence(self, sequence: tuple[str, ...] | list[str]) -> None:
        if len(sequence) != len(self.stops):
            raise ValueError("Sequence length does not equal the number of route stops")
        if len(set(sequence)) != len(sequence):
            raise ValueError("Sequence contains duplicate stops")
        if set(sequence) != set(self.stops):
            raise ValueError("Sequence and route stop identifiers differ")
        if sequence[0] != self.station_stop_id:
            raise ValueError("The station must be the first stop")

