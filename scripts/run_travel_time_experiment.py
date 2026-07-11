from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from lastmile.data import load_routes
from lastmile.pairwise import PairwiseZonePreferenceModel
from lastmile.splits import chronological_station_split
from lastmile.travel_experiments import (
    evaluate_travel_time_stream,
    select_travel_preference_weight,
    travel_validation_summary,
)

ROOT = Path(__file__).resolve().parents[1]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(4 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run confirmatory supplied-travel-time experiment")
    parser.add_argument("--validation-limit", type=int)
    parser.add_argument("--test-limit", type=int)
    args = parser.parse_args()

    config = json.loads((ROOT / "configs" / "experiment.json").read_text(encoding="utf-8"))
    data_root = ROOT / "data" / "raw" / "training"
    route_path = data_root / "route_data.json"
    sequence_path = data_root / "actual_sequences.json"
    travel_path = data_root / "travel_times.json"
    routes = load_routes(route_path, sequence_path)
    split = chronological_station_split(
        routes,
        train_fraction=config["split"]["train_fraction"],
        validation_fraction=config["split"]["validation_fraction"],
    )
    model = PairwiseZonePreferenceModel(
        smoothing=config["model"]["laplace_smoothing"],
        minimum_support=config["model"]["pairwise_minimum_support"],
    ).fit(split.train)

    validation_routes = split.validation[: args.validation_limit]
    validation = evaluate_travel_time_stream(
        validation_routes,
        model,
        config["model"]["pairwise_weight_grid"],
        str(travel_path),
    )
    summary = travel_validation_summary(validation)
    tolerance = config["model"]["median_cost_tolerance"]
    selected_weight = select_travel_preference_weight(summary, tolerance)

    test_routes = split.test[: args.test_limit]
    test = evaluate_travel_time_stream(
        test_routes,
        model,
        [selected_weight],
        str(travel_path),
    )

    output = ROOT / "artifacts" / "travel_time_experiment"
    output.mkdir(parents=True, exist_ok=True)
    validation.to_csv(output / "validation_route_results.csv", index=False)
    summary.to_csv(output / "validation_weight_summary.csv", index=False)
    test.to_csv(output / "test_route_results.csv", index=False)
    metadata = {
        "selected_preference_weight": selected_weight,
        "median_travel_time_tolerance": tolerance,
        "pairwise_minimum_support": config["model"]["pairwise_minimum_support"],
        "train_routes": len(split.train),
        "validation_routes_evaluated": len(validation_routes),
        "test_routes_evaluated": len(test_routes),
        "route_data_sha256": sha256(route_path),
        "actual_sequences_sha256": sha256(sequence_path),
        "travel_times_sha256": sha256(travel_path),
        "travel_times_bytes": travel_path.stat().st_size,
        "selection_rule": (
            "Lowest validation median pairwise disagreement among weights with "
            "median supplied-travel-time increase <= 5% versus nearest neighbour."
        ),
    }
    (output / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2, sort_keys=True), encoding="utf-8"
    )
    print(summary.to_string(index=False))
    print(json.dumps(metadata, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()

