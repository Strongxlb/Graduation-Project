# Revision results log (post-review)

All experiments run against the frozen three-zone baseline in `wq_common.py`.
Environment: conda env `water-supply` (numpy 2.4.2, wntr 1.4.0). Cache in `baseline_cache/`.

Convention: `σ = 0.1 mg/L` is **one standard deviation** of the Gaussian observation error.
Wall coefficients are reported in `m/day`; the bulk coefficient `k_b` in `day⁻¹`.

---

## Step 1 — frozen baseline (reproduces draft §4.4)

Config: monitors `107/113/15/145/209/231`; inlet 1.0, tank 0.5; 72 h sim, 24 h warm-up,
1 h reporting, 5 min quality step; `k_b = -0.5`; true `(k_w,old, k_w,avg, k_w,new) = (-1.0, -0.1, -0.05) m/day`;
noise seed 42, sample seed 0; 2000 uniform-prior draws; behavioural `RMSE < 0.12`.

Reproduction check (cache vs draft) — **exact match**:

| quantity | cache | draft |
|---|---|---|
| behavioural | 1685/2000 (84.25%) | 1685/2000 (84%) |
| min RMSE | 0.0979 | 0.098 |
| clipped points | 28 | 28 |
| post-warm-up hours | 49 | 49 |
| junctions | 92 | 92 |
| k_w,old | -0.961 ± 0.317 | -0.96 ± 0.32 |
| k_w,avg | -0.120 ± 0.045 | -0.12 ± 0.045 |
| k_w,new | -0.053 ± 0.027 | -0.053 ± 0.027 |

Cache `baseline.npz` holds all 2000 candidate predictions `C_all (2000 × 49 × 92)`, so
Steps 3/6/8 recompute RMSE and weights **without re-running EPANET**.

---

## Step 2 — prior vs behavioural identifiability (corrects the overclaim)

Prior SD of a uniform range `[a, b]`:

```
prior_SD = (b − a) / √12
```

| Group | Prior range | Prior mid | Prior SD | Beh. mean | Beh. SD | SD retained | Mean shift toward truth (prior SD) | True |
|---|---|---|---|---|---|---|---|---|
| old | [-1.5, -0.2] | -0.850 | 0.375 | -0.961 | 0.317 | 84.5% | 0.30 | -1.00 |
| average | [-0.2, -0.04] | -0.120 | 0.046 | -0.120 | 0.045 | 98.0% | 0.00 | -0.10 |
| new | [-0.10, -0.005] | -0.0525 | 0.027 | -0.053 | 0.027 | 98.9% | 0.03 | -0.05 |

Interpretation:

- **old — partially informed**: distribution contracts to 84.5% of prior width and the
  weighted mean moves 0.30 prior SD toward the truth (of the 0.40 prior SD the truth sits
  from the midpoint).
- **average / new — effectively not informed**: distributions retain 98–99% of prior width
  and the weighted means sit on the prior midpoints. Their apparent agreement with the true
  values is a consequence of the prior ranges having been centred near those values.

Deleted overclaim (was in §4.4): *"The weighted mean of every group lies close to its true value."*
Applied to draft `..._06.docx` (overclaim removed, table inserted, average restated as
"essentially unconstrained"; Conclusion updated). Final table numbers to be locked in the
Step-11 rewrite (draft currently rounds 98%/99% to 97%/98%).

---

## Step 3 — behavioural-threshold sensitivity (no EPANET re-run)

Sampling SD of the RMSE statistic at the truth:

```
sd(RMSE) ≈ σ / √(2N) = 0.10 / √(2·294) = 0.0041 mg/L      (N = 6 monitors × 49 h = 294)
```

Observed minimum RMSE = 0.0979 mg/L.

| Threshold | Retained | Retention | SD above noise floor | old SD retained | avg SD retained | new SD retained | band node15 | band node107 | nonzero-risk nodes |
|---|---|---|---|---|---|---|---|---|---|
| 0.107 | 1126 | 56.3% | 1.70 | 69.1% | 91.4% | 88.8% | 0.098 | 0.077 | 25 |
| 0.110 | 1323 | 66.1% | 2.42 | 73.1% | 94.3% | 93.1% | 0.106 | 0.079 | 25 |
| 0.120 | 1685 | 84.3% | 4.85 | 84.5% | 98.0% | 98.9% | 0.140 | 0.082 | 25 |

Weighted means: old moves toward the truth as the threshold tightens
(-0.961 → -1.026 → -1.044); average/new stay on the prior midpoint at every threshold.

Top-6 risk nodes are **stable** across thresholds:
`131 > 243 > 141 > 139 > 15 > 143` (nonzero-risk node count fixed at 25).

Conclusions:

- The original 0.12 threshold sits 4.85 sd(RMSE) above the noise floor, so a parameter set
  at the truth passes with near-certainty — the filter only rejects grossly wrong sets.
- Tightening to a defensible ≈95% band (0.107) sharpens **old** but leaves **average/new**
  at the prior, so their non-identifiability is a property of the monitoring array, not the
  threshold.
- The operational risk ranking is robust to the threshold choice.
