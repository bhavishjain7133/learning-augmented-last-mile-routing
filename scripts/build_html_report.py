from __future__ import annotations

import html
import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = Path(r"C:\Users\bhavi\.codex\plugins\cache\openai-curated-remote\data-analytics\0.2.6-d37358633e00")
TEMPLATE = PLUGIN / "assets" / "html-report-shell.html"
REPORT = ROOT / "report"
RESULTS = ROOT / "artifacts" / "confirmatory_results"
REPORT.mkdir(exist_ok=True)


def source(value: str, identifier: str, file_name: str) -> str:
    return (
        f'<span class="source-tooltip" tabindex="0" aria-describedby="{identifier}">{value}'
        f'<span class="source-tooltip-content" id="{identifier}" role="tooltip">'
        f'Source: local experiment artifact<br>File: {html.escape(file_name)}</span></span>'
    )


def validation_fallback(rows: list[dict[str, float]]) -> str:
    width, height = 960, 420
    left, right, top, bottom = 90, 35, 35, 75
    x_min, x_max = 2.2, 6.8
    y_min, y_max = 0.33, 0.515

    def x(value: float) -> float:
        return left + (value - x_min) / (x_max - x_min) * (width - left - right)

    def y(value: float) -> float:
        return height - bottom - (value - y_min) / (y_max - y_min) * (height - top - bottom)

    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Validation travel-time and driver-disagreement trade-off">']
    for tick in [2.5, 3.5, 4.5, 5.5, 6.5]:
        xpos = x(tick)
        parts.append(f'<line x1="{xpos:.1f}" y1="{top}" x2="{xpos:.1f}" y2="{height-bottom}" stroke="var(--grid)"/>')
        parts.append(f'<text x="{xpos:.1f}" y="{height-bottom+24}" text-anchor="middle" fill="var(--secondary)" font-size="12">{tick:g}%</text>')
    for tick in [0.35, 0.40, 0.45, 0.50]:
        ypos = y(tick)
        parts.append(f'<line x1="{left}" y1="{ypos:.1f}" x2="{width-right}" y2="{ypos:.1f}" stroke="var(--grid)"/>')
        parts.append(f'<text x="{left-12}" y="{ypos+4:.1f}" text-anchor="end" fill="var(--secondary)" font-size="12">{tick:.2f}</text>')
    guard = x(5.0)
    parts.append(f'<line x1="{guard:.1f}" y1="{top}" x2="{guard:.1f}" y2="{height-bottom}" stroke="#202733" stroke-dasharray="6 5"/>')
    ordered = sorted(rows, key=lambda row: row["travel_increase_pct"])
    points = " ".join(f'{x(row["travel_increase_pct"]):.1f},{y(row["disagreement"]):.1f}' for row in ordered)
    parts.append(f'<polyline points="{points}" fill="none" stroke="#2F6BFF" stroke-width="3"/>')
    for row in ordered:
        xpos, ypos = x(row["travel_increase_pct"]), y(row["disagreement"])
        selected = row["weight"] == 2.0
        parts.append(f'<circle cx="{xpos:.1f}" cy="{ypos:.1f}" r="{8 if selected else 5}" fill="{None if selected else "#2F6BFF"}" stroke="{"#D69E00" if selected else "#2F6BFF"}" stroke-width="{3 if selected else 1}"/>'.replace('fill="None"', 'fill="none"'))
        parts.append(f'<text x="{xpos+8:.1f}" y="{ypos-8:.1f}" fill="var(--text)" font-size="11">w={row["weight"]:g}</text>')
    parts.append(f'<text x="{(left+width-right)/2:.1f}" y="{height-18}" text-anchor="middle" fill="var(--text)" font-size="13">Median travel-time increase vs nearest neighbour</text>')
    parts.append(f'<text transform="translate(20 {(top+height-bottom)/2:.1f}) rotate(-90)" text-anchor="middle" fill="var(--text)" font-size="13">Median pairwise disagreement</text>')
    parts.append('</svg>')
    return "".join(parts)


def station_fallback(rows: list[dict[str, float]]) -> str:
    width, height = 960, 590
    label_x, zero_x, top, bottom = 120, 900, 25, 35
    minimum = min(row["median_official_delta"] for row in rows) * 1.12
    row_height = (height - top - bottom) / len(rows)
    parts = [f'<svg viewBox="0 0 {width} {height}" role="img" aria-label="Median official-score change by station">']
    parts.append(f'<line x1="{zero_x}" y1="{top}" x2="{zero_x}" y2="{height-bottom}" stroke="var(--text)"/>')
    for index, row in enumerate(rows):
        center = top + (index + 0.5) * row_height
        bar_start = zero_x + row["median_official_delta"] / (-minimum) * (zero_x - label_x - 20)
        parts.append(f'<text x="{label_x-10}" y="{center+4:.1f}" text-anchor="end" fill="var(--text)" font-size="11">{html.escape(row["station_code"])}</text>')
        parts.append(f'<rect x="{bar_start:.1f}" y="{center-row_height*0.32:.1f}" width="{zero_x-bar_start:.1f}" height="{row_height*0.64:.1f}" fill="#2F6BFF"/>')
        parts.append(f'<text x="{bar_start+7:.1f}" y="{center+4:.1f}" fill="#fff" font-size="10">{row["median_official_delta"]:.3f}</text>')
    parts.append('</svg>')
    return "".join(parts)


def main() -> None:
    headline = json.loads((RESULTS / "headline_metrics.json").read_text(encoding="utf-8"))
    methods = pd.read_csv(RESULTS / "test_method_summary.csv")
    stations = pd.read_csv(RESULTS / "station_summary.csv")
    tradeoff = pd.read_csv(RESULTS / "validation_tradeoff.csv")
    css = re.search(r"<style>(.*?)</style>", TEMPLATE.read_text(encoding="utf-8"), re.S).group(1)

    validation_rows = [
        {
            "weight": float(row.preference_weight),
            "travel_increase_pct": 100 * float(row.median_travel_time_increase_fraction),
            "disagreement": float(row.median_pairwise_disagreement),
            "official_score": float(row.median_official_score),
        }
        for row in tradeoff.itertuples()
    ]
    station_rows = [
        {
            "station_code": str(row.station_code),
            "routes": int(row.routes),
            "median_official_delta": float(row.median_official_delta),
            "improved_fraction": float(row.improved_fraction),
        }
        for row in stations.sort_values("median_official_delta", ascending=False).itertuples()
    ]

    payload = {
        "charts": [
            {
                "id": "validation-tradeoff",
                "height": 360,
                "type": "scatter",
                "dataset": {
                    "id": "validation-tradeoff",
                    "title": "Validation trade-off",
                    "data": validation_rows,
                    "chart_spec": {
                        "id": "validation-tradeoff",
                        "dataset": "validation-tradeoff",
                        "title": "Validation trade-off",
                        "type": "scatter",
                        "encodings": {
                            "x": {"field": "travel_increase_pct", "label": "Median travel-time increase (%)", "type": "quantitative"},
                            "y": {"field": "disagreement", "label": "Median pairwise disagreement", "type": "quantitative"},
                            "tooltip": [
                                {"field": "weight", "label": "Preference weight", "type": "quantitative"},
                                {"field": "official_score", "label": "Median official score", "type": "quantitative"},
                            ],
                        },
                        "xAxisTitle": "Median travel-time increase vs nearest neighbour (%)",
                        "yAxisTitle": "Median pairwise disagreement",
                        "valueFormat": "number",
                    },
                },
            },
            {
                "id": "station-heterogeneity",
                "height": 520,
                "type": "bar",
                "settings": {"orientation": "horizontal", "groupMode": "grouped"},
                "dataset": {
                    "id": "station-heterogeneity",
                    "title": "Station heterogeneity",
                    "data": station_rows,
                    "chart_spec": {
                        "id": "station-heterogeneity",
                        "dataset": "station-heterogeneity",
                        "title": "Station heterogeneity",
                        "type": "bar",
                        "encodings": {
                            "x": {"field": "station_code", "label": "Station", "type": "nominal"},
                            "y": {"field": "median_official_delta", "label": "Median official-score change", "type": "quantitative"},
                            "tooltip": [
                                {"field": "routes", "label": "Test routes", "type": "quantitative"},
                                {"field": "improved_fraction", "label": "Fraction improved", "type": "quantitative"},
                            ],
                        },
                        "xAxisTitle": "Station",
                        "yAxisTitle": "Pairwise-zone minus nearest neighbour",
                        "valueFormat": "number",
                    },
                },
            },
        ]
    }
    (REPORT / "report-payload.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    method_rows = []
    for row in methods.itertuples():
        method_rows.append(
            "<tr>"
            f"<td>{html.escape(str(row.method).replace('_', ' ').title())}</td>"
            f"<td>{source(str(int(row.routes)), f'method-routes-{row.Index}', 'artifacts/confirmatory_results/test_method_summary.csv')}</td>"
            f"<td>{source(f'{row.official_score_median:.4f}', f'method-score-{row.Index}', 'artifacts/confirmatory_results/test_method_summary.csv')}</td>"
            f"<td>{source(f'{row.travel_time_seconds_median:.0f}', f'method-time-{row.Index}', 'artifacts/confirmatory_results/test_method_summary.csv')}</td>"
            f"<td>{source(f'{row.zone_reentries_median:.0f}', f'method-zone-{row.Index}', 'artifacts/confirmatory_results/test_method_summary.csv')}</td>"
            "</tr>"
        )

    score_reduction = 100 * headline["aggregate_median_score_reduction_fraction"]
    improved = 100 * headline["route_fraction_improved"]
    travel = 100 * headline["median_travel_time_increase_fraction"]
    ci_low, ci_high = headline["paired_median_delta_bootstrap_95_ci"]
    report_html = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><meta name="color-scheme" content="light dark"><title>Learning Driver Preferences for Last-Mile Routing</title><style>{css}</style></head>
<body><div class="shell"><header class="topbar"><div class="brand"><span class="mark" aria-hidden="true"></span>Technical Research Report</div><div class="meta">Amazon Last Mile training data · July 2026</div></header>
<main data-report-audience="technical">
<article class="reading">
<div class="kicker">Learning-augmented optimization</div>
<header data-contract-section="title"><h1>Learning Driver Preferences for Last-Mile Routing</h1></header>
<p class="deck">An interpretable zone-ordering model produced substantially more driver-like routes than nearest-neighbour routing, while accepting a small, pre-bounded travel-time trade-off.</p>
<section class="summary" data-contract-section="technical-summary"><div class="summary-label">Technical summary</div><div class="summary-body">
<p><strong>The locked model reduced the aggregate median official Amazon route score by {source(f'{score_reduction:.1f}%', 'summary-reduction', 'artifacts/confirmatory_results/headline_metrics.json')} on {source('926', 'summary-routes', 'artifacts/confirmatory_results/headline_metrics.json')} untouched chronological test routes.</strong> Lower is better; the median fell from {source('0.1011', 'summary-nn', 'artifacts/confirmatory_results/headline_metrics.json')} to {source('0.0607', 'summary-model', 'artifacts/confirmatory_results/headline_metrics.json')}.</p>
<p>The learned route scored better on {source(f'{improved:.1f}%', 'summary-improved', 'artifacts/confirmatory_results/headline_metrics.json')} of test routes. The paired median score difference was {source('-0.0421', 'summary-delta', 'artifacts/confirmatory_results/headline_metrics.json')} with a route-bootstrap {source(f'95% interval [{ci_low:.4f}, {ci_high:.4f}]', 'summary-ci', 'artifacts/confirmatory_results/headline_metrics.json')}.</p>
<p>This gain came with a median supplied-travel-time increase of {source(f'{travel:.2f}%', 'summary-travel', 'artifacts/confirmatory_results/headline_metrics.json')} versus nearest neighbour, consistent with the validation-only {source('5%', 'summary-guardrail', 'artifacts/travel_time_experiment/run_metadata.json')} selection guardrail.</p>
</div></section>
<section class="metrics">
<div class="metric"><div class="metric-label">Median score reduction</div><div class="metric-value">{source(f'{score_reduction:.1f}%', 'metric-reduction', 'artifacts/confirmatory_results/headline_metrics.json')}</div><div class="metric-note">Official score; aggregate medians</div></div>
<div class="metric"><div class="metric-label">Routes improved</div><div class="metric-value">{source(f'{improved:.1f}%', 'metric-improved', 'artifacts/confirmatory_results/headline_metrics.json')}</div><div class="metric-note">Paired route comparison</div></div>
<div class="metric"><div class="metric-label">Median travel-time change</div><div class="metric-value">{source(f'+{travel:.2f}%', 'metric-travel', 'artifacts/confirmatory_results/headline_metrics.json')}</div><div class="metric-note">Versus nearest neighbour</div></div>
<div class="metric"><div class="metric-label">Median re-entry reduction</div><div class="metric-value">{source('21', 'metric-reentry', 'artifacts/confirmatory_results/headline_metrics.json')}</div><div class="metric-note">Fewer zone re-entries per route</div></div>
</section>
<section class="narrative" data-contract-section="key-findings"><h2>Validation locked a preference weight before the test was opened</h2><p>Driver disagreement fell as more weight was placed on learned zone precedence. The selected weight was the best validation value that stayed inside the predeclared median travel-time guardrail; larger weights improved imitation further but breached that constraint.</p></section>
</article>
<div class="wide"><figure class="card source-figure"><div class="card-head"><h3>Validation travel-time and driver-disagreement trade-off</h3><p>Seven declared preference weights on 916 chronological validation routes; lower disagreement is better.</p></div><div class="chart-wrap"><div data-recharts-chart="validation-tradeoff"><div class="chart-fallback" data-recharts-fallback>{validation_fallback(validation_rows)}</div><div data-recharts-live aria-hidden="true"></div></div></div><figcaption class="chart-note">The gold-outlined fallback point marks weight 2; the dashed reference marks the 5% median travel-time guardrail.</figcaption><button type="button" class="source-tooltip" aria-describedby="chart-source-validation">Source<span class="source-tooltip-content" id="chart-source-validation" role="tooltip">Source: local experiment artifact<br>File: artifacts/confirmatory_results/validation_tradeoff.csv</span></button></figure></div>
<article class="reading">
<section class="narrative"><h2>The model improved driver-likeness without simply recreating a geometric sweep</h2><p>On the untouched test set, the learned model beat both nearest neighbour and the angular zone baseline on the official score. Its zero median zone re-entry is structural: the constructor exhausts a zone before entering another one.</p></section>
<section class="card table-card"><div class="card-head"><h3>Untouched test-set method comparison</h3><p>Median metrics across the same 926 routes; official score is lower-is-better.</p></div><div class="table-scroll"><table><thead><tr><th>Method</th><th>Routes</th><th>Official score</th><th>Travel time (s)</th><th>Zone re-entries</th></tr></thead><tbody>{''.join(method_rows)}</tbody></table></div></section>
<section class="narrative"><h2>All stations improved in median, but effect size varied materially</h2><p>Every station had a negative median score difference, yet the magnitude varied by almost fivefold. This heterogeneity supports station-level monitoring and a distance-only fallback rather than a single unmonitored deployment rule.</p></section>
</article>
<div class="wide"><figure class="card source-figure"><div class="card-head"><h3>Median official-score change by station</h3><p>Pairwise-zone score minus nearest-neighbour score; lower values favour the learned model.</p></div><div class="chart-wrap"><div data-recharts-chart="station-heterogeneity"><div class="chart-fallback" data-recharts-fallback>{station_fallback(station_rows)}</div><div data-recharts-live aria-hidden="true"></div></div></div><figcaption class="chart-note">Station cuts are descriptive rather than pre-registered confirmatory hypotheses.</figcaption><button type="button" class="source-tooltip" aria-describedby="chart-source-station">Source<span class="source-tooltip-content" id="chart-source-station" role="tooltip">Source: local experiment artifact<br>File: artifacts/confirmatory_results/station_summary.csv</span></button></figure></div>
<article class="reading">
<section class="narrative" data-contract-section="scope-data-and-metric-definitions"><h2>Scope and metric definitions</h2><p>The public 2021 Amazon Last Mile Routing Research Challenge training bundle contains historical routes from 17 delivery stations over 2018-07-19 to 2018-08-26. The station-aware chronological split contains {source('4,270', 'scope-train', 'artifacts/travel_time_experiment/run_metadata.json')} training, {source('916', 'scope-validation', 'artifacts/travel_time_experiment/run_metadata.json')} validation, and {source('926', 'scope-test', 'artifacts/travel_time_experiment/run_metadata.json')} test routes. The official score multiplies sequence deviation by edit-distance cost per edit; supplied travel time is the sum of directed matrix costs along the open route.</p></section>
<section class="narrative" data-contract-section="methodology"><h2>Hierarchical pairwise preferences remain interpretable</h2><p>Training estimates the probability that zone A precedes zone B within a station, with Laplace smoothing and back-off to parent-zone and global estimates when exact support is sparse. Route construction combines a Borda-style preference score with the supplied directed travel-time matrix. Hyperparameters were selected only on validation routes; test metrics were computed once after locking weight {source('2.0', 'method-weight', 'artifacts/travel_time_experiment/run_metadata.json')}.</p></section>
<section class="narrative" data-contract-section="limitations-uncertainty-and-robustness-checks"><h2>The result is predictive evidence, not a causal claim</h2><p>The paired route bootstrap places the median official-score gain away from zero, and all station medians move in the same direction. However, historical driver sequences are demonstrations rather than verified optima. The dataset does not identify effects on driver workload, service time, safety, or delivery success. Package time windows and service duration are not hard constraints in the current constructor.</p><div class="caveat"><strong>Metric caveat.</strong> The official sequence-deviation formula has permutation edge cases: an exact reverse traversal can receive zero sequence deviation. The project preserves the reference implementation and therefore triangulates conclusions with pairwise disagreement, travel time, adjacent-edge recall, and zone re-entry.</div></section>
<section class="narrative" data-contract-section="recommended-next-steps"><h2>Recommended next steps</h2><ul><li>Add package time-window and service-duration feasibility checks.</li><li>Evaluate a station-adaptive preference weight with nested validation, retaining the current global model as the benchmark.</li><li>Run ablations for exact-zone, parent-zone, and global back-off components.</li><li>Stress-test temporal transfer beyond the short 2018 observation window before making deployment claims.</li></ul></section>
<section class="narrative" data-contract-section="further-questions"><h2>Further questions</h2><ul><li>Do learned preferences reduce cognitive load, or merely reproduce operational habits?</li><li>Which station characteristics explain effect-size heterogeneity?</li><li>Can time-window feasibility be added without eroding the driver-likeness gain?</li></ul></section>
</article></main></div><!-- DATA_ANALYTICS_HTML_REPORT_RUNTIME --></body></html>'''
    (REPORT / "report-shell.html").write_text(report_html, encoding="utf-8")
    print(REPORT / "report-shell.html")


if __name__ == "__main__":
    main()
