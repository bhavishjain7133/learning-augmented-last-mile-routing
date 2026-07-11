# Research Protocol

## Question

Can an interpretable model of driver zone-ordering preferences improve sequence similarity relative to distance-only routing without causing a large increase in supplied travel time?

## Unit and hypotheses

The unit of analysis is one historical delivery route. Stop and edge records are nested within routes and are never split independently.

1. The learned-preference hybrid should reduce pairwise sequence disagreement relative to nearest-neighbour routing on held-out routes.
2. Its travel-time increase relative to the strongest distance-only baseline must be reported rather than hidden inside a composite score.
3. Station and route-quality subgroup results are descriptive and not tuned.
4. Structural zone coherence and learned zone ordering must be evaluated separately.

## Mathematical decision rule

For station \(s\), the model estimates a smoothed pairwise probability

\[
\widehat p_s(a\prec b)
=
\frac{N_s(a\prec b)+\alpha}
     {N_s(a\prec b)+N_s(b\prec a)+2\alpha}.
\]

Evidence backs off from exact station-zone pairs to station parent-zone pairs, global parent-zone pairs, and finally a neutral probability of \(0.5\).

At current stop \(i\), candidate zone \(q\), and remaining-zone set \(R\), the implemented greedy decision minimizes

\[
J_w(q\mid i,R)
=
\frac{\min_{j:z(j)=q}d_{ij}}
     {\operatorname{median}_{r\in R}\min_{j:z(j)=r}d_{ij}}
+
w\left[
1-\frac{1}{|R|-1}
\sum_{r\in R\setminus\{q\}}\widehat p_s(q\prec r)
\right].
\]

After selecting a zone, within-zone nearest neighbour exhausts all of its stops.

Interpretation controls:

- the rule is a local greedy heuristic, not a globally optimal route solver;
- \(w=0\) remains zone-contiguous and is not equivalent to stop-level nearest neighbour;
- zone exhaustion structurally produces zero re-entry when zone labels are fixed;
- learned probabilities determine zone-block ordering, not contiguity itself;
- pairwise estimates need not be transitive.

## Split policy

Routes are ordered chronologically within station: earliest 70% train, next 15% validation, latest 15% test. The public evaluation set is reserved for an optional final external check.

## Baselines

1. observed driver sequence (reference only; its official score is zero by definition);
2. geodesic nearest neighbour;
3. travel-time nearest neighbour;
4. angular zone sweep plus within-zone nearest neighbour;
5. 2-opt initialized by nearest neighbour;
6. pairwise learned zone ordering plus within-zone nearest neighbour.

The angular zone baseline is the key structural ablation because it enforces zone contiguity without using learned pairwise precedence.

## Model selection

The declared preference-weight grid is \(w\in\{0,0.25,0.5,1,2,4,8\}\).

The selected weight is the setting with the lowest validation median pairwise disagreement among settings whose median supplied-travel-time increase is at most 5% relative to nearest neighbour. This rule is frozen before test evaluation.

The validation frontier is additionally inspected for Pareto dominance using median supplied-travel-time increase and median official score. This analysis explains model behaviour but does not replace the predeclared selection rule.

## Metrics

- supplied travel time and geodesic proxy distance;
- official Amazon challenge route score;
- normalized pairwise sequence disagreement;
- adjacent-edge recall;
- zone re-entry/backtracking count;
- runtime and route validity.

Report medians, paired differences, bootstrap confidence intervals, and the fraction of routes improved. Use several sequence metrics because the official sequence-deviation formula has permutation edge cases.

## Leakage and claim controls

- split routes before fitting transition counts or scalers;
- never use actual validation or test sequences as route-construction features;
- do not use route-quality label as a predictive feature;
- fit station statistics on training data only;
- tune the preference weight on validation routes and freeze it before test;
- attribute zero re-entry to the construction rule rather than to preference learning;
- do not claim causal effects on workload, safety, fuel, emissions, or delivery outcomes;
- publish no numerical claim until the experiment and an independent metric spot-check are preserved in a reproducible artifact.
