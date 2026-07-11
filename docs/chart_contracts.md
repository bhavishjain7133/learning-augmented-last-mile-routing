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
## Toy routing trade-off

- Question: How does the preference weight change the route on a small directed graph?
- Takeaway: the route changes only after a threshold; stronger learned alignment can require additional path cost.
- Family: relationship; connected scatter with consolidated regime labels.
- Data: 6 declared weights and 2 unique toy route regimes.
- Surface: static Matplotlib output in the mathematical notebook.
- Palette: single blue root with direct labels.
- Output: artifacts/research_story/toy_tradeoff.png.

## Empirical validation Pareto frontier

- Question: Which preference weights are efficient in median official score and travel-time cost?
- Takeaway: weight 2 is on the frontier and inside the guardrail; weights 4 and 8 are dominated and outside the guardrail.
- Family: relationship and uncertainty/benchmark; connected frontier with open dominated points and a guardrail reference.
- Data: 7 weight-level aggregates from 916 chronological validation routes.
- Surface: static Matplotlib output in the mathematical notebook.
- Palette: blue frontier, gold open dominated points, dark-neutral guardrail.
- Output: artifacts/research_story/empirical_pareto_frontier.png.

## Structural and learned-routing ablation

- Question: Does learned ordering add value beyond merely exhausting zones?
- Takeaway: angular zone sweep also eliminates median re-entry but has much worse official score and travel time than learned pairwise-zone routing.
- Family: comparison; two-panel categorical bar chart.
- Data: 3 algorithmic methods over 926 untouched test routes.
- Surface: static Matplotlib output in the mathematical notebook.
- Palette: neutral nearest-neighbour, open blue structural baseline, blue learned method.
- Output: artifacts/research_story/method_ablation.png.
