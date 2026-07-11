# Report Source Notes

Audience: technical. Delivery mode: portable self-contained HTML because the native report renderer was unavailable in this Codex desktop session.

Required section map: title; technical summary; key findings; scope/data/metric definitions; methodology; limitations/uncertainty/robustness; recommended next steps; further questions. All are present in `report.html`.

Evidence inputs:

- `artifacts/travel_time_experiment/run_metadata.json`
- `artifacts/travel_time_experiment/validation_route_results.csv`
- `artifacts/travel_time_experiment/test_route_results.csv`
- `artifacts/confirmatory_results/headline_metrics.json`
- `artifacts/confirmatory_results/validation_tradeoff.csv`
- `artifacts/confirmatory_results/test_method_summary.csv`
- `artifacts/confirmatory_results/station_summary.csv`

Visual QA:

- Desktop: 2/2 live Recharts mounts rendered as SVG; no console errors; no page overflow; chart labels remained inside their cards.
- Narrow viewport: 390 x 844 override; one-column metric cards; horizontal chart scrolling enabled; no page overflow.
- No-JavaScript shell: 2/2 inline-SVG fallbacks visible and no page overflow.
- Source provenance: 35 source-tooltip affordances, including a visible Source control on both chart figures.

Omitted from the HTML report: the full route-level scatter and paired-difference histogram remain in the executed notebook because the report reading path is clearer with the validation trade-off, exact method table, and station heterogeneity chart. No evidence is omitted from the notebook.
