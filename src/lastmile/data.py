from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Iterator

from .types import Route, Stop


def _ordered_sequence(sequence_record: dict[str, object]) -> tuple[str, ...]:
    actual = sequence_record.get("actual", sequence_record)
    if not isinstance(actual, dict):
        raise ValueError("Actual sequence record must be a mapping")
    return tuple(stop_id for stop_id, _ in sorted(actual.items(), key=lambda item: int(item[1])))


def load_routes(
    route_data_path: str | Path,
    actual_sequences_path: str | Path | None = None,
    limit: int | None = None,
) -> list[Route]:
    """Load route metadata and optional observed sequences."""
    with Path(route_data_path).open("r", encoding="utf-8") as handle:
        route_records = json.load(handle)
    sequences: dict[str, object] = {}
    if actual_sequences_path is not None:
        with Path(actual_sequences_path).open("r", encoding="utf-8") as handle:
            sequences = json.load(handle)

    routes: list[Route] = []
    for index, (route_id, record) in enumerate(route_records.items()):
        if limit is not None and index >= limit:
            break
        stops = {
            stop_id: Stop(
                stop_id=stop_id,
                latitude=float(stop_record["lat"]),
                longitude=float(stop_record["lng"]),
                stop_type=str(stop_record["type"]),
                zone_id=(
                    None
                    if stop_record.get("zone_id") in (None, "", "nan", "NaN")
                    else str(stop_record["zone_id"])
                ),
            )
            for stop_id, stop_record in record["stops"].items()
        }
        actual_sequence = _ordered_sequence(sequences[route_id]) if route_id in sequences else None
        route = Route(
            route_id=route_id,
            station_code=str(record["station_code"]),
            route_date=date.fromisoformat(str(record["date_YYYY_MM_DD"])),
            departure_time_utc=str(record["departure_time_utc"]),
            executor_capacity_cm3=int(record["executor_capacity_cm3"]),
            route_score=record.get("route_score"),
            stops=stops,
            actual_sequence=actual_sequence,
        )
        if actual_sequence is not None:
            route.validate_sequence(actual_sequence)
        routes.append(route)
    return routes


def iter_travel_time_matrices(
    travel_times_path: str | Path,
) -> Iterator[tuple[str, dict[str, dict[str, float]]]]:
    """Stream route-level matrices from the roughly 1.8 GB training JSON file."""
    try:
        import ijson
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Install ijson to stream the travel-time file") from exc
    with Path(travel_times_path).open("rb") as handle:
        for route_id, matrix in ijson.kvitems(handle, ""):
            yield route_id, {
                origin: {destination: float(value) for destination, value in row.items()}
                for origin, row in matrix.items()
            }


def load_selected_travel_times(
    travel_times_path: str | Path, route_ids: set[str]
) -> dict[str, dict[str, dict[str, float]]]:
    selected: dict[str, dict[str, dict[str, float]]] = {}
    for route_id, matrix in iter_travel_time_matrices(travel_times_path):
        if route_id in route_ids:
            selected[route_id] = matrix
            if len(selected) == len(route_ids):
                break
    missing = route_ids - set(selected)
    if missing:
        raise KeyError(f"Travel-time matrices missing for {len(missing)} requested routes")
    return selected

