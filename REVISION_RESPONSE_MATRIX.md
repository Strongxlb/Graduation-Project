# Response to the review of 25 July 2026

Organised by the **review's own numbering**, not by the order the work happened in, so each comment
can be checked against its response directly. Source:
`meetings/meeting-老师/7.25-review/REVIEW_Ruixin_Peng_Draft_Project_IIS2_25Jul2026.pdf`.

Status vocabulary, used strictly:

- **closed** — the comment is answered and the evidence is in the repository.
- **closed, stronger** — answered, and the corrected analysis changes the conclusion in a way the
  comment did not anticipate. These need the supervisor's attention most, because the *response*
  differs from what was asked for.
- **partly closed** — the main point is answered but a named piece of evidence is still missing.
- **open** — not yet done.
- **thesis document** — the work is in the `.docx`, not in this repository.

All numbers below are produced by the scripts named. `Net3/validate_artifacts.py` catches a
**subset** of numerical drift, missing weighting declarations, unit/path errors and forbidden
phrasing; it does **not** establish semantic consistency (stale node IDs, formal/informal label
mismatches, or over-claims that do not contain a near-miss number). `Net3/RESULTS_LOG.md` is the
long-form record and must still be read.

---

## Priority 1 — must be corrected before submission

### 3.1 The GLUE ensemble is, for two of three parameters, indistinguishable from the prior

| field | content |
|---|---|
| **Comment** | For `average` and `new` the behavioural distribution *is* the prior (97–98% of prior width retained); the agreement of the weighted means with the imposed truths is an artefact of centring the prior ranges on those truths. Delete "the weighted mean of every group lies close to its true value", add prior-to-behavioural width ratios, and state plainly that the two coefficients are not informed. |
| **Risk in the draft** | The strongest sentence in the Results was the least defensible one: a prior-centring coincidence was read as successful recovery. |
| **Change made** | Overclaim deleted. Width-ratio table added for all three groups (Step 2). The displaced-prior experiment the comment recommended was run (Step 4) and then made robust over 30 noise realisations and two thresholds (Step 4d). **Beyond that**: the reason the ensemble equalled the prior was diagnosed, and it is not the monitoring array. |
| **Code** | `step1_freeze_baseline.py`, `step3_threshold_sensitivity.py`, `step4_displaced_prior.py`, `step4d_displaced_robust.py` |
| **Artifact** | `baseline_meta.json`, `step3_threshold.json`, `step4_displaced_prior.json`, `step4d_displaced_robust.json` |
| **Status** | **closed, stronger** |
| **What changed beyond the comment** | The informal GLUE score `exp(−½(RMSE/σ)²)` is not a Gaussian likelihood: it drops the factor `N = 294`, which is equivalent to assuming an observation error of `σ√N = 1.71 mg/L` — 17× the sensor noise and larger than the inlet concentration. Under a formal censored Gaussian likelihood, on the *same* observations and draws, all three coefficients contract to **25–31%** of the prior width instead of 86–98%. So "the data do not inform average and new" was a statement about the scoring rule, not about the data. |
| **Repeated-noise check (Step 14)** | 100 independent noise realisations on the fixed 8192-member library: formal posterior-mean bias is ≤0.15 of the estimator's own sampling SD for every coefficient; empirical SD / Case-A CRLB ≈ 1.04 / 1.06 / 1.12; nominal 90% weighted-quantile coverage ≈ 0.89 / 0.88 / 0.85. The informal comparator over-covers (≈0.98–0.99) by being ~2.6–2.9× wider within a realisation. |
| **Remaining limitation** | Realisations share one Sobol prediction library, so Monte Carlo errors are not independent; ESS median ≈ 158 bounds how finely interval endpoints are resolved. This is a local consistency / calibration check under the synthetic generative model, not an external validation. |

### 3.2 The behavioural threshold cannot discriminate

| field | content |
|---|---|
| **Comment** | `RMSE < 0.12` sits ≈4.9 sampling SD above the noise floor, so it rejects only grossly wrong sets. Justify the threshold against the sampling distribution of the objective (a 95% band is ≈0.107) and report retention for at least two thresholds. |
| **Risk in the draft** | The 84% retention rate was presented as a property of the parameter space rather than of the threshold. |
| **Change made** | `threshold_for_sigma(σ) = σ(1 + z/√(2N))` implemented and used, giving 0.107 at σ = 0.1; three thresholds reported (0.107 / 0.110 / 0.120) with retention, objective-scale distance and per-coefficient widths. The "95%" label is now stated precisely: it is the sampling distribution of the RMSE **at the truth**, not a credible interval for the parameters. |
| **Code** | `wq_common.threshold_for_sigma`, `step3_threshold_sensitivity.py` |
| **Artifact** | `step3_threshold.json` |
| **Status** | **closed, stronger** |
| **What changed beyond the comment** | Tightening 0.120 → 0.107 recovers about a seventh of the gap for `old` and almost none for `avg`/`new`, whereas switching to a formal likelihood cuts every SD threefold. **No threshold can fix an inefficient score.** The formal analysis therefore carries no threshold at all, and the threshold sweep is reported as a sensitivity analysis *of the informal comparator*. |
| **Remaining limitation** | The behavioural-set concept survives only in the comparator, so the draft's GLUE framing has to be rewritten as "informal behavioural weighting sensitivity" wherever it appears. |

### 3.3 The experiment cannot detect structural error, and the search was centred on the answer

| field | content |
|---|---|
| **Comment** | Truth and fit share the same three groups, solver, timesteps and hydraulics — a complete inverse crime. The 7×7×7 grid over ranges centred on the truth puts the nearest node 0.007–0.067 m/day away, so "recovery to the nearest grid node" is near-guaranteed, and the ±0.12 m/day ten-realisation spread is about half a grid step, i.e. quantisation. Recommended (the single most valuable addition): generate a truth with finer heterogeneity than the fitted model and report how far the ensemble sits from any simple average of the true field. |
| **Risk in the draft** | The Discussion generalised about calibration reliability from a design that excluded the one phenomenon — precise-but-biased structural error — that the generalisation was about. |
| **Change made** | Three structural-error experiments: uncorrelated per-pipe jitter at ±20% (5a), a magnitude sweep with a **`jitter = 0` control** (5c), and length-correlated within-zone heterogeneity that separates the arithmetic from a length-weighted target (5d). Grid quantisation quantified explicitly (5e): the old-zone grid step is 0.2170 m/day, half-step 0.1085, so the grid fit cannot resolve the biases being discussed and only the weighted mean can. |
| **Code** | `step5_structural_error.py`, `step5c_jitter_sweep.py`, `step5d_structured.py` |
| **Artifact** | `step5_structural_error.json`, `step5c_jitter_sweep.json`, `step5d_structured.json` |
| **Status** | **partly closed** |
| **What changed beyond the comment** | Two measurement errors in our own first attempt were found and corrected. (i) There was no `jitter = 0` control, so the reported bias mixed structural error with the realisation's noise; with the control, the structural *increment* is what can be attributed. (ii) The structural residual has a **grid-resolution floor** of 0.0055 mg/L at zero heterogeneity, so "the residual is 7% of the noise floor" overstated it about fivefold — the true structural part at ±20% is 1.3%. Most importantly, measuring with the formal likelihood **reverses the sign of the conclusion**: the old-zone structural increment is −0.049 m/day (0.36 posterior SD) at ±50% jitter, where the informal score gave −0.013 and 0.10 SD. The informal score's apparent robustness to heterogeneity was inertia, and it was masking a real precise-but-biased effect. |
| **Field ensemble — this reverses the single-field reading a second time** | 25 independent heterogeneity fields at ±20% under the formal weighting give a structural increment for `old` of **+0.0107 ± 0.0335** m/day: the *opposite sign* to the single field's −0.0325, and `\|mean\| / SD` of 0.32, 0.04 and 0.24 for old/average/new. So at symmetric within-zone heterogeneity there is **no systematic structural bias detectable above field-to-field variability**, and the conclusion reverts to the original one — symmetric mean-zero heterogeneity averages out. The corrections established on the way still hold (subtract the control, the informal score understates whatever is present, the residual has a grid floor), but they do not add up to a precise-but-biased effect for symmetric heterogeneity. Step 5d's length-correlated design is where a systematic direction appears, and that is still a single field. |
| **Remaining limitation** | Length weighting is only one candidate effective weighting and must not be called residence-weighted; the **sensitivity- or Jacobian-weighted** effective mean has not been computed. Step 5d needs its own field ensemble before its direction is quoted as a magnitude. |

### 3.4 Unit inconsistency between text and figures

| field | content |
|---|---|
| **Comment** | Text says m/day; all three GLUE distribution figures label axes "(/day)". Regenerate labels and audit every reported coefficient. |
| **Change made** | Axis labels regenerated in m/day; the log's `mean ± SD (mg/L)` header for wall coefficients corrected to `m/day`. An automated rule now enforces it: `validate_artifacts.py` fails if a line mentions a coefficient with `(mg/L)` or `k_b` with `(mg/L)`, so this class of error cannot silently return. |
| **Code** | all `step*.py` figure labels; `validate_artifacts.py` (`UNIT_RULES`) |
| **Status** | **closed** |
| **Remaining limitation** | The same error originates in the foundation notebook, which is outside this repository. |

### 3.5 The noise-sensitivity check is imported from a different experiment

| field | content |
|---|---|
| **Comment** | The σ = 0.02/0.05/0.10 figures come from the foundation notebook's global single-parameter experiment (different monitors, five length-based groups, different truth, lumped coefficient). Re-run the sweep inside the three-zone setup — preferable, and not expensive. |
| **Change made** | Re-run inside the three-zone setup over σ = 0.02/0.05/0.10/0.15, 30 noise realisations each, with the behavioural threshold scaling as `σ(1 + 1.645/√(2N))`; reports behavioural width retained per coefficient and the predictive band at node 15. |
| **Code** | `step6_noise_sensitivity.py` |
| **Artifact** | `step6_noise_sensitivity.json` |
| **Status** | **closed, stronger** |
| **Also fixed this pass** | Re-run under **formal censored primary** (+ informal comparator). Realisations with an empty behavioural set are counted; ESS is reported as median / p5 / min / fraction `<100`. With 8192 Sobol draws **all 30 realisations are valid at every σ**. The email answer changes: under the primary rule a **σ ≈ 0.10** sensor already retains 27 / 30 / 29% of prior width; the earlier "σ ≲ 0.05 required" claim was an informal-score artefact (same data: informal 65 / 91 / 87%). |
| **Remaining limitation** | Under the formal rule, σ ≤ 0.05 is sampling-limited on this fixed library (ESS median ≈ 20.9 at 0.05 and ≈ 1.8 at 0.02). Those rows indicate direction, not magnitude; quantifying tighter sensors needs a likelihood-adapted design. |

---

## Priority 2 — alignment with the shared notebook

### #1 Systematic sensor error (bias, drift)

| field | content |
|---|---|
| **Comment** | At the ±0.1 mg/L class the systematic term dominates. A +0.05 mg/L offset at one informative monitor shifts the estimate by more than the whole random spread, and the effect is **concave — halving the offset retains ~70% of the bias**. |
| **Change made** | Two-sided offsets −0.10 … +0.10 mg/L at node 15 under the **formal** weighting, 30 noise realisations, plus the six-monitor location sweep under the same formal primary (+ informal comparator; Step 8c). Rank agreement with the unbiased case is reported on the full 92-node risk field (Spearman, Kendall) and on the top-6 set (Jaccard), and the number of observations pushed onto the sensor floor is tracked. The comment's first claim is confirmed emphatically: +0.05 mg/L shifts `k_w,old` by **2.19 posterior SD** and +0.10 by 3.87 SD, so a systematic offset dominates the random spread several times over. |
| **Code** | `step8_sensor_bias.py`, `step8c_bias_bynode.py`, `step8d_sensor_drift.py` |
| **Artifact** | `step8_sensor_bias.json`, `step8c_bias_bynode.json`, `step8d_sensor_drift.json` |
| **Status** | **closed, stronger** — both halves of "bias, drift" are now run |
| **Drift (the half that was missing)** | Step 8d models drift as a linear ramp `b(t) = D·(t−t₀)/48` across the assessment window and runs it against **two constant-bias controls on identical noise**: `const(D/2)`, the mean-equivalent, and `const(D)`, the end-equivalent. Result: **a drift is its own mean.** The drift shift is 0.98–0.99 of the mean-equivalent constant shift at node 231 and 0.89–0.91 at node 15 — so Step 8's constant-bias sweep transfers to a drift evaluated at the drift's mean, and drift is not a separate phenomenon requiring its own risk analysis. Where it does depart (node 15), **censoring is the mechanism**: a ramp spends only part of the window at the extreme offset, so it clips fewer observations (6→10 against 5→13 for the constant), and at an old-zone monitor already near the sensor floor that changes the information content. The `const(D)` arm reproduces Steps 8 and 8c exactly (−3.82 / +3.87 SD at node 15; −5.94 SD at node 231), so the three scripts cross-check rather than merely agreeing in narrative. |
| **On the concavity — the review is right, and the earlier contradiction was our error** | Measured with the formal likelihood, `shift(+0.025)/shift(+0.05) = 53%`, i.e. above the 50% that linearity would give, so the effect **is** sub-linear/concave as the comment states, though weaker than ~70%. An earlier version of this response reported it as *convex* (45%): that figure came from the informal GLUE score, whose flatness inverts the curvature as well as shrinking the shift. This is the third place where the informal score reverses a conclusion, after 3.2 and 3.3. |
| **New result worth reporting** | The **risk field is far more robust to sensor bias than the parameters are.** Even at ±0.10 mg/L, where `k_w,old` moves by nearly 4 posterior SD, the 92-node risk ranking has Spearman ≥ 0.999 against the unbiased case; the top-6 set is unchanged for every negative offset and loses one node (Jaccard 0.71) at the positive ones. So a biased sensor corrupts the coefficient badly while leaving the operational prioritisation almost intact — and more so than the `P_bar` figures suggest: ranked by the cumulative deficit `E[A]` that Step 10 publishes, 23 of the 24 arms in the six-monitor sweep leave the top-6 unchanged, and no drift arm in Step 8d changes it at all. |
| **Node 15 is the right headline but not the worst location** | The six-monitor sweep under the formal primary shows the largest *normalised* corruption is at **average-zone monitor 231: −5.94 posterior SD at −0.10 mg/L**, then new-zone 113 (−4.44 SD); node 15 reaches −3.82 / +3.87 SD. Cross-zone leakage is also not negligible in SD units — biasing a new-zone monitor moves `average` by up to 2.0 SD, biasing an average-zone monitor moves `new` by up to 2.7 SD, which is the `average`↔`new` confounding Step 7's sloppiest eigen-direction predicts. The earlier "avg/new hardly respond" reading came from the informal weighting, which flattens exactly the weakly-informed coefficients. |
| **Remaining limitation** | Only a **monotone linear ramp starting from zero** is modelled; a drift already part-developed at the window start, a step change, a non-monotone excursion and a realistic fouling curve are not run, so the supported claim is the narrow one — for a monotone drift, the mean offset over the calibration window is what the estimate responds to. The response is also asymmetric, as censoring predicts (`|neg|/|pos|` = 1.14 / 1.19 / 0.99 at ±0.025 / ±0.05 / ±0.10, with the censored count running 13 → 5 across the sweep), so results must always be quoted with the sign. Risk-band crossing counts are not yet reported. |

### #2 A priori identifiability (Fisher information, CRLB, profile likelihood)

| field | content |
|---|---|
| **Comment** | Converts the central finding from an observation into a prediction: compute which coefficients are identifiable *before* calibrating, then confirm with GLUE. |
| **Change made** | Fisher information and CRLB under three nested models — `k_w` only, `+k_b`, `+6 sensor offsets` — with marginal CRLB via the Schur complement (Step 7); profile likelihood with ΔNLL ≤ 1.92 (Step 7b); AR(1) versions of both (Step 7c). |
| **Code** | `step7_fisher.py`, `step7_verify.py`, `step7b_profile.py`, `step7c_ar1.py`, `step7c_profile_ar1.py` |
| **Artifact** | `step7_fisher.json`, `step7b_profile.json`, `step7c_ar1.json`, `step7c_profile_ar1.json` |
| **Status** | **closed, stronger** |
| **What changed beyond the comment** | The prediction and the calibration now **agree quantitatively**, which is the check the comment was reaching for. The formally weighted ensemble's empirical SD is within 1–5% of the Case-A CRLB (0.0938 vs 0.0947; 0.0142 vs 0.0135; 0.0078 vs 0.0080) — i.e. the formal posterior spread is **locally consistent with the Case-A CRLB**. That is a consistency check under the same model, truth and error assumptions, not a frequentist-efficiency proof. Step 14's 100-realisation empirical SD / CRLB ratios (≈1.04 / 1.06 / 1.12) strengthen the same local reading, with nominal-90% coverage at 0.89 / 0.88 / 0.85 — slightly under nominal for `new`, so the intervals are approximately but not exactly calibrated. The informal score gives 2.8–3.1× the bound on the same data. Separately, `step7_verify.py` was reporting the **Jacobian-column cosine** as a parameter correlation; the two differ in sign — cosine **+0.333 / +0.770 / +0.831** against estimator correlation **−0.547 / −0.839 / −0.842** — and it is the negative estimator correlation that carries the bulk–wall compensation story. Both are now written into `step7_fisher.json` (`kb_confounding`) rather than only printed, so the distinction is checkable. |
| **Case C is the realism verdict** | With `k_b` and six per-monitor offsets carried as nuisance parameters, CRLB/prior-SD is **0.67 (old) / 2.24 (average) / 1.09 (new)** — old retains limited identifiability, average and new go above their prior and are practically unidentifiable. Case B (adding `k_b` alone) inflates the CRLB by 1.19× for old but 1.84–1.85× for average/new, which is the same ordering Step 8b then measures empirically. |
| **Grid quantisation now measured and removed** | The profile is recomputed continuously — Nelder–Mead over the two nuisance coefficients at each target value, endpoints by Brent bisection on `ΔNLL − 1.92`, **7770** EPANET evaluations, run under both the censored (primary) and iid likelihoods. Under the primary rule every interval was **too narrow on the grid**, by +39.0% (`old`), +14.8% (`average`) and +28.2% (`new`) in half-width, with endpoints moving ~0.8 of a grid step and always outward. That is the signature of quantisation, not noise: a grid stops at the last node inside the interval. Only the continuous intervals should be quoted, and the AR(1) widening factor of 2.00× for `old` in #4 is explained by the same cause — its independent-case denominator was one of these narrow grid intervals. |
| **Step convergence and scaling now checked** | Each coefficient was re-differenced across a fourfold to tenfold range of step with **scale-dependent** FD steps (`old 0.02`, `average 0.005`, `new 0.0025`). The Case-A CRLB varies by about 1% across the sweep. On scaling: the raw condition number of ~215 is largely a **units artefact** — the coefficients differ in scale by 20× — and on the prior-scaled, dimensionless matrix it is **3.2** (eigenvalues 24.5 / 16.6 / 7.6 against raw 23906 / 5106 / 111). That qualifies the "eigenvalues spanning three orders of magnitude" framing: it describes the units, not the identifiability. The sloppiest direction is `old −0.297, average −0.663, new +0.687`, i.e. average traded against new. |
| **Remaining limitation** | Fisher is linearised at the synthetic truth, so it is an oracle benchmark rather than a true pre-experiment design tool; a prior-averaged or worst-case Fisher would be needed for that. |

### #3 Censored likelihood

| field | content |
|---|---|
| **Comment** | 28 of 438 observations were clipped at zero, concentrated in the low-residual old zone where the risk map is decided; the draft clips the data but then uses unweighted RMSE, which is misspecified there. |
| **Change made** | Tobit-type censored Gaussian implemented — Gaussian density on positive observations, `log Φ(−μ/σ)` on clipped zeros — and compared with the naive exact-zero treatment on identical data over 30 realisations (Step 9). |
| **Code** | `step9_zeroclip.py`, `wq_common.log_censored` |
| **Artifact** | `step9_zeroclip.json` |
| **Status** | **closed, stronger** |
| **What changed beyond the comment** | The censored likelihood is no longer a side check: it is the **primary weighting** for every headline parameter, risk and scenario number. Two of the comment's premises also shifted at the corrected warm-up: the census is now 10 of 294 calibration points (43 of 1014 over the record), and the clipping is **no longer confined to the old zone** — one point falls at an average-zone monitor, because the average zone depletes far enough by 120 h to reach the sensor floor. |
| **Remaining limitation** | The correction is small: measurable in the weighted mean (old −1.0405 censored vs −1.0289 naive, a −0.0116 shift) and **invisible on the 21-point grid profile**, whose 0.065 m/day step is five times the shift. It is *not* invisible in general — the **continuous** profile of Step 7b resolves it, giving `old` = [−1.1720, −0.8106] censored against [−1.1517, −0.7973] iid, i.e. a shift toward stronger decay with a 2.0% wider half-width. The correct statement is "grid-based profiles cannot resolve the censoring correction, whereas the continuous profile shows a modest shift and widening"; the earlier "profile intervals are identical" wording described the grid only and must not be generalised. |

### #4 Error autocorrelation

| field | content |
|---|---|
| **Comment** | All intervals assume hourly independence, so every uncertainty figure is a floor. The operational analysis uses AR(1) with ρ = 0.4. |
| **Change made** | AR(1) covariance built as a per-sensor Toeplitz block, `Σ_block[t,s] = σ²ρ^|t−s|`, and applied to both the Fisher/CRLB route and a full profile likelihood over the residual grid (Steps 7c). Each coefficient widens by its own factor (1.44–1.49× for CRLB) rather than by one mechanical scalar. |
| **Code** | `step7c_ar1.py`, `step7c_profile_ar1.py` |
| **Artifact** | `step7c_ar1.json`, `step7c_profile_ar1.json` |
| **Status** | **closed** |
| **Also done this pass** | The ρ sweep is implemented: CRLB inflation runs 1.00× (ρ = 0) → 1.21× → 1.48× → 1.83× → **2.13–2.47×** (ρ = 0.8), with effective sample size falling 294 → 33. Even at ρ = 0.8 the CRLB/prior ratio only reaches 0.72, so all three coefficients stay nominally identifiable in Case A — the autocorrelation assumption changes the width substantially but not the identifiability verdict. |
| **Remaining limitation** | ρ remains **assumed**: the baseline observations are generated iid, so no value of ρ is supported by this data set. The thesis must write "if the errors had AR(1) structure with ρ = X" and never "the errors are autocorrelated with ρ = X". Estimating ρ needs real monitoring residuals. |

### #5 Bulk–wall compensation

| field | content |
|---|---|
| **Comment** | `k_b` is fixed at −0.5 day⁻¹ and excluded from the ensemble, yet it is the parameter that trades off against `k_w`; any error in it is absorbed into the wall coefficients and the risk map. Repeat GLUE at `k_b ± 20%`. |
| **Change made** | The calibration was repeated at `k_b ∈ {−0.4, −0.5, −0.6}` (Step 8b) under the **formal censored primary** over **30 noise realisations**, with the risk field taken as the median over them; `k_b` is additionally carried as a nuisance parameter in the Fisher analysis (Step 7 Case B), where marginalising it inflates the `k_w` CRLBs by 1.19× (old) and 1.84–1.85× (average/new). |
| **Code** | `step8b_kb_sensitivity.py`, `step7_fisher.py` (Case B) |
| **Artifact** | `step8b_kb_sensitivity.json`, `step7_fisher.json` |
| **Status** | **closed, stronger** — and the conclusion is the opposite of the one the earlier response recorded |
| **What changed beyond the comment** | The single-seed gap is closed: 30 realisations, formal weighting, median risk field. Under the formal likelihood ±20% `k_b` moves `average` by 1.41–1.53 posterior SD and `new` by 1.49–1.58 SD, against 0.56–0.66 SD for `old` — the *weakly informed* coefficients absorb the bulk-decay error, exactly the ordering Fisher Case B predicts. The informal score puts the same shifts at 0.11–0.40 SD, a four- to fivefold understatement, which is why the earlier table read as a null result. |
| **The risk conclusion is reversed — but the size of the reversal depends on the risk metric** | The earlier response said the risk product was insensitive to `k_b`, which is not sayable as stated. The **full-network** ranking does stay broadly rank-correlated on both metrics (Spearman 0.976 / 0.933 on `P_bar`, 0.980 / 0.935 on `E[A]`). The **leading set** behaves differently on each: ranked by the time-averaged probability `P_bar` it retains only four of six at both signs (Jaccard 0.50, and the reordering reaches rank 20); ranked by the cumulative deficit `E[A]` that Step 10 publishes, it is **unchanged at −0.4** and loses **one** node at −0.6 in a sixth/seventh-place exchange. The defensible sentence is: *the broad network-wide risk pattern remained strongly rank-correlated; the duration-ranked shortlist was sensitive to bulk-decay misspecification, while the deficit-ranked shortlist changed only by one boundary exchange.* Jaccard compares membership, not order within the set. |
| **Depth check — the turnover is not a cut-off artefact** | Because `6` is a chosen cut-off, the comparison was repeated at k = 3/5/6/10/15 and every entering node traced to its rank in the correctly specified field. The Jaccard is **worse at k = 3 (0.20, one of three shared) than at k = 6 (0.50)**, the opposite of what a boundary effect gives. At `k_b = −0.4` the reference 3rd and 4th nodes fall to 8th and **20th**; at `−0.6` a node ranked **12th rises to 2nd**. Only node 131 is common to every leading set, and it is saturated (risk 1.0000, below threshold for the whole window) so it cannot move. A near-tie plateau does exist at ranks 4–6 (0.4699 / 0.4696 / 0.4694, against 0.4490 at rank 7) and explains why those three interchange, but not the larger moves. The median rank change over all 92 junctions is 1.0 place, which is why Spearman stays high while the leading set turns over. **The sentence "the instability is confined to the prioritisation boundary while the core is stable" was tested and is false.** |
| **Attribution — do not over-claim this one** | The hot-spot sensitivity appears under **both** weightings: the informal comparator also gives Jaccard 0.50 at both ±20%. So this is **not** a fourth case of the informal score reversing a conclusion. What the formal rule changes is the *parameter* displacement (1.4–1.6 SD against 0.28–0.40 SD), a magnitude, not the risk verdict. The earlier "ranking robust" statement was primarily a **reporting inconsistency**: the superseded text asserted "Top nodes are unchanged at every k_b" directly beneath a table listing `131, 141, 139` / `131, 129, 141` / `131, 243, 20`, three visibly different sets, with a quoted node list matching none of them. The weighting and the single seed made it easy to miss; they are not what made it false. |
| **Remaining limitation** | `k_b` is still *fixed* at each of three values rather than estimated jointly with the three `k_w`; a four-parameter ensemble would replace this sensitivity sweep with a marginal posterior. Only ±20% was tested. |

### #6 Held-out validation

| field | content |
|---|---|
| **Comment** | The key claim is extrapolation of risk to 86 unmonitored junctions; leave-one-monitor-out validation is the standard evidence and is cheap with six monitors. |
| **Change made** | Leave-one-monitor-out over all six monitors, 30 noise realisations: held-out prediction RMSE 0.092–0.103 mg/L under the formal primary (0.091–0.102 informal) against a σ = 0.1 noise floor, 90% band coverage 0.90–0.94 under both. |
| **Code** | `step11_loo.py` |
| **Artifact** | `step11_loo.json` |
| **Status** | **closed, stronger** |
| **What changed beyond the comment** | Two harder tests were added, and the harder one **undercuts what LOO appeared to show**. Leave-one-**zone**-out (both monitors of a zone dropped): the dropped zone's coefficient reverts *exactly* to its prior midpoint, with 100% of the prior width retained — `old` to −0.850 (error +0.150), `average` to −0.120. Each coefficient is informed by its own two monitors and nothing else; there is no spatial borrowing. Yet the held-out **prediction** RMSE stays ≈0.10 mg/L and coverage 0.90–0.96 even for the zone that has learned nothing. So **predictive success is not evidence of parameter identifiability**, and LOO cannot be read as validating the coefficients. It succeeds because the prior is centred near the truth — the same artefact as §3.1, so §3.1 and #6 are one problem seen twice. Validation at 20 junctions that never enter any calibration gives 0.6–0.8% mean error against the truth with 1.00 coverage against a nominal 0.90, i.e. conservative rather than calibrated bands. The weighted predictive quantile the comment suggested is implemented and reported alongside the normal approximation; here they agree. |
| **Also done this pass** | The heterogeneous leave-one-zone-out was run (±20% per-pipe truth, 8 fields, one zone unobserved, formal weighting). Row by row it matches the homogeneous formal case — coefficient errors +0.139 / −0.020 / +0.012 against +0.149 / −0.020 / +0.001, SD retained 100 / 100 / 55% against 100 / 100 / 57% — so **the cost of an unobserved zone dominates the cost of ±20% structural error by a wide margin**. Prediction at unmonitored junctions stays at 0.8–1.2% relative error. One figure goes sub-nominal: coverage for the dropped `new` zone is 0.88 against 0.90, the only such case, and it is the one combining a structural discrepancy with a partially-informed coefficient. Also found: `new` is the **only** zone with spatial borrowing, keeping 57% of its prior width with both its monitors gone, which matches its being the upstream zone with the largest per-unit sensitivity at every monitor. |
| **Remaining limitation** | All four tests are internal: the truth is always model-generated, so none of this is external validity. The claim the evidence supports is **spatial prediction**, not parameter identification; those are separate claims and the thesis must not use one to support the other. |

### #7 Toolchain verification (known-answer test)

| field | content |
|---|---|
| **Comment** | A known-answer test — single pipe with an analytic first-order solution — establishes that the coefficients are realised as intended. One paragraph buys considerable credibility. |
| **Risk in the draft** | Every result depends on WNTR writing `k_b` and `k_w` into EPANET with the units and the per-second conversion we assume. Nothing in the project tested that assumption directly; the unit error the review found in 3.4 shows the assumption is not self-evidently safe. |
| **Change made** | Single pipe, one reservoir, constant demand, analytic first-order solution. Three arms: (i) pure bulk decay against `C = C0 exp(k_b t_res)` over a fourfold range of `k_b` — worst relative error **1.1 × 10⁻⁴** against a 10⁻³ tolerance, and the error grows with the amount of decay, which is discretisation rather than a scaling mistake; (ii) wall decay checked for exact agreement with the bulk case at `k_w = 0`, monotonicity in `k_w`, and staying above the infinite-mass-transfer bound — EPANET's first-order wall rate combines `k_w` with the mass-transfer coefficient `k_f`, so an exact analytic value is not available and the report says so; (iii) the conversion helper itself. All pass. |
| **Code** | `step13_known_answer.py` |
| **Artifact** | `step13_known_answer.json` |
| **Status** | **closed** |
| **Note** | The "linearity known-answer check" in `step12_scenarios.py` is a different thing: it verifies that first-order kinetics scale with the source concentration, not that the coefficients equal what we set. |

### #8 The ±0.1 mg/L convention

| field | content |
|---|---|
| **Comment** | The draft treats ±0.1 as one standard deviation; read as a 95% band it implies σ ≈ 0.05 and halves every interval. State the convention explicitly. |
| **Change made** | Stated in the log's front matter with the arithmetic spelled out, and a one-sentence form drafted for the Methodology. `σ` is one standard deviation everywhere in the code (`wq_common.SIGMA_OBS`). |
| **Status** | **closed** |
| **Remaining limitation** | The sentence still has to be inserted into the `.docx`. |

---

## Priority 3 — framing of the risk product

| field | content |
|---|---|
| **Comment** | (i) Name the outcome correctly: a sensor-conditioned probabilistic forecast from a network model, not a spatial measurement, and not a statement about whether water is safe. (ii) The time-averaged probability conflates a node marginally below the threshold at all times with a node far below it for two hours; report exceedance duration or depth alongside `P`. |
| **Change made** | (ii) is implemented and is now the main risk output: below-threshold duration, cumulative deficit and window minimum, each as a weighted expectation with 5–95% bands, plus water age as a reaction-independent diagnostic (Step 10). `P_min` (window breach) and `P_bar` (time-averaged) are kept explicitly distinct in the scenario work (Step 12). (i) is written into the log as a product statement, including what the map is **not**. |
| **Code** | `step10_risk_metrics.py`, `step12_scenarios.py` |
| **Artifact** | `step10_risk_metrics.json`, `step12_scenarios.json`, `step12_risk_register.csv` |
| **Status** | **closed** for the repository, **thesis document** for the Discussion wording |
| **Also done this pass** | The reporting-resolution question is answered rather than left open: re-running the highest-weight members at 3600 / 900 / 300 s changes network-mean `E[D]` by **−1.6%** and `E[A]` by **−0.7%**, with an identical top-10 set. The change is *negative*, so hourly reporting slightly over-estimates duration rather than missing excursions — trapezoidal smearing of crossings outweighs any dip lost between reports — and most of it appears by 900 s and stops, which is what convergence looks like. Hourly reporting is adequate **because the field is smooth on the hour scale here**, not by assumption. |
| **Remaining limitation** | Unweighted, consumer-only and demand-weighted network means are now all reported (and they move in opposite directions). The water-age corroboration remains mechanistic, not independent validation; ordinary Spearman p-values and iid junction bootstrap CIs are omitted because the 92 junctions are strongly spatially dependent — only a descriptive ρ and a spatial-block bootstrap width are kept. |

---

## §6 Length, structure, presentation, references

| field | content |
|---|---|
| **Comment** | 59 pages against a 30-page limit; no heading styles, no numbered sections or figures, no tables, placeholders remaining, front matter missing; engage with the statistical critique of GLUE (Stedinger et al. 2008; Mantovan and Todini 2006), consider Powell et al. (2000). |
| **Status** | **thesis document** — outside this repository, except the references |
| **What this repository contributes** | The GLUE critique is no longer something to cite politely: this project now contains a concrete, quantified instance of exactly what those papers warn about (the factor-`N` omission, the 2.8–3.2× inflation over the CRLB, and the resulting prior domination). That makes the required engagement short and pointed. The numeric prose the comment wants converted to tables already exists as tables in `RESULTS_LOG.md` and as machine-readable JSON. |

---

## Work done that the review did not ask for

These were not review comments, but they were prerequisites for the numbers being trustworthy, and
two of them changed published conclusions.

| item | why it was necessary | outcome |
|---|---|---|
| **Warm-up convergence test** (`step0_warmup_convergence.py`) | The 24 h warm-up was never justified, while the high-risk junctions have mean water ages of 34–45 h. | Chlorine concentration criteria pass at **120 h**, chosen as a **pragmatic finite-horizon warm-up**; residual ~5.5% cycle-to-cycle deficit drift remains and water age is **horizon-dependent and unconvergeable** inside the 168 h ceiling. Absolute ages must never be quoted as steady state; the cache was rebuilt and risk severity / top nodes moved. |
| **Model-file freezing** (`models/net3_frozen/Net3.inp`, SHA-256 checked on import) | The pipeline read `Net3.inp` from the installed WNTR package, so a library upgrade could silently change the model underneath every cached result. | Frozen copy with a hard hash check; a tampered file now raises on import. |
| **Provenance manifest** (`provenance.py`) | Nothing recorded which code, configuration or library versions produced a cached result. | `cache_manifest.json` records config hash, `.inp` hash, **`wq_common` hash**, per-step script hashes, git commit **and** tree/dirty-diff hashes, plus exact numpy/scipy versions. Critical cache invalidation includes `wq_common` and library exact versions — not commit id alone. A dirty working tree is identified, not pretended clean; a final release still needs a clean-tree rerun. |
| **Artifact validator** (`validate_artifacts.py`) | The log claimed "every number is produced by a script; nothing is hand-entered", which was false — numbers were transcribed by hand and had drifted. | Registered claims, weighting declarations, near-miss drift, and forbidden phrasing. Useful against numerical drift; **not** a proof of semantic consistency. |
| **Repeated-noise calibration** (`step14_repeated_noise.py`) | Formal results were quoted from one noise realisation; CRLB agreement alone does not establish bias or coverage. | 100 redraws: formal means nearly unbiased; empirical SD locally consistent with Case-A CRLB; 90%/95% coverage near nominal; informal over-covers by width. |
| **Config-keyed grid caches** | `step7b_rmse_grid.npy` and `step7c_resid_grid.npy` were cached on file existence alone, so after the warm-up change three scripts silently reused grids built under the old configuration and reported stale intervals. | Grids are now keyed on the config and `.inp` hashes; a mismatch rebuilds or raises. |
| **Sobol sampling and a convergence check** | The formal likelihood is far sharper than the informal score, so the earlier pre-Sobol draw count (~2k) gave it an effective sample size of only ~37. | 8192 scrambled-Sobol draws (ESS 157); leading `2^k` subsets give an exact convergence table showing the quantiles stable to 0.01 prior SD. |

---

## Summary for the supervisor

Five things in this response need a decision rather than just reading:

1. **The central diagnosis has moved.** The review's 3.1 said the data do not inform two of three
   coefficients. The corrected analysis says the *informal GLUE score* does not, and the data do —
   corroborated by Case-A CRLB local consistency and by Step 14's repeated-noise calibration. The
   dissertation's identifiability narrative has to be rewritten around that distinction, and it
   becomes a stronger contribution: a quantified demonstration of the Stedinger / Mantovan–Todini
   critique on a controlled synthetic case.
2. **The informal score reverses conclusions in three separate places**, so it cannot be left as the
   analysis of record anywhere: it hides the structural bias in 3.3, makes the threshold look like
   the binding choice in 3.2, and inverts the curvature of the sensor-bias response in #1. In each
   case the formal likelihood recovers the effect the review expected, or a stronger version of it.
   A *fourth* effect is a magnitude and not a reversal: it understates the `k_b`-induced parameter
   displacement of #5 four- to fivefold, while both weightings agree on the risk verdict.
3. **One published conclusion is now reversed, not merely refined — and its cause is not what it
   looks like.** The earlier response said the risk product was insensitive to `k_b` ±20%. Over 30
   realisations the full-network ordering is indeed robust, but the top-6 set **retains only four of
   its six hot-spots at both ±20%**, under *both* weightings. The defect was therefore a **reporting
   inconsistency** — a summary sentence contradicting the table printed directly above it — not a
   weighting-induced reversal. Anywhere the draft says the risk map is insensitive to `k_b`, that
   sentence has to go; and the general lesson is that a high whole-network rank correlation is not
   evidence that the actionable shortlist is invariant.
3. **The warm-up correction is not cosmetic.** Absolute severity numbers moved ~10% and the
   top-risk node list changed, so any figure carried over from the draft must be re-checked against
   the current artifacts rather than trusted.
4. **Single-realisation results in this project have reversed twice under scrutiny**, both times
   because a hidden dependence on one arbitrary choice was removed, and neither time was it visible
   from the fit quality. The structural-bias claim flipped when a `jitter = 0` control was added and
   again when one heterogeneity field became 25; the sensor-bias curvature flipped when the weighting
   changed. The methodological lesson belongs in the Discussion: **in this setup a good fit and a
   single realisation are jointly capable of supporting the wrong conclusion**, and the defences that
   worked were a paired control, an ensemble over the arbitrary choice, and a formal likelihood
   whose posterior spread is locally consistent with the Case-A CRLB.
