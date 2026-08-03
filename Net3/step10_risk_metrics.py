"""Step 10: operational risk metrics (duration + depth) and water-age corroboration.

A single probability P(C < C_MIN) conflates *how long* and *how far below* the threshold a node sits.
We therefore report, from the behavioural ensemble (weights recomputed at the primary threshold
0.107): the original probability re-expressed as a duration, two genuine severity metrics (minimum
concentration and cumulative deficit), and one reaction-independent hydraulic diagnostic (water age).

IMPORTANT — time axis: the post-warm-up record is t = 24, 25, ..., 72 h = 49 reporting points but
only 48 one-hour intervals. Durations and cumulative deficits are therefore trapezoidally integrated
over the 48 intervals (max duration = 48 h), not summed over 49 points.

Per behavioural member i and node n:
    D_{i,n} = ∫ 1[C<C_MIN] dt        (below-threshold duration, trapezoid, h)
    A_{i,n} = ∫ max(0, C_MIN−C) dt   (cumulative deficit, trapezoid, mg/L·h)
    M_{i,n} = min_t C_{i,n}(t)        (minimum concentration; per-member min, then weighted — Method A)
Reported as weighted expectation AND weighted 5/50/95 % quantiles across the ensemble.
"""
import os
import json
import numpy as np
from scipy.stats import spearmanr, pearsonr
import wntr
import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figures")
C_MIN = 0.2

cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
C_all = cache["C_all"].astype(np.float64)                 # (2000, 49, 92)
ALL_NODES = list(cache["all_nodes"])
RMSE = cache["RMSE"]
sigma = B.SIGMA_OBS
n_t = C_all.shape[1]                                       # 49 reporting points
T_WINDOW = n_t - 1                                         # 48 one-hour intervals

w = np.exp(-0.5 * (RMSE / sigma) ** 2) * (RMSE < B.RMSE_THR)
w = w / w.sum()
print(f"behavioural set at threshold {B.RMSE_THR}: {(RMSE < B.RMSE_THR).sum()}/{len(RMSE)}")
print(f"time window: {n_t} reporting points = {T_WINDOW} h (24->72)")

# ---- per-member metrics (trapezoidal over 48 intervals) ----
trapz = getattr(np, "trapezoid", getattr(np, "trapz", None))
below = (C_all < C_MIN).astype(np.float64)
D = trapz(below, dx=1.0, axis=1)                           # (2000, 92) hours below, max 48
deficit = np.maximum(0.0, C_MIN - C_all)
A = trapz(deficit, dx=1.0, axis=1)                         # (2000, 92) mg/L·h
M = C_all.min(axis=1)                                      # (2000, 92) per-member minimum

Dbar = w @ D                                               # expected duration
Abar = w @ A                                               # expected cumulative deficit
Mbar = w @ M
frac = Dbar / T_WINDOW                                     # = original time-averaged P(C<C_MIN)


def wquantile(vals, weights, qs):
    o = np.argsort(vals)
    v, cw = vals[o], np.cumsum(weights[o])
    cw = (cw - 0.5 * weights[o]) / weights.sum()           # Hazen plotting positions
    return [float(np.interp(q, cw, v)) for q in qs]


# ---- water age (reaction-independent) with time-window diagnostics ----
wn = wntr.network.WaterNetworkModel(B.PRACTICE_INP)
wn.options.time.duration = B.DURATION_H * 3600
wn.options.time.hydraulic_timestep = B.HYDRAULIC_TIMESTEP_S
wn.options.time.report_timestep = B.REPORT_TIMESTEP_S
wn.options.time.quality_timestep = B.QUALITY_TIMESTEP_S
wn.options.quality.parameter = "AGE"
age_df = wntr.sim.EpanetSimulator(wn).run_sim().node["quality"][ALL_NODES] / 3600.0   # (73, 92) hours
age_full = age_df.values                                   # 0..72
age_post = age_full[B.WARMUP_H:]                           # 24..72 (49 rows)
mean_age_post = age_post.mean(axis=0)                      # post-warm-up mean (primary)
mean_age_last24 = age_full[B.DURATION_H - 24:].mean(axis=0)  # last diurnal cycle (48..72)
final_age = age_full[-1]                                   # steady-ish final hour (t=72)

print("\nwater-age window diagnostics for the leading nodes:")
print(f"{'node':>5} | {'t=24':>6} {'t=48':>6} {'t=72':>6} | {'mean24-72':>9} {'mean48-72':>9}")
for node in ["243", "131", "166", "141"]:
    j = ALL_NODES.index(node)
    print(f"{node:>5} | {age_full[24, j]:6.1f} {age_full[48, j]:6.1f} {age_full[72, j]:6.1f} | "
          f"{mean_age_post[j]:9.1f} {mean_age_last24[j]:9.1f}")

# ---- correlations over all junctions (Spearman primary + bootstrap CI) ----
n_nodes = len(ALL_NODES)
rho_dur, p_dur = spearmanr(mean_age_post, Dbar)
rho_def, p_def = spearmanr(mean_age_post, Abar)
r_dur, _ = pearsonr(mean_age_post, Dbar)
rng = np.random.default_rng(0)
boot = []
for _ in range(2000):
    idx = rng.integers(0, n_nodes, n_nodes)
    boot.append(spearmanr(mean_age_post[idx], Dbar[idx]).statistic)
ci = (float(np.percentile(boot, 2.5)), float(np.percentile(boot, 97.5)))
print(f"\ncorrelation over all n={n_nodes} junctions (mean water age vs risk):")
print(f"  duration : Spearman {rho_dur:.2f} (p={p_dur:.1e}, boot95%[{ci[0]:.2f},{ci[1]:.2f}])  Pearson {r_dur:.2f}")
print(f"  deficit  : Spearman {rho_def:.2f} (p={p_def:.1e})")

# ---- top nodes by cumulative deficit, with 5-95% ensemble bands ----
order = np.argsort(Abar)[::-1]
print(f"\n=== top-10 risk nodes (ranked by expected cumulative deficit) ===")
print(f"{'node':>5} | {'dur E[5-95]':>18} | {'deficit E[5-95]':>20} | {'minC 50[5-95]':>18} | {'age':>5}")
top = []
for i in order[:10]:
    node = ALL_NODES[i]
    dq = wquantile(D[:, i], w, [0.05, 0.95])
    aq = wquantile(A[:, i], w, [0.05, 0.95])
    mq = wquantile(M[:, i], w, [0.05, 0.50, 0.95])
    top.append({"node": node, "dur_mean": float(Dbar[i]), "dur_5_95": dq,
                "deficit_mean": float(Abar[i]), "deficit_5_95": aq,
                "minC_5_50_95": mq, "frac": float(frac[i]), "mean_age_h": float(mean_age_post[i])})
    print(f"{node:>5} | {Dbar[i]:5.1f} [{dq[0]:4.1f},{dq[1]:4.1f}] | "
          f"{Abar[i]:5.2f} [{aq[0]:4.2f},{aq[1]:4.2f}] | {mq[1]:.3f}[{mq[0]:.2f},{mq[2]:.2f}] | {mean_age_post[i]:5.1f}")

report = {"C_MIN": C_MIN, "threshold": B.RMSE_THR, "T_window_h": T_WINDOW, "n_nodes": n_nodes,
          "corr": {"spearman_dur": float(rho_dur), "p_dur": float(p_dur), "boot95_dur": ci,
                   "pearson_dur": float(r_dur), "spearman_def": float(rho_def)},
          "age_windows_note": "primary = post-warm-up mean (24-72 h)",
          "top10": top}
with open(os.path.join(HERE, "baseline_cache", "step10_risk_metrics.json"), "w") as f:
    json.dump(report, f, indent=2)
print("\nsaved step10_risk_metrics.json")

# ---- figures ----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.5, 5))

top5 = set(ALL_NODES[i] for i in order[:5])
colors = ["crimson" if n in top5 else "steelblue" for n in ALL_NODES]
axA.scatter(mean_age_post, Dbar, c=colors, s=28, alpha=0.75)
for i in order[:5]:
    axA.annotate(ALL_NODES[i], (mean_age_post[i], Dbar[i]), textcoords="offset points",
                 xytext=(5, 4), fontsize=9, color="crimson")
axA.set_xlabel("mean water age (h), post-warm-up — reaction-independent")
axA.set_ylabel("expected hours below 0.2 mg/L (of 48 h)")
axA.set_title(f"(a) Risk associated with water age\nSpearman = {rho_dur:.2f} "
              f"(n={n_nodes}, boot95% [{ci[0]:.2f},{ci[1]:.2f}])")
axA.grid(alpha=0.3)

top10 = order[:10]
nodes10 = [ALL_NODES[i] for i in top10]
durs = [Dbar[i] for i in top10]
err = np.array([[Dbar[i] - wquantile(D[:, i], w, [0.05])[0] for i in top10],
                [wquantile(D[:, i], w, [0.95])[0] - Dbar[i] for i in top10]])
err = np.clip(err, 0, None)
axB.barh(range(len(top10)), durs, xerr=err, color="firebrick", capsize=3,
         error_kw={"ecolor": "0.3", "lw": 1})
axB.set_yticks(range(len(top10)))
axB.set_yticklabels(nodes10)
axB.invert_yaxis()
for k, i in enumerate(top10):
    axB.annotate(f"minC={Mbar[i]:.2f}, age={mean_age_post[i]:.0f}h",
                 (durs[k], k), textcoords="offset points", xytext=(6, 0),
                 va="center", fontsize=7.5, color="0.25")
axB.axvline(T_WINDOW, color="0.6", ls=":", lw=1)
axB.set_xlabel("expected hours below 0.2 mg/L (bars = 5-95% ensemble band)")
axB.set_title("(b) Top-10 nodes: expected duration (+5-95%), depth and age")
axB.grid(alpha=0.3, axis="x")
axB.set_xlim(0, T_WINDOW * 1.45)

plt.tight_layout()
figpath = os.path.join(FIGDIR, "step10_risk_metrics.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")
print("figure saved to", figpath)
