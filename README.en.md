# Uncertainty-aware calibration of first-order chlorine decay in three DMAs — Bristol Water Field Lab

> This README reflects the project scope confirmed by the supervisor's email on **2026-05-25**.
> Chinese: [`README.md`](./README.md) ｜ English (this file)
> Execution plan: [`plan1.md`](./plan1.md) ｜ Literature list: [`background/Literature/literature.md`](./background/Literature/literature.md)

---

## 1. Project context

This is an MSc dissertation project for **Imperial College London CIVE70058 Research Dissertation – Environmental** (30 ECTS / 60 CATS). Final deliverables:

- **Research paper** — submitted by 2026-08-21 12:00; technical / scientific paper format; up to 12,000 words.
- **Research poster** — submitted by 2026-08-28 12:00; visual summary of motivation / method / results / conclusion.
- Mid-project checkpoints:
  - **2026-06-19** — Supervisor checkpoint / progress report.
  - **2026-07-03** — Student checkpoint / reflection.

This repository tracks code, models, data documentation, result figures, and dissertation drafts. All key progress is recorded via Git/GitHub and synchronised in weekly meeting minutes.

---

## 2. Research topic

Working title: **Uncertainty-aware calibration of first-order chlorine residual decay modelling in the Bristol Water Field Lab — a three-DMA comparative study**.

The project uses the existing EPANET model of three monitored DMAs in the Bristol Water Field Lab together with ten free-chlorine online monitors. **Measured chlorine residuals at the three DMA inlets are used as time-varying source boundaries** in WNTR/EPANET; **the seven downstream monitors are used for calibration and validation**. Key concepts:

- **EPANET / WNTR** — water-quality simulation platform (EPANET 2.2 engine + WNTR Python wrapper).
- **First-order chlorine decay** — only first-order bulk (`k_b`) + first-order wall (`k_w`) + the boundary-layer mass-transfer term (Rossman 1994 / EPANET 2.2 Manual).
- **Three-DMA comparative calibration** — heterogeneous pipe material/age → heterogeneous `k_w` → one `k_w` per DMA, then quantify cross-DMA transferability.
- **Ensemble-based uncertainty** — GLUE (Plan A) or Bayesian MCMC / hierarchical partial pooling (Plan B) to quantify parameter and predictive uncertainty.
- **Time-varying inlet boundary** — the three inlet monitors feed directly into the source pattern; **inlet chlorine is not a calibration parameter**.
- **DPD / colorimetric / online-sensor uncertainty** — measurement error enters the likelihood; avoid over-confidence in "perfect" observations.

---

## 3. Motivation

Chlorine residual in distribution networks directly governs microbial safety. Traditional calibration treats observations as exact, but real measurements are affected by sensor precision, DPD colorimetric error, sampling location/time, and model-structure error. Ignoring these uncertainties can yield over-confident parameters and misleading risk judgements.

More importantly: **real networks are partitioned into multiple DMAs, with heterogeneous pipe material and age**. A `k_w` calibrated in one DMA may not predict another — a question raised repeatedly in the literature (Hallam 2002, Maleki 2023) but rarely answered head-on. Leveraging the natural three-DMA structure of the Bristol Water Field Lab, this project upgrades *"estimate one `k_w`"* to:

1. **Heterogeneity question** — how different are the three DMA `k_w` values? Statistically significant?
2. **Transferability question** — when a model calibrated on DMA-A is applied to DMA-B / C, how much does predictive reliability drop?
3. **Does uncertainty change the conclusion?** — with posterior intervals on `k_w`, is the "DMA difference" a real signal or noise?

A residual target of `0.2 mg/L` is used as a placeholder threshold for risk figures, to be confirmed with the supervisor.

---

## 4. Research questions & objectives

### 4.1 Research questions

1. **Baseline** — Using the existing EPANET model and WNTR `simulate_chlorine(kb, kw)`, can we reproduce the observed chlorine time-series at the seven downstream monitors across the three DMAs?
2. **Deterministic calibration** — Under the framework "one shared `k_b` + one `k_w` per DMA", what are the best-fit values?
3. **Uncertainty propagation** — With explicit DPD / online-sensor measurement-error modelling, what are the posterior / confidence intervals on the parameters?
4. **Inter-DMA heterogeneity** — Are the three `k_w` posteriors significantly different? Is the difference consistent with pipe material/age (Hallam 2002 / Maleki 2023)?
5. **Transferability** — When parameters learned on DMA-A are applied to DMA-B / C, by how much do predictive RMSE and coverage (CRPS) deteriorate?
6. **Threshold judgement** — Under uncertainty, how does the spatial / temporal probability of falling below `0.2 mg/L` evolve?

### 4.2 Overall objective

Build a **reproducible, uncertainty-aware, cross-DMA comparative** EPANET/WNTR chlorine-calibration workflow, producing per-DMA `k_w` posteriors, cross-DMA predictive reliability metrics, and per-node threshold-exceedance probability distributions.

### 4.3 Concrete tasks

- **Literature review** — chlorine decay mechanics (A1/A2/A3/A4/A5/A6), EPANET/WNTR (B1/B2/B3), uncertainty methods (E1/E3/E4/E5/E6/E7), measurement error (D2/D3/D4/D5), regulatory thresholds (F1/F2).
- **Baseline simulation** — get the supervisor-supplied Jupyter notebook running `simulate_chlorine(kb, kw)`; warm-up on Net3, then switch to the Bristol 3-DMA model.
- **Data pipeline** — 3 inlet monitors → time-varying source pattern; 7 downstream monitors → 5 for calibration, 2 held-out for validation (split to be confirmed in Week 5).
- **Deterministic calibration (baseline)** — weighted least squares for `(k_b, k_w_A, k_w_B, k_w_C)`; metrics NSE / RMSE / MAE.
- **Uncertainty calibration (Plan A)** — GLUE (Beven & Binley 1992, E6) — Monte Carlo + likelihood weighting; 5–95% parameter and predictive intervals.
- **Uncertainty calibration (Plan B)** — Bayesian hierarchical model (Gelman BDA, E7 Ch 5) — three `k_w` share a family prior, partial pooling; MCMC via `emcee` or `pymc`.
- **Cross-DMA transferability** — calibrate on DMA-A, posterior-predictive-check on DMA-B / C.
- **Result interpretation** — per-DMA `k_w` posterior violin plots, cross-DMA CRPS / coverage comparison, per-node threshold-exceedance probability heatmaps.
- **Paper writing** — per §7 structure (Introduction / Background / Methodology / Results / Discussion / Conclusion).

---

## 5. Scope

### 5.1 In scope (per supervisor email)

- Three monitored DMAs from the existing Bristol Water Field Lab EPANET model.
- **First-order** chlorine kinetics (bulk + wall + mass-transfer).
- Continuous chlorine measurements from 10 monitors (3 inlet → boundary, 7 downstream → calibration / validation).
- Parameters: `k_b` (possibly shared across DMAs) + one `k_w` per DMA (three values).
- Uncertainty method: **ensemble-based** (GLUE first; Bayesian / hierarchical as the advanced track).
- DPD / online-sensor measurement-error modelling (D2/D3/D4/D5 references).
- Result figures, reproducible workflow, paper and poster materials.

### 5.2 Out of scope (explicitly excluded by supervisor)

- **No hydraulic calibration** — trust the existing model for node demands and pipe roughness.
- **No multi-species modelling (EPANET-MSX)** — no TOC / DBP / biofilm coupling.
- **No operational optimisation** — no sensor placement, pipe cleaning planning, or booster optimisation.
- No new hardware sensor development; no full lab water-chemistry experiments.
- AI tool outputs are not submitted directly as dissertation content; AI-assisted coding / language polishing / idea organisation must be disclosed per Imperial / CEE policy.

### 5.3 To be confirmed (Tuesday 2026-06-02 meeting)

- **Data delivery format & timeline** — when do we get the 10-monitor data? CSV? SCADA dump? frequency? duration?
- **EPANET `.inp` access** — where is the file? Are pipe material / diameter / age fields complete?
- **`k_b` sharing assumption** — same source water ⇒ pooled `k_b`, or per-DMA?
- **"Ensemble-based method" — exact preference?** GLUE / ensemble Kalman / approximate Bayesian?
- **Work-package structure** — WP5 = hierarchical Bayesian; what are WP1–WP4?
- **Threshold definition** — keep `0.2 mg/L` or align with UK SI 2016/614 / WHO?

---

## 6. Methodology

### 6.1 Baseline modelling

1. Load the Bristol 3-DMA EPANET `.inp` model in WNTR; identify the three DMA inlet nodes and the seven downstream monitor nodes.
2. Feed the three inlet chlorine time-series into the source pattern (time-varying boundary).
3. Run `simulate_chlorine(kb, kw)` with EPANET options `CHEMICAL`, `BULK ORDER 1`, `WALL ORDER 1`, and trial values (e.g. `k_b = -0.5 /day`, `k_w = -0.15 m/day`).
4. Output simulated concentrations at the 7 downstream nodes; visually compare to observations; confirm magnitude / trend reasonable.

### 6.2 Deterministic calibration (baseline)

Minimise the weighted residual between simulation and observation:

```
J(k_b, k_w_A, k_w_B, k_w_C) = Σ_{node i, time t} [ (y_obs - y_sim) / σ_i ]²
```

with `σ_i` from the measurement-error model (DPD ±0.02 mg/L or online sensor ±5% full-scale). Output a point estimate; evaluate with RMSE / MAE / NSE. **This is a baseline, not the final result.**

### 6.3 Uncertainty-aware calibration

#### Plan A — GLUE (Beven & Binley 1992, E6)

1. LHS / uniform sampling of `(k_b, k_w_A, k_w_B, k_w_C)` over prior ranges, `N ≈ 10⁴` draws.
2. Run `simulate_chlorine(kb, kw)` for each.
3. Compute NSE or Gaussian likelihood weights; discard non-behavioural samples (NSE < 0.6).
4. Weighted aggregation → marginal parameter distributions + 5–95% predictive intervals.

#### Plan B — Bayesian hierarchical MCMC (Gelman BDA, E7 Ch 5 / Ch 11)

```
k_w_d ~ Normal(mu_kw, tau_kw²)           # DMA d ∈ {A, B, C} share family prior
mu_kw  ~ Normal(0.15, 0.10²)             # informed by Hallam 2002 / Maleki 2023
tau_kw ~ HalfNormal(0.05)                # scale of inter-DMA heterogeneity
k_b    ~ LogNormal(log 0.5, 0.5²)        # network-wide (same source water)
y_obs ~ Normal(y_sim(k_b, k_w_d), sigma_meas²)
```

Run ≥ 4 chains × 5,000 samples (incl. warmup) with `emcee` or `pymc`; monitor `R̂ < 1.05`, ESS > 1000. Posterior outputs: per-DMA `k_w` 50% / 95% intervals + the `tau_kw` posterior (quantifying inter-DMA heterogeneity).

### 6.4 Cross-DMA transferability

Split calibration data by DMA:
- Train posterior on DMA-A → posterior predictive check on DMA-B / C.
- Report: per-DMA posterior predictive RMSE, CRPS, 95% interval coverage.
- Significant heterogeneity ⇒ a single-`k_w` model does not transfer ⇒ per-DMA calibration is necessary; otherwise a pooled `k_w` simplification is justified.

### 6.5 Evaluation

Core criteria:

- Reproduction quality of the 7 downstream chlorine time-series (hourly / sub-hourly).
- Whether the three `k_w` values are significantly different (judged by the `tau_kw` posterior being away from zero).
- Decay in cross-DMA predictive reliability (CRPS / coverage).
- Which nodes / time windows are most likely to fall below `0.2 mg/L`; exceedance probability maps.
- Engineering implications for Bristol Water operations (e.g. which pipe material is the highest-value renewal priority).

---

## 7. Paper structure

### 7.1 Introduction

Why does chlorine modelling in distribution networks matter? Why does measurement uncertainty affect calibration? What are the research questions, objectives, and contributions of this project?

- **Background** — drinking-water safety, disinfection residuals, network water-quality risk.
- **Problem** — traditional calibration ignores observation error, leading to over-confident decisions.
- **Contribution** — an uncertainty-aware calibration workflow for three-DMA real-world data, demonstrated on the Bristol Water Field Lab.

### 7.2 Background / Literature review

- **Chlorine decay** — bulk vs wall decay, age, temperature, organic matter, pipe-wall heterogeneity (A1–A6).
- **Water-quality modelling** — EPANET water-quality solver, WNTR Python workflow (B1–B3).
- **Calibration methods** — least squares, optimisation, sensitivity analysis (C1–C6).
- **Uncertainty methods** — sensor uncertainty, measurement error, Monte Carlo, GLUE, Bayesian / hierarchical MCMC (D2–D5, E1–E7).

### 7.3 Methodology

- Bristol 3-DMA EPANET model and data source.
- Parameter ranges, calibration targets, time windows.
- Measurement-error model assumptions.
- Plan A: GLUE workflow; Plan B: Bayesian hierarchical MCMC workflow.
- Evaluation metrics and figure plan.

### 7.4 Results

- Network topology and monitor locations.
- Observed vs simulated time-series at the 7 downstream monitors.
- Pre / post calibration error metrics.
- Per-DMA `k_w` posterior violin plots; `tau_kw` posterior (heterogeneity scale).
- Predictive intervals for chlorine.
- Cross-DMA transferability (CRPS / coverage).
- Threshold-exceedance probability heatmap.

### 7.5 Discussion

- Sensor uncertainty impact on calibration credibility.
- How the `0.2 mg/L` exceedance judgement changes from deterministic to probabilistic.
- Engineering implications of inter-DMA heterogeneity (material / age signal vs noise).
- Limitations: data quantity, model-structure error, identifiability, generalisability.

### 7.6 Conclusion

- Answer each research question.
- Summarise the value of uncertainty-aware calibration.
- Future work: longer monitoring records, in-line sensor integration, full Bayesian hierarchical pooling, more DMAs, MSX coupling.

---

## 8. Timeline

The project runs from approximately 2026-05-15 to the research paper submission on 2026-08-21 (~13 weeks), with the poster due 2026-08-28.

| Phase | Window | Goal | Output |
| --- | --- | --- | --- |
| Week 1 | 2026-05-15 → 2026-05-22 | Project framing, toolchain, literature v1 | README, literature list, repo bootstrap, WNTR demo |
| Week 2 | 2026-05-23 → 2026-06-02 | Read supervisor materials; run starter notebook | Notebook runs on Net3; 6 new notes (A6 / B1 / B2 / E6 / E7); Tuesday Q-list |
| Week 3-4 | 2026-06-03 → 2026-06-12 | Switch to Bristol 3-DMA `.inp`; data pipeline | Working model + data schema + baseline simulation |
| Week 5 (M1 prep) | 2026-06-13 → 2026-06-19 | Supervisor checkpoint | Progress report; Plan A (GLUE) running |
| Week 6-7 | 2026-06-20 → 2026-07-03 | Deterministic + Plan A done; Student checkpoint | Baseline calibration; GLUE intervals |
| Week 8-9 | 2026-07-04 → 2026-07-17 | Plan B (Bayesian hierarchical MCMC) | Posterior plots; convergence diagnostics |
| Week 10 | 2026-07-18 → 2026-07-24 | Cross-DMA transferability + result figures | All Results figures finalised |
| Week 11 | 2026-07-25 → 2026-07-31 | Methodology / Results / Discussion writing | Paper body draft |
| Week 12 | 2026-08-01 → 2026-08-07 | Full draft for supervisor review | Full draft |
| Week 13 | 2026-08-08 → 2026-08-21 | Revisions, proof-reading, submission | Final research paper |
| Poster | 2026-08-22 → 2026-08-28 | Poster design and submission | Final research poster |

---

## 9. Workflow

### 9.1 Git / GitHub

- All code and documents tracked in Git/GitHub.
- At least one meaningful commit per phase.
- No large raw data, temporary outputs, or private data in the repository.
- Code, figures, and dissertation drafts must remain traceable.

### 9.2 Suggested directory layout

```text
codes/
  README.md / README.en.md
  plan1.md                 # weekly execution plans
  background/              # literature notes, key concepts, formula notes
    Literature/            # PDFs + literature.md
    notes/                 # per-paper reading notes (A/B/C/D/E/F subfolders)
  data/                    # data documentation, cleaning scripts, small example data
  models/                  # EPANET .inp or model configurations
  notebooks/               # Jupyter notebooks (supervisor starter + project use)
  src/                     # Python / WNTR analysis code
  results/                 # figures, tables, statistical outputs
  thesis/                  # research paper drafts and structure
  meetings/                # weekly meeting minutes
  learning/                # tutorials and learning resources (e.g. git_learning.md)
```

### 9.3 Shared cloud folder

Suggested layout for the shared cloud folder:

- `background/` — papers, reports, literature notes.
- `data/` — raw data, processed data, data documentation.
- `code/` — backup or links matching the GitHub repository.
- `results/` — figures and tables that go directly into the paper.
- `thesis/` — paper drafts, supervisor feedback, version history.
- `weekly meetings/` — meeting minutes, question lists, action items.

---

## 10. Weekly meeting template

Format: weekly F2F or Teams; keep a fixed cadence.

```markdown
## Meeting YYYY-MM-DD

### 1. Completed last week
- 

### 2. Issues encountered
- 

### 3. My proposed solution
- 

### 4. Supervisor feedback
- 

### 5. Plan for next week
- 

### 6. Items needing supervisor confirmation
- 
```

Three preparations before each meeting:

1. What was actually done last week.
2. The single most blocking issue.
3. My own proposed solution — bring proposals, not just questions.

---

## 11. Current priorities (updated 2026-05-25)

### Confirmed ✓

- [x] Project title and scope formalised: 3-DMA + first-order + ensemble-based + excludes hydraulics / MSX / optimisation (supervisor email).
- [x] Literature list v1 (28+ entries across A–F).
- [x] 12 in-depth reading notes filed (A1 / A2 / A3 / A4 / C1 / C2 / C5 / D2 / E1 / E3 / E5 / F2).

### Required before Tuesday 2026-06-02 meeting

- [ ] **Run the supervisor's Jupyter notebook** `simulate_chlorine(kb, kw)` (Net3 warm-up).
- [ ] **Download and skim** B1 Klise 2017 (WNTR paper), B2 EPANET 2.2 Manual (water-quality chapter only), A6 Vasconcelos 1997.
- [ ] **Prepare the question list for the supervisor** (pre-fill in `meetings/2026-06-02.md`): data format, `.inp` access, `k_b` sharing assumption, exact "ensemble-based" preference, WP structure, threshold definition.

### Weeks 3–4 (06-03 → 06-12)

- [ ] Obtain the Bristol 3-DMA `.inp` and the 10-monitor data.
- [ ] Switch `simulate_chlorine` from Net3 to the real model.
- [ ] Build the inlet → time-varying source-pattern pipeline.
- [ ] Baseline deterministic calibration (WLS).

### Week 5+ (after M1)

- [ ] Plan A working: GLUE Monte Carlo + likelihood weighting.
- [ ] Plan B working: Bayesian hierarchical MCMC (`emcee` or `pymc`).
- [ ] Cross-DMA transferability (posterior predictive checks).

---

## 12. AI tools disclosure

Imperial / CEE allows the use of generative AI tools where not explicitly prohibited, but submitted material must reflect the author's own understanding, judgement and writing. Where AI is used (code generation, grammar checks, language polishing, figure captions, brainstorming), the use must be disclosed and cited per CEE policy. All AI-generated content must be human-verified; it does not substitute for literature reading, modelling judgement, or result interpretation.
