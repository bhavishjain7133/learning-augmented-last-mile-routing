from __future__ import annotations

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "01_data_quality_audit.ipynb"


def main() -> None:
    notebook = nbf.v4.new_notebook()
    notebook["metadata"]["kernelspec"] = {
        "display_name": "Python 3",
        "language": "python",
        "name": "python3",
    }
    notebook["metadata"]["language_info"] = {"name": "python", "version": "3.12"}
    notebook["cells"] = [
        nbf.v4.new_markdown_cell(
            "# Amazon Last-Mile Data Quality Audit\n\n"
            "Source: 2021 Amazon Last Mile Routing Research Challenge training data.\n\n"
            "## tl;dr\n\n"
            "- The training core contains 6,112 routes from 17 stations between "
            "2018-07-19 and 2018-08-26.\n"
            "- Route IDs are unique; every route has one station, a complete observed "
            "sequence, and no missing drop-off zone ID.\n"
            "- A station-aware chronological split yields 4,270 train, 916 validation, "
            "and 926 test routes.\n"
            "- The median route contains 151 stops; algorithm runtime must be evaluated "
            "at this operational scale.\n"
            "- Only 102 routes are labelled Low quality, so quality-subgroup findings "
            "must carry uncertainty. No model-performance claim is made here."
        ),
        nbf.v4.new_markdown_cell(
            "## Context & Methods\n\n"
            "The grain is one historical route. We verify IDs, station-stop integrity, "
            "observed-sequence coverage, zone completeness, labels, temporal coverage, "
            "and chronological station-aware splits.\n\n"
            "### Key Assumptions\n\n"
            "- Each route contains exactly one Station stop.\n"
            "- The observed sequence contains exactly the route stop identifiers.\n"
            "- Route quality is descriptive, never a predictive feature.\n"
            "- Obfuscated coordinates are not reverse-geocoded."
        ),
        nbf.v4.new_code_cell(
            "from pathlib import Path\n"
            "import json\n"
            "import matplotlib.pyplot as plt\n"
            "import pandas as pd\n\n"
            "from lastmile.audit import profile_routes\n"
            "from lastmile.data import load_routes\n"
            "from lastmile.splits import chronological_station_split\n\n"
            "ROOT = Path.cwd()\n"
            "if not (ROOT / 'data').exists():\n"
            "    ROOT = ROOT.parent\n"
            "DATA = ROOT / 'data' / 'raw' / 'training'\n"
            "ARTIFACTS = ROOT / 'artifacts' / 'data_audit'\n"
            "ARTIFACTS.mkdir(parents=True, exist_ok=True)\n"
            "plt.rcParams.update({'figure.dpi': 120, 'font.size': 10})"
        ),
        nbf.v4.new_markdown_cell("## Data\n\n### 1. Load and validate route records"),
        nbf.v4.new_code_cell(
            "routes = load_routes(DATA / 'route_data.json', DATA / 'actual_sequences.json')\n"
            "split = chronological_station_split(routes)\n"
            "profile = profile_routes(routes, split)\n"
            "(ARTIFACTS / 'route_profile.json').write_text(\n"
            "    json.dumps(profile, indent=2, sort_keys=True), encoding='utf-8'\n"
            ")\n"
            "print(json.dumps(profile, indent=2, sort_keys=True))"
        ),
        nbf.v4.new_markdown_cell("### 2. Build a bounded route-level table"),
        nbf.v4.new_code_cell(
            "route_frame = pd.DataFrame({\n"
            "    'route_id': [route.route_id for route in routes],\n"
            "    'station_code': [route.station_code for route in routes],\n"
            "    'date': [route.route_date for route in routes],\n"
            "    'route_score': [route.route_score for route in routes],\n"
            "    'stop_count': [len(route.stops) for route in routes],\n"
            "})\n"
            "route_frame.head()"
        ),
        nbf.v4.new_markdown_cell("## Results\n\n### 3. Route volume by station"),
        nbf.v4.new_code_cell(
            "station_counts = route_frame['station_code'].value_counts().sort_values()\n"
            "fig, ax = plt.subplots(figsize=(8, 5.5))\n"
            "bars = ax.barh(station_counts.index, station_counts.values, "
            "color='#2F6BFF', edgecolor='#17325C', linewidth=0.6)\n"
            "ax.bar_label(bars, padding=3, fontsize=8)\n"
            "ax.set_title('Training routes by delivery station')\n"
            "ax.set_xlabel('Historical routes (2018-07-19 to 2018-08-26)')\n"
            "ax.set_ylabel('Station code')\n"
            "ax.spines[['top', 'right']].set_visible(False)\n"
            "fig.tight_layout()\n"
            "fig.savefig(ARTIFACTS / 'routes_by_station.png', bbox_inches='tight')\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell("### 4. Operational route-size distribution"),
        nbf.v4.new_code_cell(
            "median_stops = route_frame['stop_count'].median()\n"
            "fig, ax = plt.subplots(figsize=(8, 4.5))\n"
            "ax.hist(route_frame['stop_count'], bins=30, color='#7FA6FF', "
            "edgecolor='#17325C', linewidth=0.5)\n"
            "ax.axvline(median_stops, color='#222222', linestyle='--', linewidth=1.5, "
            "label=f'Median = {median_stops:.0f}')\n"
            "ax.set_title('Stops per historical route')\n"
            "ax.set_xlabel('Stops including station')\n"
            "ax.set_ylabel('Routes')\n"
            "ax.legend(frameon=False)\n"
            "ax.spines[['top', 'right']].set_visible(False)\n"
            "fig.tight_layout()\n"
            "fig.savefig(ARTIFACTS / 'stops_per_route.png', bbox_inches='tight')\n"
            "plt.show()"
        ),
        nbf.v4.new_markdown_cell("### 5. Split and quality summary"),
        nbf.v4.new_code_cell(
            "quality_summary = pd.DataFrame({\n"
            "    'check': ['Duplicate route IDs', 'Invalid station count', "
            "'Sequence/stop mismatches', 'Missing drop-off zones', "
            "'Observed-sequence coverage'],\n"
            "    'value': [profile['duplicate_route_id_count'], "
            "profile['invalid_station_count'], profile['sequence_stop_mismatch_count'], "
            "profile['missing_dropoff_zone_count'], profile['observed_sequence_coverage']]\n"
            "})\n"
            "display(quality_summary)\n"
            "display(pd.Series(profile['split_route_counts'], name='routes').to_frame())"
        ),
        nbf.v4.new_markdown_cell(
            "## Takeaways\n\n"
            "- Use the executed outputs above as controlling evidence.\n"
            "- Low-quality routes are rare, so subgroup uncertainty must be shown.\n"
            "- Median route size determines the runtime budget for local search.\n"
            "- Travel-time and package files remain required for final experiments."
        ),
    ]
    NOTEBOOK.parent.mkdir(parents=True, exist_ok=True)
    nbf.write(notebook, NOTEBOOK)
    print(NOTEBOOK)


if __name__ == "__main__":
    main()
