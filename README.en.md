# Uncertainty-aware calibration and identifiability of grouped first-order chlorine wall-decay coefficients (a controlled EPANET Net3 three-zone study)

> This README is the **2026-08 revision**, reflecting the actual research after the supervisor's paper review of 2026-07-25 (see [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md)).
> Chinese: [`README.md`](./README.md) ｜ English (this file)
> Execution plan: [`plan1.md`](./plan1.md) ｜ Literature list: [`background/Literature/literature.md`](./background/Literature/literature.md)

---

## 0. In one sentence

On the **EPANET Net3** benchmark network, partitioned by pipe material/age into three contiguous zones (**old / average / new**), we use a **known synthetic truth** to generate noisy observations and systematically study the **uncertainty-aware calibration** and **identifiability** of the first-order wall-decay coefficients `k_w`: what the data can actually constrain, where GLUE's honest limitations lie, how structural / systematic / autocorrelated / censoring errors affect the estimates, and how parameter uncertainty does (and does not) propagate into the operational low-chlorine **risk map**. Everything is reproducible and script-driven; results live in [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md).

---

## 1. Project context

This is an MSc dissertation for **Imperial College London CIVE70058 Research Dissertation – Environmental** (30 ECTS / 60 CATS). Final deliverables:

- **Research paper** — due 2026-08-21 12:00; scientific-paper format; up to 12,000 words.
- **Research poster** — due 2026-08-28 12:00.
- Completed checkpoints: 2026-06-19 supervisor checkpoint; 2026-07-03 student checkpoint.
- **Current phase**: the supervisor returned a paper review + a revised Jupyter notebook on 2026-07-25; the work is now in **final revision** (Priority-1 corrections + Priority-2 methodological additions) and integrating the experiments into the manuscript.

The repository tracks code, models, result figures, literature notes and dissertation drafts; all key progress is recorded via Git.

---

## 2. Research topic

Revised working title: **Uncertainty-aware calibration and identifiability of grouped first-order chlorine wall-decay coefficients — a controlled EPANET Net3 three-zone study**.

The point is not to "estimate one number" but to answer: **given realistic monitor density and measurement noise, can the grouped `k_w` be identified at all, and what does that mean for operational risk?** A **synthetic truth** is used as a controlled testbed — because the truth is known, identifiability can be assessed rigorously, "precise" can be separated from "unbiased", and validation can be honest. Keywords:

- **EPANET / WNTR** — EPANET 2.2 water-quality engine + WNTR Python wrapper (`wntr 1.4.0`).
- **First-order chlorine decay** — first-order bulk (`k_b`) + first-order wall (`k_w`) (Rossman 1994 / EPANET 2.2 Manual).
- **Grouped `k_w` (material/age zones)** — Net3 split by node coordinates into old / average / new contiguous zones, one `k_w` per zone — reducing the "multi-DMA heterogeneity" question to a controlled synthetic case.
- **GLUE (informal likelihood)** — Beven & Binley 1992; this project confronts its statistical inefficiency and threshold/prior dependence head-on.
- **Formal identifiability tools** — Fisher information / Cramér–Rao lower bound (CRLB), profile likelihood, AR(1) covariance correction.
- **Measurement error in the likelihood** — Gaussian observation noise, systematic bias, zero-clipping (censored likelihood); avoid over-confidence in "perfect" observations.
- **Operational risk propagation** — duration/depth/cumulative deficit of nodes below the operational threshold `0.2 mg/L`, corroborated by water age.

---

## 3. Motivation

Chlorine residual directly governs microbial safety. Traditional calibration treats observations as exact and reports single-point parameters, which can yield **over-confident parameters** and **misleading risk judgements**. Two neglected issues:

1. **Identifiability** — with sparse monitors and non-trivial noise, **not all grouped `k_w` are identifiable from the data**. Without checking, "successful calibration" may just be a **prior-centring** artefact.
2. **Error structure** — observations carry systematic bias, temporal autocorrelation, and **zero-clipping** at low residuals (`C_obs = max(0, C_true+ε)`); the model also has structural error. All of these can decouple "good fit" from "correct parameters" (precise-but-biased).

This project makes both points concrete on a **synthetic three-zone case with known truth**, and carries the conclusions all the way to the **operational risk map**: even if some `k_w` are poorly identified, are the risk hot-spots still robust? In this study `0.2 mg/L` is a **selected operational low-chlorine threshold** (representative operational value), **not** a legal/compliance safety limit.

---

## 4. Research questions and objectives

### 4.1 Research questions (mapped to completed experiments)

1. **Baseline reproduction** — can the three-zone downstream chlorine series be reproduced and frozen into a reproducible GLUE baseline? (Step 1)
2. **Identifiability** — with 6 monitors (2 per zone) and σ = 0.1 noise, to what extent is each grouped `k_w` constrained? (Steps 2–4, 7, 7b)
3. **Threshold/prior dependence** — how is the behavioural threshold set on principled grounds, and are the conclusions robust to threshold/prior? (Steps 3, 4)
4. **Error-source sensitivity** — how do structural error, systematic sensor bias, `k_b` misspecification (bulk–wall compensation), temporal autocorrelation AR(1), and zero-clipping each affect the estimates? (Steps 5, 7c, 8, 8b, 9)
5. **Required sensor accuracy** (the supervisor's email question) — how small must sensor σ be for useful chlorine predictions? (Step 6)
6. **Risk propagation and validation** — does parameter uncertainty change the operational low-chlorine **hot-spot ranking**? Is the risk map physically corroborated? Can the model predict **unseen** monitors? (Steps 10, 11)

### 4.2 Overall objective

Build a **reproducible, uncertainty-aware, identifiability-focused** workflow for grouped-`k_w` calibration and risk assessment that honestly delimits what GLUE can do and what the data can constrain, and that propagates parameter uncertainty all the way to operational risk decisions and predictive validation.

---

## 5. Scope

### 5.1 In scope

- **EPANET Net3** benchmark network (WNTR's bundled `.inp`), split by coordinates into old/average/new contiguous zones.
- **First-order** kinetics (bulk + wall); `k_b` fixed at `-0.5 day⁻¹`, estimating three grouped `k_w`.
- **Synthetic truth** + Gaussian observation noise (σ = 0.1 mg/L is **one standard deviation**); 6 monitors (2 per zone).
- **GLUE** (2000 uniform-prior draws) + **formal identifiability** (Fisher/CRLB, profile, AR(1)).
- Error modelling: systematic bias, `k_b` misspecification, zero-clipping (censored / Tobit-type likelihood).
- Operational risk: duration/depth/cumulative deficit below `0.2 mg/L` + water-age corroboration + LOO predictive validation.

### 5.2 Out of scope

- **No hydraulic calibration** — demands and roughness trust the existing model.
- **No multi-species modelling** (EPANET-MSX); no TOC/DBP/biofilm coupling.
- **No operational optimisation** (no sensor placement / flushing / booster optimisation).
- Real Bristol 3-DMA field data are **not** included in this revision (the study uses the controlled Net3 synthetic case as the vehicle for the methodology; a known truth is prerequisite for identifiability analysis).
- AI tools are used only for code assistance / language polishing / idea organisation, disclosed per Imperial/CEE rules, never submitted directly as dissertation content.

---

## 6. Method framework and key settings

### 6.1 Frozen baseline (Step 1)

- Synthetic truth: `k_b = -0.5 day⁻¹` (fixed); `k_w`: old `-1.0`, average `-0.1`, new `-0.05` (`m/day`).
- Monitors (2 per zone): new `107/113`, old `15/145`, average `209/231`.
- Timing: 72 h simulation, 24 h warm-up → **49 reporting points = 48 h window**; observation noise `σ = 0.1 mg/L`.
- GLUE: 2000 uniform-prior draws, caching **every candidate's prediction at all 92 nodes**, so downstream experiments reuse the cache without re-running EPANET.

Prior ranges (`m/day`):

```
old      : [-1.5,  -0.2 ]
average  : [-0.2,  -0.04]
new      : [-0.10, -0.005]
```

### 6.2 GLUE and the behavioural threshold (Steps 2–3)

Informal Gaussian weighting and behavioural threshold:

```
w_i ∝ exp[ -½ · (RMSEᵢ / σ)² ] · 1[ RMSEᵢ < RMSE_thr ]
RMSE_thr = σ · (1 + z / √(2·N_resid))      # z=1.645 → one-sided 95% band; σ=0.1, N_resid=294 → 0.107
```

Primary threshold `0.107` (the draft's looser `0.12` is kept for comparison).

### 6.3 Identifiability: formal tools (Steps 7 / 7b / 7c)

- **Fisher / CRLB (a priori)** — `F = Jᵀ J / σ²`, marginalised via the Schur complement, giving the **theoretical minimum variance** for a given sensitivity and noise level.
- **Profile likelihood (a posteriori / practical)** — fix one coefficient, re-optimise the others; `ΔNLL ≤ 1.92` gives the 95% interval.
- **AR(1) autocorrelation** — recompute `F = JᵀΣ⁻¹J` and the profile with covariance `Σ[t,s] = σ²ρ^|t−s|`, quantifying interval inflation (not a single mechanical multiplier).

Read in two layers: **(1) controlled-baseline identifiability** (Fisher A ↔ profile ↔ GLUE under the same conditions); **(2) realism sensitivity** (+`k_b`, + sensor bias, AR(1), censoring).

### 6.4 Error-source sensitivity (Steps 5 / 8 / 8b / 9)

Structural error (pipe-level jitter / length-correlated heterogeneity), systematic sensor bias, `k_b ±20%` (bulk–wall compensation), and zero-clipping censored likelihood:

```
uncensored (obs>0): Gaussian    -½·((obs-μ)/σ)²
clipped-0  (obs=0): P(Y*≤0)     log Φ(-μ/σ)      # scipy log_ndtr
```

### 6.5 Operational risk and validation (Steps 6 / 10 / 11)

- **Required-accuracy sweep** — σ = 0.02 / 0.05 / 0.10 / 0.15, threshold scaled with σ.
- **Risk metrics** (trapezoidal over the 48 h window): below-`0.2 mg/L` **duration**, **minimum concentration**, **cumulative deficit** `∫max(0,0.2−C)dt`; ensemble-weighted expectation + 5–95% bands.
- **Water age** — a hydraulic diagnostic independent of the reaction coefficients, used as **physical corroboration** of the risk pattern (Spearman rank correlation).
- **Leave-one-monitor-out (LOO)** — hold out a monitor, calibrate on the other five, then predict it; check out-of-sample error and band coverage.

Reproduction: see §9 and the "Files and how to reproduce" header of [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md).

---

## 7. Key findings (summary of Steps 1–11)

> Full data, tables and figures are in [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md); highlights below.

1. **Only the dominant old coefficient is appreciably constrained** — under GLUE the old posterior narrows markedly, while average/new stay near the prior (weakly informed); the draft's "all three recovered well" was partly a **prior-centring** artefact (Steps 2, 4).
2. **Threshold/risk robustness** — a principled threshold `0.107` (95% band above the noise floor); tightening mainly sharpens old, and the risk hot-spot ranking is robust to the threshold (Step 3).
3. **old is one-sidedly identifiable** — the observations pull old back toward the truth from the weak-decay side but constrain the strong side only weakly (Steps 4/4b).
4. **Structural error → precise-but-biased** — robust under symmetric jitter; length-correlated within-zone heterogeneity makes GLUE track the length-weighted mean **precisely but with bias** (Step 5).
5. **Required accuracy** — σ ≲ 0.05 is needed to tighten the low-residual nodes that decide the risk map; `±0.1` recovers only old + the coarse risk pattern; `±0.15` is essentially back to the prior (Step 6, answering the supervisor's email).
6. **Formal vs informal** — under the idealised baseline both Fisher (CRLB/prior 0.25/0.29/0.29) and profile deem all three identifiable; GLUE is much broader and more prior-sensitive (the informal likelihood drops the factor `N`, a statistical inefficiency). Realism factors (`k_b`, sensor bias, AR(1)) substantially weaken average/new, while old stays comparatively robust (Steps 7/7b/7c).
7. **Systematic error** — a `+0.05` bias at node 15 shifts old by ≈ 0.5 behavioural SD, `+0.10` by ≈ 1.4 SD; `k_b ±20%` shifts `k_w` by ∓0.03–0.04 via bulk–wall compensation; **neither changes** the risk hot-spot ranking (Steps 8/8b).
8. **Zero-clipping (L=0) robustness** — of the 294 calibration points only 8 are clipped to 0 (all in the old zone; 28/438 over the full record); treating zeros as exact vs a censored likelihood gives **effectively identical** `k_w`, profile, node-15 risk and hot-spot ranking — the original treatment did not materially bias the conclusions (Step 9).
9. **Physically anchored risk map** — duration/depth give a richer risk picture than a single probability; risk correlates with water age at `Spearman 0.73` (n=92, bootstrap `[0.63,0.80]`) — risk is governed by **residence time + the identifiable old decay** (Step 10).
10. **Out-of-sample validation** — LOO predicts an unseen monitor with RMSE ≈ the noise floor `0.1`, 90% band coverage 92–94%, and stable parameters — **old moves only when an old-zone monitor is dropped**, independently confirming where its information lives (Step 11).
11. **Overall line** — parameter uncertainty **does propagate** into the *magnitude* of the risk metrics (see the 5–95% bands), but the **ranking of the leading hot-spots is stable** under the tested perturbations (threshold, `k_b`, bias, noise).

---

## 8. Dissertation structure (aligned to the actual results)

- **Introduction** — chlorine safety, why measurement uncertainty affects calibration, the identifiability problem for grouped `k_w`, and the contribution.
- **Background / Literature** — first-order chlorine decay, EPANET/WNTR water-quality simulation, GLUE and its critiques (Mantovan & Todini 2006 / Stedinger 2008), Fisher/CRLB and profile likelihood, measurement error and censoring.
- **Methodology** — Net3 three-zone setup, synthetic truth and noise, GLUE + threshold derivation, Fisher/profile/AR(1), error sensitivity (structure/bias/`k_b`/censoring), risk metrics and LOO.
- **Results** — Steps 1–11 (identifiability → error sensitivity → required accuracy → risk and validation).
- **Discussion** — GLUE's conservatism and statistical inefficiency, the identifiability gradient, precise-but-biased, the meaning of required sensor accuracy for water-safety plans, limitations (AR(1) makes idealised intervals optimistic, water age not at steady state, etc.).
- **Conclusion** — answer each research question; the value of uncertainty-aware calibration; future work (real multi-DMA data, hierarchical Bayes, longer runs for steady-state water age, denser ensembles).

---

## 9. Reproduction

Code is in [`Net3/`](Net3/), conda env `water-supply` (`numpy 2.4.2`, `wntr 1.4.0`). Core files:

- [`Net3/wq_common.py`](Net3/wq_common.py) — the frozen three-zone baseline config + WNTR/EPANET helpers (monitors, zoning, seeds, priors, timing).
- `Net3/step1_freeze_baseline.py` — build the synthetic truth + noisy observations + 2000-draw GLUE, caching all predictions.
- `Net3/step3 … step11_*.py` — threshold, displaced prior, structural error, noise sweep, Fisher/profile/AR(1), sensor bias, `k_b`, censored, risk metrics, LOO.
- [`Net3/RESULTS_LOG.md`](Net3/RESULTS_LOG.md) — **methods, tables, figures and conclusions of every experiment** (every number is produced by a script; the header lists all files and run commands).
- `Net3/baseline_cache/` — caches (`baseline.npz`, etc.) so downstream experiments avoid re-running EPANET.

Typical run (from `Net3/`):

```
export MPLCONFIGDIR=/tmp/mpl
python step1_freeze_baseline.py        # ~40 s (2000 EPANET runs)
python step7b_profile.py               # builds the 21³ grid
python step10_risk_metrics.py          # risk metrics + water age
python step11_loo.py                   # leave-one-out validation
```

---

## 10. Timeline (revised, 2026-08)

| Stage | Status |
| --- | --- |
| Baseline reproduction + GLUE (Steps 1–2) | ✅ done |
| Identifiability + threshold/displaced prior (Steps 3–4) | ✅ done |
| Error sensitivity (structure/noise/Fisher/bias/`k_b`/censoring, Steps 5–9) | ✅ done |
| Risk metrics + water age + LOO validation (Steps 10–11) | ✅ done |
| **Rewrite Results / Discussion / Conclusion (Step 12)** | ⏳ in progress |
| Figure/unit unification, length compression, Word formatting (Step 13) | ⏳ to do |
| Research paper submission | due 2026-08-21 |
| Research poster submission | due 2026-08-28 |

---

## 11. Workflow

- **Git/GitHub** — at least one meaningful commit per stage; do not commit large raw data / temporary outputs / private data; keep code, figures and drafts traceable.
- **Result provenance** — all numbers are generated by scripts and written to `RESULTS_LOG.md` and `baseline_cache/`; no hand-entered values.
- **Suggested layout** — `background/` (literature) ｜ `Net3/` (code + cache + results) ｜ `thesis/` (drafts + figures) ｜ `meetings/` (minutes).

---

## 12. Note on AI-tool use

Imperial/CEE permits generative-AI use where not explicitly forbidden, but submitted content must reflect one's own understanding, judgement and expression. Any AI use for code generation, grammar checking, language polishing, figure captions or idea organisation must be disclosed and cited per faculty rules; all AI output must be human-checked and cannot replace literature reading, modelling judgement or interpretation of results.
