"""Step 12: operational temperature / ageing scenario projection of the GLUE ensemble.

Transplants the supervisor's WSP risk-scenario framework onto THIS project's three-zone
GLUE calibration (not the homogeneous Gaussian posterior of the enclosed notebook).

Pipeline
--------
  GLUE behavioural ensemble (threshold 0.107, 1126/2000)
    -> Arrhenius temperature scaling of k_b and the three zonal k_w
    -> optional illustrative ageing-reactivity multipliers on the three zones
    -> network-wide chlorine prediction
    -> window-breach probability, time-averaged probability, duration, deficit
    -> likelihood x consequence risk bands, maps, risk register
    -> control-measure evaluation: heatwave source dosing 1.00 / 1.15 / 1.30 mg/L

Three sources of scenario uncertainty are propagated jointly, with COMMON RANDOM NUMBERS
(one draw per behavioural member, reused across every scenario and dose) so that scenario
differences are physical rather than Monte-Carlo noise:
  1. kinetic coefficients          -- the GLUE behavioural ensemble itself
  2. activation energies           -- Ea_bulk ~ N(45, 8^2), Ea_wall ~ N(35, 10^2) kJ/mol
  3. water temperature actually reached -- dT ~ N(0, 1^2) degC added to the scenario mean

Two probability definitions are reported and kept DISTINCT (they are not interchangeable):
  P_min  = sum_i w_i * 1[ min_t C_i(t) < C_crit ]   window-breach probability
  P_bar  = E[D] / T_window                          time-averaged below-threshold
                                                     probability (the Step-10 quantity)
The assessment window is t = 24..72 h (48 one-hour intervals), so P_min is a 48-hour
window minimum -- systematically higher than a 24-hour "daily minimum" and therefore not
directly comparable with the supervisor's notebook figures.

Numerical bound: zonal k_w are clipped to CLIP_LO purely as a solver guard. CLIP_LO is set
far outside the physical range reached by any scenario, and the number of clipped members
is reported and asserted to be zero, so no reported mean is distorted by the bound.

Caveats for the thesis: T_ref = 12 degC and the ageing alphas are illustrative planning
assumptions, not Net3 asset records; calibrated coefficients are effective parameters at an
assumed reference regime; the product is a calibration-conditioned scenario projection, not
a sensor nowcast, and scenario maps cannot be verified against data.
"""
from __future__ import annotations

import os
import json
import time

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.stats import truncnorm
import wntr

import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figures")
CACHEDIR = os.path.join(HERE, "baseline_cache")
os.makedirs(FIGDIR, exist_ok=True)

# ---- operational / scenario constants (illustrative) ----
C_CRIT = 0.2
T_REF_C = 12.0
R_GAS = 8.314
EA_BULK_MEAN, EA_BULK_SD = 45000.0, 8000.0     # J/mol
EA_WALL_MEAN, EA_WALL_SD = 35000.0, 10000.0    # J/mol
T_SD_C = 1.0                                   # water-temperature uncertainty (degC)
EA_MIN = 5000.0                                # J/mol, physical lower bound for Ea draws
T_VALID_C = (8.0, 24.0)                        # stated validity range of the assessment
CLIP_LO = -8.0                                 # inert solver guard (see module docstring)
DOSES = [1.00, 1.15, 1.30]
DRAW_SEED = 12

# Illustrative ageing-reactivity stress on the three material/age zones. The baseline model
# ALREADY distinguishes new/average/old k_w, so ageing is applied as an escalation-only
# stress (all alpha >= 1); alpha_new < 1 would weaken already-weak new pipes and
# double-count the zone structure. These are NOT asset measurements for Net3.
ALPHA_SETS = {
    "mild":    {"new": 1.00, "average": 1.15, "old": 1.40},
    "central": {"new": 1.00, "average": 1.35, "old": 1.85},
    "severe":  {"new": 1.00, "average": 1.50, "old": 2.20},
}
ALPHA_ZONE = ALPHA_SETS["central"]
ALPHA_NONE = {"new": 1.0, "average": 1.0, "old": 1.0}

SCENARIO_DEF = {
    "A_baseline": {"label": "A. Baseline 12 °C", "T": 12.0, "alpha": ALPHA_NONE},
    "B_warm":     {"label": "B. Warm season 16 °C", "T": 16.0, "alpha": ALPHA_NONE},
    "C_heatwave": {"label": "C. Heatwave 20 °C", "T": 20.0, "alpha": ALPHA_NONE},
    "D_heat_age": {"label": "D. Heatwave 20 °C + ageing stress", "T": 20.0, "alpha": ALPHA_ZONE},
}

LIK_LABEL = {1: "rare", 2: "unlikely", 3: "possible", 4: "likely", 5: "almost certain"}
CONS_LABEL = {0: "non-consumer", 1: "minor", 2: "moderate", 3: "major"}
CONTROL = {
    "very high": "Review dosing/booster strategy; consider flushing or turnover improvement",
    "high": "Confirmatory sampling; review local operation and demand assumptions",
    "medium": "Scheduled sampling within the monitoring programme; watch trend",
    "low": "No action beyond routine monitoring",
    "not applicable": "Not applicable",
}

trapz = np.trapezoid if hasattr(np, "trapezoid") else np.trapz


def arrhenius_factor(t_c, ea, t_ref_c=T_REF_C):
    t = np.asarray(t_c, dtype=float) + 273.15
    t_ref = float(t_ref_c) + 273.15
    return np.exp(-(np.asarray(ea, dtype=float) / R_GAS) * (1.0 / t - 1.0 / t_ref))


def likelihood_band(p):
    if p < 0.05:
        return 1
    if p < 0.20:
        return 2
    if p < 0.50:
        return 3
    if p < 0.80:
        return 4
    return 5


def risk_band(score):
    if score == 0:
        return "not applicable"
    if score <= 3:
        return "low"
    if score <= 6:
        return "medium"
    if score <= 9:
        return "high"
    return "very high"


def base_demand_L_s(wn, nodes):
    """Net3 base demand is CFS in the .inp; x1000 gives L/s."""
    return pd.Series({n: 1000.0 * sum(ts.base_value
                                      for ts in wn.get_node(n).demand_timeseries_list)
                      for n in nodes})


def consequence_from_demand(demand):
    served = demand[demand > 0]
    q1, q2 = served.quantile([1 / 3, 2 / 3])

    def band(d):
        if d <= 0:
            return 0
        return 1 if d <= q1 else (2 if d <= q2 else 3)

    return demand.apply(band), float(q1), float(q2)


def metrics_from_C(C, w, t_window):
    """C: (n_members, n_t, n_nodes) -> the four node-level risk metrics."""
    D = trapz((C < C_CRIT).astype(np.float64), dx=1.0, axis=1)          # hours below
    A = trapz(np.maximum(0.0, C_CRIT - C), dx=1.0, axis=1)              # mg/L*h deficit
    M = C.min(axis=1)                                                   # window minimum
    P_min = w @ (M < C_CRIT).astype(np.float64)
    Dbar = w @ D
    return {"P_min": P_min, "P_bar": Dbar / t_window, "Dbar": Dbar, "Abar": w @ A, "M": M}


def run_ensemble(idx, S_old, S_avg, S_new, ea_b, ea_w, dT, T_mean, alpha, inlet,
                 nodes, tank_mgl=None, duration_h=B.DURATION_H, warmup_h=B.WARMUP_H,
                 members=None, quiet=False):
    """Forward every behavioural member under one scenario / dose."""
    sel = np.arange(len(idx)) if members is None else members
    n = len(sel)
    n_t = (duration_h - warmup_h) + 1
    C = np.empty((n, n_t, len(nodes)), dtype=np.float32)
    kb_used = np.empty(n)
    kw_used = {"old": np.empty(n), "average": np.empty(n), "new": np.empty(n)}
    n_clipped = 0
    tank = B.TANK_INIT_MGL if tank_mgl is None else tank_mgl
    t0 = time.time()
    for k, m in enumerate(sel):
        i = idx[m]
        t_water = T_mean + dT[m]
        fb = float(arrhenius_factor(t_water, ea_b[m]))
        fw = float(arrhenius_factor(t_water, ea_w[m]))
        raw = {"old": S_old[i] * fw * alpha["old"],
               "average": S_avg[i] * fw * alpha["average"],
               "new": S_new[i] * fw * alpha["new"]}
        n_clipped += sum(1 for v in raw.values() if v < CLIP_LO)
        kwz = {z: float(np.clip(v, CLIP_LO, 0.0)) for z, v in raw.items()}
        kb = B.KB_FIXED * fb
        kb_used[k] = kb
        for z in kw_used:
            kw_used[z][k] = kwz[z]
        C[k] = B.simulate_chlorine(
            kb, 0.0,
            pre_run=B.make_kw_hook(kwz["old"], kwz["average"], kwz["new"]),
            monitor_nodes=nodes, inlet_mgl=inlet, tank_mgl=tank,
            duration_hours=duration_h,
        ).values[warmup_h:].astype(np.float32)
        if not quiet and ((k + 1) % 300 == 0 or (k + 1) == n):
            print(f"    {k + 1}/{n}  ({time.time() - t0:.1f}s)")
    return C, kb_used, kw_used, n_clipped


def draw_network_background(ax, wn):
    for p in wn.pipe_name_list:
        lk = wn.get_link(p)
        x0, y0 = wn.get_node(lk.start_node_name).coordinates
        x1, y1 = wn.get_node(lk.end_node_name).coordinates
        ax.plot([x0, x1], [y0, y1], color="0.85", lw=0.6, zorder=1)


def scatter_nodes(ax, wn, nodes, values, vmin, vmax, cmap="viridis"):
    xs = [wn.get_node(n).coordinates[0] for n in nodes]
    ys = [wn.get_node(n).coordinates[1] for n in nodes]
    return ax.scatter(xs, ys, c=values, s=30, cmap=cmap, vmin=vmin, vmax=vmax,
                      edgecolors="0.3", linewidths=0.3, zorder=2)


def mark_monitors(ax, wn):
    xs = [wn.get_node(n).coordinates[0] for n in B.MONITOR_NODES]
    ys = [wn.get_node(n).coordinates[1] for n in B.MONITOR_NODES]
    ax.scatter(xs, ys, s=90, facecolors="none", edgecolors="navy",
               linewidths=1.6, zorder=5, label="monitors")


# ============================== setup ==============================
cache = np.load(os.path.join(CACHEDIR, "baseline.npz"), allow_pickle=True)
S_old = cache["S_old"].astype(np.float64)
S_avg = cache["S_avg"].astype(np.float64)
S_new = cache["S_new"].astype(np.float64)
RMSE = cache["RMSE"].astype(np.float64)
C_all = cache["C_all"].astype(np.float64)
ALL_NODES = [str(n) for n in cache["all_nodes"]]

w_raw = np.exp(-0.5 * (RMSE / B.SIGMA_OBS) ** 2) * (RMSE < B.RMSE_THR)
idx = np.where(w_raw > 0)[0]
w = w_raw[idx] / w_raw[idx].sum()
n_beh = len(idx)
T_WINDOW = C_all.shape[1] - 1

print(f"behavioural ensemble at RMSE < {B.RMSE_THR}: {n_beh}/{len(RMSE)}")
print(f"assessment window: {C_all.shape[1]} points = {T_WINDOW} h (t = 24..72)")
print(f"T_ref = {T_REF_C} °C, water-T uncertainty SD = {T_SD_C} °C, clip guard {CLIP_LO} m/day")
print(f"ageing stress (central) = {ALPHA_ZONE}")

# Activation energies are drawn from normals TRUNCATED at EA_MIN rather than clipped, so no
# draw can be non-physical and no probability mass piles up on the bound.
rng = np.random.default_rng(DRAW_SEED)


def draw_truncated_ea(mean, sd, n):
    a = (EA_MIN - mean) / sd
    return truncnorm.rvs(a, np.inf, loc=mean, scale=sd, size=n, random_state=rng)


ea_b = draw_truncated_ea(EA_BULK_MEAN, EA_BULK_SD, n_beh)
ea_w = draw_truncated_ea(EA_WALL_MEAN, EA_WALL_SD, n_beh)
dT = rng.normal(0.0, T_SD_C, n_beh)          # common random numbers across all scenarios

assert ea_b.min() >= EA_MIN and ea_w.min() >= EA_MIN, "non-physical activation energy drawn"
T_lo = min(s["T"] for s in SCENARIO_DEF.values()) + float(dT.min())
T_hi = max(s["T"] for s in SCENARIO_DEF.values()) + float(dT.max())
assert T_VALID_C[0] <= T_lo and T_hi <= T_VALID_C[1], (
    f"sampled water temperature {T_lo:.2f}–{T_hi:.2f} °C leaves the stated "
    f"{T_VALID_C[0]}–{T_VALID_C[1]} °C validity range")
print(f"Ea draws (kJ/mol): bulk {ea_b.min()/1000:.1f}–{ea_b.max()/1000:.1f}, "
      f"wall {ea_w.min()/1000:.1f}–{ea_w.max()/1000:.1f} (truncated at {EA_MIN/1000:.0f})")
print(f"sampled water temperature spans {T_lo:.2f}–{T_hi:.2f} °C, "
      f"inside the {T_VALID_C[0]}–{T_VALID_C[1]} °C validity range")

wn0 = wntr.network.WaterNetworkModel(B.PRACTICE_INP)
DEMAND = base_demand_L_s(wn0, ALL_NODES)
CONSEQUENCE, q1, q2 = consequence_from_demand(DEMAND)
DEM = DEMAND.values
DEM_TOT = float(DEM.sum())
print(f"consequence terciles (L/s): {q1:.2f}, {q2:.2f}; total demand {DEM_TOT:.1f} L/s "
      f"over {int((DEM > 0).sum())} consumer nodes\n")


def risk_bands_for(P):
    scores = np.array([likelihood_band(float(p)) * int(CONSEQUENCE[n])
                       for n, p in zip(ALL_NODES, P)])
    return np.array([risk_band(int(s)) for s in scores]), scores


# ============================== scenarios ==============================
t_all = time.time()
results = {}
clip_log = {}
for key, spec in SCENARIO_DEF.items():
    print(f"=== {spec['label']} ===")
    C, kb_used, kw_used, n_clip = run_ensemble(
        idx, S_old, S_avg, S_new, ea_b, ea_w, dT,
        T_mean=spec["T"], alpha=spec["alpha"], inlet=B.INLET_CHLORINE_MGL, nodes=ALL_NODES)
    met = metrics_from_C(C, w, T_WINDOW)
    results[key] = {**met, "label": spec["label"], "T": spec["T"], "C": C,
                    "kb_mean": float(w @ kb_used),
                    "kw_old_mean": float(w @ kw_used["old"]),
                    "kw_avg_mean": float(w @ kw_used["average"]),
                    "kw_new_mean": float(w @ kw_used["new"])}
    clip_log[key] = n_clip
    at = met["P_min"] > 0.5
    print(f"  weighted mean kb {results[key]['kb_mean']:.3f} /day | "
          f"kw_old {results[key]['kw_old_mean']:.3f} m/day | clipped {n_clip}")
    print(f"  P_min>0.5 nodes {int(at.sum())} | demand at risk {DEM[at].sum():.1f} L/s\n")

# ratio check: scenario D vs C wall coefficient must equal alpha_old once the guard is inert
ratio_DC = results["D_heat_age"]["kw_old_mean"] / results["C_heatwave"]["kw_old_mean"]
print(f"verification  mean kw_old(D)/mean kw_old(C) = {ratio_DC:.4f}  "
      f"(alpha_old = {ALPHA_ZONE['old']:.2f})")
assert sum(clip_log.values()) == 0, f"clip guard active: {clip_log}"
assert abs(ratio_DC - ALPHA_ZONE["old"]) < 1e-6, "ageing multiplier not applied cleanly"
print("clip guard inert in every scenario (0 clipped draws)\n")

# reference row at exactly T_ref (cached forward runs) for continuity with Steps 1-11
ref = metrics_from_C(C_all[idx], w, T_WINDOW)

# ---- ageing-stress sensitivity: is scenario D driven by alpha_old = 1.85? ----
print("=== ageing-stress sensitivity (mild / central / severe) ===")
alpha_rows = []
for name, alpha in ALPHA_SETS.items():
    if name == "central":
        met = results["D_heat_age"]
    else:
        C_a, _, kwa, n_clip = run_ensemble(idx, S_old, S_avg, S_new, ea_b, ea_w, dT,
                                           T_mean=20.0, alpha=alpha,
                                           inlet=B.INLET_CHLORINE_MGL, nodes=ALL_NODES,
                                           quiet=True)
        assert n_clip == 0, f"clip guard active in ageing sensitivity ({name})"
        met = metrics_from_C(C_a, w, T_WINDOW)
        del C_a
    P = met["P_min"]
    at = P > 0.5
    bands, _ = risk_bands_for(P)
    alpha_rows.append({
        "ageing_set": name, "alpha_avg": alpha["average"], "alpha_old": alpha["old"],
        "P_min_gt_0.5_nodes": int(at.sum()),
        "demand_at_risk_L_s": round(float(DEM[at].sum()), 1),
        "high_or_very_high": int(np.isin(bands, ["high", "very high"]).sum()),
        "indeterminate": int(((P > 0.05) & (P < 0.95)).sum()),
        "net_mean_E_duration_h": round(float(met["Dbar"].mean()), 3),
        "net_mean_E_deficit": round(float(met["Abar"].mean()), 3),
    })
    print(f"  {name:>7}: P_min>0.5 {int(at.sum()):3d} | demand {DEM[at].sum():5.1f} L/s "
          f"| high/v-high {int(np.isin(bands, ['high', 'very high']).sum()):2d} "
          f"| indeterminate {int(((P > 0.05) & (P < 0.95)).sum()):2d} "
          f"| mean E[A] {met['Abar'].mean():.3f}")
print()

# ============================== corrective dosing ==============================
# Inlet dose scales BOTH reservoir source quality and tank initial quality, so the whole
# source regime is raised consistently. Leaving tanks at their un-dosed initial value would
# confound the result with a fixed boundary condition.
print("=== corrective dosing under heatwave (control-measure evaluation) ===")
SUB_STRIDE = 8
sub = np.arange(0, n_beh, SUB_STRIDE)
w_sub = w_raw[idx][sub] / w_raw[idx][sub].sum()
dose_results = {}
dose_C_sub = {}          # short-horizon trajectories of the SAME subset, for the paired test
for dose in DOSES:
    print(f"  inlet {dose:.2f} mg/L (tank initial {B.TANK_INIT_MGL * dose:.2f} mg/L)")
    if abs(dose - 1.0) < 1e-12:
        met = {k: results["C_heatwave"][k] for k in ("P_min", "P_bar", "Dbar", "Abar", "M")}
        dose_C_sub[dose] = results["C_heatwave"]["C"][sub].copy()
    else:
        C_d, _, _, n_clip = run_ensemble(idx, S_old, S_avg, S_new, ea_b, ea_w, dT,
                                         T_mean=20.0, alpha=ALPHA_NONE, inlet=dose,
                                         nodes=ALL_NODES, tank_mgl=B.TANK_INIT_MGL * dose,
                                         quiet=True)
        assert n_clip == 0
        met = metrics_from_C(C_d, w, T_WINDOW)
        dose_C_sub[dose] = C_d[sub].copy()
        del C_d
    dose_results[dose] = met

# linearity known-answer check: with all sources scaled, first-order kinetics give C ∝ dose
m0 = int(np.argmax(w))
C1, _, _, _ = run_ensemble(idx, S_old, S_avg, S_new, ea_b, ea_w, dT, T_mean=20.0,
                           alpha=ALPHA_NONE, inlet=1.0, nodes=ALL_NODES,
                           tank_mgl=B.TANK_INIT_MGL, members=[m0], quiet=True)
C13, _, _, _ = run_ensemble(idx, S_old, S_avg, S_new, ea_b, ea_w, dT, T_mean=20.0,
                            alpha=ALPHA_NONE, inlet=1.3, nodes=ALL_NODES,
                            tank_mgl=B.TANK_INIT_MGL * 1.3, members=[m0], quiet=True)
lin_err = float(np.max(np.abs(C13 - 1.3 * C1)))
print(f"  linearity check max|C(1.3) - 1.3*C(1.0)| = {lin_err:.2e} mg/L "
      "(first-order kinetics scale with the source regime)")

# Paired warm-up test: IDENTICAL members, weights and scenario draws; only the simulation
# horizon changes, so any difference is attributable to warm-up length alone.
LONG_DUR, LONG_WARM = 168, 120
paired_rows = []
print(f"  paired warm-up test on {len(sub)} identical members "
      f"({B.DURATION_H} h / {B.WARMUP_H} h warm-up  vs  {LONG_DUR} h / {LONG_WARM} h)")
for dose in DOSES:
    met_s = metrics_from_C(dose_C_sub[dose], w_sub, T_WINDOW)
    C_l, _, _, n_clip = run_ensemble(idx, S_old, S_avg, S_new, ea_b, ea_w, dT, T_mean=20.0,
                                     alpha=ALPHA_NONE, inlet=dose, nodes=ALL_NODES,
                                     tank_mgl=B.TANK_INIT_MGL * dose, duration_h=LONG_DUR,
                                     warmup_h=LONG_WARM, members=sub, quiet=True)
    assert n_clip == 0
    met_l = metrics_from_C(C_l, w_sub, LONG_DUR - LONG_WARM)
    del C_l
    at_s, at_l = met_s["P_min"] > 0.5, met_l["P_min"] > 0.5
    paired_rows.append({
        "inlet_dose_mgl": dose,
        "short_P_min_gt_0.5_nodes": int(at_s.sum()),
        "long_P_min_gt_0.5_nodes": int(at_l.sum()),
        "short_demand_at_risk_L_s": round(float(DEM[at_s].sum()), 1),
        "long_demand_at_risk_L_s": round(float(DEM[at_l].sum()), 1),
        "short_net_mean_E_duration_h": round(float(met_s["Dbar"].mean()), 3),
        "long_net_mean_E_duration_h": round(float(met_l["Dbar"].mean()), 3),
        "short_net_mean_E_deficit": round(float(met_s["Abar"].mean()), 4),
        "long_net_mean_E_deficit": round(float(met_l["Abar"].mean()), 4),
    })
del dose_C_sub
print(f"\ntotal runtime {time.time() - t_all:.1f}s\n")

# ============================== tables ==============================
summary_rows = []
for key, r in results.items():
    P = r["P_min"]
    bands, _ = risk_bands_for(P)
    at = P > 0.5
    summary_rows.append({
        "scenario": r["label"],
        "mean_kb": round(r["kb_mean"], 3),
        "mean_kw_old": round(r["kw_old_mean"], 3),
        "P_min_gt_0.5_nodes": int(at.sum()),
        "demand_at_risk_L_s": round(float(DEM[at].sum()), 1),
        "pct_demand_at_risk": round(100 * float(DEM[at].sum()) / DEM_TOT, 1),
        "high_or_very_high": int(np.isin(bands, ["high", "very high"]).sum()),
        "indeterminate": int(((P > 0.05) & (P < 0.95)).sum()),
        "net_mean_P_bar": round(float(r["P_bar"].mean()), 4),
        "net_mean_E_duration_h": round(float(r["Dbar"].mean()), 3),
        "net_mean_E_deficit": round(float(r["Abar"].mean()), 4),
    })
summary_df = pd.DataFrame(summary_rows)
print("Scenario risk summary (GLUE behavioural ensemble; network means are unweighted "
      "arithmetic means over all 92 junctions):\n")
print(summary_df.to_string(index=False))
print(f"\nreference (T = T_ref exactly, cached): P_min>0.5 nodes "
      f"{int((ref['P_min'] > 0.5).sum())}, demand at risk "
      f"{DEM[ref['P_min'] > 0.5].sum():.1f} L/s, net-mean E[A] {ref['Abar'].mean():.4f}")

dose_rows = []
base_at = results["A_baseline"]["P_min"] > 0.5
base_at_risk = float(DEM[base_at].sum())
for dose, met in dose_results.items():
    at = met["P_min"] > 0.5
    dose_rows.append({
        "inlet_dose_mgl": dose,
        "P_min_gt_0.5_nodes": int(at.sum()),
        "demand_at_risk_L_s": round(float(DEM[at].sum()), 1),
        "pct_demand_at_risk": round(100 * float(DEM[at].sum()) / DEM_TOT, 1),
        "net_mean_P_min": round(float(met["P_min"].mean()), 4),
        "net_mean_E_duration_h": round(float(met["Dbar"].mean()), 3),
        "net_mean_E_deficit": round(float(met["Abar"].mean()), 4),
        "median_over_nodes_of_mean_window_min_mgl": round(float(np.median(w @ met["M"])), 3),
    })
dose_df = pd.DataFrame(dose_rows)
print(f"\nBaseline (12 °C, 1.0 mg/L) demand at risk: {base_at_risk:.1f} L/s")
print("Heatwave dosing evaluation (reservoir AND tank source quality scaled):\n")
print(dose_df.to_string(index=False))
restored = dose_df["demand_at_risk_L_s"].min() <= base_at_risk + 1e-9
print(f"\nsource dosing alone {'restores' if restored else 'does NOT restore'} the "
      "pre-heatwave demand-at-risk position (control-measure evaluation, not a "
      "dosing recommendation).")
print(f"\nPaired warm-up test — identical {len(sub)} members, weights and draws; "
      "only the horizon differs:\n")
print(pd.DataFrame(paired_rows).to_string(index=False))

# ---- escalation and ageing increment ----
P_A = results["A_baseline"]["P_min"]
P_C = results["C_heatwave"]["P_min"]
P_D = results["D_heat_age"]["P_min"]
dP_age = P_D - P_C
bands_A, _ = risk_bands_for(P_A)
bands_D, _ = risk_bands_for(P_D)

esc = np.where((bands_A != bands_D) & (DEM > 0))[0]
esc = esc[np.argsort(-DEM[esc])]
esc_rows = [{
    "node": ALL_NODES[j],
    "P_min_baseline": round(float(P_A[j]), 3),
    "P_min_heatwave": round(float(P_C[j]), 3),
    "P_min_heat_ageing": round(float(P_D[j]), 3),
    "dP_ageing": round(float(dP_age[j]), 3),
    "demand_L_s": round(float(DEM[j]), 2),
    "band_current": bands_A[j],
    "band_heat_ageing": bands_D[j],
    "monitored": ALL_NODES[j] in B.MONITOR_NODES,
} for j in esc]
esc_df = pd.DataFrame(esc_rows)
esc_demand = float(esc_df["demand_L_s"].sum()) if len(esc_df) else 0.0
print(f"\n{len(esc_df)} consumer junctions change risk band A -> D; demand {esc_demand:.1f} L/s "
      f"({100 * esc_demand / DEM_TOT:.0f}% of network)\n")
if len(esc_df):
    print(esc_df.head(12).to_string(index=False))

# ---- risk register ----
unc = P_A * (1.0 - P_A)
prio_raw = CONSEQUENCE.values * unc
prio = np.where(DEM > 0, prio_raw / (prio_raw.max() + 1e-12), 0.0)

register = pd.DataFrame([{
    "node": n,
    "P_min_current": round(float(P_A[j]), 3),
    "P_min_heatwave": round(float(P_C[j]), 3),
    "P_min_heat_ageing": round(float(P_D[j]), 3),
    "P_bar_current": round(float(results["A_baseline"]["P_bar"][j]), 3),
    "E_duration_current_h": round(float(results["A_baseline"]["Dbar"][j]), 2),
    "E_deficit_current_mgL_h": round(float(results["A_baseline"]["Abar"][j]), 3),
    "demand_L_s": round(float(DEM[j]), 2),
    "likelihood": LIK_LABEL[likelihood_band(float(P_A[j]))],
    "consequence": CONS_LABEL[int(CONSEQUENCE[n])],
    "risk_score": int(likelihood_band(float(P_A[j])) * int(CONSEQUENCE[n])),
    "risk_band_current": bands_A[j],
    "risk_band_heat_ageing": bands_D[j],
    "escalates_under_heat": bool(bands_A[j] != bands_D[j]),
    "monitored": n in B.MONITOR_NODES,
    "sampling_priority": round(float(prio[j]), 3),
    "control_measure": CONTROL.get(bands_A[j], "Not applicable"),
} for j, n in enumerate(ALL_NODES)])
register = register.sort_values(["risk_score", "P_min_current"], ascending=False)
reg_path = os.path.join(CACHEDIR, "step12_risk_register.csv")
register.to_csv(reg_path, index=False)
print(f"\nrisk register -> {reg_path} ({len(register)} rows)")

# ============================== figures ==============================
fig, axes = plt.subplots(2, 2, figsize=(12.5, 10))
for ax, key in zip(axes.ravel(), ["A_baseline", "B_warm", "C_heatwave", "D_heat_age"]):
    draw_network_background(ax, wn0)
    sc = scatter_nodes(ax, wn0, ALL_NODES, results[key]["P_min"], 0.0, 1.0, cmap="inferno")
    mark_monitors(ax, wn0)
    ax.set_title(results[key]["label"])
    ax.set_aspect("equal")
    ax.axis("off")
fig.colorbar(sc, ax=axes.ravel().tolist(), shrink=0.85,
             label=r"$P_{\min}$: P(min C over 24–72 h < 0.2 mg/L)")
fig.suptitle("Step 12 — GLUE-propagated window-breach probability under temperature "
             "and ageing-stress scenarios", y=0.98)
fig.savefig(os.path.join(FIGDIR, "step12_scenario_maps.png"), dpi=140, bbox_inches="tight")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.5, 7))
draw_network_background(ax, wn0)
lim = max(float(np.max(np.abs(dP_age))), 0.05)
sc = scatter_nodes(ax, wn0, ALL_NODES, dP_age, -lim, lim, cmap="coolwarm")
mark_monitors(ax, wn0)
for j in np.argsort(-dP_age)[:8]:
    x, y = wn0.get_node(ALL_NODES[j]).coordinates
    ax.annotate(ALL_NODES[j], (x, y), textcoords="offset points", xytext=(4, 4),
                fontsize=7, color="0.15")
ax.set_aspect("equal")
ax.axis("off")
fig.colorbar(sc, ax=ax, shrink=0.85, label=r"$\Delta P_{\min}$ = P(D) − P(C)")
ax.set_title("Ageing-reactivity increment at 20 °C\n"
             "(extra window-breach probability from the illustrative zone multipliers)")
ax.legend(loc="lower left", fontsize=8)
fig.savefig(os.path.join(FIGDIR, "step12_ageing_delta.png"), dpi=140, bbox_inches="tight")
plt.close(fig)

fig, axes = plt.subplots(1, 3, figsize=(16.5, 4.6))
labs = [r["scenario"].split(". ", 1)[-1] for r in summary_rows]
x = np.arange(len(labs))
axes[0].bar(x - 0.18, [r["P_min_gt_0.5_nodes"] for r in summary_rows], 0.36,
            color="firebrick", label=r"nodes $P_{\min}>0.5$")
axes[0].set_ylabel(r"junctions with $P_{\min}>0.5$")
ax0b = axes[0].twinx()
ax0b.plot(x + 0.18, [r["pct_demand_at_risk"] for r in summary_rows], "o-",
          color="steelblue", lw=2)
ax0b.set_ylabel("% of network demand at risk")
axes[0].set_xticks(x)
axes[0].set_xticklabels(labs, rotation=15, ha="right")
axes[0].set_title("(a) Scenario escalation")
axes[0].grid(alpha=0.3, axis="y")

axes[1].bar([f"{d:.2f}" for d in dose_df["inlet_dose_mgl"]],
            dose_df["demand_at_risk_L_s"], color="darkorange")
axes[1].axhline(base_at_risk, color="steelblue", ls="--", lw=1.5,
                label=f"baseline ({base_at_risk:.1f} L/s)")
ax1b = axes[1].twinx()
ax1b.plot([f"{d:.2f}" for d in dose_df["inlet_dose_mgl"]],
          dose_df["net_mean_E_deficit"], "s-", color="0.25", lw=1.8,
          label="mean E[A]")
ax1b.set_ylabel("network-mean E[A] (mg/L·h)")
axes[1].set_xlabel("heatwave inlet dose (mg/L)")
axes[1].set_ylabel("demand at risk (L/s)")
axes[1].set_title("(b) Control-measure evaluation")
axes[1].legend(fontsize=8, loc="lower left")
axes[1].grid(alpha=0.3, axis="y")

a_lab = [r["ageing_set"] for r in alpha_rows]
axes[2].bar(a_lab, [r["P_min_gt_0.5_nodes"] for r in alpha_rows], color="seagreen")
axes[2].axhline(summary_rows[2]["P_min_gt_0.5_nodes"], color="crimson", ls="--", lw=1.5,
                label="heatwave, no ageing")
for k, r in enumerate(alpha_rows):
    axes[2].annotate(f"α_old={r['alpha_old']:.2f}", (k, r["P_min_gt_0.5_nodes"]),
                     textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8)
axes[2].set_ylabel(r"junctions with $P_{\min}>0.5$")
axes[2].set_title("(c) Ageing-stress sensitivity")
axes[2].legend(fontsize=8)
axes[2].grid(alpha=0.3, axis="y")

fig.tight_layout()
fig.savefig(os.path.join(FIGDIR, "step12_summary.png"), dpi=140, bbox_inches="tight")
plt.close(fig)
print("figures -> figures/step12_{scenario_maps,ageing_delta,summary}.png")

# ============================== json ==============================
report = {
    "description": "Step 12 operational temperature/ageing scenario projection of the "
                   "three-zone GLUE ensemble",
    "threshold": B.RMSE_THR,
    "n_behavioural": int(n_beh),
    "C_CRIT": C_CRIT,
    "assessment_window_h": [B.WARMUP_H, B.DURATION_H],
    "T_window_intervals": int(T_WINDOW),
    "definitions": {
        "P_min": "sum_i w_i * 1[min_t C_i(t) < C_crit] over t = 24..72 h "
                 "(48-hour window minimum, NOT a 24-hour daily minimum)",
        "P_bar": "E[D]/T_window, the Step-10 time-averaged below-threshold probability",
        "E_duration_h": "weighted expected hours below C_crit, trapezoid over 48 intervals",
        "E_deficit": "weighted expected cumulative deficit, mg/L*h",
        "network_mean": "unweighted arithmetic mean over all 92 junctions",
        "indeterminate": "0.05 < P_min < 0.95",
        "demand_at_risk": "sum of base demand over junctions with P_min > 0.5 "
                          "(zero-demand nodes contribute 0)",
        "median_over_nodes_of_mean_window_min_mgl":
            "per junction take the GLUE-weighted mean of the per-member window minimum, "
            "then the median of those 92 node values (NOT a pooled member-node median)",
        "likelihood_bands_on_P_min": {
            "rare": "P_min < 0.05", "unlikely": "0.05 <= P_min < 0.20",
            "possible": "0.20 <= P_min < 0.50", "likely": "0.50 <= P_min < 0.80",
            "almost certain": "P_min >= 0.80"},
        "likelihood_scores": {"rare": 1, "unlikely": 2, "possible": 3, "likely": 4,
                              "almost certain": 5},
        "consequence_scores": {"non-consumer (base demand = 0)": 0,
                               "minor (0 < d <= tercile1)": 1,
                               "moderate (tercile1 < d <= tercile2)": 2,
                               "major (d > tercile2)": 3},
        "consequence_terciles": "1/3 and 2/3 quantiles of base demand over the 59 junctions "
                                "with non-zero base demand (Net3 CFS x 1000 -> L/s)",
        "risk_score": "likelihood score x consequence score, range 0-15",
        "risk_band_mapping": {"not applicable": "score = 0", "low": "1 <= score <= 3",
                              "medium": "4 <= score <= 6", "high": "7 <= score <= 9",
                              "very high": "score >= 10"},
        "sampling_priority": "consequence SCORE (0-3, not raw demand) x P_min(1 - P_min), "
                             "normalised by its maximum; forced to 0 at zero-demand nodes",
    },
    "uncertainty_sources": {
        "kinetics": "GLUE behavioural ensemble (1126 members, weights at threshold 0.107)",
        "Ea_bulk_J_per_mol": {"mean": EA_BULK_MEAN, "sd": EA_BULK_SD},
        "Ea_wall_J_per_mol": {"mean": EA_WALL_MEAN, "sd": EA_WALL_SD},
        "water_temperature_C": f"dT ~ N(0, {T_SD_C}^2) added to the scenario mean",
        "common_random_numbers": True,
    },
    "T_ref_C": T_REF_C,
    "clip_guard_m_per_day": CLIP_LO,
    "clipped_draws_per_scenario": clip_log,
    "kw_old_ratio_D_over_C": round(float(ratio_DC), 6),
    "ageing_alphas_illustrative": ALPHA_SETS,
    "ageing_sensitivity": alpha_rows,
    "sigma_convention": "observation sigma = 0.1 mg/L is one standard deviation",
    "product_statement": (
        "GLUE calibration-conditioned scenario projection from the network model; not a "
        "sensor nowcast, not a spatial measurement, and not a statement that water is safe"
    ),
    "consequence_terciles_L_s": [q1, q2],
    "scenario_summary": summary_rows,
    "reference_at_T_ref_exact": {
        "P_min_gt_0.5_nodes": int((ref["P_min"] > 0.5).sum()),
        "demand_at_risk_L_s": round(float(DEM[ref["P_min"] > 0.5].sum()), 1),
        "net_mean_E_deficit": round(float(ref["Abar"].mean()), 4),
    },
    "dosing_heatwave": dose_rows,
    "dosing_boundary": "reservoir source quality AND tank initial quality both scaled by dose",
    "dosing_linearity_check": {
        "max_abs_err_mgL": lin_err,
        "conditions": "holds under fixed hydraulics and demands, first-order bulk and wall "
                      "kinetics, and proportional scaling of ALL source and initial chlorine "
                      "concentrations; a dose factor r is then equivalent to evaluating the "
                      "unscaled field against C_crit / r",
    },
    "dosing_paired_warmup_test": {
        "design": "identical member subset, weights and scenario draws; only the simulation "
                  "horizon differs, so the contrast isolates warm-up length",
        "short": {"duration_h": B.DURATION_H, "warmup_h": B.WARMUP_H},
        "long": {"duration_h": LONG_DUR, "warmup_h": LONG_WARM},
        "n_members": int(len(sub)), "subset_stride": SUB_STRIDE, "rows": paired_rows,
    },
    "baseline_demand_at_risk_L_s": base_at_risk,
    "dosing_restores_baseline": bool(restored),
    "n_escalating_consumer_nodes": int(len(esc_df)),
    "escalating_demand_L_s": esc_demand,
    "top_escalating": esc_rows[:15],
    "top_ageing_delta": [
        {"node": ALL_NODES[j], "dP_min": round(float(dP_age[j]), 3),
         "P_C": round(float(P_C[j]), 3), "P_D": round(float(P_D[j]), 3),
         "demand_L_s": round(float(DEM[j]), 2)}
        for j in np.argsort(-dP_age)[:10]
    ],
    "review_triggers": [
        "sensor QA failure / reference-check disagreement / sensor service",
        "hydraulic model or demand allocation revised",
        "source/treatment regime changes inlet chlorine",
        "water temperature moves outside the 8-24 degC scenario range",
        "forecast heat episode (switch to the scenario-D register; pre-authorise response)",
        "mains rehabilitation or burst altering the assumed age profile",
        "calibration record exceeds its approved age",
    ],
    "runtime_s": round(time.time() - t_all, 1),
}
with open(os.path.join(CACHEDIR, "step12_scenarios.json"), "w") as f:
    json.dump(report, f, indent=2)
print("json -> baseline_cache/step12_scenarios.json")
print("\nDONE Step 12")
