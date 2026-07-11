from __future__ import annotations

import argparse
import shutil
import urllib.request
from pathlib import Path

BASE_URL = "https://amazon-last-mile-challenges.s3.us-west-2.amazonaws.com/almrrc2021"

FILES = {
    "training/actual_sequences.json": (
        "almrrc2021-data-training/model_build_inputs/actual_sequences.json", 9_665_078
    ),
    "training/invalid_sequence_scores.json": (
        "almrrc2021-data-training/model_build_inputs/invalid_sequence_scores.json", 414_742
    ),
    "training/route_data.json": (
        "almrrc2021-data-training/model_build_inputs/route_data.json", 78_972_162
    ),
    "training/package_data.json": (
        "almrrc2021-data-training/model_build_inputs/package_data.json", 375_437_806
    ),
    "training/travel_times.json": (
        "almrrc2021-data-training/model_build_inputs/travel_times.json", 1_817_146_363
    ),
    "evaluation/eval_actual_sequences.json": (
        "almrrc2021-data-evaluation/model_score_inputs/eval_actual_sequences.json", 4_625_218
    ),
    "evaluation/eval_invalid_sequence_scores.json": (
        "almrrc2021-data-evaluation/model_score_inputs/eval_invalid_sequence_scores.json", 207_138
    ),
    "evaluation/eval_route_data.json": (
        "almrrc2021-data-evaluation/model_apply_inputs/eval_route_data.json", 37_777_768
    ),
    "evaluation/eval_package_data.json": (
        "almrrc2021-data-evaluation/model_apply_inputs/eval_package_data.json", 166_201_035
    ),
    "evaluation/eval_travel_times.json": (
        "almrrc2021-data-evaluation/model_apply_inputs/eval_travel_times.json", 843_104_906
    ),
}
BUNDLES = {
    "core": [
        "training/actual_sequences.json",
        "training/invalid_sequence_scores.json",
        "training/route_data.json",
    ],
    "training": [key for key in FILES if key.startswith("training/")],
    "evaluation": [key for key in FILES if key.startswith("evaluation/")],
    "all": list(FILES),
}


def download_file(relative_name: str, data_root: Path) -> None:
    source_key, expected_size = FILES[relative_name]
    destination = data_root / relative_name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size == expected_size:
        print(f"SKIP {relative_name} (size verified)")
        return
    temporary = destination.with_suffix(destination.suffix + ".part")
    url = f"{BASE_URL}/{source_key}"
    print(f"GET  {relative_name} ({expected_size / 1_000_000:.1f} MB)")
    request = urllib.request.Request(url, headers={"User-Agent": "lastmile-research/0.1"})
    with urllib.request.urlopen(request) as response, temporary.open("wb") as output:
        shutil.copyfileobj(response, output, length=1024 * 1024)
    if temporary.stat().st_size != expected_size:
        raise RuntimeError(
            f"Size mismatch for {relative_name}: got {temporary.stat().st_size}, "
            f"expected {expected_size}"
        )
    temporary.replace(destination)


def main() -> None:
    parser = argparse.ArgumentParser(description="Download official Amazon Last-Mile data")
    parser.add_argument("--bundle", choices=sorted(BUNDLES), default="core")
    parser.add_argument("--data-root", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    for relative_name in BUNDLES[args.bundle]:
        download_file(relative_name, args.data_root)


if __name__ == "__main__":
    main()

