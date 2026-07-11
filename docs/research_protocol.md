# Research Protocol

## Question

Can an interpretable model of driver zone-transition preferences improve
sequence similarity relative to distance-only routing without causing a large
increase in travel time or zone backtracking?

## Unit and hypotheses

The unit of analysis is one historical delivery route. Stop and edge records are
nested within routes and are never split independently.

1. The learned-preference hybrid should reduce pairwise sequence disagreement
   relative to nearest-neighbour routing on held-out routes.
2. Its travel-time increase relative to the strongest distance-only baseline
   must be reported rather than hidden inside a composite score.
3. Station and route-quality subgroup results are descriptive and not tuned.

## Split policy

Routes are ordered chronologically within station: earliest 70% train, next 15%
validation, latest 15% test. The public evaluation set is reserved for an
optional final external check.

## Baselines

1. observed driver sequence (reference);
2. geodesic nearest neighbour;
3. travel-time nearest neighbour;
4. angular zone sweep plus within-zone nearest neighbour;
5. 2-opt initialized by nearest neighbour;
6. learned zone-transition preference plus travel cost.

## Metrics

- supplied travel time and geodesic proxy distance;
- normalized pairwise sequence disagreement;
- adjacent-edge recall;
- zone re-entry/backtracking count;
- runtime and route validity.

Report medians, interquartile ranges, paired differences, bootstrap confidence
intervals, and the fraction of routes improved.

## Leakage and claim controls

- split routes before fitting transition counts or scalers;
- never use actual test sequences as route-construction features;
- do not use route-quality label as a predictive feature;
- fit station statistics on training data only;
- tune the preference weight on validation routes and freeze it before test;
- publish no numerical claim until the experiment and an independent metric
  spot-check are preserved in a reproducible artifact.

