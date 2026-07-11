# CV and Interview Notes

## Recommended title

**Learning-Augmented Human-Centric Last-Mile Routing** | Python, Operations Research, Interpretable Machine Learning

## CV bullets

- Formulated last-mile routing as an interpretable learning-augmented graph problem, combining normalized directed travel costs with hierarchically smoothed pairwise zone-precedence estimates learned from 6,112 Amazon delivery routes.
- Reduced aggregate median official route score by **39.9%** versus nearest-neighbour routing on 926 untouched chronological test routes, improving **88.1%** of routes with a **4.83%** paired median travel-time increase under validation-only model selection.
- Characterized the Pareto trade-off between travel efficiency and behavioral imitation through toy analysis, preference-weight sensitivity, structural ablation, and route-level robustness; showed that weight 2 is validation-efficient while stronger weights are dominated, and separated zone-contiguity effects from learned zone ordering.

## 30-second interview explanation

I framed the project as a learning-augmented routing trade-off rather than another black-box route predictor. Historical routes provide smoothed pairwise probabilities that one delivery zone precedes another. At each step, the planner combines normalized directed travel time with an interpretable preference penalty, then exhausts the selected zone by nearest neighbour. A toy directed graph explains the limiting cases, and validation experiments trace the Pareto frontier. Weight 2 was selected under a predeclared 5% median travel-time guardrail. On 926 untouched test routes, it reduced the aggregate median official score by 39.9% and improved 88.1% of routes at a 4.83% paired median travel-time increase.

## The most important conceptual distinction

Zero zone re-entry is a consequence of the zone-exhaustion construction, not evidence that the preference model learned contiguity. Learning contributes the order of the zone blocks. The angular zone baseline also has zero median re-entry but performs much worse on official score and travel time, which isolates the value of learned ordering.

## What not to claim

- Do not call the method globally optimal, competition-winning, or a complete vehicle-routing solver.
- Do not claim it reduces actual delivery time, driver workload, fuel, emissions, or safety risk.
- Do not call the result causal.
- Do not attribute zero zone re-entry solely to learning.
- Do not imply package time windows are enforced.
- Say “aggregate median score reduction” for the 39.9% number because it compares method-level medians.

## Likely viva questions

**What exactly is optimized?**
At each zone decision, the greedy rule minimizes normalized directed travel time plus a weight times one minus the average learned probability that the candidate zone precedes the other remaining zones. It is a sequence of local decisions, not one globally optimized tour objective.

**What happens at weight zero?**
Weight zero removes the learned preference term, but the algorithm still selects and exhausts complete zones. It is therefore a zone-contiguous distance heuristic, not stop-level nearest neighbour.

**Why pairwise zone precedence?**
It is interpretable, data-efficient, and supports hierarchical fallback from exact station-zone pairs to parent-zone and global evidence.

**How do you know the result is not only caused by zone contiguity?**
The angular zone sweep also enforces contiguity and has zero median re-entry, yet its median official score is 0.0978 and median travel time is 13,021.5 seconds. Learned pairwise ordering reaches 0.0607 at 11,740.0 seconds.

**Why choose weight 2?**
Among the prespecified weights satisfying the validation median travel-time guardrail, weight 2 had the lowest median pairwise disagreement. It also lies on the empirical official-score/travel-time frontier; weights 4 and 8 are dominated and breach the guardrail.

**Why chronological splitting?**
It prevents future route patterns from leaking into preference estimates and tests forward temporal transfer within each station.

**What is the main limitation?**
The greedy rule has no global optimality guarantee, historical route imitation does not establish operational benefit causally, and time-window feasibility is not enforced.
