# Sudoku Solver Sensitivity — Confirmatory Protocol v1

## 1. Study Objective

This experiment tests whether pre-solve structural characteristics of a
Sudoku puzzle are associated with its sensitivity to a controlled change
in search strategy.

The confirmatory experiment follows an exploratory 100-puzzle pilot.
The pilot is not used as confirmatory evidence.

---

## 2. Research Question

Can pre-solve Sudoku constraint structure explain variation in search
complexity when the variable-selection strategy of an otherwise
controlled recursive backtracking solver is changed?

---

## 3. Experimental Unit

The base experimental unit is a Sudoku puzzle P.

Each puzzle is evaluated under two deterministic solver configurations:

1. BT_NAIVE v1.0
2. BT_MRV v1.0

This produces paired observations for every puzzle.

---

## 4. Frozen Solver Configurations

### BT_NAIVE v1.0

- Recursive backtracking
- First empty cell in row-major order
- Candidate order 1 through 9
- Deterministic execution
- Existing instrumentation semantics remain unchanged

### BT_MRV v1.0

Identical to BT_NAIVE except for variable selection:

- Select the empty cell with minimum remaining values (MRV)
- Ties resolved by first occurrence in row-major order
- Candidate order remains 1 through 9
- Deterministic execution

No solver modification is permitted after confirmatory data collection
begins.

---

## 5. Instrumentation

Primary search-effort measure:

- recursive_calls

Secondary search measures:

- candidate_checks
- committed_assignments
- backtracked_assignments
- backtrack_events
- search_nodes
- max_depth

The following invariants must hold:

candidate_checks =
constraint_rejections + committed_assignments

recursive_calls =
committed_assignments + 1

committed_assignments - backtracked_assignments =
solution_depth

search_nodes =
recursive_calls

Any observation violating an invariant is rejected and investigated
before analysis.

MRV candidate-domain evaluations used for variable selection are not
included in candidate_checks.

Therefore candidate_checks and recursive_calls in this experiment
characterize search-tree behaviour rather than total computational work
performed by the heuristic.

Runtime is not a primary outcome in this protocol.

---

## 6. Primary Outcome

For puzzle P:

SSI(P) =
ln((Calls_NAIVE(P) + 1) /
   (Calls_MRV(P) + 1))

Interpretation:

SSI > 0:
BT_MRV required fewer recursive calls.

SSI = 0:
Both strategies required equal recursive calls.

SSI < 0:
BT_MRV required more recursive calls.

SSI is an operational log-ratio measure used in this study.

No claim of novelty for the metric is made.

---

## 7. Secondary Outcomes

The raw paired outcomes are retained:

Calls_NAIVE(P)

Calls_MRV(P)

Additional descriptive quantities include:

- NAIVE/MRV recursive-call ratio
- proportion of puzzles where MRV uses fewer calls
- proportion with equal calls
- proportion where MRV uses more calls
- cross-solver rank correlation

SSI will not replace reporting of the underlying raw search costs.

---

## 8. Pre-Solve Structural Variables

The confirmatory analysis will use variables selected before examination
of the confirmatory results.

### Density baseline

- empty_cells

### Candidate-domain structure

- mean_domain_size
- candidate_domain_entropy
- pair_ratio

These were selected from the exploratory pilot because they showed the
strongest associations with solver sensitivity.

They are not treated as independent discoveries because they may encode
related aspects of constraint structure.

### Secondary structural controls

- domain_variance
- singleton_ratio
- triple_ratio
- row_clue_variance
- column_clue_variance
- box_clue_variance

### Propagation variables

The previously frozen naked-single propagation protocol is retained.

Propagation features are secondary because the exploratory pilot showed
weak associations with solver sensitivity.

No new structural feature will be introduced after confirmatory results
have been inspected.

---

## 9. Confirmatory Hypotheses

### H1 — Structural sensitivity

Pre-solve constraint structure is associated with solver sensitivity
SSI.

### H1a — Puzzle density

Greater empty-cell count is associated with higher SSI.

Expected direction:

positive.

### H1b — Candidate-domain breadth

Greater mean candidate-domain size is associated with higher SSI.

Expected direction:

positive.

### H1c — Candidate-domain entropy

Greater candidate-domain entropy is associated with higher SSI.

Expected direction:

positive.

### H1d — Pair prevalence

Greater pair ratio is associated with lower SSI.

Expected direction:

negative.

These directional hypotheses were formulated from exploratory pilot
results and must therefore be evaluated on independent confirmatory
data.

---

## 10. Primary Statistical Analysis

For each prespecified primary structural variable, report:

- Pearson correlation with SSI
- Spearman rank correlation with SSI
- sample size
- effect direction

Spearman association is emphasized because search-complexity
distributions may be strongly skewed.

Effect sizes and uncertainty should be reported rather than relying only
on significance thresholds.

A multivariable model may subsequently test whether candidate-domain
features explain variation beyond the density baseline.

The density-only model must remain an explicit baseline.

---

## 11. Exploratory vs Confirmatory Separation

The original 100-puzzle dataset is designated:

EXPLORATORY PILOT

It was used to:

- develop instrumentation
- debug the experimental pipeline
- select structural variables
- formulate directional hypotheses

It must not be included in the primary confirmatory dataset.

Results from the pilot and confirmatory sample must be reported
separately.

---

## 12. Confirmatory Dataset

The confirmatory dataset must contain puzzles not included in the
100-puzzle exploratory pilot.

### Sample size

The primary confirmatory sample will contain exactly 10,000 unique
Sudoku puzzles.

### Stratified sampling

The Sudoku Exchange source difficulty categories will be sampled
separately:

- Easy: 2,500 puzzles
- Medium: 2,500 puzzles
- Hard: 2,500 puzzles
- Diabolical: 2,500 puzzles

Total:

10,000 puzzles.

This stratification is intended to provide controlled coverage across
the four source categories. It does not imply that these categories are
equally prevalent in any broader Sudoku population.

### Pilot exclusion

Every puzzle appearing in the 100-puzzle exploratory pilot must be
excluded before confirmatory sampling.

Exclusion must be based on the canonical 81-cell puzzle representation,
not only puzzle ID.

### Duplicate handling

Exact duplicate puzzle strings must not occur in the confirmatory
sample.

Duplicate detection must operate on the canonical 81-cell puzzle
representation.

If the same puzzle occurs more than once in the source data, only one
instance may be eligible for the confirmatory sample.

### Sampling seed

The confirmatory sampling seed is:

20261003

The same seed must reproduce the same selected puzzle set when applied
to the same source files and sampling implementation.

### Sampling order

For each source difficulty stratum:

1. Read and validate source records.
2. Convert each puzzle to the canonical 81-cell representation.
3. Reject malformed records.
4. Exclude puzzles appearing in the exploratory pilot.
5. Remove exact duplicate puzzle strings.
6. Apply deterministic seeded sampling.
7. Select exactly 2,500 puzzles.

No solver-derived information or structural feature values may be used
during puzzle selection.

### Confirmatory identifiers

Selected puzzles will receive deterministic confirmatory identifiers:

- CE00001 onward for Easy
- CM00001 onward for Medium
- CH00001 onward for Hard
- CD00001 onward for Diabolical

Source difficulty labels are retained as metadata and are not treated as
ground-truth computational difficulty.

## 13. Source Difficulty Labels

Source difficulty labels are retained as metadata.

They are not treated as ground-truth computational complexity labels.

Solver-specific search complexity is measured directly using the
instrumented solvers.

---

## 14. Data Integrity

Before statistical analysis:

1. Puzzle IDs must be unique.
2. Puzzle strings must be valid.
3. Exact duplicate puzzle strings must be detected.
4. Both solvers must process the same puzzle set.
5. Both solutions must be valid.
6. Instrumentation invariants must pass.
7. Solver metadata must match the executable configuration.
8. Failed observations must be logged rather than silently removed.

---

## 15. Exclusion Rules

A puzzle may be excluded only for a documented technical reason such as:

- malformed puzzle representation
- invalid initial Sudoku state
- solver failure
- invalid returned solution
- instrumentation invariant failure
- exact duplicate puzzle

Puzzles must not be excluded because they produce unusually high or low
SSI values.

MRV-worse cases must remain in the analysis if otherwise valid.

---

## 16. Reproducibility

The confirmatory experiment must record:

- dataset source
- sampling procedure
- random seed
- solver version
- feature extractor version
- experiment code version
- puzzle count
- rejected-record count
- reason for every rejection

Generated results must be reproducible from repository code and source
data.

---

## 17. Interpretation Limits

The experiment evaluates search-tree sensitivity to a controlled
variable-selection intervention.

It does not by itself establish:

- human Sudoku difficulty
- universal Sudoku difficulty
- total computational superiority of MRV
- causal effects of individual structural features
- generalization to all Sudoku solving algorithms

Generalization beyond BT_NAIVE and BT_MRV requires additional solver
families or independent experiments.

---

## 18. Protocol Freeze

This document must be committed before the confirmatory dataset is
analyzed.

Changes made after confirmatory results are inspected must be documented
as protocol amendments and must not be presented as preregistered
decisions.