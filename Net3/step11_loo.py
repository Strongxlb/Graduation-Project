"""Step 11: leave-one-monitor-out (LOO) validation.

Predictive cross-validation the draft lacked. For each of the six monitors in turn: calibrate GLUE on
the OTHER five, then (a) check whether the three k_w estimates stay stable, and (b) predict the
held-out monitor's chlorine and measure the out-of-sample prediction error and 90% predictive-band
coverage. Reuses the cached candidate predictions (no EPANET); 30 noise realisations, median [IQR].

  held-out prediction RMSE  = sqrt(mean_t (pred_mean_m(t) − obs_m(t))²)   compared with the noise floor σ
  90% predictive band       = pred_mean ± 1.645·sqrt(Var_ensemble + σ²)   (parameter + observation noise)
  coverage                  = fraction of held-out hours inside the 90% band
"""
import os
import json
import numpy as np
import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figures")
ZKEYS = ["old", "average", "new"]
TRUE = {"old": B.KW_OLD_TRUE, "average": B.KW_AVG_TRUE, "new": B.KW_NEW_TRUE}
ZONE_OF = {"107": "new", "113": "new", "15": "old", "145": "old", "209": "average", "231": "average"}
sigma = B.SIGMA_OBS

cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
C_all = cache["C_all"].astype(np.float64)
mon_pos = list(cache["mon_pos"])
truth_full = cache["truth_all"][:, mon_pos]               # (73, 6)
S = {"old": cache["S_old"], "average": cache["S_avg"], "new": cache["S_new"]}
C_mon = C_all[:, :, mon_pos]                              # (2000, 49, 6)
NMON = len(B.MONITOR_NODES)
Z = 1.645


def thr_for(nmon):
    return sigma * (1.0 + Z / np.sqrt(2.0 * nmon * C_mon.shape[1]))


def calibrate(obs, cols):
    rmse = np.sqrt(((C_mon[:, :, cols] - obs[:, cols][None]) ** 2).mean(axis=(1, 2)))
    w = np.exp(-0.5 * (rmse / sigma) ** 2) * (rmse < thr_for(len(cols)))
    if w.sum() == 0:
        return None
    return w / w.sum()


def q(a):
    return float(np.median(a)), float(np.percentile(a, 25)), float(np.percentile(a, 75))


SEEDS = list(range(42, 72))
all_cols = list(range(NMON))

# ---- full-6-monitor reference (median over noise) ----
full = {z: [] for z in ZKEYS}
for seed in SEEDS:
    rng = np.random.default_rng(seed)
    obs = np.clip(truth_full + rng.normal(0, sigma, truth_full.shape), 0, None)[B.WARMUP_H:]
    w = calibrate(obs, all_cols)
    for z in ZKEYS:
        full[z].append(float(w @ S[z]))
print("=== Step 11: leave-one-monitor-out validation (30 noise, median) ===")
print(f"full-6 reference: old {np.median(full['old']):.3f}  avg {np.median(full['average']):.3f}  "
      f"new {np.median(full['new']):.3f}\n")

print(f"{'held-out':>12} | {'k_old':>7} {'k_avg':>7} {'k_new':>7} | {'pred RMSE@m':>11} | {'90% cov':>7}")
report = {"sigma": sigma, "noise_floor": sigma, "full6": {z: float(np.median(full[z])) for z in ZKEYS},
          "rows": []}
example = {}
for m in range(NMON):
    node = B.MONITOR_NODES[m]
    cols = [c for c in all_cols if c != m]
    kw = {z: [] for z in ZKEYS}
    pred_rmse, cover = [], []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        obs = np.clip(truth_full + rng.normal(0, sigma, truth_full.shape), 0, None)[B.WARMUP_H:]
        w = calibrate(obs, cols)
        if w is None:
            continue
        for z in ZKEYS:
            kw[z].append(float(w @ S[z]))
        pm = w @ C_mon[:, :, m]                                   # predicted mean trajectory at held-out m
        pv = w @ (C_mon[:, :, m] - pm[None]) ** 2                 # ensemble variance
        psd = np.sqrt(pv + sigma ** 2)                            # + observation noise
        lo, hi = pm - Z * psd, pm + Z * psd
        o = obs[:, m]
        pred_rmse.append(float(np.sqrt(((pm - o) ** 2).mean())))
        cover.append(float(((o >= lo) & (o <= hi)).mean()))
        if seed == 42:
            example[node] = {"t": np.arange(B.WARMUP_H, B.DURATION_H + 1), "pm": pm, "lo": lo, "hi": hi, "obs": o}
    row = {"node": node, "zone": ZONE_OF[node],
           "k_old": q(kw["old"]), "k_avg": q(kw["average"]), "k_new": q(kw["new"]),
           "pred_rmse": q(pred_rmse), "coverage90": q(cover)}
    report["rows"].append(row)
    print(f"{node+' ('+ZONE_OF[node]+')':>12} | {row['k_old'][0]:7.3f} {row['k_avg'][0]:7.3f} "
          f"{row['k_new'][0]:7.3f} | {row['pred_rmse'][0]:11.3f} | {row['coverage90'][0]:6.2f}")

print(f"\nnoise floor σ = {sigma}; pred RMSE ≈ σ ⇒ the held-out monitor is predicted as well as noise allows")
with open(os.path.join(HERE, "baseline_cache", "step11_loo.json"), "w") as f:
    json.dump(report, f, indent=2, default=lambda o: o.tolist() if isinstance(o, np.ndarray) else float(o))
print("saved step11_loo.json")

# ---- figure ----
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.5, 4.8))

nodes = [r["node"] for r in report["rows"]]
rmses = [r["pred_rmse"][0] for r in report["rows"]]
errlo = [r["pred_rmse"][0] - r["pred_rmse"][1] for r in report["rows"]]
errhi = [r["pred_rmse"][2] - r["pred_rmse"][0] for r in report["rows"]]
cols = ["firebrick" if ZONE_OF[n] == "old" else ("goldenrod" if ZONE_OF[n] == "average" else "steelblue")
        for n in nodes]
axA.bar([f"{n}\n({ZONE_OF[n]})" for n in nodes], rmses, yerr=[errlo, errhi], color=cols, capsize=3,
        error_kw={"ecolor": "0.3"})
axA.axhline(sigma, color="k", ls="--", lw=1.3, label=f"noise floor σ = {sigma}")
axA.set_ylabel("held-out prediction RMSE (mg/L)")
axA.set_title("(a) LOO out-of-sample prediction error vs noise floor\n(median; bars = IQR over 30 noise)")
axA.legend(fontsize=8)
axA.grid(alpha=0.3, axis="y")

ex = example.get("15", example[nodes[0]])
node_ex = "15" if "15" in example else nodes[0]
axB.fill_between(ex["t"], np.clip(ex["lo"], 0, None), ex["hi"], color="steelblue", alpha=0.25,
                 label="90% predictive band")
axB.plot(ex["t"], ex["pm"], color="steelblue", lw=2, label="predicted mean (held out)")
axB.plot(ex["t"], ex["obs"], "o", color="crimson", ms=3, label=f"held-out obs (node {node_ex})")
axB.set_xlabel("time (h)")
axB.set_ylabel("chlorine (mg/L)")
axB.set_title(f"(b) Predicting held-out monitor {node_ex} from the other five")
axB.legend(fontsize=8)
axB.grid(alpha=0.3)

plt.tight_layout()
figpath = os.path.join(FIGDIR, "step11_loo.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")
print("figure saved to", figpath)
