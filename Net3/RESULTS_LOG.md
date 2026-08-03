# Revision results log (post-review)

All experiments run against the frozen three-zone baseline in `wq_common.py`, whose network file is
a frozen copy at `models/net3_frozen/Net3.inp` (SHA-256 checked on import, so a WNTR upgrade cannot
change the model silently). Environment: conda env `water-supply` (python 3.13.12, numpy 2.4.2,
scipy 1.17.1, wntr 1.4.0); `environment.yml` declares it and `environment.lock.yml` holds the full
solve. Cache in `baseline_cache/`, with its provenance in `baseline_cache/cache_manifest.json`.

Convention: `σ = 0.1 mg/L` is **one standard deviation** of the Gaussian observation error.
Wall coefficients are reported in `m/day`; the bulk coefficient `k_b` in `day⁻¹`.

**Inference convention — read this before any number below.** Three weightings appear in this log
and they are not interchangeable:

- **formal censored Gaussian likelihood — PRIMARY.** Every headline parameter, risk and scenario
  number uses it. It carries no behavioural threshold.
- **formal iid Gaussian likelihood** — the same thing with sensor-floor zeros treated as exact
  measurements; used only to isolate what the censoring correction is worth (Step 9).
- **informal GLUE score** `exp(−½(RMSE/σ)²)·1[RMSE<T]` — a **comparator**, retained because the
  draft used it and because the contrast is itself a result. It is *not* a Gaussian likelihood: it
  drops the factor `N = 294`, which makes it equivalent to assuming `σ_eff = σ√N = 1.71 mg/L`.
  Where a section reports it, the section says so.

**Timing convention.** 168 h simulation, **120 h warm-up** (justified in Step 0, not assumed), 48 h
assessment window `t = 120…168 h`, `N = 6 × 49 = 294` residuals. Numbers carried over from the
draft's 72 h / 24 h configuration are marked as superseded wherever they still appear.

**Sensor-error convention (Priority 2 #8).** Throughout, a stated sensor-error level `±X mg/L`
means the Gaussian **standard deviation σ = X**, *not* a 95% interval or a hard error bound. This
matters: read instead as a 95% band, "±0.1 mg/L" would imply `σ ≈ 0.1 / 1.96 ≈ 0.05 mg/L` and would
**halve every reported uncertainty interval** (±1σ covers ≈68%; ±1.96σ = ±0.196 covers ≈95%).
Draft fix — one sentence for the Methodology: *"In this study the stated sensor-error levels refer
to the Gaussian standard deviation σ, not to a 95% interval or a hard error bound."*

---

## Files and how to reproduce

Every number in this log comes from a script, but it is transcribed here by hand, so it can drift
when a script is re-run. `validate_artifacts.py` cross-checks the log against
`baseline_cache/*.json` and fails on any number that no artifact holds; run it after every change:

```
conda activate water-supply
cd Net3 && python provenance.py --check && python validate_artifacts.py
```

Numbers that describe a superseded run are exempt from the check and must say so in the sentence
("an earlier run…", "the draft's earlier…").


| file                             | purpose                                                                                         | writes                                                                |
| -------------------------------- | ----------------------------------------------------------------------------------------------- | --------------------------------------------------------------------- |
| `wq_common.py`                   | frozen baseline config + WNTR/EPANET helpers (monitors, zone assignment, seeds, priors, timing) | — (imported by all step scripts)                                      |
| `step0_warmup_convergence.py`    | is the warm-up long enough? successive-24 h-cycle convergence test with pre-declared criteria    | `figures/step0_warmup_convergence.png`, `step0_warmup_convergence.json` |
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
| `step13_known_answer.py`         | known-answer test: single pipe with an analytic first-order solution (Priority-2 #7)             | `baseline_cache/step13_known_answer.json` |
| `provenance.py`                  | records what produced the cache (git commit, frozen `.inp` hash, config hash, library versions) | `baseline_cache/cache_manifest.json` |
| `validate_artifacts.py`          | cross-checks this log, the figures and the JSON artifacts against each other; exits non-zero on drift | — (report on stdout) |


Run from the `Net3/` directory with the environment activated (no absolute interpreter paths, so the
commands work on any machine):

```
conda activate water-supply
cd Net3
export MPLCONFIGDIR=../.mplcache
python step1_freeze_baseline.py         # ~40 s (2000 EPANET runs)
python step3_threshold_sensitivity.py   # instant (cache only)
python step4_displaced_prior.py         # ~40 s (2000 EPANET runs)
python provenance.py                    # refresh baseline_cache/cache_manifest.json
python validate_artifacts.py            # cross-check this log against the artifacts
```

Two step scripts must not run at the same time from the same directory: WNTR writes its EPANET
scratch files as `Net3/temp.inp|rpt|bin`, so concurrent runs overwrite each other.

`baseline_cache/baseline.npz` (~30 MB) is git-ignored; rebuild it with step 1. The small
`*.json` summaries, `cache_manifest.json` and this log are version-controlled.

---

## Step 0 — is the 24 h warm-up long enough? (pre-declared convergence test)

The baseline discards the first 24 h and assesses 24–72 h, but that 24 h was never justified: the
tanks start at an assumed 0.5 mg/L, the high-risk junctions have mean water ages of 34–45 h (Step
10), and the Step 12 paired test already moved the continuous severity metrics by 10–14% when the
warm-up went to 120 h. This step decides the question with criteria fixed *before* the numbers were
seen.

**What "warmed up" means here.** Net3's demand patterns are 24 points at 1 h and pump 10 runs on a
24 h schedule, so the target state is not a constant steady state but a **cyclostationary** one: the
field over one diurnal cycle repeats in the next. Each parameter set is run once over the full
horizon and successive 24 h cycles are differenced.

**Formula**:

```
Δ(k) = max over (t in cycle k, node n) | X(t + 24, n) − X(t, n) |
```

**Properties**:

- Units follow `X` (mg/L for chlorine, h for water age, m for tank level).
- `Δ(k) → 0` means the field from hour `24k` onward is cyclostationary, so a warm-up of `24k` is
  sufficient.
- Computed for the truth and for both corners of the prior box; the weak corner is the binding case
  because the least reactive network forgets its initial condition most slowly.

**Hard horizon limit — this bounds what can be claimed.** Pump 10 is driven by *absolute-time*
controls (`IF SYSTEM TIME IS 01:00:00`, `25:00:00`, …) enumerated only to **159 h**, and the model
duration is 168 h. Past 168 h the pump would stay closed permanently, so a longer run is a different
system, not a longer warm-up. The test therefore has 7 cycles and cannot certify any warm-up beyond
144 h. Step 12's "long" setting (168 h / 120 h) was already sitting exactly on this ceiling.

**Result — worst value across the three parameter sets, per cycle pair:**

| criterion | tolerance | 0–24 | 24–48 | 48–72 | 72–96 | 96–120 | 120–144 | earliest warm-up that satisfies it |
|---|---|---|---|---|---|---|---|---|
| tank level (m) | 0.05 | 0.8185 | 0.0496 | 0.0070 | 0.0009 | 0.0001 | 0.0001 | **24 h** (verified) |
| monitor chlorine (mg/L) | 0.005 | 0.9209 | 0.0437 | 0.0234 | 0.0122 | 0.0064 | 0.0034 | **120 h** (verified) |
| network p95 chlorine (mg/L) | 0.010 | 0.9511 | 0.1061 | 0.0396 | 0.0201 | 0.0103 | 0.0054 | **120 h** (verified) |
| tank chlorine (mg/L) | 0.010 | 0.2457 | 0.0787 | 0.0416 | 0.0219 | 0.0115 | 0.0061 | **120 h** (verified) |
| risk severity, rel. change in `E[A]` | 0.02 | 0.9023 | 0.6507 | 0.1196 | 0.2042 | 0.1056 | 0.0549 | not within 168 h; extrapolates to ≈168 h (**unverified**) |
| water age p95 (h) | 1.0 | 23.999 | 21.676 | 19.043 | 16.692 | 14.630 | 12.815 | not within 168 h; extrapolates to ≈600 h (**unverified**) |

**Three findings, in order of consequence.**

1. **The hydraulics settle almost immediately; the chemistry does not.** Tank levels are periodic to
   0.0001 m after three cycles, so the driver is not the problem. Chlorine differences decay
   geometrically by roughly a factor of two per cycle and first meet all three concentration
   tolerances at a **120 h** warm-up — five times the baseline value.
2. **The integrated risk severity has not converged even at the horizon.** Network-mean cumulative
   deficit for the truth runs 0.9946 (start-up) → 0.1256 → 0.0714 → 0.0799 → 0.0901 → 0.0959
   mg/L·h: it dips after the start-up transient and then climbs **monotonically**. Small
   concentration differences still move the integral, because the deficit integrates a
   threshold crossing. The relative change halves each cycle and would reach the 2% criterion at
   about cycle 6, i.e. a 144–168 h warm-up — but the model horizon cannot supply that cycle, so it
   stays an extrapolation. This is the same effect Step 12's paired test measured as +9.8% to +14%,
   now with its cause identified: **the 24 h window sits on the descending limb of the transient,
   not on the plateau.**
3. **Water age is horizon-dependent and cannot be converged in this model at all.** The p95
   cycle-to-cycle change is still 12.8 h at 120–144 h and decays by only ~12% per cycle;
   extrapolation puts the crossing near 600 h, far past the 168 h ceiling. So `mean_age_h` in Step 10
   is a property of the chosen window, not an equilibrium water age. The water-age corroboration
   must be phrased as a rank association within a fixed window; the absolute ages must not be
   reported as steady-state values. Step 10 now stores all three window definitions
   (`mean_age_h`, `mean_age_last24_h`, `age_final_h`) so the choice is explicit.

**Configuration this implies for the pipeline.** Warm-up **120 h** with the existing 48 h assessment
window gives a 168 h total — *exactly* the model horizon, with nothing to spare. Conveniently the
residual count is unchanged: `6 monitors × 49 hours = 294`, because `168 − 120 = 72 − 24 = 48`, so
the behavioural threshold `0.107` and everything derived from `N = 294` carry over untouched. The
residual risk-severity drift at that warm-up is ~5.5% per cycle and must be stated as a limitation,
not assumed away.

---

## Step 1 — the frozen baseline

Config: monitors `107/113/15/145/209/231`; inlet 1.0, tank 0.5; **168 h simulation, 120 h warm-up**
(Step 0), 1 h reporting, 5 min quality step; `k_b = -0.5`; true
`(k_w,old, k_w,avg, k_w,new) = (-1.0, -0.1, -0.05) m/day`; noise seed 42, Sobol scramble seed 0;
**8192 = 2¹³ scrambled-Sobol prior draws**. Assessment window 48 h, so `N = 6 × 49 = 294`
residuals, unchanged.

This is no longer a reproduction of the draft. Three choices were changed deliberately, each with a
reason recorded here rather than inherited:

| choice | draft | now | why |
|---|---|---|---|
| warm-up | 24 h | 120 h | Step 0: chlorine is not cyclostationary before then |
| sampling | 2000 pseudo-random | 8192 scrambled Sobol | the formal likelihood had an effective sample size of only ~37 at 2000 draws |
| weighting | one informal score | three schemes side by side | the informal score is not a likelihood; see below |

**Three weighting schemes, same data, same draws.** The formal censored Gaussian likelihood is the
primary analysis; the formal iid one isolates the cost of treating a sensor-floor zero as an exact
measurement; the informal GLUE score is retained as a comparator.

**Formula** (per candidate, up to an additive constant):

```
formal iid       ℓ = −(1/2) Σ_j,t ((y_jt − μ_jt)/σ)²
formal censored  ℓ = −(1/2) Σ_{y>0} ((y_jt − μ_jt)/σ)²  +  Σ_{y=0} log Φ(−μ_jt/σ)
informal GLUE    ℓ = −(1/2) (RMSE/σ)²                    · 1[RMSE < threshold]
```

**Properties**:

- The informal score is the formal iid one **divided by `N = 294`**. Equivalently it is a Gaussian
  likelihood with `σ_eff = σ√N = 0.1 × 17.15 = 1.71 mg/L` — 17× the sensor noise and larger than the
  1.0 mg/L inlet concentration. That is why it is nearly flat inside the behavioural set.
- The formal schemes carry **no threshold**; a hard cut-off belongs to the GLUE comparator, not to a
  likelihood.
- 10 of the 294 window points are clipped at the sensor floor (43 of 1014 over the full record), so
  the censored and iid schemes are not identical.

| scheme | ESS | entropy (bits, of 13.00) | `k_w,old` | `k_w,avg` | `k_w,new` |
|---|---|---|---|---|---|
| formal censored (primary) | 157 | 7.97 | -0.9876 ± 0.0938 (25.0%) | -0.1091 ± 0.0142 (30.7%) | -0.0440 ± 0.0078 (28.3%) |
| formal iid | 154 | 7.94 | -0.9708 ± 0.0920 (24.5%) | -0.1087 ± 0.0141 (30.6%) | -0.0441 ± 0.0078 (28.3%) |
| informal GLUE, thr 0.107 | 4783 | 12.22 | -1.0115 ± 0.2668 (71.1%) | -0.1170 ± 0.0424 (91.8%) | -0.0492 ± 0.0242 (88.2%) |
| informal GLUE, thr 0.120 (draft) | 7062 | 12.79 | -0.9431 ± 0.3220 (85.8%) | -0.1196 ± 0.0455 (98.4%) | -0.0529 ± 0.0269 (98.0%) |

Bracketed figure is SD retained (= posterior SD / prior SD). The draft's configuration retained
**86–98%** of the prior width; the formal likelihood retains **25–31%** of it on exactly the same
observations. Nothing about the data changed — only how much of their information the weighting
extracts.

**Sampling convergence.** Leading `2^k` subsets of a scrambled Sobol set are themselves balanced
designs, so these four rows are exact sub-designs rather than ad-hoc thinning:

| draws | ESS | `k_w,old` median | `k_w,avg` median | `k_w,new` median | max median drift |
|---|---|---|---|---|---|
| 1024 | 18.8 | -0.9744 | -0.1096 | -0.0444 | — |
| 2048 | 39.3 | -0.9752 | -0.1097 | -0.0435 | 0.033 prior SD |
| 4096 | 78.0 | -0.9787 | -0.1094 | -0.0437 | 0.009 prior SD |
| 8192 | 156.7 | -0.9787 | -0.1090 | -0.0437 | 0.010 prior SD |

ESS is proportional to the number of draws (it stays at 1.9% of them), so prior sampling cannot be
made efficient by brute force — but the **quantiles have converged** anyway: the medians move by
0.01 prior SD between the last two sizes and the 5/95 endpoints by less. ESS is the conservative
diagnostic here; the Sobol design's space-filling is what buys the stability.

Minimum RMSE 0.0971 mg/L against a noise floor of 0.0960. Behavioural counts, for the comparator:
4786/8192 at 0.107 and 7084/8192 at 0.120.

Cache `baseline.npz` holds all 8192 candidate predictions `C_all (8192 × 49 × 92)` plus both formal
log-likelihoods, so every later step recomputes weights **without re-running EPANET**.

---

## Step 2 — prior vs behavioural identifiability (corrects the overclaim)

Prior SD of a uniform range `[a, b]`:

```
prior_SD = (b − a) / √12
```


| Group   | Prior range     | Prior mid | Prior SD | True  | informal mean ± SD (retained) | formal mean ± SD (retained) |
| ------- | --------------- | --------- | -------- | ----- | ----------------------------- | --------------------------- |
| old     | [-1.5, -0.2]    | -0.850    | 0.375    | -1.00 | -0.9431 ± 0.3220 (85.8%)      | -0.9876 ± 0.0938 (25.0%)    |
| average | [-0.2, -0.04]   | -0.120    | 0.046    | -0.10 | -0.1196 ± 0.0455 (98.4%)      | -0.1091 ± 0.0142 (30.7%)    |
| new     | [-0.10, -0.005] | -0.0525   | 0.027    | -0.05 | -0.1196 → see note            | -0.0440 ± 0.0078 (28.3%)    |

The informal column uses the draft's threshold 0.120 so that it reproduces the configuration the
overclaim came from; `k_w,new` there is -0.0529 ± 0.0269 (98.0% retained).

Interpretation, which has to be split by scheme because the two disagree about the *conclusion*, not
just the digits:

- **Under the informal GLUE score the original criticism stands.** All three distributions retain
  86–98% of the prior width and the weighted means sit near the prior midpoints. Their apparent
  agreement with the true values is a consequence of the prior ranges having been centred near
  those values, not of the data.
- **Under the formal likelihood it does not.** The same observations contract all three
  coefficients to 25–31% of the prior width. So "the data do not identify average and new" was
  never a statement about the data; it was a statement about the score used to weight them.

Deleted overclaim (was in §4.4): *"The weighted mean of every group lies close to its true value."*
The replacement claim must name the inference convention: under the informal GLUE score the means
are prior-dominated, under the formal likelihood all three are informed but still biased by up to
~0.7 posterior SD on this single noise realisation.

---

## Step 3 — behavioural-threshold sensitivity (no EPANET re-run)

Sampling SD of the RMSE statistic at the truth:

```
sd(RMSE) ≈ σ / √(2N) = 0.10 / √(2·294) = 0.0041 mg/L      (N = 6 monitors × 49 h = 294)
```

Observed minimum RMSE = 0.0971 mg/L, against a noise floor of 0.0960.

**Scope of this step, restated.** The behavioural threshold belongs to the informal GLUE comparator
only — the formal likelihood carries no cut-off. So this is a sensitivity analysis *of the
comparator*, and the right conclusion to draw from it is about how much the comparator's answer
depends on an analyst's choice, not about how much the data say.

Retention and objective-scale table:


| Threshold | Retained | Retention | SD above noise floor | band node15 | band node107 | nonzero-risk nodes |
| --------- | -------- | --------- | -------------------- | ----------- | ------------ | ------------------ |
| 0.107     | 4786     | 58.4%     | 1.70                 | 0.1008      | 0.0762       | 24                 |
| 0.110     | 5668     | 69.2%     | 2.42                 | 0.1121      | 0.0788       | 24                 |
| 0.120     | 7084     | 86.5%     | 4.85                 | 0.1419      | 0.0816       | 24                 |


Per-coefficient behavioural distribution — weighted `mean ± SD (m/day)` with `SD retained`
(= behavioural SD / prior SD; prior SD = 0.375 / 0.046 / 0.027 m/day for old / avg / new):


| Threshold | k_w,old mean ± SD (retained) | k_w,avg mean ± SD (retained) | k_w,new mean ± SD (retained) |
| --------- | ---------------------------- | ---------------------------- | ---------------------------- |
| 0.107     | -1.0115 ± 0.2668 (71.1%)     | -0.1170 ± 0.0424 (91.8%)     | -0.0492 ± 0.0242 (88.2%)     |
| 0.110     | -0.9956 ± 0.2844 (75.8%)     | -0.1174 ± 0.0437 (94.5%)     | -0.0512 ± 0.0254 (92.7%)     |
| 0.120     | -0.9431 ± 0.3220 (85.8%)     | -0.1196 ± 0.0455 (98.4%)     | -0.0529 ± 0.0269 (98.0%)     |
| *formal censored (no threshold)* | *-0.9876 ± 0.0938 (25.0%)* | *-0.1091 ± 0.0142 (30.7%)* | *-0.0440 ± 0.0078 (28.3%)* |


As the threshold tightens (0.120 → 0.107):

- **old sharpens a little**: SD 0.3220 → 0.2668 (SD retained 85.8% → 71.1%) and the mean moves
toward the truth (-0.9431 → -1.0115, true -1.0).
- **average / new barely change**: SD retained stays 88–98% and the means stay near the prior
midpoint.
- **But no threshold gets close to the formal result.** Tightening from 0.120 to 0.107 recovers
about a seventh of the gap for `old` and almost none for `avg`/`new`, whereas switching to the
formal likelihood cuts every SD by a factor of three. The earlier reading — "average/new cannot be
sharpened by any threshold, so their non-identifiability is a property of the monitoring array" —
is wrong: it is a property of the *score*. The monitoring array does inform them, as the formal row
and Step 7's CRLB both show.

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

behavioural 3359/8192 (41.0%), min RMSE 0.0972. Weighting: informal GLUE, as in the draft.


| Group   | Orig mid | Displaced range (mid)     | True  | Beh. mean ± SD | SD retained | Gap to truth closed |
| ------- | -------- | ------------------------- | ----- | -------------- | ----------- | ------------------- |
| old     | -0.850   | [-2.025, -0.725] (-1.375) | -1.00 | -1.2185 ± 0.3287 | 87.6%     | 42%                 |
| average | -0.120   | [-0.226, -0.066] (-0.146) | -0.10 | -0.1272 ± 0.0407 | 88.1%     | 41%                 |
| new     | -0.0525  | [-0.125, -0.030] (-0.077) | -0.05 | -0.0556 ± 0.0175 | 63.9%     | 80%                 |


("Gap to truth closed" = distance the behavioural mean travels from the displaced midpoint
toward the truth, as a fraction of the 1 prior SD gap.)

Reading:

- The observations pull the displaced means **substantially** back toward the truth — 42%, 41% and
80% of the gap — and acceptance drops to 41%, so the objective is discriminating here.
- **This reverses what the draft's earlier run showed.** At the 24 h warm-up the same experiment
closed only 9%, 12% and 22% of the gap and retained 99.8% / 96.9% / 92.8% of the prior width, which
is what the "even the informed coefficient is not recovered" reading rested on. Under the corrected
warm-up the data are far more informative than that reading assumed.
- **Attribution is not settled.** Two things changed at once between the two runs: the warm-up
(24 h → 120 h) and the sampling design (2000 pseudo-random → 8192 Sobol). The paired-window design
used in Step 0 — one long simulation, two windows, shared noise and shared draws — is what would
separate them, and it has not been run for this experiment. Until it is, the honest statement is
that the displaced-prior conclusion is warm-up-sensitive, not that the warm-up caused all of it.
- The one-sided-identifiability claim for `k_w,old` therefore needs re-testing too; it was inferred
from the 9% figure. Step 4b's objective curves and Step 4d's 30-realisation version are the
evidence that should carry it, not this table.

Status: this single-realisation table is a first look. The robust version (30 noise
realisations × two thresholds, plus an old-toward-weaker displacement) is **Step 4d** below
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

## Step 4d — robust displaced-prior (30 noise realisations × two thresholds)

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

At threshold **0.12** (the draft's operative threshold; retention 87% DOWN / 65% OLDUP):


| coefficient | DOWN (old on strong side): gap (SD ret) | OLDUP (old on weak side): gap (SD ret) |
| ----------- | --------------------------------------- | -------------------------------------- |
| old         | 8% [4–12] (99%)                         | **62% [55–65] (69%)**                  |
| avg         | 16% [11–21] (97%)                       | 16% [11–20] (96%)                      |
| new         | 23% [14–31] (91%)                       | 13% [8–20] (93%)                       |


At threshold **0.107** (defensible ≈95% band; retention 41% DOWN / 31% OLDUP):


| coefficient | DOWN: gap (SD ret) | OLDUP: gap (SD ret)   |
| ----------- | ------------------ | --------------------- |
| old         | 29% [14–57] (92%)  | **86% [76–92] (52%)** |
| avg         | 46% [29–61] (86%)  | 44% [29–61] (87%)     |
| new         | 77% [56–81] (64%)  | 64% [41–71] (68%)     |


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
- Grid-search best fit (-1.067, -0.147, -0.052); 4543/8192 behavioural at thr 0.107, min RMSE 0.0968.


| zone    | true arith. mean | length-weighted | pipe range     | GLUE mean ± SD | grid fit | bias (GLUE − arith) |
| ------- | ---------------- | --------------- | -------------- | -------------- | -------- | ------------------- |
| old     | -1.007           | -0.989          | [-1.17, -0.80] | -1.030 ± 0.260 | -1.067   | -0.024              |
| average | -0.098           | -0.096          | [-0.12, -0.08] | -0.116 ± 0.042 | -0.120   | -0.018              |
| new     | -0.049           | -0.047          | [-0.06, -0.04] | -0.048 ± 0.023 | -0.037   | +0.001              |


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

### Step 5c — heterogeneity magnitude sweep (0 control / ±20 / 35 / 50%)

Same design, jitter magnitude increased (`step5c_jitter_sweep.py`; the homogeneous candidate
predictions are truth-independent, so the 8192 cached candidates are reused and only the truth is
re-simulated). Bias = weighted mean − true per-zone arithmetic mean.

**Two corrections were needed here, and they pull in opposite directions.** The sweep now includes a
`jitter = 0` control, and it is reported under both weightings.

*Subtract the control.* At `jitter = 0` the truth is exactly homogeneous, so nothing measured there
can be structural — whatever bias appears is that realisation's noise. The raw bias column
therefore **overstates** the structural effect; `incr` (increment over the control) is the honest
part. The control also calibrates the structural residual: 0.0055 mg/L at `jitter = 0` is pure
7×7×7 grid spacing, because a homogeneous truth is exactly representable.

*Use the formal weighting.* The informal score is nearly flat inside the behavioural set, so its
weighted mean is pinned near the centre of the accepted box and cannot follow the data. It
**understates** the structural bias — by a factor of three to four in the old zone.

| jitter | struct. resid. | above grid floor | old bias (SD) / incr | avg bias (SD) / incr | new bias (SD) / incr |
| --- | --- | --- | --- | --- | --- |
| **formal censored (primary)** | | | | | |
| 0 (control) | 0.0055 | 0.0000 | +0.012 (+0.13) / — | −0.009 (−0.64) / — | +0.006 (+0.77) / — |
| ±20% | 0.0068 | 0.0013 | −0.020 (−0.20) / **−0.0325** | −0.010 (−0.74) / −0.0012 | +0.007 (+0.93) / +0.0011 |
| ±35% | 0.0103 | 0.0048 | −0.033 (−0.33) / **−0.0458** | −0.011 (−0.78) / −0.0016 | +0.008 (+1.05) / +0.0020 |
| ±50% | 0.0145 | 0.0090 | −0.037 (−0.36) / **−0.0490** | −0.011 (−0.79) / −0.0016 | +0.009 (+1.18) / +0.0029 |
| **informal GLUE (comparator)** | | | | | |
| 0 (control) | 0.0055 | 0.0000 | −0.011 (−0.04) / — | −0.017 (−0.40) / — | +0.001 (+0.03) / — |
| ±20% | 0.0068 | 0.0013 | −0.020 (−0.07) / −0.0081 | −0.018 (−0.42) / −0.0009 | +0.001 (+0.03) / −0.0001 |
| ±35% | 0.0103 | 0.0048 | −0.022 (−0.09) / −0.0108 | −0.018 (−0.44) / −0.0015 | +0.001 (+0.05) / +0.0004 |
| ±50% | 0.0145 | 0.0090 | −0.025 (−0.10) / −0.0134 | −0.019 (−0.45) / −0.0021 | +0.002 (+0.10) / +0.0016 |

![Bias vs within-zone jitter, against the homogeneous control](figures/step5c_jitter_sweep.png)

**What the single-field table above shows, and why it is not the finding.** Read at face value, the
formal column says symmetric heterogeneity biases the old-zone coefficient, with the increment
growing monotonically to −0.049 m/day (0.36 posterior SD) at ±50%, while the informal score puts the
same increment at −0.013 (0.10 SD). The informal-versus-formal contrast is real and is the same
inertia seen elsewhere. But every row uses **one** jitter field (seed 12345), so the increment mixes
the effect of heterogeneity with the accident of one spatial arrangement. That has to be separated
before anything is claimed.

### Step 5c-ensemble — 25 independent heterogeneity fields at ±20%

The candidate predictions are truth-independent, so repeating over many fields costs one truth
simulation each. 25 fields, formal weighting, control subtracted:

| zone | bias mean | bias SD | structural increment mean | increment SD | \|mean\| / SD |
|---|---|---|---|---|---|
| old | +0.0231 | 0.0335 | **+0.0107** | 0.0335 | **0.32** |
| average | −0.0089 | 0.0046 | +0.0002 | 0.0046 | 0.04 |
| new | +0.0055 | 0.0021 | −0.0005 | 0.0021 | 0.24 |

**This reverses the single-field reading, sign included.** The ensemble-mean structural increment for
`old` is **+0.0107** m/day — weaker decay — where the single field gave **−0.0325**, stronger decay.
The field-to-field scatter is 0.0335, three times the mean, and `|mean| / SD` is 0.32, 0.04 and 0.24
for the three zones. So at ±20% symmetric within-zone heterogeneity there is **no systematic
structural bias detectable above field-to-field variability**, and the single-field number is not
separable from the choice of field.

The conclusion to carry forward is therefore the original one: **symmetric, mean-zero within-zone
heterogeneity averages out** in this network at this noise level. What the corrections established
along the way still stands and still matters — the control must be subtracted, the informal score
does understate whatever effect is present, and the structural residual has a grid floor — but none
of that adds up to a precise-but-biased effect for *symmetric* heterogeneity. For that, correlation
with the flow paths is needed, which is what Step 5d tests.

A note on how this section was arrived at, because it bears on how the thesis should treat any
single-realisation result: the claim here has now been reversed twice, first by adding the `jitter = 0`
control and switching to the formal likelihood, then by replacing one field with 25. Both reversals
came from removing a hidden dependence on one arbitrary choice, and neither would have been visible
from the fit quality, which was excellent throughout.

The structural residual grows 0.0068 → 0.0145 mg/L, but only 0.0013 → 0.0090 of that is above the
grid floor, so the earlier reading "the residual is 7% of the noise floor" overstated it by about
fivefold; against the 0.096 noise floor the true structural part at ±20% is 1.3%. The risk ranking
is unchanged across all magnitudes.

### Step 5d — structured (length-correlated) within-zone heterogeneity → precise-but-biased

Location-consistent design: the truth keeps the three **location** zones,
but within each zone `k_w` is **correlated with pipe length** (longer pipe → stronger decay,
factor 1 + 0.5·s, s ∈ [−1,1] by within-zone length rank). The per-zone **arithmetic** mean is held
exactly at the zone mean, but the **length-weighted** (≈ residence-weighted, i.e. effective) mean
is shifted stronger (`step5d_structured.py`, threshold 0.107; GLUE candidates reused from cache).

| zone | true arith. | length-weighted | GLUE mean ± SD | grid fit | bias (GLUE − arith) | lenwt − arith |
|---|---|---|---|---|---|---|
| old | -1.000 | **-1.2404** | **-1.0666 ± 0.2549** | -1.067 | **-0.0666** | -0.2404 |
| average | -0.100 | -0.1238 | -0.1300 ± 0.0416 | -0.147 | -0.0300 | -0.0238 |
| new | -0.050 | -0.0659 | -0.0593 ± 0.0248 | -0.052 | -0.0093 | -0.0159 |

![Structured heterogeneity: the fit moves toward a length-weighted value](figures/step5d_structured.png)

**Single-realisation reading (one noise draw).** The structural residual stays small (0.0063, so the
fit remains *precise*, RMSE 0.0968 ≈ the noise floor), the length-weighted mean diverges from the
arithmetic mean (old −1.2404 vs −1.000), and the fitted coefficient moves off the arithmetic mean in
that direction — old by 28% of the arithmetic → length-weighted gap, `new` 58%, `average` 126%. Those
three numbers look like a quantity that is not being recovered. They are one noise draw, and the
dose-response below shows that is what the spread looks like, not what the effect is.

### Step 5d-dose — correlation strength × 30 noise realisations

Unlike Step 5c the truth here is deterministic (length rank order), so there is no heterogeneity
field to average over; the single-realisation risk is the noise draw. And if the effect is real it
must vanish at `CORR = 0`, where the two candidate targets coincide, and grow with `CORR`. Both are
tested at once. The statistic is the fraction of the arithmetic → length-weighted gap travelled: 0
means the fit sits on the arithmetic mean, 1 on the length-weighted value.

| `CORR` | gap (old) | old: median [5, 95] | average | new |
|---|---|---|---|---|
| 0.00 | 0.0000 | control — targets coincide | control | control |
| 0.25 | −0.1202 | +1.10 [−0.29, +2.47] | +1.26 [−0.95, +3.72] | +0.98 [−0.89, +2.66] |
| 0.50 | −0.2404 | +0.86 [+0.12, +1.46] | +1.12 [−0.07, +2.43] | +0.92 [−0.03, +1.78] |
| 0.75 | −0.3606 | +0.74 [+0.23, +1.06] | +1.07 [+0.22, +1.93] | +0.89 [+0.26, +1.46] |

**Finding, and it is stronger than the single draw suggested.** The median shift fraction is
**0.74–1.26** at every correlation level and in every zone: the fitted coefficient tracks the
length-weighted value approximately fully, not partially. The single-realisation 28% / 126% / 58%
sits inside these intervals, so it was a noisy draw of a quantity whose median is near 1, and the
"undershoots by 72%" reading was an artefact of one noise seed.

The intervals also behave as a real effect should. They narrow as `CORR` grows — [−0.29, +2.47] at
0.25 against [+0.23, +1.06] at 0.75 — because the gap in the denominator grows while the noise on the
numerator does not. At `CORR = 0.75` all three intervals **exclude zero**, so at sufficient
correlation the conclusion is resolved: the fit is inconsistent with sitting on the arithmetic mean
and consistent with tracking the length-weighted value. At `CORR = 0.25` it is not resolved, which is
the honest limit of what this design can detect.

Note the contrast with Step 5c, and it is the point of having both: symmetric heterogeneity produced
no detectable bias across 25 fields, while length-**correlated** heterogeneity of the same magnitude
produces a fully resolved one. Correlation with the flow paths, not heterogeneity as such, is what
breaks the averaging-out.

**Length-weighted must not be called residence-weighted.** The reaction weight of a pipe depends on
its flow, direction, diameter, residence time and on how strongly the six monitors see it. Length is
one proxy among those, and it happens to separate the two candidate targets in this design, which
is what makes the design useful. Establishing what the fit actually estimates needs a
sensitivity- or Jacobian-weighted effective mean, which this step does not compute — that is open
work, not a result.

**Honest caveat on magnitude.** The old-zone offset of −0.0666 is 0.26 posterior SD under the
informal weighting used here, so the ensemble still covers the truth comfortably. What this step
demonstrates is the *mechanism* — the fit stays precise while the coefficient is pulled away from
the field's simple average — not a dramatic "tight-but-wrong" estimate. Note also that the grid fit
is a coarse instrument for this: the old-zone grid step is 0.2170 m/day (half-step 0.1085), larger
than the bias being measured, so `grid_fit` cannot resolve it and only the weighted mean can.

### Step 5e — grid-search recovery is "centred on the answer" (§3.3, second half)

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

| σ (mg/L) | threshold | median retention | valid runs | accepted | ESS | old SD ret. | avg SD ret. | new SD ret. | band @node15 |
|---|---|---|---|---|---|---|---|---|---|
| 0.02 | 0.021 | 0% | 30/30 | 37 | 37.0 | 15% [12–17] | 17% [12–20] | 19% [15–21] | 0.020 |
| 0.05 | 0.053 | 9% | 30/30 | 700 | 699.1 | 42% [32–48] | 47% [36–52] | 44% [37–52] | 0.053 |
| 0.10 | 0.107 | 52% | 30/30 | 4220 | 4218.0 | 65% [63–72] | 91% [83–94] | 87% [81–91] | 0.087 |
| 0.15 | 0.160 | 79% | 30/30 | 6486 | 6482.6 | 81% [77–88] | 98% [95–99] | 97% [95–98] | 0.126 |

**The three diagnostic columns are new and they close a hole in the earlier version.** Realisations
whose behavioural set came out empty used to be **skipped silently**, so the reported median was a
median over the realisations that happened to sample a good parameter set — a selection bias that
grows as σ shrinks. They are now counted (`valid runs`), together with the accepted count and the
effective sample size. With 8192 Sobol draws instead of 2000 pseudo-random ones, **all 30
realisations are valid at every σ**, so the bias is gone rather than merely visible.

![Sensor-accuracy sensitivity](figures/step6_noise_sensitivity.png)

Findings:

1. **Identifiability is set by sensor accuracy.** At σ = 0.10 only *old* is (marginally) informed
   under this informal weighting (65% of prior width; avg/new 87–91%). Tightening to σ = 0.05
   constrains all three (≈ 42–47%). Loosening to σ = 0.15 leaves everything close to the prior
   (81–98%).
2. **Prediction uncertainty scales ~linearly with σ.** The 5–95% band at the risk-governing
   old-zone node 15 grows from 0.020 (σ = 0.02) to 0.126 mg/L (σ = 0.15).
3. **σ = 0.02 is still sampling-limited, but for a different reason than before.** Every realisation
   now yields a behavioural set, yet the median accepted count is only 37 and the ESS 37.0, well
   under the ~100 effective members a 5–95% interval needs before each tail rests on more than a
   handful. The row is flagged `sampling_limited` in the artifact on that criterion. Its widths
   indicate a direction, not a magnitude; exploiting σ = 0.02 needs a denser ensemble near the
   optimum (importance or adaptive sampling), not a looser threshold.
4. **Read this table as a property of the informal comparator.** It uses the σ-scaled behavioural
   threshold, so it inherits the inefficiency quantified in Steps 1 and 7. A formal-likelihood
   version of this sweep would give tighter widths at every σ and has not been run.

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
coefficient below its prior — a heuristic, not a strict theorem.)

**The formal ensemble attains the bound.** This is the check that closes the whole GLUE-vs-Fisher
argument, and it is new:

| coefficient | Case-A CRLB | formal censored ensemble SD | ratio | informal GLUE SD |
|---|---|---|---|---|
| old | 0.09472 | 0.09380 | **0.99** | 0.26679 |
| average | 0.01340 | 0.01416 | **1.06** | 0.04240 |
| new | 0.00792 | 0.00776 | **0.98** | 0.02419 |

The empirical spread of the formally weighted ensemble sits within 1–6% of the Cramér–Rao bound —
i.e. the formal analysis is efficient, and the Fisher computation is corroborated by an entirely
independent route. The informal score gives 2.8–3.1× the bound on the *same* observations. So the
long-standing "GLUE is three times wider than the CRLB" gap was never evidence that the data are
uninformative, nor a bug in the Jacobian: it is the inefficiency of the score. Only the formal rows
are like-for-like with a CRLB, because the bound describes an efficient estimator under the correct
likelihood.

![Fisher/CRLB with nuisance parameters](figures/step7_fisher.png)

**Case A is the like-for-like benchmark** for the baseline GLUE (both fix k_b and assume no sensor
bias). Cases B and C are **realism sensitivity analyses**, not descriptions of the baseline GLUE.

Findings:

1. **Idealised A — the data do contain information about all three** (CRLB/prior 0.25/0.29/0.29 < 1).
   In fact new/avg have *higher per-unit sensitivity* than old (near-source pipes lie upstream of
   the whole network; direct max|ΔC| up to 0.087 for new vs 0.007 for old). So the observations are
   not fundamentally devoid of information about avg/new.
2. **The A-vs-GLUE gap is entirely the score, and this is now demonstrated rather than argued.**
   The informal GLUE also fixes k_b and ignores bias, so its like-for-like benchmark is A; it gives
   0.71/0.92/0.88 against the bound's 0.25/0.29/0.29. The formal ensemble on the same data gives
   0.25/0.31/0.28 — the bound, to within 6%. The residual explanations previously offered for the
   gap (threshold, zero-clipping, non-linearity, finite sampling, old's one-sided response) are
   therefore second-order at most: dropping the factor `N` from the likelihood accounts for it, as
   Stedinger 2008 / Mantovan & Todini 2006 predict. It must **not** be attributed to k_b or bias,
   which are absent from both.
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
5. **The condition number on the raw matrix is mostly a units artefact.** κ ≈ 216 / 103 / 111 for
   A/B/C looks like a badly ill-conditioned problem, but the three coefficients differ in scale by a
   factor of 20, so eigenvalues of the unnormalised information matrix mix magnitudes as much as
   geometry. Rescaling the parameters by their prior SD makes them dimensionless:

   | form | eigenvalues (Case A) | condition number |
   |---|---|---|
   | raw | 24056 / 5189 / 111 | **216** |
   | prior-scaled | 24.7 / 16.6 / 7.7 | **3.2** |

   On the dimensionless matrix the spread is a factor of **3.2**, not 216, so the three coefficients
   are far more comparably informed than the raw number suggests. This also qualifies the framing the
   review quoted from the operational notebook — "eigenvalues spanning three orders of magnitude for
   three zonal coefficients" — which is a statement about the units, not about identifiability. The
   sloppiest direction, in prior-SD units, is `old −0.301, average −0.658, new +0.690`: essentially
   **average traded against new**, which is the same confounding every other diagnostic finds. Note
   also that the *smaller* κ for B/C does not mean better identifiability — κ is only the relative
   imbalance between directions, and adding nuisance parameters lowers the total information.
6. **The finite-difference step is not driving any of this.** `H = 0.02` is 2% of the old truth but
   40% of the new one, so each coefficient was re-differenced over a range of steps:

   | coefficient | steps tested | step as % of truth | Case-A CRLB spread over the sweep |
   |---|---|---|---|
   | old | 0.005 – 0.04 | 0.5 – 4% | **0.10%** |
   | average | 0.002 – 0.02 | 2 – 20% | **1.00%** |
   | new | 0.001 – 0.01 | 2 – 20% | **1.14%** |

   The CRLB is flat to ~1% across a fourfold to tenfold change of step, so the derivatives are
   converged and the shared 0.02 carries at most a ~1% error even where it is a 40% perturbation. The
   concern was legitimate and the answer is that it does not matter at this precision.

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

**Two versions are reported, because the grid one is quantised.** The 21-point grid steps 0.0650
m/day in the `old` direction — coarser than several effects discussed elsewhere in this log (the
censoring shift is 0.012, structural increments ~0.01) — so a grid interval can only place its
endpoints on nodes *inside* the true interval, and is therefore biased narrow. The continuous version
minimises the two nuisance coefficients with Nelder–Mead at each target value and locates the
endpoints by Brent bisection on `ΔNLL − 1.92`; 2316 distinct EPANET evaluations, 75 s.

| coefficient | grid 95% | continuous 95% | grid half-width | continuous half-width | change | endpoint move |
|---|---|---|---|---|---|---|
| old | [−1.110, −0.850] | **[−1.1517, −0.7973]** | ±0.1300 | ±0.1772 | **+36.3%** | 0.81 grid steps |
| average | [−0.136, −0.088] | **[−0.1367, −0.0817]** | ±0.0240 | ±0.0275 | **+14.5%** | 0.78 grid steps |
| new | [−0.057, −0.034] | **[−0.0600, −0.0296]** | ±0.0119 | ±0.0152 | **+28.4%** | 0.83 grid steps |

**The grid understated every interval, by 15–36%.** The endpoints move by about 0.8 of a grid step in
all three cases and always outward, which is the signature of quantisation rather than of noise: a
grid cannot find a crossing that falls between nodes, so it stops at the last node inside. The
continuous unconstrained minimum is at `k_w = (−0.9555, −0.1067, −0.0443)` with NLL 138.6980, against
138.7895 for the best grid neighbourhood.

The truth −1.0 / −0.1 / −0.05 lies inside every interval under both versions. Only the continuous
intervals should be quoted, and the same caution applies to anything else read off that grid — which
is why the AR(1) widening factor for `old` in Step 7c (2.00×) should not be read as physical: its
independent-case denominator was one of these too-narrow grid intervals.

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
| old | ±0.0947 | ±0.1406 | 1.48× | 0.25 | 0.37 |
| average | ±0.0134 | ±0.0199 | 1.49× | 0.29 | 0.43 |
| new | ±0.0079 | ±0.0114 | 1.44× | 0.29 | 0.42 |

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
| old | [-1.110, -0.850] | [-1.240, -0.720] | ±0.130 → ±0.260 | 2.00× |
| average | [-0.136, -0.088] | [-0.144, -0.072] | ±0.024 → ±0.036 | 1.50× |
| new | [-0.057, -0.034] | [-0.067, -0.029] | ±0.012 → ±0.019 | 1.60× |

The `old` factor of 2.00× should not be read as a physical result: the grid step in that direction
is 0.065 m/day, so each endpoint is quantised to about half the half-width being reported and the
ratio of two quantised numbers is coarse. `average` and `new` are on finer grids and their profile
widening (1.50–1.60×) agrees with the Fisher-CRLB widening (1.44–1.49×): both formal
tools react to AR(1) the same modest way, and the truth still lies inside every AR(1) interval — so
AR(1) inflates but does not overturn the idealised identifiability. (The scalar `√[(1+ρ)/(1−ρ)]≈1.53`
is only a reference; the per-coefficient factors above come from the full covariance.)

---

## Step 8 — systematic sensor bias (GLUE, empirical) — Priority-2 #1

A constant offset is added to one informative old-zone monitor (node 15) and the calibration is
re-run (`step8_sensor_bias.py`; cache reused, 30 noise realisations, **formal censored weighting** —
measuring the damage with the informal score would understate it, as Step 5c shows for structural
error). The sweep is **two-sided**, because observations are censored at the sensor floor and a
negative offset is therefore not the mirror image of a positive one. Posterior SD of `k_w,old` with
no offset (the random spread) = **0.1012**.

| bias @ node 15 | old mean | old shift | shift / SD | avg mean | new mean | censored pts | ρ_Spearman | τ_Kendall | top-6 Jaccard |
|---|---|---|---|---|---|---|---|---|---|
| −0.100 | −1.4274 | −0.3869 | −3.82 | −0.1017 | −0.0498 | 13 | 1.000 | 0.990 | 1.00 |
| −0.050 | −1.3028 | −0.2623 | −2.59 | −0.1033 | −0.0493 | 9 | 1.000 | 0.994 | 1.00 |
| −0.025 | −1.1745 | −0.1339 | −1.32 | −0.1033 | −0.0500 | 8 | 1.000 | 0.996 | 1.00 |
| 0.000 | −1.0405 | +0.0000 | +0.00 | −0.1028 | −0.0509 | 7 | 1.000 | 1.000 | 1.00 |
| +0.025 | −0.9231 | +0.1174 | +1.16 | −0.1020 | −0.0519 | 6 | 1.000 | 0.994 | 1.00 |
| +0.050 | −0.8192 | +0.2213 | +2.19 | −0.1013 | −0.0529 | 5 | 0.999 | 0.991 | 0.71 |
| +0.100 | −0.6486 | +0.3919 | +3.87 | −0.0993 | −0.0551 | 5 | 0.999 | 0.988 | 0.71 |

Rank columns compare the 92-node risk field against the unbiased case; `top-6 Jaccard` compares the
hot-spot sets.

![Systematic bias pushes the calibrated coefficient](figures/step8_sensor_bias.png)

Findings:

1. **A systematic bias dominates the random spread by a factor of several.** A +0.05 mg/L offset at
   node 15 moves `k_w,old` from −1.0405 to −0.8192 — **2.19 posterior SD**, away from the truth −1.0
   — and +0.10 gives **3.87 SD**. The review's claim that "a +0.05 mg/L offset shifts the estimate by
   more than the entire random spread" is confirmed, and understated. A positive bias (sensor
   over-reads) makes the fit infer *weaker* decay.
2. **Only the locally-sensed coefficient moves.** `avg`/`new` shift by ≤0.004 across the whole ±0.10
   sweep — the bias corrupts `old`, not the others.
3. **The risk field is far more robust than the parameter.** At ±0.10, where `k_w,old` has moved
   almost 4 posterior SD, the 92-node risk ranking still has Spearman 0.999 and Kendall ≥ 0.988
   against the unbiased case. The top-6 set is *unchanged* for every negative offset and loses one
   node at +0.05 and +0.10 (Jaccard 0.71). So an uncorrected sensor bias wrecks the coefficient while
   leaving the operational prioritisation nearly intact — which is reassuring operationally and a
   warning against reading the coefficient as physical.
4. **Shape — the review is right, and our first answer was wrong.** Halving the offset
   (0.05 → 0.025) retains **53%** of the shift: above the 50% that linearity would give, so the
   response is sub-linear/**concave**, as the review states, though weaker than the ~70% it cites.
   An earlier version of this section reported *convex/39%*. That figure came from the informal GLUE
   score, whose flatness inverts the curvature as well as shrinking the shift. This is the third
   place where the informal score reverses a conclusion, after Steps 3 and 5c.
5. **The response is asymmetric, and censoring is why.** `|negative| / |positive|` shift ratios are
   1.14, 1.19 and 0.99 at ±0.025, ±0.05 and ±0.10, while the number of observations sitting on the
   sensor floor runs 13 → 5 across the sweep. A negative offset pushes observations onto the floor,
   where a censored point carries different information from an unclipped one. Bias results must
   therefore always be quoted with their sign; a single ± figure is not meaningful.
6. **Empirical counterpart to Step 7 Case C.** Fisher showed per-monitor offsets *absorb* the signal
   (avg/new → unidentifiable); this run shows a real offset *biases* the most robustly informed
   coefficient. A real bias would be estimable and correctable by reference sampling — the
   operational notebook's QA step; this quantifies the **uncorrected** impact. Only a constant offset
   is modelled here, not drift.

**Why node 15, and does the location matter? (bias-location sweep, `step8c_bias_bynode.py`).** The
same offset was injected at each of the six monitors in turn (two per zone: new 107/113, old 15/145,
average 209/231; threshold 0.107, 30 noise). Δ = shift of each coefficient's behavioural mean from
the unbiased baseline (means old −1.040 / avg −0.119 / new −0.052; SDs 0.260 / 0.042 / 0.024).

| offset | biased node (zone) | Δold | Δavg | Δnew | own-coef shift/SD | risk top-3 |
|---|---|---|---|---|---|---|
| +0.05 | 107 (new) | -0.0248 | -0.0016 | +0.0103 | +0.43 | 131, 129, 141 |
| +0.05 | 113 (new) | -0.0241 | -0.0021 | +0.0110 | +0.46 | 131, 129, 141 |
| +0.05 | **15 (old)** | **+0.1042** | +0.0011 | -0.0007 | +0.42 | 131, 129, 141 |
| +0.05 | 145 (old) | +0.0722 | -0.0001 | +0.0028 | +0.29 | 131, 129, 141 |
| +0.05 | 209 (avg) | -0.0194 | +0.0090 | +0.0077 | +0.21 | 131, 129, 141 |
| +0.05 | 231 (avg) | -0.0056 | +0.0239 | +0.0002 | +0.57 | 131, 129, 141 |
| +0.10 | 107 (new) | -0.0795 | -0.0072 | +0.0226 | +0.94 | 131, 129, 141 |
| +0.10 | 113 (new) | -0.0768 | -0.0128 | +0.0235 | +0.98 | 131, 129, 141 |
| +0.10 | **15 (old)** | **+0.3182** | +0.0038 | -0.0022 | +1.29 | 131, 129, 139 |
| +0.10 | 145 (old) | +0.2468 | +0.0029 | +0.0060 | +1.00 | 131, 129, 139 |
| +0.10 | 209 (avg) | -0.0448 | +0.0219 | +0.0194 | +0.52 | 131, 129, 141 |
| +0.10 | 231 (avg) | -0.0128 | +0.0483 | +0.0001 | +1.15 | 131, 129, 141 |

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
| -0.4 | -1.0741 (-0.0373) | -0.1286 | -0.0613 | 131, 141, 139 |
| -0.5 | -1.0368 (+0.0000) | -0.1170 | -0.0517 | 131, 129, 141 |
| -0.6 | -1.0086 (+0.0282) | -0.1049 | -0.0422 | 131, 243, 20 |

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
| full record (6 × 169 h) | **43 / 1014** | the whole 168 h simulation |
| calibration (6 × 49 post-warm-up h) | **10 / 294** | the points actually used to fit |
| by node | 15 (old): 6, 145 (old): 3, 231 (average): 1 | old 9, average 1, new 0 |

At the corrected warm-up the clipping is no longer confined to the old zone: one point now falls at
an average-zone monitor. The concentration in the average zone has dropped far enough by 120 h to
reach the sensor floor occasionally, which the 24 h window never showed.

**Naive-exact-0 vs censored-at-0 (median [IQR] over 30 noise realisations):**

| coefficient | truth | naive median [IQR] | censored median [IQR] | Δ median |
|---|---|---|---|---|
| old | −1.0 | −1.0289 [−1.1180, −0.9700] | −1.0405 [−1.1324, −0.9850] | −0.0116 |
| average | −0.1 | −0.1027 [−0.1122, −0.0952] | −0.1028 [−0.1122, −0.0953] | −0.00003 |
| new | −0.05 | −0.0510 [−0.0566, −0.0434] | −0.0509 [−0.0564, −0.0433] | +0.00007 |

- node-15 fraction of hours below 0.2: naive `0.470` vs censored `0.470` (identical);
- high-risk top-3 — ranked by expected time-fraction below 0.2 mg/L under the **formal-likelihood-
  weighted ensemble** over all 8192 candidates: **131, 141, 129 — identical** under both estimators,
  and now also identical to the primary risk map of Step 10, because both use the formal weighting;
- old profile 95% interval (baseline): naive `[−1.110, −0.850]` = censored `[−1.110, −0.850]`.

The profile intervals being *exactly* equal is a resolution artefact, not a null result. The
ensemble means do move — censored −1.0405 against naive −1.0289, a shift of −0.0116 — but the 21-point
grid steps 0.065 m/day in the `old` direction, five times the shift, so no grid-based interval can
register it. The censoring correction is measurable in the weighted mean and invisible in the
profile; only the first should be quoted.

![Zero-clipping census (10/294) and the old profile at L=0: naive vs censored overlap](figures/step9_zeroclip.png)

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
> *Results.* Ten of the 294 post-warm-up calibration observations were clipped to zero — six at
> node 15, three at node 145 and one at node 231 (43 of 1014 over the full record), so the censoring
> is concentrated in, but not confined to, the low-residual old zone. Across 30 independent noise
> realisations the median old-group estimate changed from −1.0289 to −1.0405 m/day when the censored
> likelihood replaced the exact-zero treatment, while the average- and new-group estimates were
> unchanged; the low-chlorine summary and the risk ranking were identical.
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
far below* the threshold a node sits. From the ensemble weighted by the formal censored likelihood
(with the informal GLUE score reported alongside as a comparator) we therefore report the original probability re-expressed as a duration,
**two** genuine severity metrics (minimum concentration, cumulative deficit) and **one**
reaction-independent hydraulic diagnostic (water age) — i.e. *one operational re-expression + two
severity metrics + one hydraulic diagnostic*, not "three new metrics" (`step10_risk_metrics.py`).

**Time axis.** The post-warm-up record is `t = 120 … 168 h` = **49 reporting points but
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
| 131 | **48.0 [48.0, 48.0]** | **4.22 [4.11, 4.32]** | 0.034 [0.03, 0.03] | 70.2 |
| 141 | 22.3 [20.0, 24.0] | 2.20 [2.08, 2.35] | 0.068 [0.06, 0.07] | 50.8 |
| 139 | 22.0 [22.0, 22.0] | 1.82 [1.73, 1.91] | 0.102 [0.10, 0.11] | 53.8 |
| 145 | 12.0 [12.0, 12.0] | 1.68 [1.62, 1.73] | 0.031 [0.03, 0.03] | 31.3 |
| 15 | 22.0 [22.0, 22.0] | 1.38 [1.16, 1.59] | 0.055 [0.05, 0.06] | 38.9 |
| 143 | 22.0 [22.0, 22.0] | 1.16 [0.95, 1.37] | 0.062 [0.06, 0.07] | 39.6 |
| 129 | 24.0 [24.0, 24.0] | 0.84 [0.80, 0.88] | 0.147 [0.15, 0.15] | 53.2 |
| 253 | 8.0 [8.0, 8.0] | 0.75 [0.72, 0.79] | 0.099 [0.09, 0.10] | 30.3 |

**Water age ↔ risk (all n = 92 junctions):** Spearman `0.73` (bootstrap 95 % `[0.61, 0.81]`) for
duration and `0.72` for deficit; Pearson `0.86`. Spearman is the primary statistic (risk metrics are
non-linear and many nodes are 0). The ordinary p-value is deliberately not quoted: the 92 junctions
share pipes, flow paths and tank states, so they are nowhere near 92 independent samples and any
p-value computed as if they were is meaningless. The bootstrap interval resamples nodes and is also
optimistic for the same reason; treat `0.73` as a descriptive effect size.

**Robustness of the pattern to the inference convention.** Both weightings give effectively the same
operational answer, which is the question the review asked:

| scheme | ESS | network-mean E[D] (h) | network-mean E[A] | top-10 overlap with primary |
|---|---|---|---|---|
| formal censored (primary) | 157 | 3.431 | 0.2181 | — |
| informal GLUE | 4783 | 3.417 | 0.2207 | Jaccard 0.82 |

The aggregate severity differs by 1.2% between schemes and eight of ten hot-spot nodes are shared.
The node identities are, however, **more sensitive to the warm-up than to the weighting**: node 243,
previously ranked worst by deficit, leaves the top ten entirely at the corrected 120 h warm-up.

**Which network average?** An unweighted mean over 92 junctions counts a zero-demand node the same as
the largest consumer. 59 of the 92 junctions carry non-zero demand, totalling 192.6 L/s, so the
choice matters and all three are reported rather than one being taken silently:

| metric | unweighted (all 92) | consumer-only (59) | demand-weighted |
|---|---|---|---|
| `E[D]` (h) | 3.4309 | **4.4610** | **2.3554** |
| `E[A]` (mg/L·h) | 0.2181 | 0.3053 | 0.1567 |
| min C (mg/L) | 0.4922 | 0.4412 | 0.5297 |

The two adjustments move in **opposite** directions, and the reason is a result in itself:
consumer-only is *worse* than unweighted (4.46 vs 3.43 h) while demand-weighted is *better* (2.36 h).
That combination can only happen if the risk concentrates at **small** consumers rather than large
ones — network extremities and low-turnover dead-ends, which is where long residence time is
expected. So the worst chlorine conditions coincide with the least demand.

This has two consequences for reporting. The unweighted figure used elsewhere in this log is the
**conservative** choice, not a flattering one — demand-weighting would lower every severity number by
about a third. And a demand-weighted headline would understate exactly the customers the risk map is
supposed to find, so the consumer-only average is the one to quote alongside any demand-weighted
figure.

**Does hourly reporting miss short excursions?** The water-quality solver steps at 300 s but the risk
metrics integrate the **hourly** report, so a dip beginning and ending inside one hour is invisible,
and trapezoidal integration of a binary indicator places any crossing at the midpoint between
reports. The 12 highest-weight members were re-run at three reporting resolutions:

| report step | points in window | network-mean `E[D]` (h) | network-mean `E[A]` | top-10 Jaccard vs hourly |
|---|---|---|---|---|
| 3600 s | 49 | 3.436 | 0.2180 | 1.00 |
| 900 s | 193 | 3.374 | 0.2159 | 1.00 |
| 300 s | 577 | 3.380 | 0.2164 | 1.00 |

Going from hourly to the solver's own 300 s changes `E[D]` by **−1.6%** and `E[A]` by **−0.7%**, and
the top-10 set is identical. Two things are worth noting. The change is **negative**, so hourly
reporting slightly *over*-estimates duration rather than missing excursions — the smearing of
crossings by trapezoidal integration outweighs any dip lost between reports. And most of the change
appears by 900 s and does not continue to 300 s, which is what convergence looks like. **Hourly
reporting is therefore adequate here**, and it is adequate because the chlorine field is smooth on
the hour scale in this network, not because sub-hourly behaviour was assumed away.

![Risk associated with water age; top nodes' expected duration with 5-95% bands](figures/step10_risk_metrics.png)

Findings:

1. **Duration and depth give different internal rankings within a broadly overlapping hotspot
   cluster.** Node **131** is worst on both counts here (below 0.2 for the full 48 h *and* the
   largest deficit at 4.22 mg/L·h), but below it the two metrics disagree: **145** is a *deep but
   short* risk (min C 0.031, only 12 h) while **129** is *long but shallow* (24 h, min C 0.147, the
   smallest deficit in the table). The cluster {131, 141, 139, 145, 15, 143, 129, 253} overlaps
   broadly across metrics while the internal order changes, which is the point of reporting duration
   and depth separately.
2. **Ensemble uncertainty is much tighter than under the informal score.** With the formal weighting
   the 5–95 % bands collapse to a fraction of their previous width (node 15: 22.0 [22.0, 22.0] h,
   where the informal ensemble gave 8–24 h). That is the same efficiency gain seen in the parameters,
   propagated into the risk metrics: the earlier wide bands were mostly the weighting's inertia, not
   irreducible parameter uncertainty.
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
   result — hence Spearman, not absolute ages, is reported as the finding. **Step 0 settles what
   this parenthetical used to leave open: a longer run does not fix it.** The cycle-to-cycle change
   in the age field is still 12.8 h at a 120–144 h warm-up and decays by only ~12% per cycle, so the
   crossing extrapolates to ≈600 h — far beyond the 168 h the model permits. Absolute water ages in
   Net3 are therefore horizon-dependent by construction, not merely under-converged here, and must
   never be quoted as steady-state values. The three window definitions are stored in
   `step10_risk_metrics.json` under `age_windows` so the choice is always explicit.
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
| 107 (new) | -1.040 | -0.116 | -0.051 | 0.097 | 0.92 |
| 113 (new) | -1.036 | -0.116 | -0.052 | 0.102 | 0.90 |
| **15 (old)** | **-0.985** | -0.115 | -0.053 | 0.095 | 0.94 |
| 145 (old) | -1.025 | -0.117 | -0.051 | 0.091 | 0.94 |
| 209 (average) | -1.037 | -0.119 | -0.053 | 0.099 | 0.92 |
| 231 (average) | -1.035 | -0.119 | -0.052 | 0.098 | 0.92 |

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
4. **But this is the easy case, and on its own it does not support the claim it was asked for.**
   Every held-out monitor has a partner in the same zone, so the zone stays observed. Two harder
   tests were added.

### Step 11b — leave-one-ZONE-out: what happens when a zone becomes unobserved

Both monitors of one zone are dropped, so the calibration has four monitors and one zone with no
sensor at all. This is the test that speaks to the actual claim.

Both weightings are run: informal for continuity with Step 11a, formal so that the heterogeneous-truth
test below differs from this one *only* in the truth.

| scheme | zone dropped | monitors | `k_w,old` | `k_w,avg` | `k_w,new` | own-coef error | own SD retained | pred RMSE | 90% cov |
|---|---|---|---|---|---|---|---|---|---|
| informal | old | 15, 145 | **−0.850** | −0.115 | −0.052 | **+0.150** | **100%** | 0.100 | 0.96 |
| informal | average | 209, 231 | −1.045 | **−0.120** | −0.054 | **−0.020** | **100%** | 0.099 | 0.93 |
| informal | new | 107, 113 | −1.035 | −0.116 | **−0.052** | −0.002 | 95% | 0.100 | 0.92 |
| formal | old | 15, 145 | **−0.851** | −0.102 | −0.051 | **+0.149** | **100%** | 0.100 | 0.96 |
| formal | average | 209, 231 | −1.038 | **−0.120** | −0.050 | **−0.020** | **100%** | 0.099 | 0.92 |
| formal | new | 107, 113 | −1.049 | −0.101 | **−0.049** | +0.001 | **57%** | 0.101 | 0.90 |

**Finding, and it changes what the LOO result is worth.** Remove a zone's two monitors and that
zone's coefficient **reverts to its prior midpoint** — `old` to −0.850 (prior mid −0.850) with 100% of
the prior width retained, `average` to −0.120 (prior mid −0.120), also 100%. Under both weightings.
So for those two zones each coefficient is informed by its own two monitors and by nothing else.

`new` is the exception and it is instructive: under the formal likelihood it keeps **57%** of the
prior width even with both its monitors gone, so some information about it does arrive from
elsewhere. That fits Step 7's Jacobian, where `new` has the largest per-unit sensitivity at *every*
monitor (max |ΔC| 0.087 against 0.007 for `old`) because the new-zone pipes sit upstream of the whole
network. Spatial borrowing exists, but only for the zone the water passes through first.

The decisive observation is the pair of right-hand columns: **prediction quality is unchanged**.
Held-out RMSE is still ≈0.10 mg/L and coverage still 0.92–0.96, even for the zone whose coefficient
carries a +0.150 error and has learned nothing. So **predictive success is not evidence of parameter
identifiability**, and the LOO result of Step 11a cannot be read as validating the coefficients.
Prediction survives because the prior is centred near the truth — the same artefact the review
identified in §3.1 — so the prior-mean prediction is already good. §3.1's problem and §4-#6's
validation are the same problem seen twice.

### Step 11c — junctions that never enter any calibration

20 unmonitored junctions (seed 7), predicted against the **noise-free truth**. The band construction
differs from Step 11a on purpose: predicting a truth value needs the parameter spread only, with no
measurement-noise term, because there is no sensor there to add noise.

| weighting | 90% coverage (normal approx.) | 90% coverage (weighted quantile) | mean \|pred − truth\| / mean\|truth\| |
|---|---|---|---|
| informal GLUE | 1.00 | 1.00 | 0.006 |
| formal censored | 1.00 | 1.00 | 0.008 |

Nominal coverage is 0.90, so both schemes **over-cover**: the bands are conservative rather than
calibrated. Mean prediction error at unmonitored junctions is 0.6–0.8% of the local concentration.
The weighted-quantile band is reported alongside the normal approximation because the ensemble is
skewed and censored at zero, where a symmetric band is not conservative in the direction that
matters; here the two agree, so the approximation is adequate at these junctions.

### Step 11d — the hardest case: leave-one-zone-out on a heterogeneous truth

Tests a–c all use a truth generated by the same three-zone model that is then fitted, so no structural
discrepancy can appear. Here the truth carries ±20% per-pipe heterogeneity (the Step 5c design, 8
independent fields) **and** a zone is unobserved, so extrapolation and structural error are tested
together — the combination the risk map actually relies on. Formal weighting, so the only difference
from the formal rows of Step 11b is the truth. The coefficient error is measured against each field's
own arithmetic zone mean, so it is not inflated by the heterogeneity itself.

| zone dropped | own-coef error | own SD retained | pred RMSE | 90% cov | unmonitored rel. error |
|---|---|---|---|---|---|
| old | +0.139 | 100% | 0.098 | 0.96 | 0.008 |
| average | −0.020 | 100% | 0.097 | 0.94 | 0.012 |
| new | +0.012 | 55% | 0.102 | 0.88 | 0.011 |

**The structural discrepancy adds almost nothing on top of losing the sensors.** Compare row by row
with the formal rows of Step 11b: coefficient errors +0.139 / −0.020 / +0.012 against +0.149 / −0.020
/ +0.001, SD retained 100 / 100 / 55% against 100 / 100 / 57%, prediction RMSE and coverage within
0.005 and 0.02. Prediction at unmonitored junctions stays at 0.8–1.2% relative error. So in this
network, at this noise level, **the cost of an unobserved zone dominates the cost of ±20% within-zone
structural error by a wide margin** — consistent with Step 5c, where the same heterogeneity produced
no detectable bias across 25 fields.

One number does move in the right direction to be worth noting: coverage for the dropped `new` zone
falls to 0.88, just under the nominal 0.90, the only sub-nominal figure in any of these tests. It is
the case with both a structural discrepancy and the partially-informed coefficient, so it is where
the bands would be expected to lose calibration first.

**What the four tests together do and do not establish.** They establish internal consistency and
they locate its limits precisely: the calibrated ensemble reproduces unseen monitors at the noise
floor and unseen junctions to about 1%, with conservative bands, and it keeps doing so under ±20%
structural error. They do **not** establish external validity — the truth is always model-generated —
and Step 11b shows they do not even establish that the coefficients are informed, since prediction
succeeds while a coefficient sits at its prior. The honest summary is that **spatial prediction and
parameter identification are separately valid claims here, and only the first of them is supported.**

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
(`k_b = −0.5` fixed; formal censored weights, 2196/8192 draws retained, ESS 157). The supervisor's
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
- The window is **48 h** (`t = 120…168`, post warm-up), so `P_min` is a 48-hour window
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
draws span `17.59–72.05` (bulk) and `5.10–70.24` kJ/mol (wall), all above the 5 kJ/mol bound. The water-temperature
offset is now truncated too, to `±4.0 °C`, which is exactly the range that keeps every scenario mean
inside the stated `8–24 °C` validity window; realised temperatures span `8.48–23.50 °C` and no draw
needed resampling. All of these are recorded in `step12_scenarios.json` rather than only printed,
so they can be checked.

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

All means below are weighted by the **formal censored likelihood** (the primary scheme from Step 1);
the informal GLUE score is not used for these headline numbers.

| Scenario | mean k_b | mean k_w,old | `P_min>0.5` nodes | demand at risk | % demand | high/very-high | indeterminate | net-mean `P_bar` | net-mean `E[D]` (h) | net-mean `E[A]` (mg/L·h) |
|---|---|---|---|---|---|---|---|---|---|---|
| A. Baseline 12 °C | −0.504 | −0.994 | 21 | 36.3 L/s | 18.8 % | 10 | 0 | 0.0708 | 3.398 | 0.2216 |
| B. Warm season 16 °C | −0.655 | −1.222 | 28 | 45.0 L/s | 23.4 % | 13 | 8 | 0.0884 | 4.245 | 0.3645 |
| C. Heatwave 20 °C | −0.848 | −1.501 | 29 | 47.8 L/s | 24.8 % | 14 | 4 | 0.1087 | 5.218 | 0.5218 |
| D. Heatwave + ageing stress | −0.848 | −2.777 | 31 | 49.4 L/s | 25.6 % | 15 | 4 | 0.1232 | 5.912 | 0.5790 |

Continuity check against Steps 1–11: with the temperature held at `T_ref` exactly (cached
`C_all`, no `δT`), the baseline gives 21 nodes / 36.3 L/s and `E[A] = 0.2181`. Sampling the
stated temperature uncertainty therefore did **not materially change** the baseline
classification — the `P_min>0.5` count and demand at risk are unchanged and network-mean
`E[A]` moves by under 2 % (`0.2181 → 0.2216`).

![Four-panel window-breach probability maps](figures/step12_scenario_maps.png)

![Ageing increment ΔP_min = P(D) − P(C) at 20 °C](figures/step12_ageing_delta.png)

![Scenario escalation, dosing evaluation and ageing sensitivity](figures/step12_summary.png)

**Escalation.** Seven consumer junctions change risk band between A and D, carrying 18.9 L/s
(10 % of network demand); **six of the seven are unmonitored**. The largest ageing-only
increments at the same temperature (D − C) are nodes 217 (`ΔP_min = +0.346`), 239 (`+0.155`)
and 215 (`+0.091`).

**Ageing-stress sensitivity — is scenario D an artefact of `α_old = 1.85`?**

| ageing set | `α_avg` | `α_old` | `P_min>0.5` nodes | demand at risk | high/very-high | indeterminate | net-mean `E[D]` (h) | net-mean `E[A]` (mg/L·h) |
|---|---|---|---|---|---|---|---|---|
| mild | 1.15 | 1.40 | 30 | 49.4 L/s | 15 | 4 | 5.515 | 0.550 |
| central | 1.35 | 1.85 | 31 | 49.4 L/s | 15 | 4 | 5.912 | 0.579 |
| severe | 1.50 | 2.20 | 31 | 49.4 L/s | 16 | 4 | 6.178 | 0.599 |

The **headline binary metrics are nearly insensitive** to the tested multiplier range: the count
varies only from 30 to 31, demand at risk stays at 49.4 L/s and the indeterminate count is
constant. The **continuous severity metric increases monotonically** (`E[A]` 0.550 → 0.579 →
0.599 mg/L·h), and node-level probabilities do move with `α`. So the hot-spot conclusion is
robust to the multiplier choice, but the magnitude of the ageing penalty is not — it should be
reported as a stress-test range, never as "the effect of ageing".

### 12.4 Corrective dosing (control-measure evaluation, not a recommendation)

The dose scales **both** the reservoir source quality and the tank initial quality, so the whole
source regime is raised consistently. (An earlier run left tanks fixed at `0.5 mg/L`, which
confounded the result with an un-dosed boundary condition.) `inlet = 1.00` reuses scenario C.

| inlet (mg/L) | `P_min>0.5` nodes | demand at risk | % demand | net-mean `P_min` | net-mean `E[D]` (h) | net-mean `E[A]` (mg/L·h) | median-over-nodes of mean window min (mg/L) |
|---|---|---|---|---|---|---|---|
| 1.00 | 29 | 47.8 L/s | 24.8 % | 0.3246 | 5.218 | 0.5218 | 0.463 |
| 1.15 | 28 | 45.0 L/s | 23.4 % | 0.3112 | 4.628 | 0.4527 | 0.532 |
| 1.30 | 28 | 45.0 L/s | 23.4 % | 0.2915 | 4.288 | 0.3957 | 0.601 |

(The last column takes, per junction, the likelihood-weighted mean of the per-member window minimum,
then the median across the 92 junctions — it is **not** a pooled member-node median. It scales
almost exactly with the dose, `0.463 × 1.15 = 0.532`, `0.463 × 1.30 = 0.601`.)

**Linearity known-answer test.** Measured `max |C(1.3) − 1.3·C(1.0)| = 1.4e-05 mg/L`. Stated
precisely: *under fixed hydraulics and demands, first-order bulk and wall kinetics, and
proportional scaling of all source and initial chlorine concentrations, increasing the dose by a
factor `r` is mathematically equivalent to evaluating the unscaled concentration field against a
threshold `C_crit / r`.* This equivalence is a property of that idealisation — it does **not**
imply that dosing is linear in a real network with dose-dependent chemistry, DBP formation or
booster constraints.

**Paired warm-up test — the roles are now reversed.** In the draft version of this script the
168 h / 120 h horizon was the experimental arm being tested against a 72 h / 24 h baseline. Step 0
settled that question, so 168 h / 120 h is now the baseline and the short horizon is the
comparator: the rows below measure **what the draft's warm-up cost**, not whether the current one
is adequate. Identical 275-member subset (stride 8), identical weights and identical `(E_a, δT)`
draws; only the simulation horizon differs.

| inlet (mg/L) | nodes short / long | demand at risk short / long | `E[D]` short / long (h) | `E[A]` short / long (mg/L·h) | rel. change |
|---|---|---|---|---|---|
| 1.00 | 31 / 31 | 49.5 / 49.5 L/s | 5.370 / 5.389 | 0.5052 / 0.5484 | +8.6 % |
| 1.15 | 29 / 29 | 45.2 / 47.8 L/s | 4.655 / 4.788 | 0.4306 / 0.4789 | +11.2 % |
| 1.30 | 29 / 28 | 45.2 / 45.0 L/s | 4.040 / 4.369 | 0.3736 / 0.4220 | +13.0 % |

Read honestly, with one caveat that has grown: the subset is now less representative than before
(long-horizon subset `E[A] = 0.5484` against the full ensemble's `0.5218`, a 5 % gap, because the
formal weights are concentrated and a stride-8 thinning samples them unevenly). So the +8.6 % to
+13.0 % figures carry a few percent of subset error and should be read as "of order 10 %", which
is also what Step 0's cycle-to-cycle analysis independently gives. The **conclusion is unchanged**
under both horizons: node counts and demand at risk are essentially the same, every metric still
improves monotonically with dose, and demand at risk stays well above the 36.3 L/s baseline.

**Read the binary and continuous columns together.** The identical 45.0 L/s at 1.15 and 1.30 is
a **threshold artefact**, not evidence that the extra dose does nothing: the continuous metrics
improve monotonically (`E[D]` 5.22 → 4.63 → 4.29 h; `E[A]` 0.522 → 0.453 → 0.396). Even so,
+30 % dose leaves 45.0 L/s at risk against 36.3 L/s at baseline — **source dosing alone does not
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
   nodes rise 21 → 28 → 29 from 12 → 16 → 20 °C; demand at risk 18.8 % → 24.8 %; network-mean
   `E[A]` more than doubles (0.222 → 0.522 mg/L·h).
2. **Ageing at the same temperature adds a spatially selective increment** (29 → 31 nodes;
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

---

## Step 13 — known-answer test: are the coefficients realised as we set them? (Priority-2 #7)

Every number in this log rests on an assumption that was never tested directly: that a coefficient
written in `1/day` or `m/day`, divided by 86400 and handed to WNTR, arrives in EPANET as that
coefficient. The review found a unit error in the reported figures (§3.4), so the assumption is not
self-evidently safe. This is the single-pipe analytic check the review asked for
(`step13_known_answer.py`): one reservoir, one 1000 m pipe of 0.3 m diameter, a constant 0.05 m³/s
demand, `C0 = 1.0 mg/L`, 24 h.

**Arm 1 — pure bulk decay against the analytic solution.** With no wall reaction the concentration
at the far end once the front has passed is exact.

**Formula**:

```
C = C0 · exp(k_b · t_res),     t_res = L / v
```

**Properties**:

- Units: `k_b` in 1/s after conversion, `t_res` in s, `C` in mg/L.
- The test is a *unit* test in the literal sense: a wrong conversion factor changes `C` by a
  constant relative amount at every `k_b`.

| `k_b` (1/day) | `t_res` (h) | EPANET `C` | analytic `C` | relative error |
|---|---|---|---|---|
| −0.50 | 0.3927 | 0.991845 | 0.991852 | 6.8 × 10⁻⁶ |
| −1.00 | 0.3927 | 0.983744 | 0.983771 | 2.7 × 10⁻⁵ |
| −2.00 | 0.3927 | 0.967699 | 0.967805 | 1.1 × 10⁻⁴ |

Worst relative error **1.1 × 10⁻⁴** against a 10⁻³ tolerance. The error *grows with the amount of
decay* across a fourfold range of `k_b`, which is the signature of the quality solver's time
discretisation; a wrong conversion factor would instead show a constant relative offset. So the
conversion and the units are confirmed.

**Arm 2 — wall decay: monotonicity and a bound, not an exact value.** EPANET's first-order wall
reaction is limited by mass transfer as well as by `k_w`, through an overall rate constant

```
k_overall = k_b + (4 / D) · (k_w · k_f) / (k_w + k_f)
```

so `C` cannot be predicted from `k_w` alone without the mass-transfer coefficient `k_f`, which
depends on the flow regime. What *is* assertable was checked at `k_b = −0.5` 1/day over
`k_w ∈ {0, −0.1, −0.5, −1, −2}` m/day: `k_w = 0` reproduces the pure-bulk run **exactly**, `C`
falls monotonically as `k_w` strengthens, and `C` stays above the `k_f`-free limit in which the wall
term would be `(4/D)·k_w`. All three hold. That is enough to establish the wall coefficient is
applied with the intended sign and scale, and it is stated as such rather than as an exact analytic
match.

**Arm 3 — the conversion helper itself.**
`per_day_to_per_second(−1.0) = −0.0000115741 per second`, i.e. exactly `−1/86400`.

All checks pass. One paragraph of the thesis should state this: the toolchain realises the
coefficients as intended, so the calibration results are about the inverse problem and not about a
units mistake.
