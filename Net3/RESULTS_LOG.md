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
   (avg/new → unidentifiable); this GLUE run shows a real offset *biases* the one identifiable
   coefficient. At the ±0.1 class the systematic term is a first-order error source, but in this
   information-poor array it biases only the locally-sensed coefficient and leaves the risk ranking
   intact. (A real bias would be estimable/correctable via reference sampling — the operational
   notebook's QA step; this quantifies the *uncorrected* impact.)

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

