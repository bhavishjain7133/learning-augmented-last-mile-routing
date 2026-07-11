from __future__ import annotations

from math import asin, cos, radians, sin, sqrt
from typing import Mapping

from .types import Stop

EARTH_RADIUS_KM = 6371.0088


def haversine_km(first: Stop, second: Stop) -> float:
    """Return great-circle distance in kilometres between two stops."""
    lat1, lon1 = radians(first.latitude), radians(first.longitude)
    lat2, lon2 = radians(second.latitude), radians(second.longitude)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    return 2 * EARTH_RADIUS_KM * asin(sqrt(a))


def build_haversine_matrix(stops: Mapping[str, Stop]) -> dict[str, dict[str, float]]:
    return {
        origin: {
            destination: haversine_km(origin_stop, destination_stop)
            for destination, destination_stop in stops.items()
        }
        for origin, origin_stop in stops.items()
    }

