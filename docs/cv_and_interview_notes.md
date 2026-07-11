# CV and Interview Notes

## Recommended title

**Learning from Drivers for Human-Centric Last-Mile Routing** | Python, NumPy, pandas, scikit-learn, Matplotlib

## CV bullets

- Developed an interpretable hierarchical pairwise zone-preference model on 6,112 public Amazon last-mile routes using station-aware chronological train/validation/test splits and the official challenge scorer.
- Reduced aggregate median official route score by **39.9%** versus nearest-neighbour routing on 926 untouched test routes, improving **88.1%** of routes while limiting the paired median travel-time increase to **4.83%** through validation-only model selection.
- Eliminated median zone re-entry (21 to 0) and built a reproducible streaming evaluation pipeline for a 1.8 GB directed travel-time dataset, with unit tests, executed notebooks, uncertainty analysis, and a self-contained technical report.

Use all three bullets only when space permits. For a one-page CV, keep the first two.

## 30-second interview explanation

Distance-only routes can look efficient but conflict with tacit driver knowledge about the order in which delivery zones are usually served. I learned interpretable pairwise zone-ordering preferences from historical routes, with station and hierarchy-aware fallback for sparse cases, and combined them with directed travel time during route construction. I selected the preference weight only on chronological validation data under a 5% median travel-time guardrail. On 926 untouched test routes, the model reduced the aggregate median official Amazon route score by 39.9% and improved 88.1% of routes, at a 4.83% paired median travel-time increase.

## What not to claim

- Do not call the method globally optimal or competition-winning.
- Do not claim it reduces actual delivery time, driver workload, fuel, or emissions.
- Do not call the result causal.
- Do not imply package time windows are enforced; they are a stated extension.
- Say “aggregate median score reduction” for the 39.9% number, because it compares method-level medians.

## Likely viva questions

**Why chronological splitting?** To prevent future route patterns from leaking into preference estimates and to test forward temporal transfer within each station.

**Why not optimize only travel time?** The research question is a constrained behavioral-imitation problem: improve driver-likeness while bounding operational cost, not replace one objective with another.

**Why pairwise zone precedence?** It is interpretable, data-efficient, and naturally supports hierarchical fallback when exact zone pairs are sparse.

**Why is the travel-time increase acceptable?** It was not declared acceptable after seeing test results. The 5% median guardrail and selection rule were fixed on validation data; the untouched test median was 4.83%.

**What is the main limitation?** Historical route imitation does not establish driver preference or operational benefit causally, and the current model does not enforce package time-window feasibility.
