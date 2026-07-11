"""Official Amazon challenge route score, adapted from MIT-CAVE/rc-cli.

The original scoring implementation is MIT licensed:
Copyright (c) 2021 MIT Center for Transportation & Logistics.
Source: https://github.com/MIT-CAVE/rc-cli/blob/main/scoring/score.py
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np


def sequence_deviation(actual_closed: Sequence[str], proposed_closed: Sequence[str]) -> float:
    """Reproduce the challenge Sequence Deviation component."""
    actual = list(actual_closed[1:-1])
    proposed = list(proposed_closed[1:-1])
    if len(actual) < 2:
        return 0.0
    actual_position = {stop_id: index for index, stop_id in enumerate(actual)}
    comparison = [actual_position[stop_id] for stop_id in proposed]
    comparison_sum = sum(
        abs(comparison[index] - comparison[index - 1]) - 1
        for index in range(1, len(comparison))
    )
    count = len(actual)
    return (2 / (count * (count - 1))) * comparison_sum


def _normalization_parameters(
    matrix: Mapping[str, Mapping[str, float]],
) -> tuple[float, float]:
    values = np.fromiter(
        (float(value) for row in matrix.values() for value in row.values()),
        dtype=float,
    )
    standard_deviation = float(values.std())
    if standard_deviation == 0:
        raise ValueError("Official score is undefined for a constant travel-time matrix")
    return float(values.min()), standard_deviation


def _normalized_cost(
    first: str,
    second: str,
    matrix: Mapping[str, Mapping[str, float]],
    minimum: float,
    standard_deviation: float,
) -> float:
    # Equivalent to the official z-score normalization followed by shifting the
    # minimum normalized value to zero.
    return (float(matrix[first][second]) - minimum) / standard_deviation


def _erp_dynamic_programming(
    actual: Sequence[str],
    proposed: Sequence[str],
    matrix: Mapping[str, Mapping[str, float]],
    minimum: float,
    standard_deviation: float,
    gap_penalty: float,
) -> tuple[float, int]:
    """Exact ERP fallback with the official substitution-first tie priority."""
    rows = len(actual) + 1
    columns = len(proposed) + 1
    costs = np.zeros((rows, columns), dtype=float)
    edits = np.zeros((rows, columns), dtype=np.int32)
    costs[:, 0] = np.arange(rows) * gap_penalty
    costs[0, :] = np.arange(columns) * gap_penalty
    edits[:, 0] = np.arange(rows)
    edits[0, :] = np.arange(columns)

    for row in range(1, rows):
        for column in range(1, columns):
            substitution = costs[row - 1, column - 1] + _normalized_cost(
                actual[row - 1],
                proposed[column - 1],
                matrix,
                minimum,
                standard_deviation,
            )
            delete_actual = costs[row - 1, column] + gap_penalty
            delete_proposed = costs[row, column - 1] + gap_penalty
            best = min(substitution, delete_actual, delete_proposed)
            costs[row, column] = best
            if best == substitution:
                edits[row, column] = edits[row - 1, column - 1] + int(
                    actual[row - 1] != proposed[column - 1]
                )
            elif best == delete_actual:
                edits[row, column] = edits[row - 1, column] + 1
            else:
                edits[row, column] = edits[row, column - 1] + 1
    return float(costs[-1, -1]), int(edits[-1, -1])


def erp_per_edit(
    actual_closed: Sequence[str],
    proposed_closed: Sequence[str],
    matrix: Mapping[str, Mapping[str, float]],
    gap_penalty: float = 1000.0,
) -> float:
    minimum, standard_deviation = _normalization_parameters(matrix)
    diagonal_cost = sum(
        _normalized_cost(first, second, matrix, minimum, standard_deviation)
        for first, second in zip(actual_closed, proposed_closed)
    )
    mismatch_count = sum(
        first != second for first, second in zip(actual_closed, proposed_closed)
    )
    if mismatch_count == 0:
        return 0.0

    # Equal-length sequences require at least one insertion and one deletion to
    # leave the diagonal. If the full diagonal path costs less than two gaps,
    # the official ERP optimum is exactly the diagonal substitution path.
    if len(actual_closed) == len(proposed_closed) and diagonal_cost < 2 * gap_penalty:
        return diagonal_cost / mismatch_count

    total_cost, edit_count = _erp_dynamic_programming(
        actual_closed,
        proposed_closed,
        matrix,
        minimum,
        standard_deviation,
        gap_penalty,
    )
    return 0.0 if edit_count == 0 else total_cost / edit_count


def official_route_score(
    actual_sequence: Sequence[str],
    proposed_sequence: Sequence[str],
    matrix: Mapping[str, Mapping[str, float]],
    gap_penalty: float = 1000.0,
) -> float:
    """Return the official lower-is-better score for one valid route."""
    if len(actual_sequence) != len(proposed_sequence):
        raise ValueError("Actual and proposed routes have different lengths")
    if set(actual_sequence) != set(proposed_sequence):
        raise ValueError("Actual and proposed routes contain different stops")
    if actual_sequence[0] != proposed_sequence[0]:
        raise ValueError("Proposed route must start at the station")
    station = actual_sequence[0]
    actual_closed = tuple(actual_sequence) + (station,)
    proposed_closed = tuple(proposed_sequence) + (station,)
    return sequence_deviation(actual_closed, proposed_closed) * erp_per_edit(
        actual_closed,
        proposed_closed,
        matrix,
        gap_penalty,
    )

