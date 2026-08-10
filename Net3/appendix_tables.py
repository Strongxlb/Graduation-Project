"""Generate the appendix tables for the Research Paper from the cached artifacts.

Writes Figures/paper/appendix_tables.md, which 00-thesis/build.sh splices into the manuscript at
`{{A:<label>}}` markers. Labels are letters plus an index (A1, F2, ...) rather than running
numbers, so inserting an appendix does not renumber every table after it.

Nothing here recomputes a result. Every value is read from baseline_cache/, so an appendix table
cannot drift from the artifact the main text quotes.
"""
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "baseline_cache")
OUT = os.path.join(HERE, "Figures", "paper", "appendix_tables.md")


def load(name):
    with open(os.path.join(CACHE, name)) as f:
        return json.load(f)


def table(rows, header):
    """A pipe table. Cells are pre-formatted strings; no rounding happens here by accident."""
    out = ["| " + " | ".join(header) + " |",
           "|" + "|".join(["---"] * len(header)) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(c) for c in r) + " |")
    return "\n".join(out)


blocks = []


def add(label, caption, body):
    blocks.append("## %s\n\n%s\n\n%s\n" % (label, caption, body))


# ---------------------------------------------------------------- A: warm-up and horizon
s0 = load("step0_warmup_convergence.json")
crit_order = ["tank_max_dLevel", "monitor_max_dC", "network_p95_dC", "tank_max_dC",
              "risk_rel_dDeficit", "age_p95_dAge"]
crit_name = {
    "tank_max_dLevel": "Tank level (m)",
    "monitor_max_dC": "Monitor chlorine (mg L-1)",
    "network_p95_dC": "Network 95th-percentile chlorine (mg L-1)",
    "tank_max_dC": "Tank chlorine (mg L-1)",
    "risk_rel_dDeficit": "Risk severity, relative change in E[A]",
    "age_p95_dAge": "Water age, 95th percentile (h)",
}
rows = []
for k in crit_order:
    c = s0["per_criterion"][k]
    w = c["worst_by_cycle"]
    fp = c.get("first_pass_warmup_h")
    if fp is not None:
        verdict = "%d h (verified)" % fp
    else:
        ex = c.get("extrapolated_warmup_h")
        verdict = "not met within 168 h; extrapolates to ~%s h (unverified)" % ex
    rows.append([crit_name[k], c["tolerance"]] +
                ["%.4f" % v if v >= 1e-4 else "%.1e" % v for v in w] + [verdict])
add("A1",
    "Table A1. Cyclostationarity diagnostics. Worst value across the truth and both corners of "
    "the prior box, for each pair of successive 24 h cycles. Tolerances were declared before the "
    "values were seen.",
    table(rows, ["Criterion", "Tolerance", "0-24", "24-48", "48-72", "72-96", "96-120",
                 "120-144", "Earliest warm-up satisfying it"]))

truth = [c["sets"]["truth"] for c in s0["cycles"]]
add("A2",
    "Table A2. Network-mean cumulative deficit for the truth, by cycle. The integrated severity "
    "falls after the start-up transient and then rises monotonically, which is why the 2% "
    "criterion is not met inside the model horizon.",
    table([["%d-%d h" % (24 * i, 24 * i + 24), "%.4f" % t["net_mean_deficit"],
            "%.4f" % t["risk_rel_dDeficit"]] for i, t in enumerate(truth)],
          ["Cycle", "Net-mean deficit (mg L-1 h)", "Relative change"]))

# ---------------------------------------------------------------- B: numerical and unit checks
s13 = load("step13_known_answer.json")
add("B1",
    "Table B1. Bulk-decay arm of the known-answer test against the analytic first-order solution "
    "at the far end of a single pipe. The relative error grows with the amount of decay, which is "
    "the signature of the quality solver's time discretisation; a wrong conversion factor would "
    "instead give a constant relative offset.",
    table([["%.2f" % r["kb_per_day"], "%.4f" % r["t_res_h"], "%.6f" % r["epanet_c"],
            "%.6f" % r["analytic_c"], "%.1e" % r["rel_error"]] for r in s13["bulk_arm"]["rows"]],
          ["k_b (1/day)", "Residence time (h)", "EPANET C", "Analytic C", "Relative error"]))

add("B2",
    "Table B2. Wall-decay arm. The exact concentration cannot be predicted from the wall "
    "coefficient alone because EPANET's first-order wall reaction is also limited by mass "
    "transfer, so what is asserted is the sign, monotonicity, and that the result stays above the "
    "mass-transfer-free limit.",
    table([["%.2f" % r["kw_per_day"], "%.6f" % r["epanet_c"], "%.6f" % r["extra_decay_vs_kw0"],
            "%.6f" % r["kf_free_lower_bound_c"],
            "yes" if r["above_bound"] else ("n/a" if r["above_bound"] is None else "NO")]
           for r in s13["wall_arm"]["rows"]],
          ["k_w (m/day)", "EPANET C", "Extra decay vs k_w=0", "Mass-transfer-free bound",
           "Above bound"]))

s15 = load("step15_unit_equivalence.json")
rows = []
for name, c in s15["comparisons"].items():
    rows.append([name.replace("_", " "), "%.2e" % c["max_abs_diff_mg_L"],
                 "%.2e" % c["max_rel_diff"],
                 "%d -> %d" % (c["n_points_below_threshold_ref"],
                               c["n_points_below_threshold_other"]),
                 "%d of %d" % (c["n_cells_with_different_hours_below"], c["n_cells"])])
add("B3",
    "Table B3. Unit-equivalence test over 256 leading Sobol candidates. The corrected "
    "implementation reproduces the superseded one to floating-point precision. The units-only arm "
    "shows what correcting the concentrations while leaving the solver tolerance at the EPANET "
    "default would have cost.",
    table(rows, ["Comparison", "Max absolute difference (mg L-1)", "Max relative difference",
                 "Points below threshold", "Duration cells that differ"]))

# ---------------------------------------------------------------- C: threshold and displacement
s3 = load("step3_threshold.json")
rows = []
for r in s3["rows"]:
    rows.append(["%.3f" % r["threshold"], r["count"], "%.1f%%" % (100 * r["retention"]),
                 "%.2f" % r["sd_above_floor"]] +
                ["%.4f (%.1f%%)" % (r[z]["sd"], 100 * r[z]["sd_retained"])
                 for z in ("old", "avg", "new")])
add("C1",
    "Table C1. Behavioural-threshold sweep for the informal comparator. Tightening the cut-off "
    "removes candidates but cannot restore the information factor the score omits, so the "
    "retained widths stay far above the formal values.",
    table(rows, ["Threshold (mg L-1)", "Retained", "Retention", "SD above sigma",
                 "old SD (retained)", "average SD (retained)", "new SD (retained)"]))

s4d = load("step4d_displaced_robust.json")
rows = []
for design, d in s4d["designs"].items():
    for scheme, sc in d["by_scheme"].items():
        for z in ("old", "avg", "new"):
            g = sc["groups"][z]
            rows.append([design, scheme.replace("_", " "), z,
                         "%.0f%% [%.0f-%.0f]" % (100 * g["gap_med"], 100 * g["gap_iqr"][0],
                                                 100 * g["gap_iqr"][1]),
                         "%.0f%%" % (100 * g["sd_ret_med"])])
add("C2",
    "Table C2. Displaced-prior recovery over 30 noise realisations, as the median fraction of the "
    "imposed displacement recovered with its interquartile range, and the retained prior width. "
    "DOWN displaces every coefficient towards stronger decay; OLDUP displaces the old coefficient "
    "the other way.",
    table(rows, ["Design", "Rule", "Coefficient", "Displacement recovered [IQR]",
                 "Prior SD retained"]))

# ---------------------------------------------------------------- D: Fisher mechanics
s7 = load("step7_fisher.json")
rows = []
for case, c in s7["cases"].items():
    rows.append([case, "%.1f" % c["condition_number"]] +
                ["%.4f (%.0f%%)" % (c["coef"][z]["crlb"], 100 * c["coef"][z]["crlb_over_prior"])
                 for z in ("old", "average", "new")])
add("D1",
    "Table D1. Cramer-Rao bounds under nested nuisance models, obtained from the marginal (Schur) "
    "information. Percentages are the bound as a fraction of the prior standard deviation.",
    table(rows, ["Case", "Condition number", "old", "average", "new"]))

rows = []
for z, c in s7["fd_step_convergence"].items():
    for r in c["rows"]:
        rows.append([z, "%.4g" % r["step"], "%.1f%%" % (100 * r["step_over_truth"]),
                     "yes" if r["is_default"] else "", "%.6f" % r["crlb"]])
add("D2",
    "Table D2. Finite-difference step convergence for the Jacobian. Steps are scale-dependent "
    "rather than shared, because one absolute step would be a 2% perturbation of the old "
    "coefficient and a 40% perturbation of the new one.",
    table(rows, ["Coefficient", "Step", "As % of truth", "Default", "Case-A bound"]))

g = s7["fisher_geometry"]
add("D3",
    "Table D3. Eigenvalues of the Case-A information matrix in raw and prior-scaled form. The "
    "raw condition number is dominated by the factor of twenty between the coefficient scales; "
    "on the dimensionless matrix the spread is far smaller.",
    table([["Raw"] + ["%.0f" % v for v in g["eigenvalues_raw"]] +
           ["%.0f" % g["condition_number_raw"]],
           ["Prior-scaled"] + ["%.1f" % v for v in g["eigenvalues_prior_scaled"]] +
           ["%.1f" % g["condition_number_prior_scaled"]]],
          ["Form", "Eigenvalue 1", "Eigenvalue 2", "Eigenvalue 3", "Condition number"]))

# ---------------------------------------------------------------- E: structural heterogeneity
s5c = load("step5c_jitter_sweep.json")
rows = []
for r in s5c["rows"]:
    for z in ("old", "average", "new"):
        zz = r["zones"][z]
        rows.append(["%.0f%%" % (100 * r["jitter"]), z, "%.4f" % zz["arith"],
                     "%+.4f" % zz["bias"], "%+.2f" % zz["bias_in_sd"],
                     "%+.4f" % zz["bias_increment_vs_control"]])
add("E1",
    "Table E1. Symmetric within-zone heterogeneity under the primary rule. The increment is the "
    "bias net of a paired homogeneous control run on the same noise, which is the part that can "
    "be attributed to the imposed structure.",
    table(rows, ["Jitter", "Zone", "True arithmetic mean", "Raw bias", "In posterior SD",
                 "Increment over control"]))

fe = {z: s5c["rows"][1]["field_ensemble"][z] for z in ("old", "average", "new")
      if "field_ensemble" in s5c["rows"][1]}
if fe:
    add("E2",
        "Table E2. The same design repeated over 25 independent heterogeneity fields at plus or "
        "minus 20%. The mean increment is a fraction of the field-to-field scatter in every zone, "
        "so no systematic bias is distinguishable from the choice of field.",
        table([[z, "%+.4f" % fe[z]["bias_mean"], "%.4f" % fe[z]["bias_sd"],
                "%+.4f" % fe[z]["increment_mean"], "%.4f" % fe[z]["increment_sd"],
                "%.2f" % fe[z]["increment_mean_over_sd"]] for z in fe],
              ["Zone", "Bias mean", "Bias SD", "Increment mean", "Increment SD",
               "|mean| / SD"]))

s5d = load("step5d_structured.json")
rows = []
for z, d in s5d["zones"].items():
    for scheme, sc in d["by_scheme"].items():
        rows.append([z, scheme.replace("_", " "), "%.4f" % d["arith"], "%.4f" % d["lenwt"],
                     "%.4f" % sc["mean"], "%+.4f" % sc["bias"],
                     "%+.4f" % sc["homogeneous_baseline_offset"],
                     "%.0f%%" % (100 * sc["shift_frac_of_lenwt_gap"])])
add("E3",
    "Table E3. Length-structured heterogeneity in the reference realisation. The homogeneous "
    "baseline offset is what the same rule returns with no structural error at all and must be "
    "subtracted before a shift is read as structural.",
    table(rows, ["Zone", "Rule", "Arithmetic mean", "Length-weighted proxy", "Posterior mean",
                 "Shift", "Homogeneous offset", "Fraction of gap"]))

# ---------------------------------------------------------------- F: per-arm sensor error
s8c = load("step8c_bias_bynode.json")
rows = []
for r in s8c["rows"]:
    if r["scheme"] != "formal_censored":
        continue
    rows.append([r["node"], r["zone"], "%+.3f" % r["offset"],
                 "%+.2f" % r["d_old_over_sd"], "%+.2f" % r["d_avg_over_sd"],
                 "%+.2f" % r["d_new_over_sd"], int(r["n_censored_med"]),
                 "%.4f" % r["risk_spearman_vs_unbiased"],
                 "%.2f" % r["risk_top6_jaccard_vs_unbiased"],
                 "%.2f" % r["deficit_top6_jaccard_vs_unbiased"]])
add("F1",
    "Table F1. Every arm of the sensor-bias sweep under the primary rule, as the displacement of "
    "each coefficient in baseline posterior standard deviations. Rank statistics compare the "
    "92-junction risk field with the unbiased case.",
    table(rows, ["Node", "Zone", "Offset (mg L-1)", "old", "average", "new", "Censored points",
                 "Spearman", "Top-6 Jaccard (duration)", "Top-6 Jaccard (deficit)"]))

s8d = load("step8d_sensor_drift.json")
rows = []
for node, arms in s8d["equivalence"].items():
    for mag, e in arms.items():
        rows.append([node, mag, "%+.4f" % e["drift_shift"], "%+.4f" % e["const_mean_shift"],
                     "%+.4f" % e["const_end_shift"], "%.2f" % e["drift_over_const_mean"],
                     "%.2f" % e["drift_over_const_end"]])
add("F2",
    "Table F2. Sensor drift against its mean-equivalent and end-equivalent constant-bias controls "
    "on identical noise. A monotone drift acts, to within about a tenth, as a constant bias at "
    "its mean over the window.",
    table(rows, ["Node", "End offset D", "Drift shift", "const(D/2)", "const(D)",
                 "Drift / const(D/2)", "Drift / const(D)"]))

# ---------------------------------------------------------------- G: risk-assessment mechanics
s10 = load("step10_risk_metrics.json")
a = s10["age_risk_association"]
bb = a["block_bootstrap"]
add("G1",
    "Table G1. Water-age association and the resampling design behind its interval. Whole spatial "
    "blocks are resampled rather than individual junctions, because junctions sharing pipes, flow "
    "paths and tank states are not independent samples. The interval is a descriptive width, not "
    "a significance test.",
    table([["Spearman, duration", "%.4f" % a["spearman_dur"]],
           ["Spearman, deficit", "%.4f" % a["spearman_def"]],
           ["Pearson, duration", "%.4f" % a["pearson_dur"]],
           ["Junctions", a["n_junctions"]],
           ["Blocks", bb["n_blocks"]],
           ["Block rule", bb["block_rule"]],
           ["Resamples", bb["n_resamples"]],
           ["95% interval, Spearman duration",
            "[%.3f, %.3f]" % tuple(bb["ci95_spearman_dur"])]],
          ["Quantity", "Value"]))

nav = s10["network_averages"]
rows = [[m.replace("_", " "), "%.4f" % v["unweighted_all_junctions"],
         "%.4f" % v["consumer_only"], "%.4f" % v["demand_weighted"]]
        for m, v in nav["by_metric"].items()]
add("G2",
    "Table G2. Three network averages for each risk metric. Consumer-only is worse than "
    "unweighted while demand-weighted is better, which can only happen if the risk concentrates "
    "at small consumers.",
    table(rows, ["Metric", "Unweighted (all 92)",
                 "Consumer-only (%d)" % nav["n_consumer_junctions"], "Demand-weighted"]))

s12 = load("step12_scenarios.json")
u = s12["uncertainty_sources"]
add("G3",
    "Table G3. Scenario draw specification. One draw per retained ensemble member is reused "
    "across every scenario and dose as a common random number, so scenario differences are "
    "physical rather than Monte Carlo noise.",
    table([["Retained draws", "%d of %d (weight above %g of the maximum)"
            % (s12["n_retained_draws"], s12["n_total_draws"], s12["weight_floor_relative"])],
           ["Discarded weight mass", "%.2e" % s12["discarded_weight_mass"]],
           ["Bulk activation energy", "N(%.0f, %.0f^2) J/mol, truncated below at %.0f"
            % (u["Ea_bulk_J_per_mol"]["mean"], u["Ea_bulk_J_per_mol"]["sd"],
               u["Ea_bulk_J_per_mol"]["truncated_at"])],
           ["Realised bulk range", "%.0f to %.0f J/mol"
            % (u["Ea_bulk_J_per_mol"]["drawn_min"], u["Ea_bulk_J_per_mol"]["drawn_max"])],
           ["Wall activation energy", "N(%.0f, %.0f^2) J/mol, truncated below at %.0f"
            % (u["Ea_wall_J_per_mol"]["mean"], u["Ea_wall_J_per_mol"]["sd"],
               u["Ea_wall_J_per_mol"]["truncated_at"])],
           ["Realised wall range", "%.0f to %.0f J/mol"
            % (u["Ea_wall_J_per_mol"]["drawn_min"], u["Ea_wall_J_per_mol"]["drawn_max"])],
           ["Water temperature", u["water_temperature_C"]],
           ["Realised temperature range", "%.2f to %.2f degC"
            % tuple(u["water_temperature_span_C"])],
           ["Draws resampled at the bound", u["water_temperature_draws_resampled"]],
           ["Common random numbers", u["common_random_numbers"]]],
          ["Quantity", "Specification"]))

# ---------------------------------------------------------------- H: risk register
with open(os.path.join(CACHE, "step12_risk_register.csv")) as f:
    reg = list(csv.DictReader(f))
keep = ["node", "P_min_current", "P_min_heatwave", "P_min_heat_ageing", "P_bar",
        "E_duration_h", "E_deficit_mgL_h", "demand_L_s", "likelihood_band",
        "consequence_band", "risk_band_breach", "risk_band_severity", "risk_band_governing"]
keep = [k for k in keep if reg and k in reg[0]]
hdr = [k.replace("_", " ") for k in keep]
rows = []
for r in sorted(reg, key=lambda x: -float(x.get("E_deficit_mgL_h") or 0)):
    rows.append([r[k] for k in keep])
add("H1",
    "Table H1. The complete risk register, all 92 junctions, ordered by expected cumulative "
    "deficit. Banding rules are given in the main text; the governing band is the higher of the "
    "breach and severity bands.",
    table(rows, hdr))

# ---------------------------------------------------------------- write
os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w") as f:
    f.write("<!-- Generated by Net3/appendix_tables.py. Do not edit by hand. -->\n\n")
    f.write("\n".join(blocks))
print("wrote %s  (%d tables)" % (os.path.relpath(OUT, HERE), len(blocks)))
