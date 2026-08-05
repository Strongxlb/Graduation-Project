# Uncertainty-aware calibration and identifiability of grouped first-order chlorine wall-decay coefficients (a controlled EPANET Net3 three-zone study)

> This README is the **2026-08 revision**, reflecting the actual research after the supervisor's paper review of 2026-07-25 (see [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md)).
> Chinese: [`README.md`](./README.md) ｜ English (this file)
> Historical execution plan (**superseded** — it describes a Bristol three-DMA field-data study, not this work): [`plan1.md`](./plan1.md) ｜ Literature list: [`background/Literature/literature.md`](./background/Literature/literature.md)

## 0. In one sentence

On the **EPANET Net3** benchmark network, pipes are partitioned by node coordinates into three **synthetic spatial zones** (**old / average / new** — labels are imposed; Net3 has no real pipe-age/material record). A **known synthetic truth** generates noisy observations for a controlled study of **uncertainty-aware calibration** and **identifiability** of first-order wall-decay coefficients `k_w`: what the data can constrain, how large the gap is between **informal GLUE** and a **formal likelihood**, how structural / systematic / autocorrelated / censoring errors affect estimates, and how parameter uncertainty does (and does not) propagate into the operational low-chlorine **risk map**. The primary analysis uses a **censored formal Gaussian likelihood**; informal GLUE is retained throughout as a **comparator** — the contrast is itself a result. Everything is reproducible and script-driven; results live in [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md); point-by-point responses are in [`REVISION_RESPONSE_MATRIX.md`](REVISION_RESPONSE_MATRIX.md).

## 1. Project context

This is an MSc dissertation for **Imperial College London CIVE70058 Research Dissertation – Environmental** (30 ECTS / 60 CATS). Final deliverables:

- **Research paper** — due 2026-08-21 12:00; scientific-paper format; up to 12,000 words.
- **Research poster** — due 2026-08-28 12:00.
- Completed checkpoints: 2026-06-19 supervisor checkpoint; 2026-07-03 student checkpoint.
- **Current phase**: final revision after the 2026-07-25 review (Priority-1 corrections + Priority-2 methodological additions) and integration into the manuscript.

The repository tracks code, models, result figures, literature notes and dissertation drafts; key progress is recorded via Git.

## 2. Research topic

Revised working title: **Uncertainty-aware calibration and identifiability of grouped first-order chlorine wall-decay coefficients — a controlled EPANET Net3 three-zone study**.

The point is not to "estimate one number" but to answer: **given realistic monitor density and measurement noise, can the grouped `k_w` be identified, and what does that mean for operational risk?** A **synthetic truth** is used as a controlled testbed. Keywords:

- **EPANET / WNTR** — EPANET 2.2 water-quality engine + WNTR Python wrapper (`wntr 1.4.0`).
- **First-order chlorine decay** — first-order bulk (`k_b`) + first-order wall (`k_w`) (Rossman 1994 / EPANET 2.2 Manual).
- **Grouped `k_w` (three synthetic zones)** — split by node coordinates (`y ≤ 10` → average; else `x ≤ 26` → new; else old; cross-zone pipes assigned to the newer side). Labels are synthetic, not Net3 material/age data.
- **Three inference conventions side by side** — primary: **censored formal Gaussian likelihood** (`log Φ(−μ/σ)` at the sensor floor); `formal_iid` isolates the censoring treatment; **GLUE (informal likelihood)** (Beven & Binley 1992) is the **comparator**. The gap between them is a core result (Mantovan & Todini 2006 / Stedinger 2008 made quantitative).
- **Formal identifiability tools** — Fisher information / Cramér–Rao lower bound (CRLB), continuous profile likelihood, AR(1) covariance correction.
- **Measurement error in the likelihood** — Gaussian noise, systematic bias, zero-clipping (censored likelihood).
- **Operational risk propagation** — duration / depth / cumulative deficit below the operational threshold `0.2 mg/L`, corroborated by water age.

## 3. Motivation

Chlorine residual governs microbial safety. Traditional calibration treats observations as exact and reports point estimates, which can yield **over-confident parameters** and **misleading risk judgements**. Two neglected issues:

1. **Identifiability** — with sparse monitors and non-trivial noise, **not all grouped `k_w` are identifiable**. Without checking, "successful calibration" may be a **prior-centring** artefact.
2. **Error structure** — systematic bias, temporal autocorrelation, **zero-clipping** at low residuals (`C_obs = max(0, C_true+ε)`), plus structural model error. These can decouple "good fit" from "correct parameters" (precise-but-biased).

This project makes both points concrete on a **synthetic three-zone case with known truth**, and carries conclusions to the **operational risk map**. Here `0.2 mg/L` is a **selected operational low-chlorine threshold**, not a legal/compliance limit.

## 4. Research questions and objectives

### 4.1 Research questions (mapped to completed experiments)

1. **Baseline and warm-up** — can a reproducible three-zone baseline be frozen with warm-up length chosen by a convergence test rather than convention? (Steps 0, 1)
2. **Identifiability** — with 6 monitors (2 per zone) and σ = 0.1 noise, how tightly is each grouped `k_w` constrained? (Steps 2–4, 7, 7b, 14)
3. **Threshold/prior dependence** — how is the behavioural threshold set, and are conclusions robust? (Steps 3, 4)
4. **Error-source sensitivity** — structural error, sensor bias, `k_b` misspecification, AR(1), zero-clipping. (Steps 5, 7c, 8, 8b, 9)
5. **Required sensor accuracy** (supervisor email) — how small must σ be for useful chlorine predictions? (Step 6)
6. **Risk propagation and validation** — does parameter uncertainty change operational hot-spot ranking? Is the risk map hydraulically corroborated? Can the model predict unseen monitors? (Steps 10, 11)

### 4.2 Overall objective

Build a **reproducible, uncertainty-aware, identifiability-focused** workflow for grouped-`k_w` calibration and risk assessment that honestly delimits what informal GLUE can do and what the data can constrain, and that propagates parameter uncertainty to operational risk decisions and predictive validation.

## 5. Scope

### 5.1 In scope

- **EPANET Net3** benchmark network, split by coordinates into old/average/new contiguous zones.
- **First-order** kinetics (bulk + wall); `k_b` fixed at `-0.5 day⁻¹`, estimating three grouped `k_w`.
- **Synthetic truth** + Gaussian observation noise (σ = 0.1 mg/L is **one standard deviation**); 6 monitors (2 per zone).
- **8192 scrambled-Sobol prior draws**, three weighting schemes + **formal identifiability** (Fisher/CRLB, continuous profile, AR(1)).
- Error modelling: systematic bias, `k_b` misspecification, zero-clipping (censored / Tobit-type likelihood).
- Operational risk: duration/depth/cumulative deficit below `0.2 mg/L` + water-age corroboration + LOO predictive validation.

### 5.2 Out of scope

- **No hydraulic calibration** — demands and roughness trust the existing model.
- **No multi-species modelling** (EPANET-MSX); no TOC/DBP/biofilm coupling.
- **No operational optimisation** (no sensor placement / flushing / booster optimisation).
- Real Bristol 3-DMA field data are **not** included in this revision.
- AI tools are used only for code assistance / language polishing / idea organisation, disclosed per Imperial/CEE rules.

## 6. Method framework and key settings

### 6.1 Frozen baseline (Step 1)

- Synthetic truth: `k_b = -0.5 day⁻¹` (fixed); `k_w`: old `-1.0`, average `-0.1`, new `-0.05` (`m/day`).
- Monitors (2 per zone): new `107/113`, old `15/145`, average `209/231`.
- Timing: **168 h simulation, 120 h warm-up** → **49 reporting points = 48 h window**; observation noise `σ = 0.1 mg/L`. Warm-up length comes from Step 0, not convention; because `168 − 120 = 72 − 24 = 48`, the residual count `N = 6 × 49 = 294` is unchanged.
- Sampling: **8192 = 2¹³ scrambled Sobol** draws (not pseudo-random) — the formal likelihood is far sharper than the informal score; under the superseded pre-Sobol design its ESS was only ~37. Leading `2^k` subsets support an exact convergence table at 1024/2048/4096/8192. The cache stores **every candidate's prediction at all 92 nodes**.

Prior ranges (`m/day`):

```
old      : [-1.5,  -0.2 ]
average  : [-0.2,  -0.04]
new      : [-0.10, -0.005]
```

### 6.2 Three weighting conventions (Steps 1–3)

**Primary: censored formal Gaussian likelihood.** Density on uncensored points; left-censoring probability at the sensor floor:

```
ℓ(θ) = −½ · Σ_{y>0} ((y − μ)/σ)²  +  Σ_{y=0} log Φ(−μ/σ)
```

**Comparator: informal GLUE score** (the draft's rule), with a behavioural threshold:

```
GLUE:  w_i ∝ exp[ −½ · (RMSEᵢ/σ)² ] · 1[ RMSEᵢ < RMSE_thr ]
thr:   RMSE_thr = σ · (1 + z/√(2·N_resid))     # z=1.645; σ=0.1, N=294 → 0.107
```

The informal score equals the formal iid Gaussian likelihood **divided by `N = 294`** — equivalently assuming `σ_eff = σ√N = 1.71 mg/L`. It is nearly flat inside the behavioural set. The threshold belongs to the **comparator only**; the formal likelihood carries no hard cut.

### 6.6 Warm-up choice and toolchain verification (Steps 0 / 13 / 14)

- **Step 0** — demand patterns and pump schedules are 24 h periodic; the right criterion is cycle-to-cycle field recurrence with pre-declared tolerances. At 120 h the chlorine concentration criteria pass, but residual **~5.1%** cycle-to-cycle drift remains in the integrated deficit and water-age p95 still changes by **12.8 h**. So 120 h is a **pragmatic finite-horizon warm-up**, not a fully cyclostationary risk/age state. Hard ceiling: pump 10's absolute-time controls stop at 159 h, so runs beyond 168 h break the 24 h pump pattern.
- **Step 13** — single-pipe analytic bulk check; wall arm verifies sign / monotonicity / bound only (mass-transfer prevents an exact wall analytic match without further controls).
- **Step 14** — 100 independent noise redraws on the fixed candidate library: bias of the formal posterior mean, empirical SD vs Case-A CRLB, and nominal 90%/95% coverage.

### 6.3 Identifiability: formal tools (Steps 7 / 7b / 7c)

- **Fisher / CRLB (a priori)** — `F = Jᵀ J / σ²`, marginalised via the Schur complement.
- **Profile likelihood (a posteriori / practical)** — fix one coefficient, re-optimise the others; `ΔNLL ≤ 1.92` gives the 95% interval. Continuous endpoints are primary; the 21-point grid is visualisation only.
- **AR(1)** — recompute with `Σ[t,s] = σ²ρ^|t−s|`.

Read in two layers: **(1) controlled-baseline identifiability** (Fisher A ↔ profile ↔ formal ensemble); **(2) realism sensitivity** (+`k_b`, +sensor bias, AR(1), censoring).

### 6.4 Error-source sensitivity (Steps 5 / 8 / 8b / 9)

Structural error (pipe-level jitter / length-correlated heterogeneity), systematic sensor bias, `k_b ±20%` (bulk–wall compensation), and zero-clipping censored likelihood.

### 6.5 Operational risk and validation (Steps 6 / 10 / 11)

- **Required-accuracy sweep** — σ = 0.02 / 0.05 / 0.10 / 0.15 under **formal primary** (+ informal comparator).
- **Risk metrics** — below-`0.2 mg/L` duration, minimum, cumulative deficit; ensemble-weighted expectation + 5–95% bands; unweighted / consumer-only / demand-weighted network means.
- **Water age** — descriptive Spearman association (no iid p-value); spatial-block bootstrap width.
- **LOO / leave-one-zone-out** — predictive success ≠ parameter identifiability.

## 7. Key findings (summary of Steps 0–14)

> Full tables and figures: [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md). Point-by-point status: [`REVISION_RESPONSE_MATRIX.md`](REVISION_RESPONSE_MATRIX.md).

1. **"average/new are unidentifiable" was a statement about the scoring rule, not the data.** On the same observations and draws, informal GLUE (draft threshold 0.12) retains **86 / 98 / 98%** of prior width; censored formal retains **25 / 31 / 28%** (Steps 1–3).
2. **Formal posterior spread is locally consistent with the Case-A CRLB — not a proof of frequentist efficiency.** Single-run SD within 1–5% of CRLB; over 100 noise realisations, empirical SD / CRLB ≈ 1.04 / 1.06 / 1.12 and nominal 90% coverage ≈ 0.85–0.89. Informal is ~2.8–3.1× wider and over-covers by being wide (Steps 7 / 7b / 14).
3. **No threshold repairs an inefficient score.** Tightening 0.12 → 0.107 recovers little; switching to the formal likelihood cuts every SD threefold (Step 3).
4. **A 24 h warm-up (draft / superseded) is inadequate; 120 h is a finite-horizon pragmatic choice, not full convergence.** Concentration criteria pass at 120 h with residual ~5.1% deficit drift; water age does not settle inside the 168 h ceiling (Step 0).
5. **Symmetric heterogeneity shows no detectable structural bias; *structured* heterogeneity produces a directional shift** toward a **length-weighted proxy**. The structure tested is a synthetic pipe-**length** correlation — **not** a flow-path, residence-time or Jacobian weighting, and not a recovered effective coefficient (Steps 5c / 5d).
6. **Required accuracy (revised): σ ≈ 0.10 is already useful under the formal primary.** Formal retains **27 / 30 / 29%** of prior width at σ = 0.10; the earlier "σ ≲ 0.05 required" claim was an informal-score artefact. σ ≤ 0.05 is sampling-limited on the fixed Sobol library (Step 6).
7. **Uncorrected sensor bias can destroy coefficients while leaving the full-network risk ranking almost intact.** At node 15, +0.05 / +0.10 mg/L move old by **2.19 / 3.87** posterior SD; Spearman of the 92-node risk field stays ≥ 0.999. Across the two-sided six-monitor sweep the largest *normalised* corruption is **not** node 15 but average-zone **node 231 (−5.94 posterior SD at −0.10)**, and cross-zone leakage reaches 2.7 SD — the average↔new confounding Fisher's sloppiest direction predicts (Steps 8 / 8c).
8. **A sensor drift is, to a good approximation, its own mean.** Modelled as a linear ramp `b(t) = D·(t−t₀)/48` across the window and run against two constant-bias controls on identical noise, the drift shift is **0.98–0.99** of the mean-equivalent constant shift at node 231 and **0.89–0.91** at node 15 — about half the end-equivalent one. Step 8's constant-bias sweep therefore transfers to a drift evaluated at the drift's mean; where it departs, censoring is the mechanism (a ramp clips fewer observations, 6→10 against 5→13). Only a monotone ramp from zero is tested (Step 8d).
9. **Zero-clipping is measurable but small** (10 of 294 calibration points). It is invisible on the 21-point *grid* profile but visible on the *continuous* one (old [−1.1720, −0.8106] censored vs [−1.1517, −0.7973] iid) (Step 9).
10. **Risk vs water age**: descriptive Spearman ρ = 0.73, spatial-block bootstrap 95% **[0.455, 0.897]**. Water age comes from the *same* hydraulic model, so this is reaction-independent internal corroboration, not independent validation — a conservative descriptive width, not a significance interval; ordinary p-values and iid junction bootstraps removed. Unweighted / consumer-only / demand-weighted means move in opposite directions — risk concentrated among small users (Step 10).
11. **Predictive success ≠ parameter identifiability.** Leave-one-zone-out returns the dropped zone's coefficient to the prior midpoint while prediction RMSE stays ≈ noise floor (Step 11).
12. **Scenario headlines (formal ensemble):** baseline 21 nodes / 55.4 L/s at risk; heatwave 29 / 67.8; heat+ageing 31 / 69.4. Tested +30% source dose improves continuous severity but does not restore baseline demand-at-risk (Step 12).
13. **What `k_b` ±20% does to the shortlist depends on the risk metric, and the two disagree.** Formal weighting, 30 noise realisations, median risk field. The network-scale Spearman is high on both metrics (P_bar 0.976 / 0.933; E[A] 0.980 / 0.935), but the leading sets differ. Ranked by the **time-averaged probability `P_bar`** the top-6 keeps only four of six at both signs (Jaccard 0.50), Jaccard is *worse* at k = 3 (**0.20**) and the reference 4th-ranked node falls to **20th** — not a cut-off artefact. Ranked by the **cumulative deficit `E[A]`**, which is what Step 10's headline table uses, the top-6 is **unchanged** at −0.4 and loses one node at −0.6 in a sixth/seventh-place exchange (143 out, 129 in), with top-3 and top-5 identical. The difference is mechanical: `P_bar` counts hours and is highly sensitive to the many nodes near the threshold, while `E[A]` weights by depth and its leaders are separated by it. **No claim about `k_b` changing (or not changing) the hot-spot list is meaningful without naming the metric.** The superseded "ranking unchanged" claim had a separate defect: it was written directly beneath a table of three visibly different node sets (Step 8b). For contrast, the sensor-error family barely moves the `E[A]` shortlist: 23 of Step 8c's 24 arms leave it unchanged and no Step 8d drift arm changes it at all, so **`k_b` misspecification is the only perturbation tested here that moves the deficit-ranked operational shortlist** (Steps 8 / 8c / 8d).
14. **Continuous profile intervals are 15–39% wider (half-width) than the 21-point grid** under the censored primary; prior-scaled Fisher condition number is 3.2, not 215 (Steps 7 / 7b).
15. **The chlorine concentration unit was wrong by 1000×; corrected, and measured to change nothing.** WNTR stores concentration internally in kg/m³ whatever `inpfile_units` says, so `initial_quality = 1.0` simulated **1000 mg/L** — source, tanks, σ and the 0.2 mg/L threshold all 1000× too high. It was invisible because first-order kinetics are linear in C and σ and the threshold sat on the same scale, so every ratio was preserved; the reaction coefficients carry no mass unit and were never affected. Fixed at the model boundary, with EPANET's absolute quality tolerance scaled with it — without that the fix alone would introduce a **17.8%** maximum relative error. Measured on the full re-run: reported field unchanged to **2.3 × 10⁻⁷**, and two of 1720 checked log numbers moved. Every scientific conclusion stands verbatim; what is corrected is the physical interpretation on which the sensor-accuracy, threshold and dosing statements depend (Step 15).
16. **The demand weights were read without their patterns — a correction that is *not* a relabelling.** The consequence axis of the risk register used WNTR's `base_demand` field, but four Net3 junctions encode a large demand as 1 GPM times a large pattern, so the base field reports them as 0.063 L/s each instead of 16.7 / 108.4 / 75.3 / 284.6 — **70 % of the network's water, counted as four of its smallest users**. Using `average_expected_demand` instead: network total 192.6 → **690.7 L/s**, consequence terciles 1.16 / 3.39 → **1.67 / 4.38 L/s**, scenario demand at risk 36.3 / 45.0 / 47.8 / 49.4 → **55.4 / 64.7 / 67.8 / 69.4 L/s**, but as a *share* of network demand 18.8–25.6 % → **8.0–10.0 %** because the denominator grew faster. It **strengthens** finding 10: demand-weighted `E[D]` falls 2.36 → **1.23 h**, so risk sits at small consumers even more sharply than first reported. No conclusion reverses (Steps 10 / 12).
17. **Methodological lesson:** single-realisation results were overturned twice under scrutiny and the informal score reverses conclusions in **three** places (threshold, structural bias, bias curvature); a fourth effect is an understated magnitude, not a reversal. A separate failure mode is method-independent: **a summary sentence that does not follow from the table above it** (Step 8b). Defences that worked were paired controls, ensembles over arbitrary choices, a formal likelihood, multi-route corroboration, and reading each conclusion against its own table.

## 8. Dissertation structure

- **Introduction** — chlorine safety, measurement uncertainty, grouped-`k_w` identifiability, contribution.
- **Background / Literature** — first-order decay, EPANET/WNTR, GLUE critiques, Fisher/CRLB/profile, measurement error and censoring.
- **Methodology** — Net3 three-zone setup, synthetic truth, formal primary + informal comparator, Fisher/profile/AR(1), error sensitivity, risk metrics and LOO.
- **Results** — Steps 0–14.
- **Discussion** — scoring-rule vs data information; ideal vs practical identifiability; parameter unreliability ≠ risk-map unreliability; limitations (finite-horizon warm-up, assumed AR(1) ρ, illustrative scenario kinetics, no field validation).
- **Conclusion** — answer each research question; future work.

## 9. Reproduction

Code is in [`Net3/`](Net3/), conda env `water-supply` (`python 3.13.12`, `numpy 2.4.2`, `scipy 1.17.1`, `wntr 1.4.0`). See [`environment.yml`](environment.yml) / [`environment.lock.yml`](environment.lock.yml). Network file is the frozen copy `models/net3_frozen/Net3.inp` with SHA-256 check on import.

- [`Net3/wq_common.py`](Net3/wq_common.py) — frozen baseline config + helpers + three weightings.
- `Net3/step1_freeze_baseline.py` — synthetic truth + noisy observations + **8192 Sobol** library.
- `Net3/step3 … step14_*.py` — full experimental suite.
- [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md) — methods, tables, figures, conclusions.
- [`Net3/provenance.py`](Net3/provenance.py) — git commit/tree/dirty-diff hashes, `.inp` hash, `wq_common` + step-script hashes, exact library versions, config hash.
- [`Net3/validate_artifacts.py`](Net3/validate_artifacts.py) — registered claims, weighting fields, numerical drift, forbidden wording; **does not** establish semantic consistency.

```
conda activate water-supply
cd Net3
export MPLCONFIGDIR=../.mplcache
python step0_warmup_convergence.py
python step1_freeze_baseline.py        # ~280 s (8192 × 168 h EPANET)
python step7b_profile.py
python step10_risk_metrics.py
python step11_loo.py
python step13_known_answer.py
python step14_repeated_noise.py        # ~10 s, cache only
python provenance.py
python validate_artifacts.py
```

Two step scripts must not run concurrently from the same directory (shared WNTR scratch files).

## 10. Timeline (revised, 2026-08)

| Stage | Status |
| --- | --- |
| Warm-up test + frozen baseline (Steps 0–1) | ✅ done |
| Three weightings + threshold/displaced prior (Steps 2–4) | ✅ done |
| Error sensitivity (Steps 5–9) | ✅ done |
| Risk metrics + four-layer validation (Steps 10–11) | ✅ done |
| Scenarios + known-answer test (Steps 12–13) | ✅ done |
| Repeated-noise calibration (Step 14) | ✅ done |
| Reproducibility infrastructure | ✅ done (clean release tag still pending) |
| **Rewrite Results / Discussion / Conclusion** | ⏳ in progress |
| Formatting, numbering, front matter, references | ⏳ to do |
| Fit within the 12 000-word CIVE70058 limit (review's "30 pages" is not the rule) | ⏳ to do — the 20 Jul draft is 11 624 words at pre-review scope |
| Research paper submission | due 2026-08-21 |
| Research poster submission | due 2026-08-28 |

The scientific spine and formal primary convention are aligned in the repository; a final clean-tree release rerun and manuscript integration remain. See [`REVISION_RESPONSE_MATRIX.md`](REVISION_RESPONSE_MATRIX.md) for item-level status and remaining limitations.

## 11. Workflow

- **Git/GitHub** — at least one meaningful commit per stage; do not commit large raw data / temporary outputs / private data.
- **Result provenance** — numbers are generated by scripts into `baseline_cache/`; `validate_artifacts.py` checks consistency of transcribed prose against JSON, not correctness of the science.
- **Suggested layout** — `background/` ｜ `Net3/` ｜ `thesis/` ｜ `meetings/`.

## 12. Note on AI-tool use

Imperial/CEE permits generative-AI use where not explicitly forbidden, but submitted content must reflect one's own understanding, judgement and expression. Any AI use for code generation, grammar checking, language polishing, figure captions or idea organisation must be disclosed and cited per faculty rules; all AI output must be human-checked and cannot replace literature reading, modelling judgement or interpretation of results.
