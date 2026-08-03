# Revision results log (post-review)

All experiments run against the frozen three-zone baseline in `wq_common.py`.
Environment: conda env `water-supply` (numpy 2.4.2, wntr 1.4.0). Cache in `baseline_cache/`.

Convention: `σ = 0.1 mg/L` is **one standard deviation** of the Gaussian observation error.
Wall coefficients are reported in `m/day`; the bulk coefficient `k_b` in `day⁻¹`.

**Sensor-error convention (Priority 2 #8).** Throughout, a stated sensor-error level `±X mg/L`
means the Gaussian **standard deviation σ = X**, *not* a 95% interval or a hard error bound. This
matters: read instead as a 95% band, "±0.1 mg/L" would imply `σ ≈ 0.1 / 1.96 ≈ 0.05 mg/L` and would
**halve every reported uncertainty interval** (±1σ covers ≈68%; ±1.96σ = ±0.196 covers ≈95%).
Draft fix — one sentence for the Methodology: *"In this study the stated sensor-error levels refer
to the Gaussian standard deviation σ, not to a 95% interval or a hard error bound."*

---

## Files and how to reproduce

Every number in this log is produced by a script; nothing is hand-entered.


| file                             | purpose                                                                                         | writes                                                                |
| -------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `wq_common.py`                   | frozen baseline config + WNTR/EPANET helpers (monitors, zone assignment, seeds, priors, timing) | — (imported by all step scripts)                                      |
| `step1_freeze_baseline.py`       | build synthetic truth + noisy observations + 2000-draw GLUE; cache every prediction             | `baseline_cache/baseline.npz`, `baseline_cache/baseline_meta.json`    |
| `step3_threshold_sensitivity.py` | behavioural-threshold sweep, recomputed from the cache (no EPANET)                              | `baseline_cache/step3_threshold.json`                                 |
| `step4_displaced_prior.py`       | displaced-prior identifiability (single realisation, first look)                                | `baseline_cache/step4_displaced_prior.json`                           |
| `step4b_sensitivity_curves.py`   | single-parameter RMSE curves (why old is one-sided)                                             | `figures/step4b_sensitivity_curves.png`, `step4b_sensitivity.json`    |
| `step4d_displaced_robust.py`     | robust displaced-prior (30 noise × 2 thresholds, both directions)                               | `figures/step4d_displaced_robust.png`, `step4d_displaced_robust.json` |
| `step5_structural_error.py`      | structural error, ±20% pipe-level jitter                                                        | `figures/step5_structural_error.png`, `step5_structural_error.json`   |
| `step5c_jitter_sweep.py`         | structural error, jitter sweep ±20/35/50% (reuses cache)                                        | `figures/step5c_jitter_sweep.png`, `step5c_jitter_sweep.json`         |
| `step5d_structured.py`           | structural error, length-correlated within-zone (precise-but-biased)                            | `figures/step5d_structured.png`, `step5d_structured.json`             |
| `step6_noise_sensitivity.py`     | sensor-accuracy sweep σ=0.02/0.05/0.10/0.15 (threshold scales with σ)                            | `figures/step6_noise_sensitivity.png`, `step6_noise_sensitivity.json` |
| `step7_fisher.py`                | Fisher/CRLB a-priori identifiability (k_w, +k_b, +sensor offsets)                                | `figures/step7_fisher.png`, `step7_fisher.json` |
| `step7b_profile.py`              | profile likelihood (re-optimise others; ΔNLL 95% intervals)                                     | `figures/step7b_profile.png`, `step7b_profile.json` |
| `step8_sensor_bias.py`           | systematic sensor bias at node 15 (GLUE, empirical)                                             | `figures/step8_sensor_bias.png`, `step8_sensor_bias.json` |
| `step8b_kb_sensitivity.py`       | GLUE at k_b ± 20% — bulk–wall compensation (Priority-2 #5)                                       | `figures/step8b_kb_sensitivity.png`, `step8b_kb_sensitivity.json` |
| `step7c_ar1.py`                  | AR(1) covariance Fisher/CRLB (per-coefficient widening)                                          | `baseline_cache/step7c_ar1.json` |
| `step7c_profile_ar1.py`          | AR(1) profile likelihood (rebuilds 21³ residual grid)                                            | `baseline_cache/step7c_resid_grid.npy`, `step7c_profile_ar1.json` |
| `step8c_bias_bynode.py`          | sensor-bias location sweep across all six monitors                                              | `baseline_cache/step8c_bias_bynode.json` |
| `step9_zeroclip.py`              | zero-floor censoring (L=0): naive-exact-0 vs censored likelihood                                 | `figures/step9_zeroclip.png`, `step9_zeroclip.json` |
| `step10_risk_metrics.py`         | risk duration/depth (trapezoid, 48 h) + water-age corroboration                                 | `figures/step10_risk_metrics.png`, `step10_risk_metrics.json` |
| `step11_loo.py`                  | leave-one-monitor-out predictive validation                                                     | `figures/step11_loo.png`, `step11_loo.json` |
| `step12_scenarios.py`            | temperature/ageing scenario projection of the GLUE ensemble + dosing + risk register            | `figures/step12_*.png`, `step12_scenarios.json`, `step12_risk_register.csv` |


Run from the `Net3/` directory (conda env `water-supply`):

```
export MPLCONFIGDIR=../.mplcache
/opt/anaconda3/envs/water-supply/bin/python step1_freeze_baseline.py     # ~40 s (2000 EPANET runs)
/opt/anaconda3/envs/water-supply/bin/python step3_threshold_sensitivity.py   # instant (cache only)
/opt/anaconda3/envs/water-supply/bin/python step4_displaced_prior.py     # ~40 s (2000 EPANET runs)
```

`baseline_cache/baseline.npz` (~30 MB) is git-ignored; rebuild it with step 1. The small
`*.json` summaries and this log are version-controlled.

---

## Step 1 — frozen baseline (reproduces draft §4.4)

Config: monitors `107/113/15/145/209/231`; inlet 1.0, tank 0.5; 72 h sim, 24 h warm-up,
1 h reporting, 5 min quality step; `k_b = -0.5`; true `(k_w,old, k_w,avg, k_w,new) = (-1.0, -0.1, -0.05) m/day`;
noise seed 42, sample seed 0; 2000 uniform-prior draws; behavioural `RMSE < 0.12`.

Reproduction check (cache vs draft) — **exact match**:


| quantity           | cache              | draft           |
| ------------------ | ------------------ | --------------- |
| behavioural        | 1685/2000 (84.25%) | 1685/2000 (84%) |
| min RMSE           | 0.0979             | 0.098           |
| clipped points     | 28                 | 28              |
| post-warm-up hours | 49                 | 49              |
| junctions          | 92                 | 92              |
| k_w,old            | -0.961 ± 0.317     | -0.96 ± 0.32    |
| k_w,avg            | -0.120 ± 0.045     | -0.12 ± 0.045   |
| k_w,new            | -0.053 ± 0.027     | -0.053 ± 0.027  |


Cache `baseline.npz` holds all 2000 candidate predictions `C_all (2000 × 49 × 92)`, so
Steps 3/6/8 recompute RMSE and weights **without re-running EPANET**.

---

## Step 2 — prior vs behavioural identifiability (corrects the overclaim)

Prior SD of a uniform range `[a, b]`:

```
prior_SD = (b − a) / √12
```


| Group   | Prior range     | Prior mid | Prior SD | Beh. mean | Beh. SD | SD retained | Mean shift toward truth (prior SD) | True  |
| ------- | --------------- | --------- | -------- | --------- | ------- | ----------- | ---------------------------------- | ----- |
| old     | [-1.5, -0.2]    | -0.850    | 0.375    | -0.961    | 0.317   | 84.5%       | 0.30                               | -1.00 |
| average | [-0.2, -0.04]   | -0.120    | 0.046    | -0.120    | 0.045   | 98.0%       | 0.00                               | -0.10 |
| new     | [-0.10, -0.005] | -0.0525   | 0.027    | -0.053    | 0.027   | 98.9%       | 0.03                               | -0.05 |


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

Retention and objective-scale table:


| Threshold | Retained | Retention | SD above noise floor | band node15 | band node107 | nonzero-risk nodes |
| --------- | -------- | --------- | -------------------- | ----------- | ------------ | ------------------ |
| 0.107     | 1126     | 56.3%     | 1.70                 | 0.098       | 0.077        | 25                 |
| 0.110     | 1323     | 66.1%     | 2.42                 | 0.106       | 0.079        | 25                 |
| 0.120     | 1685     | 84.3%     | 4.85                 | 0.140       | 0.082        | 25                 |


Per-coefficient behavioural distribution — weighted `mean ± SD (mg/L)` with `SD retained`
(= behavioural SD / prior SD; prior SD = 0.375 / 0.046 / 0.027 for old / avg / new):


| Threshold | k_w,old mean ± SD (retained) | k_w,avg mean ± SD (retained) | k_w,new mean ± SD (retained) |
| --------- | ---------------------------- | ---------------------------- | ---------------------------- |
| 0.107     | -1.044 ± 0.259 (69.1%)       | -0.119 ± 0.042 (91.4%)       | -0.051 ± 0.024 (88.8%)       |
| 0.110     | -1.026 ± 0.274 (73.1%)       | -0.120 ± 0.044 (94.3%)       | -0.052 ± 0.026 (93.1%)       |
| 0.120     | -0.961 ± 0.317 (84.5%)       | -0.120 ± 0.045 (98.0%)       | -0.053 ± 0.027 (98.9%)       |


As the threshold tightens (0.120 → 0.107):

- **old sharpens**: SD 0.317 → 0.259 (SD retained 84.5% → 69.1%) and the mean moves toward
the truth (-0.961 → -1.044, true -1.0).
- **average / new barely change**: SD retained stays 89–98%, means stay on the prior
midpoint — they cannot be sharpened by any threshold, so their non-identifiability is a
property of the monitoring array, not the threshold.

Top-6 risk nodes are **stable** across thresholds:
`131 > 243 > 141 > 139 > 15 > 143` (nonzero-risk node count fixed at 25).

Conclusions:

- The original 0.12 threshold sits 4.85 sd(RMSE) above the noise floor, so a parameter set
at the truth passes with near-certainty — the filter only rejects grossly wrong sets.
- Tightening to a defensible ≈95% band (0.107) sharpens **old** but leaves **average/new**
at the prior, so their non-identifiability is a property of the monitoring array, not the
threshold.
- The operational risk ranking is robust to the threshold choice.

---

## Step 4 — displaced-prior experiment (PRELIMINARY, single noise realisation)

Same truth, same monitoring array, same baseline observations; **only the priors move**.
Each range keeps its width but its midpoint is set to `truth − 1 prior SD`. Displacement is
downward (toward stronger decay) because moving upward would make the upper bound positive;
all displaced ranges stay non-positive and still contain the truth (the truth then sits one
prior SD above the displaced midpoint).

Question: do the observations pull the behavioural mean back toward the truth?

behavioural 1755/2000 (87.8%), min RMSE 0.0979.


| Group   | Orig mid | Displaced range (mid)     | True  | Beh. mean ± SD | SD retained | Gap to truth closed |
| ------- | -------- | ------------------------- | ----- | -------------- | ----------- | ------------------- |
| old     | -0.850   | [-2.025, -0.725] (-1.375) | -1.00 | -1.341 ± 0.374 | 99.8%       | 9%                  |
| average | -0.120   | [-0.226, -0.066] (-0.146) | -0.10 | -0.141 ± 0.045 | 96.9%       | 12%                 |
| new     | -0.0525  | [-0.125, -0.030] (-0.077) | -0.05 | -0.071 ± 0.026 | 92.8%       | 22%                 |


("Gap to truth closed" = distance the behavioural mean travels from the displaced midpoint
toward the truth, as a fraction of the 1 prior SD gap.)

Preliminary reading:

- When the priors are displaced into the strong-decay regime, **none** of the three means is
pulled strongly back to the truth (only 9–22% of the gap closed).
- **old**, which was the informed coefficient in the baseline, is *not* recovered here: it
keeps 99.8% of its prior width and retention even rises to 88%. In the strong-decay regime
the old-zone residual is driven near zero (compounded by clipping), so RMSE is nearly flat
and the data cannot distinguish among strong values. This suggests **k_w,old is one-sidedly
identifiable**: the observations bound how *weak* old decay can be, not how strong.
- This connects to the Priority-2 censored-likelihood point (clipping concentrates in the
low-residual old zone).

Status: this single-realisation table is a first look. The robust version (30 noise
realisations × two thresholds, plus an old-toward-weaker displacement) is **Step 4c** below
and supersedes these numbers for reporting.

---

## Step 4b — single-parameter objective curves (why old is one-sided, avg/new flat)

Each coefficient is swept across (and beyond) its prior while the other two are held at the
truth; RMSE is computed against the baseline noisy observations
(`step4b_sensitivity_curves.py`). Noise-floor RMSE (all three at truth) = 0.098 mg/L.

Single-parameter objective: old is an asymmetric valley, avg/new are flat


| Coefficient | RMSE swing across its prior | reading                                                                                             |
| ----------- | --------------------------- | --------------------------------------------------------------------------------------------------- |
| old         | 0.045 mg/L (0.098 → 0.143)  | steep on the weak side (weak edge exceeds the 0.12 threshold → rejectable); flat on the strong side |
| avg         | 0.007 mg/L (0.098 → 0.105)  | whole prior below threshold → values indistinguishable                                              |
| new         | 0.009 mg/L (0.098 → 0.107)  | whole prior below threshold → values indistinguishable                                              |


- **old is an asymmetric valley**: the objective climbs above the behavioural threshold only on
the weak side, so the data reject weak old but cannot distinguish among strong values (flat
floor from about -0.9 to -2.2 m/day). This is the mechanism behind one-sided identifiability,
and reconciles Steps 2–3 with Step 4: old contracts under the baseline prior (which straddles
the steep wall) but not under the displaced strong-regime prior (which sits on the flat floor).
- **avg / new**: sweeping them across their entire prior moves the objective by < 0.01 mg/L —
comparable to sd(RMSE) = 0.004 and far below the 0.107/0.12 thresholds — so every value fits
the observations equally well. This is precisely why displaced ("wrong") avg/new values still
reproduce the monitored chlorine: the monitors are insensitive to them.

---

## Step 4c — robust displaced-prior (30 noise realisations × two thresholds)

Two displacement designs (`step4d_displaced_robust.py`), **each displacing all three**
coefficients (width fixed, truth kept inside), so every gap-closed value is meaningful. The two
designs differ only in old's direction:

- **DOWN**: old / avg / new midpoints all set to `truth − 1 prior SD` (strong-decay side).
- **OLDUP**: old midpoint set to `truth + 1 prior SD` (weak/steep side, upper bound capped at
−0.005 to stay non-positive); avg / new displaced down as in DOWN.

Each design: 2000 forward runs cached once, then the gap-closing statistic recomputed over 30
independent noisy observation sets and two thresholds. Reported as **median [IQR]** across noise.
`gap closed` = fraction of the displaced-midpoint → truth distance covered by the behavioural mean
(0% = stayed at prior midpoint, 100% = reached truth).

At threshold **0.12** (the draft's operative threshold; retention ≈88% DOWN / 66% OLDUP):


| coefficient | DOWN (old on strong side): gap (SD ret) | OLDUP (old on weak side): gap (SD ret) |
| ----------- | --------------------------------------- | -------------------------------------- |
| old         | 8% [7–11] (100%)                        | **60% [55–62] (70%)**                  |
| avg         | 11% [9–15] (97%)                        | 11% [9–15] (98%)                       |
| new         | 22% [16–32] (93%)                       | 14% [10–22] (95%)                      |


At threshold **0.107** (defensible ≈95% band; retention ≈46% DOWN / 33% OLDUP):


| coefficient | DOWN: gap (SD ret) | OLDUP: gap (SD ret)   |
| ----------- | ------------------ | --------------------- |
| old         | 37% [25–56] (91%)  | **84% [76–89] (56%)** |
| avg         | 39% [31–56] (87%)  | 36% [30–51] (91%)     |
| new         | 73% [59–86] (68%)  | 59% [43–79] (74%)     |


Displaced-prior pull-back over 30 noise realisations

Findings (robust):

1. **old is one-sidedly identifiable** (headline): on the weak/steep side (OLDUP) the mean is
  pulled 60% (thr 0.12) / 84% (thr 0.107) back to the truth and the distribution narrows to
   56–70%; on the strong side (DOWN) it barely moves (8% / 37%) and keeps ≈100% / 91% of the
   prior width. The observations bound how *weak* old can be, not how *strong* — exactly the
   asymmetric valley of Step 4b. (old's recovery is essentially unchanged whether avg/new are at
   baseline — earlier run gave 61%/86% — or displaced down here, 60%/84%, confirming avg/new do
   not affect old.)
2. **avg is not usefully informed and independent of old**: its pull-back is the *same* under
  DOWN and OLDUP (11% vs 11% at 0.12; 39% vs 36% at 0.107) and its width barely changes
   (97–98% at 0.12). old sitting on its good side does not rescue avg — the weak pull-back is
   avg's own marginal information, not compensation.
3. **new carries a genuine but weak signal that surfaces only near the noise floor**: the
  best-fitting samples do have new closer to the truth (so it is not pure noise), but the
   pull-back is strongly threshold-dependent — only 22% (DOWN) / 14% (OLDUP) at the operative
   0.12 with the width barely changed (93–95%), versus 73% / 59% at 0.107 where retention has
   collapsed to <half and the IQR is wide ([59–86] / [43–79]). This strong threshold-dependence,
   together with new's tiny marginal sensitivity (Step 4b RMSE swing 0.009), is itself the
   signature of a coefficient that is **not usefully identifiable**: it can be pinned only by a
   near-noise-floor threshold that retains too few samples to propagate.
4. **The threshold controls how much information surfaces**: at 0.12 everything stays low except
  old-on-its-good-side (60%); tightening to 0.107 (retaining <half the samples) inflates all
   pull-backs. This is the quantitative face of the §3.2 point that 0.12 is too loose. The
   ordering new > avg at 0.107 matches their objective sensitivity in Step 4b (RMSE swing
   0.009 > 0.007).

**Identifiability gradient (overall).** The controlled experiments give `old ≫ new > avg`:
old is (one-sidedly) robustly identifiable — recovered at the operative threshold; new carries
weak information usable only at an impractically tight threshold; avg is essentially uninformed
and independent of old. This is the quantitative, controlled version of the draft's
identifiability-gradient claim, and it is what should be reported instead of "successful recovery
of all three coefficients".

---

## Step 5 — structural-error experiment (breaks the inverse crime)

### Step 5a — mild within-zone heterogeneity (±20% pipe-level jitter)

Truth: each pipe `k_w,p = zone_mean × (1 + δ_p)`, `δ_p ~ U(-0.2, 0.2)`, seed 12345
(14 old / 37 avg / 66 new pipes). Fitted model: the same three-zone **homogeneous** model.
Same noise process (seed 42, σ=0.1, clip), same priors, **primary threshold 0.107**
(`step5_structural_error.py`; the draft's 0.12 gives the same qualitative result).

- **Noise-free structural residual** (best homogeneous fit vs the heterogeneous truth) =
**0.0069 mg/L** — only ~7% of the noise floor (0.092). The within-zone heterogeneity is
essentially invisible under σ = 0.1.
- Grid-search best fit (-1.067, -0.093, -0.052); GLUE 1080/2000 behavioural (thr 0.107), min RMSE 0.098.


| zone    | true arith. mean | length-weighted | pipe range     | GLUE mean ± SD | grid fit | bias (GLUE − arith) |
| ------- | ---------------- | --------------- | -------------- | -------------- | -------- | ------------------- |
| old     | -1.007           | -0.989          | [-1.17, -0.80] | -1.057 ± 0.252 | -1.067   | -0.051              |
| average | -0.098           | -0.096          | [-0.12, -0.08] | -0.117 ± 0.042 | -0.093   | -0.019              |
| new     | -0.049           | -0.047          | [-0.06, -0.04] | -0.051 ± 0.024 | -0.052   | -0.002              |


Risk top-6: GLUE `131,243,141,139,15,143` (= baseline); true field `131,243,15,143,139,141`
(same set, minor reorder).

Structural error ±20%: fitted homogeneous vs true heterogeneous field

**Finding (null / robustness).** ±20% *symmetric* within-zone heterogeneity produces **no
meaningful structural error**: the effective grouped coefficients match the true field averages to
within a fraction of the behavioural SD (biases −0.05 / −0.02 / −0.00, all < 0.25 SD), the
structural residual (0.007) is swamped by the noise (0.092), and the risk map is preserved. The
grouped model is **robust to mild within-zone heterogeneity**. This is *not* the "precise but
biased" pathology, because symmetric mean-zero jitter averages out — old's length-weighted mean
(−0.989) is essentially its arithmetic mean (−1.007), so the fit has nothing to be biased toward.

### Step 5b — heterogeneity magnitude sweep (±20 / 35 / 50%)

Same design, jitter magnitude increased (`step5c_jitter_sweep.py`; the homogeneous candidate
predictions are truth-independent, so the 2000 GLUE candidates are reused from the cache and only
the truth is re-simulated). Bias = GLUE behavioural mean − true per-zone arithmetic mean.


| jitter | structural residual (noise-free) | behavioural | old bias (SD)  | avg bias (SD)  | new bias (SD)  |
| ------ | -------------------------------- | ----------- | -------------- | -------------- | -------------- |
| ±20%   | 0.0069                           | 1080        | −0.051 (−0.20) | −0.019 (−0.46) | −0.002 (−0.08) |
| ±35%   | 0.0104                           | 1031        | −0.054 (−0.22) | −0.019 (−0.46) | −0.002 (−0.06) |
| ±50%   | 0.0146                           | 969         | −0.056 (−0.23) | −0.020 (−0.48) | −0.000 (−0.02) |


Bias vs within-zone jitter

**Finding.** The bias is flat and small (< 0.6 SD) even at ±50%; the structural residual grows
(0.007 → 0.015 mg/L) but stays far below the noise floor (0.092), and the risk ranking is
unchanged. The small avg/new "bias" is the prior-centring offset (GLUE mean = prior midpoint),
not structural. So symmetric within-zone heterogeneity does **not** produce a useful
precise-but-biased effect at any magnitude tested — it averages out. A genuine spatial bias would
require heterogeneity *correlated with the sensor flow paths* (residence-weighted ≠ arithmetic).

### Step 5c — structured (length-correlated) within-zone heterogeneity → precise-but-biased

Location-consistent design: the truth keeps the three **location** zones,
but within each zone `k_w` is **correlated with pipe length** (longer pipe → stronger decay,
factor 1 + 0.5·s, s ∈ [−1,1] by within-zone length rank). The per-zone **arithmetic** mean is held
exactly at the zone mean, but the **length-weighted** (≈ residence-weighted, i.e. effective) mean
is shifted stronger (`step5d_structured.py`, threshold 0.107; GLUE candidates reused from cache).

| zone | true arith. | length-weighted | GLUE mean ± SD | grid fit | bias (GLUE − arith) | lenwt − arith |
|---|---|---|---|---|---|---|
| old | -1.000 | **-1.240** | **-1.094 ± 0.247** | -1.067 | **-0.094** | -0.240 |
| average | -0.100 | -0.124 | -0.132 ± 0.041 | -0.120 | -0.032 | -0.024 |
| new | -0.050 | -0.066 | -0.062 ± 0.024 | -0.068 | -0.012 | -0.016 |

![Structured heterogeneity: GLUE tracks the length-weighted mean](figures/step5d_structured.png)

**Finding (precise-but-biased).** The structural residual is still tiny (0.006 → the fit stays
*precise*, RMSE ≈ noise floor), but now the length-weighted mean diverges from the arithmetic mean
(old −1.240 vs −1.000) and the GLUE coefficient is pulled toward it: old is fitted at −1.094,
biased −0.094 (~0.4 behavioural SD) from the arithmetic mean, i.e. ~40% of the way to the
length-weighted (effective) value. Contrast with 5a/5b (uncorrelated jitter → lenwt ≈ arith →
bias ≈ 0): the **correlation** is what breaks the averaging-out. This is the reviewer's
"precise but biased" phenomenon — a good fit that returns the residence-weighted *effective*
coefficient, not the simple average of the true field (the bias grows with correlation strength).

**Honest caveat — this is *not* the strong bias the reviewer described.** In this Net3 / six-monitor
setup at σ = 0.1 the three-zone model **reproduces the observations almost equally well for a wide
range of effective coefficients** (avg/new are unidentifiable and old is only one-sidedly
identifiable). So the structural offset, although systematic and irreducible, is **small
(old −0.094 ≈ 0.4 SD) and largely masked by the parameter uncertainty** — the behavioural
distribution still comfortably covers the truth. What is demonstrated here is the *mechanism* (the
fit stays precise while the coefficient is pulled toward the residence-weighted value), not a
dramatic "tight-but-wrong" estimate. A bias that clearly exceeds the uncertainty would require
stronger flow-correlated heterogeneity and/or more accurate sensors (lower σ → tighter posterior);
under the present information-poor array the honest conclusion is that within-zone structural error
does **not** materially distort the calibration or the risk map.

### Step 5d — grid-search recovery is "centred on the answer" (§3.3, second half)

The 7×7×7 grid ranges are chosen around the true values, so the nearest grid node to each truth is
close by construction:

| coeff | grid step | nearest node to truth | distance | half-step |
|---|---|---|---|---|
| old | 0.217 | -1.067 | 0.067 | 0.108 |
| avg | 0.027 | -0.093 | 0.007 | 0.014 |
| new | 0.016 | -0.052 | 0.002 | 0.008 |

The grid best fit found in every run — `(-1.067, -0.093, -0.052)` — is **exactly** these nearest
nodes, so "recovery to the nearest grid node" is guaranteed by the grid placement, not by the data.
Consequences:

- The deterministic grid **cannot distinguish identifiable from unidentifiable coefficients**: it
  snaps every parameter to its nearest node, so even avg/new (shown unidentifiable by GLUE)
  "recover" to the truth. This is why the draft's grid looked like successful recovery of all
  three, masking what GLUE reveals.
- The draft's reported 10-realisation spread for old (±0.12 m/day) ≈ **half a grid step** (0.108),
  i.e. largely quantisation, not genuine estimation uncertainty.

Fix for the draft: present the grid only as an implementation/plausibility check, and rely on GLUE
(with the displaced priors of Steps 2/4) for identifiability and uncertainty.

### Step 5 — overall

- **Uncorrelated within-zone heterogeneity (±20–50%)**: grouped model **robust** — GLUE ≈
  arithmetic mean, bias < 0.25 SD, risk preserved.
- **Length-correlated within-zone heterogeneity (5c)**: **precise but biased** — GLUE tracks the
  length/residence-weighted effective coefficient, biased from the arithmetic mean (old −0.094).
- **Grid search (5d)**: recovery to the nearest grid node is guaranteed by the grid being
  centred on the truth, so the deterministic "recovery of all three coefficients" is an
  artifact; only GLUE (Steps 2/4) reveals identifiability.
- Directly answers §3.3 ("report how far the behavioural ensemble sits from any simple average of
  the true field"): the distance is ≈0 when heterogeneity is uncorrelated and a clear bias toward the
  length-weighted mean when it is correlated. The
  low-residual clipping in the old zone is a further precise-but-biased source (→ Step 9).

---

## Step 6 — sensor-accuracy (noise) sensitivity  [answers the email]

Same three-zone truth; observation noise `σ = 0.02 / 0.05 / 0.10 / 0.15 mg/L` (σ = one standard
deviation; covers the supervisor's ±0.05 / ±0.10 / ±0.15). The likelihood scale equals σ and the
behavioural threshold **scales with σ** as the ~95% acceptance band
(`threshold_for_sigma`, 0.107 at σ=0.1). 30 noise realisations per σ, median [IQR]; reuses the
baseline cache (candidates are noise-independent), no EPANET (`step6_noise_sensitivity.py`).

| σ (mg/L) | threshold | median retention | old SD retained | avg SD retained | new SD retained | 5–95% band @node15 |
|---|---|---|---|---|---|---|
| 0.02 | 0.021 | ≈0% (sampling-limited) | 12%* | 19%* | 18%* | 0.016 |
| 0.05 | 0.053 | 8% | 42% [31–48] | 47% [39–53] | 45% [38–48] | 0.056 |
| 0.10 | 0.107 | 57% | 69% [65–73] | 91% [84–94] | 89% [78–92] | 0.098 |
| 0.15 | 0.160 | 83% | 85% [82–90] | 98% [96–98] | 99% [96–99] | 0.141 |

*σ = 0.02 retains ≈0 of the 2000 prior samples (see finding 3); its widths are indicative only.

![Sensor-accuracy sensitivity](figures/step6_noise_sensitivity.png)

Findings:

1. **Identifiability is set by sensor accuracy.** At σ = 0.10 only *old* is (marginally)
   identifiable (69% of prior width; avg/new ≈ 90%). Tightening to σ = 0.05 constrains all three
   (≈ 45%). Loosening to σ = 0.15 leaves everything ≈ the prior (85–99%).
2. **Prediction uncertainty scales ~linearly with σ.** The 5–95% band at the risk-governing
   old-zone node 15 grows from 0.016 (σ=0.02) to 0.141 mg/L (σ=0.15).
3. **Sampling limitation (reportable, §3.2).** At σ = 0.02 the σ-scaled 95% band retains ≈0 of the
   2000 prior samples — no random sample lies close enough to the truth. Exploiting σ = 0.02 needs
   a much denser ensemble, not a looser threshold.

**Required-accuracy conclusion (email).** To obtain useful, tight chlorine predictions at the
low-residual nodes that decide the risk map, sensor σ should be ≲ 0.05 mg/L. At the common
±0.1 mg/L class only the dominant *old* coefficient and the coarse risk pattern are recoverable
(avg/new stay unidentified); at ±0.15 mg/L calibration adds little beyond the prior. This replaces
the imported foundation-notebook noise sweep flagged in §3.5.

---

## Step 7 — a-priori identifiability: Fisher information / CRLB

**Roles of the three analyses (keep distinct).** Fisher/CRLB (Step 7) is *a priori* — it uses only
the model, sensitivities and the assumed noise level, not any realised observation set, so it
*predicts* identifiability before calibration. Profile likelihood (Step 7b) uses the *observed*
data, so it is a *practical / a-posteriori* identifiability check (formal-likelihood validation),
not a prediction. GLUE is the *global behavioural* result. The like-for-like chain at the baseline
model (k_b fixed, no bias) is **Fisher Case A ↔ profile likelihood ↔ baseline GLUE**; Cases B/C are
expanded-model (realism) predictions.

**Two-layer reading (paper structure) — keep them separate; do NOT merge them to argue that the
baseline GLUE is "realistic".**

- *Layer 1 — controlled-baseline identifiability* (identical conditions: k_b fixed, unbiased
  sensors, independent Gaussian noise, only three k_w): Fisher **Case A** (a-priori prediction) ↔
  formal **profile likelihood** (a-posteriori validation) ↔ **baseline GLUE** (behavioural
  reference). Cleanest conclusion: *the data carry information about all three; the formal
  likelihood extracts it; informal GLUE is substantially broader and more prior-sensitive.*
- *Layer 2 — realism sensitivity*: Case **B** (+k_b), Case **C** (+6 monitor offsets), **AR(1)**
  (Step 7c) and censored likelihood (Step 9) each *separately* relax one baseline assumption.
  Conclusion: *ideal identifiability is fragile to real error sources — especially avg/new — while
  old stays comparatively robust.*

These baseline assumptions are **valid by construction** for this controlled synthetic experiment
(k_b was fixed, noise was generated independent-Gaussian, no bias was injected), so **Case A is
exactly correct here** — they are only *optimistic for a real-network deployment*. So we write "valid
for the controlled baseline but optimistic for real-network application", **not** "the assumptions
are false".

**Normalization convention (so the two tables are read consistently).** Step 7 reports the **1σ**
ratio `CRLB SD / prior SD`; Step 7b reports **95%** intervals. For a uniform prior,
`prior SD = half-width/√3` and a 95% half-width `= 1.96·SD`, so the two conventions differ by
≈ `1.96/√3 ≈ 1.13`. old's `0.25` (1σ CRLB/prior-SD) and its profile `±0.16 / 0.65 ≈ 0.25`
(95% half-width / prior half-width) thus describe the **same tightness expressed two ways**, not
literally the same ratio. Both the **absolute interval** and the **CRLB/prior-SD** are reported —
never only the normalized number.

Sensitivity `J[r,j] = ∂C_r/∂k_j` at the truth (central differences; r = 6 monitors × 49 h = 294),
Fisher `F = Jᵀ J / σ²`, and the CRLB (smallest achievable SD). The CRLB for the three k_w is
computed under nested models that add the reviewer's confounders, using the marginal (Schur)
information `F_pp − F_pn F_nn⁻¹ F_np` (`step7_fisher.py`, σ = 0.10; independent noise assumed —
AR(1) (#4) quantified separately in **Step 7c**):

- **A** k_w only (k_b known, no bias) — idealised best case
- **B** + k_b (k_b trades off with k_w — Priority-2 #5)
- **C** + 6 per-monitor offsets (systematic sensor bias — Priority-2 #1)

Direct sensitivity check (max |ΔC| over a 0.04 change, others at truth): **old** moves only its own
zone nodes 15/145 by ≈0.007; **new** (near-source) moves many nodes by up to **0.087** →
new/avg have the *highest* per-unit sensitivity (near-source pipes lie upstream of the whole
network), old the lowest.

| case | old | average | new | condition # |
|---|---|---|---|---|
| A — k_w only | 0.25 ✅ | 0.29 ✅ | 0.29 ✅ | 211 |
| B — k_w + k_b | 0.30 ✅ | 0.53 ✅ | 0.54 ✅ | 103 |
| C — k_w + k_b + offsets | **0.74 ✅** | **2.30 ❌** | **1.10 ❌** | 111 |

(values = CRLB SD / prior SD, a **1σ** ratio; **< 1** means the data could *in principle* narrow the
coefficient below its prior — a heuristic, not a strict theorem. Absolute Case-A CRLB SDs:
old ±0.093, avg ±0.013, new ±0.008 mg·L⁻¹·day⁻¹-equivalent. GLUE behavioural SD/prior at 0.107:
old 0.69, avg 0.91, new 0.89.)

![Fisher/CRLB with nuisance parameters](figures/step7_fisher.png)

**Case A is the like-for-like benchmark** for the baseline GLUE (both fix k_b and assume no sensor
bias). Cases B and C are **realism sensitivity analyses**, not descriptions of the baseline GLUE.

Findings:

1. **Idealised A — the data do contain information about all three** (CRLB/prior 0.25/0.29/0.29 < 1).
   In fact new/avg have *higher per-unit sensitivity* than old (near-source pipes lie upstream of
   the whole network; direct max|ΔC| up to 0.087 for new vs 0.007 for old). So the observations are
   not fundamentally devoid of information about avg/new.
2. **The A-vs-GLUE gap is GLUE's own conservatism — not k_b or bias.** The baseline GLUE also fixes
   k_b and ignores bias, so its like-for-like benchmark is A (0.25/0.29/0.29); yet GLUE gives
   0.69/0.91/0.89 — much wider than the CRLB, and it narrows only old. This gap comes from GLUE's
   informal likelihood `exp(−½(RMSE/σ)²)` under-using the 294 residuals (it drops the factor N of a
   formal Gaussian likelihood → far too flat; Stedinger 2008 / Mantovan & Todini 2006, §6.3), plus
   the behavioural threshold, zero-clipping, global non-linearity, finite sampling and old's
   one-sided/large-range response. It must **not** be attributed to k_b/bias, which are absent from
   the baseline GLUE.
3. **Sensitivity ≠ identifiability.** new/avg respond more per unit, but their response *mimics* a
   global k_b change or a per-monitor offset (non-unique) and is easily confounded; old's response
   is smaller but *distinctive* (localised at 15/145 with a particular spatiotemporal shape), so it
   survives confounding. This is why old is the robustly identifiable one despite its lower raw
   sensitivity.
4. **Realism sensitivity (B, C).** Admitting k_b uncertainty (B) inflates the avg/new CRLB ≈1.9×
   (corr(k_w,k_b) 0.77–0.83); adding per-monitor bias (C) pushes **avg (2.30) and new (1.10) above
   their prior → practically unidentifiable**, while **old retains limited identifiability (0.74)**.
   Case C thus reproduces a *qualitatively similar* gradient to GLUE — but under an **expanded
   nuisance model the baseline GLUE did not use**, so it corroborates the robustness of the gradient
   rather than "confirming" the baseline run.
5. **Read the condition number with care.** κ ≈ 211 / 103 / 111 for A/B/C: the k_w problem is
   ill-conditioned (weakest direction ~10² less informative than the strongest). The *smaller* κ for
   B/C does **not** mean better identifiability — κ is only the relative imbalance of information
   directions; adding nuisances lowers the total information (the CRLBs rise), it does not improve it.

This delivers Priority-2 #2 (a-priori identifiability) and links to #1 (sensor bias), #5 (k_b) and
#4 (AR(1), Step 7c) as realism analyses.

**Recommended thesis statement (main identifiability line).**
> A-priori Fisher information and formal profile likelihood showed that, under the controlled
> baseline assumptions of fixed bulk decay, unbiased sensors and independent Gaussian errors, the
> six-monitor dataset contained identifiable information about all three grouped wall-reaction
> coefficients. The informal GLUE formulation produced substantially broader and more
> prior-sensitive behavioural distributions, indicating that its weighting and threshold did not
> fully exploit the information contained in the 294 residuals. Separate realism-sensitivity
> analyses showed that bulk-decay uncertainty, monitor-specific bias and temporal autocorrelation
> could substantially weaken this ideal identifiability, particularly for the average and new
> coefficients, while the old coefficient remained comparatively robust.

**What GLUE is (and is not).** The baseline GLUE is a *conservative, method-dependent behavioural
envelope* — kept for behavioural uncertainty and risk propagation — but it is **not** a calibrated
representation of all real-world uncertainty sources (it omits k_b uncertainty, monitor offsets,
AR(1) covariance and censoring). Its breadth comes from the informal likelihood + threshold + prior
+ finite sampling + non-linear parameter space, **not** from having modelled reality.

**Do not write:** "the assumptions are false" (they hold by construction here); "GLUE's width ≈
real-world identifiability" (unsupported — the nuisance terms are absent from the baseline run); or
"the formal analysis converged to the GLUE result" (Case C is a *different, expanded* model). **Do
write:** Case C produced a *qualitatively similar* identifiability gradient (old partial, avg/new
weak), corroborating the robustness of the gradient rather than confirming the baseline GLUE.

---

## Step 7b — profile likelihood (practical identifiability, a posteriori)

The third identifiability tool the reviewer asked for. **Role:** unlike Fisher/CRLB (a priori),
profile likelihood uses the *observed* data, so it is a *practical / a-posteriori* identifiability
check (formal-likelihood validation), **not** an a-priori prediction. For each coefficient, fix it
and **re-optimise the other two** (minimise SSE), giving the profile negative log-likelihood; the
95% single-parameter interval is `ΔNLL ≤ 1.92`. Formal likelihood `NLL = (N/2σ²)·RMSE²` (N = 294, σ = 0.1), read off a 21³ grid
(`step7b_profile.py`). Unlike the Step 4b *sweep* (other two fixed at the truth), the profile allows
parameter compensation.

| coefficient | profile 95% interval | half-width | Fisher CRLB 95% |
|---|---|---|---|
| old | [-1.18, -0.85] | ±0.16 | ±0.18 ✓ |
| average | [-0.128, -0.080] | ±0.024 | ±0.025 ✓ |
| new | [-0.067, -0.038] | ±0.015 | ±0.016 ✓ |

(the truth −1.0 / −0.1 / −0.05 lies inside every interval.)

![Profile likelihood: tight two-sided intervals matching the CRLB](figures/step7b_profile.png)

Findings:

1. **Under the formal likelihood all three are tightly, two-sidedly identifiable** — the profile 95%
   intervals bracket the truth and **match the Fisher CRLB 95% intervals** (Case A). The two formal
   tools agree: the observations *do* identify all three (idealised, k_b fixed, no bias).
2. **Little parameter compensation**: the profile (re-optimising the other two) ≈ the sweep (others
   at truth), so the three coefficients are not strongly confounded under the formal likelihood at
   this idealised setting.
3. **old's valley is mildly asymmetric** (shallower on the strong side), the residue of its
   one-sided tendency; but the formal likelihood still bounds it two-sided. So the "one-sided"
   description from Steps 4/4b is a *GLUE/informal-likelihood* view — under the efficient formal
   likelihood old is two-sided, though its strong side is only weakly constrained.
4. **Far tighter than GLUE.** These formal intervals are much narrower than the GLUE behavioural
   distributions (which barely narrow avg/new). The gap is GLUE's informal likelihood dropping the
   N = 294 factor (→ too flat); the profile/Fisher use the full formal likelihood. This closes the
   third leg of Priority-2 #2 and confirms the Step 7 diagnosis of GLUE inefficiency.
5. As in Step 7, this is the **idealised** benchmark (Case A); admitting k_b uncertainty and sensor
   bias (Fisher Case C) is what renders avg/new *practically* unidentifiable.

---

## Step 7c — error autocorrelation AR(1) (Layer-2 realism) — Priority-2 #4

Both formal tools above assume **independent** hourly errors. Real telemetry is temporally
autocorrelated, so those intervals are a *lower bound*. Rather than mechanically multiplying every
CRLB by the scalar effective-sample-size factor, we rebuild the observation covariance with an AR(1)
structure and recompute the Fisher information (`step7c_ar1.py`, Case A = k_w only, ρ = 0.4):

**Covariance / Fisher:**

```
per-sensor 49×49 block    Σ_block[t,s] = σ² · ρ^|t−s|          (hourly AR(1))
full covariance           Σ = block_diag(6 sensor blocks)      (294×294, sensors independent)
Fisher (AR(1))            F_AR1 = Jᵀ Σ⁻¹ J        vs   independent  F = Jᵀ J / σ²
CRLB_j = √[ (F⁻¹)_jj ]
```

**Scalar reference (quick caveat):**

```
inflation ≈ √[ (1+ρ)/(1−ρ) ] = √(1.4/0.6) ≈ 1.53
N_eff     ≈ N · (1−ρ)/(1+ρ) = 294 · 0.6/1.4 ≈ 126     (of 294 hourly points)
```

| coefficient | CRLB indep | CRLB AR(1) | widening | CRLB/prior indep | CRLB/prior AR(1) |
|---|---|---|---|---|---|
| old | ±0.093 | ±0.139 | 1.49× | 0.25 | 0.37 |
| average | ±0.013 | ±0.020 | 1.49× | 0.29 | 0.43 |
| new | ±0.008 | ±0.011 | 1.44× | 0.29 | 0.41 |

Findings:

1. **Each coefficient widens by its *own* factor** (1.44–1.49×), computed from the full covariance —
   *not* a single mechanical 1.53× applied to all. They land close to the scalar reference here
   because the temporal Jacobian shape is similar across the six sensors; the covariance route is
   the defensible one and would separate the factors more where sensitivities differ in time.
2. **AR(1) alone is a *modest* caveat.** Even at ρ = 0.4 the ideal identifiability survives
   (CRLB/prior-SD old 0.37, avg 0.43, new 0.41 — all still < 1). So autocorrelation *inflates* the
   idealised intervals ~1.5× but does **not** by itself destroy identifiability.
3. **The dominant realism weakening is k_b + offsets, not AR(1).** Compare: Case C (k_b + 6 offsets)
   pushes avg to 2.30 and new to 1.10 (unidentifiable), an order of magnitude larger effect than
   AR(1)'s ×1.5. AR(1) is therefore reported as a quantified *caveat*, not the leading realism term.

**AR(1) profile likelihood (not just Fisher).** To avoid leaving the profile side "notional", the
21³ grid was rebuilt storing the full 294-residual vector `e` at every node (`step7c_profile_ar1.py`),
so the AR(1) profile could be computed exactly as `NLL(θ) = ½·e(θ)ᵀ Σ⁻¹ e(θ)` (the attached
operational notebook uses the same AR(1) observation process). The independent profile reproduces
Step 7b (sanity check), and the AR(1) profile widens by its own per-coefficient factor:

| coefficient | independent 95% | AR(1) 95% | half-width indep → AR(1) | widening |
|---|---|---|---|---|
| old | [-1.175, -0.850] | [-1.240, -0.785] | ±0.163 → ±0.228 | 1.40× |
| average | [-0.128, -0.080] | [-0.144, -0.072] | ±0.024 → ±0.036 | 1.50× |
| new | [-0.067, -0.038] | [-0.072, -0.034] | ±0.014 → ±0.019 | 1.33× |

The profile widening (1.33–1.50×) agrees with the Fisher-CRLB widening (1.44–1.49×): both formal
tools react to AR(1) the same modest way, and the truth still lies inside every AR(1) interval — so
AR(1) inflates but does not overturn the idealised identifiability. (The scalar `√[(1+ρ)/(1−ρ)]≈1.53`
is only a reference; the per-coefficient factors above come from the full covariance.)

---

## Step 8 — systematic sensor bias (GLUE, empirical) — Priority-2 #1

A constant offset (systematic bias) is added to one informative old-zone monitor (node 15) and the
GLUE calibration is re-run (`step8_sensor_bias.py`; cache reused, threshold 0.107, 30 noise
realisations). Baseline old behavioural SD (the random spread) = **0.260**.

| bias @ node 15 | old mean | old shift | shift / SD | avg mean | new mean | top-3 risk |
|---|---|---|---|---|---|---|
| 0.000 | -1.040 | +0.000 | 0.00 | -0.119 | -0.052 | 131, 243, 141 |
| 0.025 | -0.988 | +0.052 | +0.20 | -0.118 | -0.051 | 131, 243, 141 |
| 0.050 | -0.907 | +0.133 | +0.51 | -0.117 | -0.051 | 131, 243, 141 |
| 0.100 | -0.676 | +0.364 | +1.40 | -0.111 | -0.053 | 131, 243, 141 |

![Systematic bias pushes the calibrated coefficient](figures/step8_sensor_bias.png)

Findings:

1. **A systematic bias biases the coefficient that monitor informs.** A +0.05 mg/L offset at node 15
   pushes k_w,old from −1.04 to −0.91 (shift +0.13 ≈ **0.5 behavioural SD**, away from the truth
   −1.0); +0.10 gives +0.36 (**1.4 SD**, exceeding the entire random spread). A positive bias
   (sensor over-reads) makes the fit infer *weaker* decay.
2. **Only the locally-sensed coefficient moves.** avg/new (informed by other zones) barely change
   (≤0.01) — the bias corrupts old, not the others.
3. **The risk ranking is robust.** Top nodes (131, 243, 141, …) are unchanged at every bias level:
   the operational risk product is insensitive to this single-sensor bias even while the coefficient
   is biased.
4. **Shape (setup-dependent).** The shift is *super-linear/convex* here — halving the offset
   (0.05→0.025) keeps only ~39% of the shift, so halving a sensor bias more-than-halves the
   parameter error. (This differs from the concave/~70% behaviour the reviewer cited from the
   operational notebook; here old's posterior is wide because it is only one-sidedly identified, so
   a small bias is a small fraction of the spread.)
5. **Empirical counterpart to Step 7 Case C.** Fisher showed per-monitor offsets *absorb* the signal
   (avg/new → unidentifiable); this GLUE run shows a real offset *biases* the most robustly informed
   coefficient (old). At the ±0.1 class the systematic term is a first-order error source, but in this
   information-poor array it biases only the locally-sensed coefficient and leaves the risk ranking
   intact. (A real bias would be estimable/correctable via reference sampling — the operational
   notebook's QA step; this quantifies the *uncorrected* impact.)

**Why node 15, and does the location matter? (bias-location sweep, `step8c_bias_bynode.py`).** The
same offset was injected at each of the six monitors in turn (two per zone: new 107/113, old 15/145,
average 209/231; threshold 0.107, 30 noise). Δ = shift of each coefficient's behavioural mean from
the unbiased baseline (means old −1.040 / avg −0.119 / new −0.052; SDs 0.260 / 0.042 / 0.024).

| offset | biased node (zone) | Δold | Δavg | Δnew | own-coef shift/SD | risk top-3 |
|---|---|---|---|---|---|---|
| +0.05 | 107 (new) | -0.014 | -0.001 | +0.008 | +0.35 | same |
| +0.05 | 113 (new) | -0.019 | -0.003 | +0.009 | +0.37 | same |
| +0.05 | **15 (old)** | **+0.133** | +0.002 | +0.000 | +0.51 | same |
| +0.05 | 145 (old) | +0.085 | +0.001 | +0.003 | +0.33 | same |
| +0.05 | 209 (avg) | -0.022 | +0.009 | +0.008 | +0.21 | same |
| +0.05 | 231 (avg) | -0.004 | +0.024 | +0.002 | +0.57 | same |
| +0.10 | **15 (old)** | **+0.364** | +0.008 | -0.001 | +1.40 | same |
| +0.10 | 145 (old) | +0.278 | +0.004 | +0.007 | +1.07 | same |
| +0.10 | 231 (avg) | +0.002 | +0.052 | +0.003 | +1.23 | same |

Findings (location does matter, predictably):

1. **A bias mainly corrupts the coefficient of its own zone.** The shift is concentrated in Δ(own
   zone); cross-zone leakage is small. So node 15 was chosen deliberately — old is the *only*
   robustly identifiable coefficient (Step 7) and the physically dominant one, so biasing an old
   monitor is the meaningful worst case.
2. **In absolute terms the old monitors do the most damage** (Δold +0.13 → +0.36), an order of
   magnitude larger than the avg/new coefficient shifts (≤0.05), because avg/new barely respond to
   the data (prior-dominated) and are physically small. **But normalised by their tiny SDs the
   relative corruption is comparable or larger** (node 231 → 1.23 SD at +0.10).
3. **The two monitors within a zone differ** (15 > 145; 231 > 209) — different local sensitivity /
   information content, so *which* sensor drifts, not just which zone, changes the magnitude.
4. **The risk ranking is robust at every node and offset** ("same"): the operational product is
   insensitive to a single-sensor bias regardless of location.

---

## Step 8b — GLUE at k_b ± 20% (empirical partner to Fisher Case B; Priority-2 #5)

Observations are generated at the true `k_b = -0.5`; GLUE is re-run with `k_b` fixed at
-0.4 / -0.5 / -0.6 (±20%) to see how the three grouped `k_w` are pushed by the bulk–wall trade-off
(`step8b_kb_sensitivity.py`; k_b=-0.5 reuses the cache, -0.4/-0.6 simulated; 30 noise realisations,
threshold 0.107).

| k_b | old (shift) | avg | new | top-3 risk |
|---|---|---|---|---|
| -0.4 | -1.071 (−0.031) | -0.130 | -0.059 | 131, 243, 141 |
| -0.5 | -1.040 (0) | -0.119 | -0.052 | 131, 243, 141 |
| -0.6 | -1.002 (+0.038) | -0.107 | -0.042 | 131, 243, 141 |

(baseline old behavioural SD = 0.260.)

![k_b ±20% shifts the k_w estimates (bulk–wall compensation)](figures/step8b_kb_sensitivity.png)

Findings:

1. **Bulk–wall compensation is confirmed empirically.** A weaker fixed k_b (−0.4) makes the fit
   infer *stronger* wall decay (k_w more negative); a stronger k_b (−0.6) makes it *weaker*. Any
   error in the fixed k_b is absorbed into the k_w estimates (Priority-2 #5).
2. **Magnitude.** ±20% k_b shifts old by ∓0.03–0.04 (≈0.13 behavioural SD); avg/new shift ∓0.01,
   which is a *larger* fraction of their smaller SD (~0.24 / 0.35 SD) — matching their higher
   k_b-correlation in Fisher Case B (0.77 / 0.83 vs old 0.34).
3. **Risk ranking robust.** Top nodes (131, 243, 141, …) are unchanged at every k_b → the risk
   product is insensitive to ±20% k_b misspecification.
4. **Empirical partner to Fisher Case B.** The theoretical CRLB inflation (avg/new ×1.9 when k_b is
   freed) is mirrored here by the larger relative shift of avg/new; the effect is modest at ±20% and
   does not overturn the identifiability gradient or the risk map. This closes Priority-2 #5 and
   gives Case B its empirical counterpart (as Step 8 does for Case C).

---

## Step 9 — sensitivity to zero-floor censoring (zero-clipped observations, L = 0)

The draft generates observations as `C_obs = max(0, C_true + ε)` — a hard lower bound at **L = 0** —
then calibrates with unweighted RMSE that treats every clipped `0` as an *exact* measurement. The
statistically consistent treatment of a clipped point is *left-censored*: the latent reading
`Y* = μ + ε` was only observed to be `Y* ≤ 0`, so it should contribute `Φ(−μ/σ)` to the likelihood,
not `(0 − μ)²`. This is the robustness check the review asked for — performed **on the same data at
L = 0** (`step9_zeroclip.py`).

**Tobit-type censored Gaussian likelihood (L = 0)** — a censored Gaussian on the nonlinear WNTR
predictions (hence "Tobit-*type*", not a classical linear Tobit regression):

```
uncensored (obs > 0):  Gaussian    →  −½·((obs − μ)/σ)²
clipped-0  (obs = 0):  P(Y* ≤ 0)   →  log Φ(−μ/σ)          [scipy log_ndtr]
```

Since σ is fixed, minimising the Gaussian NLL orders the parameters identically to minimising
SSE/RMSE, so the "naive" arm is the formal-Gaussian counterpart of the draft's RMSE treatment.

**Clipped-zero census (the actual calibration data):**

| scope | clipped zeros | note |
|---|---|---|
| full record (6 × 73 h) | **28 / 438** | reproduces the count in the review |
| calibration (6 × 49 post-warm-up h) | **8 / 294** | the points actually used to fit |
| by node | 15 (old): 5, 145 (old): 3 | **all 8 in the old zone**; new/avg: 0 |

**Naive-exact-0 vs censored-at-0 (median [IQR] over 30 noise realisations):**

| coefficient | truth | naive median [IQR] | censored median [IQR] | Δ median |
|---|---|---|---|---|
| old | −1.0 | −1.009 [−1.051, −0.964] | −1.021 [−1.058, −0.977] | −0.012 |
| average | −0.1 | −0.102 [−0.108, −0.095] | −0.102 [−0.108, −0.095] | −0.000 |
| new | −0.05 | −0.050 [−0.055, −0.045] | −0.050 [−0.055, −0.045] | +0.000 |

- node-15 fraction of hours below 0.2: naive `0.460` vs censored `0.462` (identical within noise);
- high-risk top-3 — ranked by expected time-fraction below 0.2 mg/L under the **formal-likelihood-
  weighted ensemble** (weights ∝ `exp(log L)` over all 2000 candidates): **131, 243, 15 — identical**
  under both estimators. *(This weighting convention differs from the informal-GLUE risk map of Steps
  8/10 — `exp(−½(RMSE/σ)²)·1[RMSE<0.107]` — so the absolute third node differs (15 here vs 141/166
  there); it is not directly comparable in absolute terms. The only claim here is that naive and
  censored give the **same** ranking, so the zero-handling does not move the risk hot-spots.)*
- old profile 95% interval (baseline): naive `[−1.18, −0.85]` = censored `[−1.18, −0.85]` (curves overlap).

![Zero-clipping census (8/294, all old zone) and the old profile at L=0: naive vs censored overlap](figures/step9_zeroclip.png)

Findings:

1. **Only 8 of 294 calibration points are clipped, and all lie in the old zone** — the low-chlorine
   strong-decay zone (28/438 over the full record, matching the review). new/avg never clip.
2. **At L = 0 the zero-clipping has a negligible effect.** naive-exact-0 and the censored likelihood
   give the same k_w to within `0.012` (old) and `0.000` (avg/new), with overlapping IQRs, the same
   node-15 risk, the same old profile interval and the same high-risk ranking. This is a **robustness
   result**: the draft's `max(0, ·)` + unweighted-RMSE choice did *not* bias the main conclusions.
3. **Why so small here — not a general equivalence.** Two reasons specific to this setup: (i)
   clipping is rare (`8/294 ≈ 2.7%`, so 286 uncensored points dominate the likelihood); (ii) a
   clipped-0 point sits where the true concentration is already ≈ 0, so "exactly 0" and "≤ 0"
   constrain a near-0 model `μ` in almost the same direction. This is an **empirical** result of the
   present experiment, **not** a theorem — exact-zero and censored likelihoods are *not* always
   equivalent; they differed negligibly here only because censoring was infrequent and confined to
   already low-residual conditions. A bias would appear if a larger fraction were censored, or if the
   recorded limit were *well above* the true value — i.e. a positive reporting limit.
4. **Reporting (≈ half a page).** State it as a robustness check: the zero-clipping is confined to
   the old zone, small in number, and does not change the estimates, node-15 risk or the risk
   ranking; the censored likelihood *confirms* the RMSE result rather than overturning it. (If a
   future dataset clipped many more points, or used a positive reporting limit, a censoring-aware
   likelihood would become necessary.)

**Draft paper text (≈ half a page) — for Step 11:**

> *Method.* Because the synthetic observations were constrained to be non-negative, observations
> recorded at zero were treated as left-censored at the imposed boundary (`L = 0`). Positive
> observations contributed a Gaussian density term, whereas zero-clipped observations contributed
> the cumulative probability `P(Y* ≤ 0) = Φ(−μ(θ)/σ)`. This Tobit-type censored Gaussian likelihood
> was compared with the baseline treatment in which zero observations were entered as exact values.
>
> *Results.* Eight of the 294 post-warm-up calibration observations were clipped to zero — five at
> node 15 and three at node 145, all in the low-residual old zone (28 of 438 over the full record).
> Across 30 independent noise realisations the median old-group estimate changed only from −1.009 to
> −1.021 m/day when the censored likelihood replaced the exact-zero treatment, while the average- and
> new-group estimates were unchanged; the profile interval and the low-chlorine summary were
> effectively identical.
>
> *Discussion.* The zero-floor treatment therefore had negligible influence on the principal
> calibration and risk conclusions in this synthetic experiment, reflecting the small number of
> clipped observations and their occurrence under already low-residual conditions. A censoring-aware
> likelihood would nevertheless become important if a larger fraction of observations were censored,
> or if the instrument had a positive reporting limit.

---

## Step 10 — operational risk metrics (duration + depth) and water-age corroboration

The risk map so far reduced to a single probability of being below the **selected operational
low-chlorine threshold** `C_MIN = 0.2 mg/L` (a representative operational value adopted in this
study, **not** a legal/compliance safety limit). A single probability conflates *how long* and *how
far below* the threshold a node sits. From the behavioural ensemble (weights recomputed at the
primary threshold 0.107) we therefore report the original probability re-expressed as a duration,
**two** genuine severity metrics (minimum concentration, cumulative deficit) and **one**
reaction-independent hydraulic diagnostic (water age) — i.e. *one operational re-expression + two
severity metrics + one hydraulic diagnostic*, not "three new metrics" (`step10_risk_metrics.py`).

**Time axis (corrected).** The post-warm-up record is `t = 24 … 72 h` = **49 reporting points but
48 one-hour intervals**. Durations and deficits are **trapezoidally integrated over the 48 intervals**
(max duration = 48 h), not summed over 49 points.

```
duration D_i,n  = ∫ 1[C<0.2] dt          (trapezoid, h;  max 48)   frac = D̄/48 ≈ original P(C<0.2)
deficit  A_i,n  = ∫ max(0, 0.2−C) dt      (trapezoid, mg/L·h)       ← genuinely new (severity)
min C    M_i,n  = min_t C_i,n(t)          (per-member min, THEN weighted = Method A)  ← genuinely new
water age       = EPANET AGE run (reaction-independent; hydraulic diagnostic)
```

Each metric is a behavioural-weighted expectation `X̄_n = Σ_i w_i X_i,n`; 5–95 % bands are weighted
ensemble quantiles (uncertainty is **not** collapsed). Ranked by expected cumulative deficit:

| node | E[dur] h [5–95] | E[deficit] mg/L·h [5–95] | min C med [5–95] | mean age h |
|---|---|---|---|---|
| 243 | 33.1 [30.5, 35.0] | **5.78 [5.70, 5.88]** | 0.000 [0.00, 0.00] | 44.9 |
| 131 | **47.5 [43.0, 48.0]** | 4.50 [4.18, 4.75] | 0.000 [0.00, 0.00] | 40.2 |
| 166 | 10.3 [9.5, 10.5] | 1.90 [1.90, 1.91] | 0.000 [0.00, 0.00] | 34.1 |
| 141 | 21.1 [20.0, 24.0] | 1.72 [1.25, 2.07] | 0.081 [0.07, 0.10] | 25.6 |
| 145 | 12.3 [12.0, 14.0] | 1.49 [1.26, 1.65] | 0.036 [0.03, 0.05] | 17.8 |
| 15 | 19.8 [8.0, 24.0] | 1.09 [0.50, 1.62] | 0.065 [0.05, 0.09] | 21.1 |
| 139 | 21.3 [18.0, 22.0] | 1.01 [0.67, 1.27] | 0.123 [0.11, 0.14] | 26.4 |
| 143 | 18.0 [7.0, 24.0] | 0.88 [0.44, 1.34] | 0.073 [0.06, 0.09] | 21.3 |

**Water age ↔ risk (all n = 92 junctions):** Spearman `0.73` (p ≈ 1e-16, bootstrap 95 %
`[0.63, 0.80]`) for duration and `0.73` for deficit; Pearson `0.74`. Spearman is the primary statistic
(risk metrics are non-linear and many nodes are 0).

![Risk associated with water age; top nodes' expected duration with 5-95% bands](figures/step10_risk_metrics.png)

Findings:

1. **Duration and depth give different internal rankings within a broadly overlapping hotspot
   cluster.** By *persistence*, node **131** is worst (below 0.2 for ≈ 47.5 of 48 h); by *severity*
   (cumulative deficit) node **243** is worst (deep *and* long, 5.78 mg/L·h); node **166** is a *deep
   but short* risk (min C ≈ 0, only ≈ 10 h). The cluster {131, 243, 166, 141, 145, 15, 139, 143}
   broadly overlaps across metrics, but the internal order changes with the metric — which is exactly
   the point of reporting duration and depth separately, so we do **not** claim an identical ranking
   throughout.
2. **Ensemble uncertainty is real and reported.** The 5–95 % bands are tight for the two worst nodes
   (243, 131) but wide for others (e.g. node 15: 8–24 h; node 143: 7–24 h) — parameter uncertainty
   propagates into the *magnitude* of the node-level risk metrics.
3. **Water age gives hydraulic corroboration of the spatial pattern.** Mean water age is strongly
   *associated* with both duration and deficit (Spearman 0.73, n = 92, bootstrap [0.63, 0.80]); the
   worst nodes also have the longest residence times. This is corroboration, **not** validation:
   water age comes from the *same* hydraulic model (not an independent measurement), correlation is
   not causation, and residual chlorine also depends on wall decay, source dosing and tank mixing.
4. **Water-age magnitudes are window-dependent (not steady state).** In this 72-h run the age field
   is still filling (age at `t = 24 h` equals the elapsed 24 h for the leading nodes, and keeps rising
   to `t = 72`), so the *absolute* mean age depends on the averaging window (post-warm-up mean 44.9 /
   40.2 h for 243/131; last-cycle mean 53.9 / 45.3 h) and differs from the draft's earlier single-
   window figures (≈ 36.0 / 34.6 h). The **rank** association is the robust, window-insensitive
   result — hence Spearman, not absolute ages, is reported as the finding. *(A longer run would be
   needed for converged absolute water ages.)*
5. **Interpretation, stated carefully.** The dominant decay term (old) is the *most robustly informed*
   coefficient under the expanded realism analyses (Steps 4/7), and water age is reaction-independent;
   so the leading hotspots are governed by residence time and the old-group decay rather than the
   weakly-informed avg/new coefficients. Consequently **parameter uncertainty affected the *magnitude*
   of the node-level risk metrics (see the 5–95 % bands) but did not materially change the leading
   hotspot ranking under the tested perturbations** (threshold, k_b ±20 %, sensor bias, noise level).
   We do **not** claim the uncertainty "does not propagate" — it does, into the magnitudes; what is
   stable is the ordering of the top hotspots.

---

## Step 11 — leave-one-monitor-out (LOO) predictive validation

The draft calibrated and evaluated on the same six monitors, with no out-of-sample check. LOO
cross-validation fills that gap: hold out one monitor, calibrate GLUE on the other five, then
(a) check the three k_w stay stable and (b) *predict* the held-out sensor and measure the
out-of-sample error and predictive-band coverage (`step11_loo.py`; cache reused, 30 noise
realisations, σ-scaled threshold for 5 monitors). Full-6 reference: old −1.041 / avg −0.119 /
new −0.052.

```
held-out pred RMSE  = √[ mean_t (pred_mean_m(t) − obs_m(t))² ]     compared with the noise floor σ = 0.1
90% predictive band = pred_mean ± 1.645·√(Var_ensemble + σ²)       (parameter + observation noise)
coverage            = fraction of held-out hours inside the 90% band
```

| held-out (zone) | k_old | k_avg | k_new | pred RMSE @m | 90% coverage |
|---|---|---|---|---|---|
| 107 (new) | -1.039 | -0.118 | -0.052 | 0.096 | 0.92 |
| 113 (new) | -1.039 | -0.118 | -0.052 | 0.098 | 0.92 |
| **15 (old)** | **-0.986** | -0.117 | -0.052 | 0.097 | 0.94 |
| **145 (old)** | **-1.010** | -0.116 | -0.051 | 0.093 | 0.94 |
| 209 (avg) | -1.036 | -0.120 | -0.053 | 0.102 | 0.92 |
| 231 (avg) | -1.041 | -0.120 | -0.052 | 0.100 | 0.92 |

(medians over 30 noise realisations; noise floor σ = 0.1 mg/L.)

![LOO out-of-sample prediction error ≈ noise floor; held-out node-15 band covers the data](figures/step11_loo.png)

Findings:

1. **Out-of-sample prediction is at the noise floor.** Every held-out monitor is predicted with
   RMSE ≈ 0.093–0.102 mg/L ≈ σ = 0.1 — i.e. the five-monitor calibration predicts the *unseen* sensor
   about as accurately as the measurement noise allows. No sign of over-fitting; the model
   generalises spatially.
2. **Uncertainty is well-calibrated.** The 90 % predictive band (parameter + observation-noise
   variance) covers 92–94 % of held-out hours — close to the nominal 90 %, slightly conservative.
   So the reported uncertainty is trustworthy out-of-sample, not just in-sample.
3. **Parameter stability confirms where the information lives.** k_avg/k_new are unchanged by dropping
   any monitor (they are prior-dominated). k_old moves perceptibly **only when an old-zone monitor is
   removed** (−1.041 → −0.986 without node 15; → −1.010 without node 145), and is unaffected by
   dropping new/avg monitors — exactly matching Fisher/profile, which locate old's information at
   monitors 15/145. Even then old stays within ~0.05 of the full-6 value.
4. **Validation summary.** LOO corroborates the whole picture: the risk-relevant predictions
   generalise to unseen locations at the noise floor with well-calibrated bands, and the calibration
   is robust to the monitor set, with old's (localised) information the only thing a single dropped
   sensor can perceptibly weaken.

---

## Step 12 — operational temperature / ageing scenario projection (WSP application)

**Role.** After calibration (Steps 1–9), baseline risk metrics (Step 10) and LOO validation
(Step 11), this step answers the operational question the supervisor posed: *given the GLUE
behavioural ensemble, what happens to network-wide low-chlorine risk under warm-season and
heatwave conditions with an ageing-reactivity stress, and does raising the source dose
restore the baseline position?*

This is **not** a re-run of the enclosed homogeneous-`k_w` notebook. The scenario *method*
(Arrhenius scaling → ensemble propagation → likelihood×consequence → risk register → dosing
evaluation) is transplanted onto **this** project's six-monitor, three-zone GLUE ensemble
(`k_b = −0.5` fixed; behavioural threshold 0.107; 1126/2000 members). The supervisor's
numbers are not comparable with these and must never be quoted as results of this study.

### 12.1 Two probability definitions — keep them distinct

Step 10 reported a *time-averaged* probability; Step 12's headline is a *window-breach*
probability. They answer different questions and both are reported.

**Formulas**:

```
P_min(s,n) = Σᵢ wᵢ · 1[ min over t ∈ [24, 72] h of C(s,i,n,t) < C_crit ]
P_bar(s,n) = E[D(s,n)] / 48                     (the Step-10 quantity)
E[D(s,n)]  = Σᵢ wᵢ · ∫ 1[C < C_crit] dt          (h, trapezoid over 48 intervals)
E[A(s,n)]  = Σᵢ wᵢ · ∫ max(0, C_crit − C) dt     (mg/L·h)
```

**Properties**:

- `P_min` = probability the node dips below `0.2 mg/L` **at least once** in the window;
  `P_bar` = probability a randomly chosen hour is below it. `P_min ≥ P_bar` always.
- The window is **48 h** (`t = 24…72`, post warm-up), so `P_min` is a 48-hour window
  minimum, **not** a 24-hour "daily minimum". For otherwise identical trajectories a
  48-hour window-breach probability **cannot be lower** than the corresponding probability
  on a nested 24-hour window, and the two are **equal** whenever the diurnal pattern
  repeats. Window length is therefore only a secondary reason not to compare with the
  supervisor's figures; the primary reasons are the different parameterisation, monitoring
  array, ensemble and simulation set-up.
- "`P_min > 0.5` nodes" counts over all 92 junctions; "indeterminate" is `0.05 < P_min < 0.95`;
  "demand at risk" sums base demand over junctions with `P_min > 0.5` (zero-demand nodes
  contribute 0); "network mean" of `E[D]` / `E[A]` is the **unweighted arithmetic mean over
  all 92 junctions**, in `h` and `mg/L·h` respectively.

### 12.2 Scenario construction

Three sources of scenario uncertainty are propagated jointly with **common random numbers** —
one `(E_a,bulk, E_a,wall, δT)` draw per behavioural member, reused across every scenario and
every dose — so scenario differences are physical, not Monte-Carlo noise.

**Formula**:

```
T(s,i)       = T_mean(s) + δTᵢ,          δTᵢ ~ N(0, 1²) °C
f(T, Ea)     = exp[ −(Ea/R) · (1/T − 1/T_ref) ],   T in K
k_b,i(s)     = (−0.5) · f(T(s,i), E_a,b,i)
k_w,g,i(s)   = k_w,g,i(T_ref) · f(T(s,i), E_a,w,i) · α_g(s),   g ∈ {old, average, new}
```

with `E_a,bulk ~ N(45, 8²)` kJ/mol and `E_a,wall ~ N(35, 10²)` kJ/mol, both **truncated below
at 5 kJ/mol** (drawn from a truncated normal rather than clipped, so no draw can be
non-physical and no probability mass piles up on the bound). The script asserts it: realised
draws span `17.6–66.1` (bulk) and `6.4–68.8` kJ/mol (wall), all positive. Sampled water
temperature spans `9.39–23.47 °C` across all four scenarios, asserted to stay inside the
stated `8–24 °C` validity range.

| key | label | mean water T | ageing multipliers `α` |
|---|---|---|---|
| A | Baseline 12 °C | 12 °C | all 1.00 |
| B | Warm season 16 °C | 16 °C | all 1.00 |
| C | Heatwave 20 °C | 20 °C | all 1.00 |
| D | Heatwave + ageing stress | 20 °C | new 1.00 / avg 1.35 / old 1.85 |

**Assumptions to state in the thesis**:

- Calibrated coefficients are **effective parameters at an illustrative reference temperature**
  `T_ref = 12 °C`; this is inherited from the supervisor's material, **not** measured from Net3.
- Ageing multipliers are **escalation-only stress-test inputs** (`α ≥ 1`), not asset records.
  Because the baseline model already distinguishes new/average/old `k_w`, `α_new < 1` is not
  used — it would weaken already-weak new pipes and double-count the zone structure. Scenario
  D is therefore named an *ageing-reactivity stress*, not "the effect of ageing".
- `C_crit = 0.2 mg/L` and the demand-based consequence terciles (`1.16`, `3.39 L/s`) are
  illustrative operational inputs, not legal limits. Demand is a **consequence proxy**, not
  population or exposure.

**Numerical guard (important).** Zonal `k_w` are clipped to `CLIP_LO = −8.0 m/day` purely as a
solver guard. An earlier run used `−3.0`, which was **active for 46.8 % of members in scenario
D** (prior lower bound `−1.5` × `f_w ≈ 1.5` × `α_old = 1.85` reaches `−5.3`) and silently
biased the reported mean. The guard is now inert: the script asserts **0 clipped draws in every
scenario**, and verifies

```
mean k_w,old(D) / mean k_w,old(C) = 1.8500 = α_old      (exact to 1e-6)
```

Any future change to the priors or to `α` must re-check this assertion.

### 12.3 Scenario results

All means below are **GLUE-weighted**.

| Scenario | mean k_b | mean k_w,old | `P_min>0.5` nodes | demand at risk | % demand | high/very-high | indeterminate | net-mean `P_bar` | net-mean `E[D]` (h) | net-mean `E[A]` (mg/L·h) |
|---|---|---|---|---|---|---|---|---|---|---|
| A. Baseline 12 °C | −0.501 | −1.045 | 22 | 36.4 L/s | 18.9 % | 10 | 8 | 0.0546 | 2.621 | 0.2210 |
| B. Warm season 16 °C | −0.652 | −1.285 | 29 | 45.2 L/s | 23.5 % | 13 | 8 | 0.0820 | 3.935 | 0.3278 |
| C. Heatwave 20 °C | −0.845 | −1.575 | 30 | 48.0 L/s | 24.9 % | 14 | 4 | 0.1118 | 5.364 | 0.4873 |
| D. Heatwave + ageing stress | −0.845 | −2.914 | 32 | 49.5 L/s | 25.7 % | 16 | 4 | 0.1257 | 6.032 | 0.5480 |

Continuity check against Steps 1–11: with the temperature held at `T_ref` exactly (cached
`C_all`, no `δT`), the baseline gives 22 nodes / 36.4 L/s and `E[A] = 0.2193`. Sampling the
stated temperature uncertainty therefore did **not materially change** the baseline
classification — the `P_min>0.5` count and demand at risk are unchanged and network-mean
`E[A]` moves by under 1 % (`0.2193 → 0.2210`).

![Four-panel window-breach probability maps](figures/step12_scenario_maps.png)

![Ageing increment ΔP_min = P(D) − P(C) at 20 °C](figures/step12_ageing_delta.png)

![Scenario escalation, dosing evaluation and ageing sensitivity](figures/step12_summary.png)

**Escalation.** Eight consumer junctions change risk band between A and D, carrying 21.8 L/s
(11 % of network demand); **seven of the eight are unmonitored**. The largest ageing-only
increments at the same temperature (D − C) are nodes 217 (`ΔP_min = +0.230`), 215 (`+0.162`)
and 239 (`+0.140`).

**Ageing-stress sensitivity — is scenario D an artefact of `α_old = 1.85`?**

| ageing set | `α_avg` | `α_old` | `P_min>0.5` nodes | demand at risk | high/very-high | indeterminate | net-mean `E[D]` (h) | net-mean `E[A]` (mg/L·h) |
|---|---|---|---|---|---|---|---|---|
| mild | 1.15 | 1.40 | 31 | 49.5 L/s | 15 | 4 | 5.759 | 0.518 |
| central | 1.35 | 1.85 | 32 | 49.5 L/s | 16 | 4 | 6.032 | 0.548 |
| severe | 1.50 | 2.20 | 32 | 49.5 L/s | 16 | 4 | 6.211 | 0.569 |

The **headline binary metrics are nearly insensitive** to the tested multiplier range: the count
varies only from 31 to 32, demand at risk stays at 49.5 L/s and the indeterminate count is
constant. The **continuous severity metric increases monotonically** (`E[A]` 0.518 → 0.548 →
0.569 mg/L·h), and node-level probabilities do move with `α`. So the hot-spot conclusion is
robust to the multiplier choice, but the magnitude of the ageing penalty is not — it should be
reported as a stress-test range, never as "the effect of ageing".

### 12.4 Corrective dosing (control-measure evaluation, not a recommendation)

The dose scales **both** the reservoir source quality and the tank initial quality, so the whole
source regime is raised consistently. (An earlier run left tanks fixed at `0.5 mg/L`, which
confounded the result with an un-dosed boundary condition.) `inlet = 1.00` reuses scenario C.

| inlet (mg/L) | `P_min>0.5` nodes | demand at risk | % demand | net-mean `P_min` | net-mean `E[D]` (h) | net-mean `E[A]` (mg/L·h) | median-over-nodes of mean window min (mg/L) |
|---|---|---|---|---|---|---|---|
| 1.00 | 30 | 48.0 L/s | 24.9 % | 0.3317 | 5.364 | 0.4873 | 0.460 |
| 1.15 | 29 | 45.2 L/s | 23.5 % | 0.3174 | 4.587 | 0.4110 | 0.529 |
| 1.30 | 29 | 45.2 L/s | 23.5 % | 0.2989 | 3.955 | 0.3532 | 0.598 |

(The last column takes, per junction, the GLUE-weighted mean of the per-member window minimum,
then the median across the 92 junctions — it is **not** a pooled member-node median. It scales
almost exactly with the dose, `0.460 × 1.15 = 0.529`, `0.460 × 1.30 = 0.598`.)

**Linearity known-answer test.** Measured `max |C(1.3) − 1.3·C(1.0)| = 2.3e-06 mg/L`. Stated
precisely: *under fixed hydraulics and demands, first-order bulk and wall kinetics, and
proportional scaling of all source and initial chlorine concentrations, increasing the dose by a
factor `r` is mathematically equivalent to evaluating the unscaled concentration field against a
threshold `C_crit / r`.* This equivalence is a property of that idealisation — it does **not**
imply that dosing is linear in a real network with dose-dependent chemistry, DBP formation or
booster constraints.

**Paired warm-up test.** Identical 141-member subset (stride 8), identical weights and identical
`(E_a, δT)` draws; **only the simulation horizon differs**, so the contrast isolates warm-up
length from ensemble composition:

| inlet (mg/L) | nodes short / long | demand at risk short / long | `E[D]` short / long (h) | `E[A]` short / long (mg/L·h) |
|---|---|---|---|---|
| 1.00 | 30 / 30 | 48.0 / 49.4 L/s | 5.367 / 5.409 | 0.4854 / 0.5330 |
| 1.15 | 29 / 29 | 45.2 / 47.8 L/s | 4.583 / 4.798 | 0.4089 / 0.4601 |
| 1.30 | 29 / 28 | 45.2 / 45.0 L/s | 3.939 / 4.391 | 0.3512 / 0.4005 |

Read honestly: the subset itself is representative (short-horizon subset `E[A] = 0.4854` vs full
ensemble `0.4873`, a 0.4 % difference), so the remaining gap **is** attributable to warm-up
length — the longer run reaches a more depleted quasi-steady state and raises `E[A]` by roughly
10 %. The **conclusion is unchanged** under both horizons: node counts and demand at risk are
essentially the same, every metric still improves monotonically with dose, and demand at risk
stays well above the 36.4 L/s baseline. Absolute severity values should nevertheless be quoted
as horizon-dependent.

**Read the binary and continuous columns together.** The identical 45.2 L/s at 1.15 and 1.30 is
a **threshold artefact**, not evidence that the extra dose does nothing: the continuous metrics
improve monotonically (`E[D]` 5.36 → 4.59 → 3.96 h; `E[A]` 0.487 → 0.411 → 0.353). Even so,
+30 % dose leaves 45.2 L/s at risk against 36.4 L/s at baseline — **source dosing alone does not
restore the pre-heatwave demand-at-risk position**. Turnover measures (flushing, storage
management, rezoning) act on residence time and should be evaluated alongside dosing. DBP
formation, taste and acceptability are not modelled.

### 12.5 Risk register, product statement and review triggers

`baseline_cache/step12_risk_register.csv` (92 rows): `P_min` under current / heatwave /
heat+ageing, `P_bar`, `E[D]`, `E[A]` at baseline, demand, likelihood, consequence, risk score
and bands, escalation flag, monitor flag, sampling priority and control-measure text.

**Classification rules (put these in Methods or an appendix — the register is not reproducible
without them).**

| likelihood band | on `P_min` | score |
|---|---|---|
| rare | `< 0.05` | 1 |
| unlikely | `0.05 – 0.20` | 2 |
| possible | `0.20 – 0.50` | 3 |
| likely | `0.50 – 0.80` | 4 |
| almost certain | `≥ 0.80` | 5 |

| consequence band | on base demand `d` (L/s) | score |
|---|---|---|
| non-consumer | `d = 0` | 0 |
| minor | `0 < d ≤ 1.16` | 1 |
| moderate | `1.16 < d ≤ 3.39` | 2 |
| major | `d > 3.39` | 3 |

Terciles are the `1/3` and `2/3` quantiles of base demand over the **59 junctions with non-zero
demand** (Net3 stores demand in CFS; `×1000` gives L/s). The risk score is
`likelihood score × consequence score` (range `0–15`), mapped as `0 → not applicable`,
`1–3 → low`, `4–6 → medium`, `7–9 → high`, `≥10 → very high`.

Sampling priority uses the **discrete consequence score (0–3), not raw demand**:

```
priority(n) = consequence_score(n) · P_min(n) · [1 − P_min(n)]     normalised by its maximum
priority(n) = 0  where base demand = 0
```

so it peaks at `P_min = 0.5` — the junctions the assessment cannot classify either way.

**Product statement (use this wording).** The output is a **GLUE calibration-conditioned
scenario projection** from the network model under stated assumptions. It is **not** a sensor
nowcast (no same-day re-conditioning is performed), **not** a spatial measurement or
geostatistical interpolation, and **not** a statement that water is safe. Chlorine residual is
one operational indicator among the WSP's preventive barriers.

**Review triggers (the assessment expires if):** sensor QA failure or reference-check
disagreement; hydraulic model or demand allocation revised; source/treatment regime change;
water temperature outside the 8–24 °C scenario range; a forecast heat episode; mains works
altering the assumed age profile; calibration record exceeding its approved age.

### 12.6 Findings for the Results / Discussion

1. **Temperature escalates risk materially but does not flatten the network.** `P_min>0.5`
   nodes rise 22 → 29 → 30 from 12 → 16 → 20 °C; demand at risk 18.9 % → 24.9 %; network-mean
   `E[A]` roughly doubles (0.221 → 0.487 mg/L·h).
2. **Ageing at the same temperature adds a spatially selective increment** (30 → 32 nodes;
   `E[A]` 0.487 → 0.548), concentrated where old/average pipes control the supply path. The
   hot-spot set is robust across the tested `α` range (31–32 nodes, 49.5 L/s), while the
   severity magnitude scales with `α` — report it as a stress range, not as a measured effect.
3. **The escalating nodes are almost all unmonitored** (7 of 8), which is an argument for
   information-led monitoring design rather than for more monitoring in general.
4. **Source dosing is an incomplete control.** +30 % inlet dose improves every continuous
   metric but does not return demand-at-risk to baseline. Under the idealisation of fixed
   hydraulics, first-order kinetics and proportional source scaling, dosing by `r` is exactly
   equivalent to testing against `C_crit / r`; it cannot buy back residence time.
5. **Scenario maps are planning products outside the calibrated regime.** The Arrhenius form,
   `T_ref` and `α_g` are assumptions; unlike the Step-11 LOO check, these projections cannot be
   verified against held-out chlorine observations. Absolute severity metrics are additionally
   horizon-dependent (paired warm-up test, §12.4).

Outputs: `figures/step12_scenario_maps.png`, `figures/step12_ageing_delta.png`,
`figures/step12_summary.png`, `baseline_cache/step12_scenarios.json`,
`baseline_cache/step12_risk_register.csv`.

