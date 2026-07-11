# Chart Contracts

## Route volume by station

- Question: Is route volume concentrated in a small number of stations?
- Takeaway: identify station imbalance for split reporting and weighting.
- Family: comparison; sorted horizontal bar.
- Data: 17 station-level rows.
- Surface: static Matplotlib output in the data-audit notebook.
- Palette: single blue root, dark keyline, direct labels.
- Output: `artifacts/data_audit/routes_by_station.png`.

## Stops per route

- Question: What is the operational size distribution of route instances?
- Takeaway: establish spread before selecting algorithmic complexity.
- Family: distribution; histogram with median reference.
- Data: 6,112 route-level observations.
- Surface: static Matplotlib output in the data-audit notebook.
- Palette: single blue root plus dark-neutral reference.
- Output: `artifacts/data_audit/stops_per_route.png`.

## Validation preference trade-off

- Question: Which preference weight best reduces driver disagreement without breaching the travel-time guardrail?
- Takeaway: weight 2 is the strongest eligible validation setting; weights 4 and 8 breach the 5% median guardrail.
- Family: relationship; connected scatter with direct weight labels and guardrail reference.
- Data: 7 validation-weight aggregates from 916 routes.
- Surface: Matplotlib notebook figure and Recharts HTML report chart with inline-SVG fallback.
- Palette: single blue root, gold selected-point outline, dark-neutral guardrail.
- Outputs: `artifacts/confirmatory_results/validation_tradeoff.png` and `report/report.html`.

## Paired official-score difference

- Question: Is the test improvement broad-based or driven by a few routes?
- Takeaway: most route-level differences favour the learned model; the paired median is -0.0421.
- Family: distribution; histogram with zero and median references.
- Data: 926 paired route-level differences.
- Surface: static Matplotlib output in the confirmatory notebook.
- Palette: blue distribution, gold median, dark-neutral zero line.
- Output: `artifacts/confirmatory_results/paired_official_score_delta.png`.

## Route-level operational trade-off

- Question: How does official-score improvement vary with travel-time change route by route?
- Takeaway: most routes improve driver-likeness, but travel-time cost is heterogeneous and includes outliers.
- Family: relationship; scatter with zero axes and a 5% reference.
- Data: 926 test routes at route grain.
- Surface: static Matplotlib output in the confirmatory notebook.
- Palette: single blue root plus gold/dark references.
- Output: `artifacts/confirmatory_results/route_level_tradeoff.png`.

## Station heterogeneity

- Question: Does the aggregate official-score gain hold across delivery stations?
- Takeaway: all 17 station medians favour the learned model, with materially different effect sizes.
- Family: comparison; sorted signed horizontal bars.
- Data: 17 station aggregates from 926 test routes.
- Surface: Matplotlib notebook figure and Recharts HTML report chart with inline-SVG fallback.
- Palette: single blue root, dark zero line, direct signed labels.
- Outputs: `artifacts/confirmatory_results/station_heterogeneity.png` and `report/report.html`.
