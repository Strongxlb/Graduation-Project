"""Step 8: systematic sensor-bias experiment (GLUE, empirical) — Priority-2 #1.

A constant offset (systematic bias) is added to ONE informative monitor (node 15, old zone) and
the GLUE calibration is re-run. We report how far the behavioural mean of the identifiable
coefficient (old) is pushed, relative to the random behavioural spread, and whether the effect is
concave (halving the offset keeps > 50% of the shift). The risk ranking is also checked.

Reuses the baseline cache (candidate predictions are observation-independent); the bias only
changes the observations, so no EPANET is re-run. Primary threshold 0.107, 30 noise realisations.
"""
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figures")
ZKEYS = ["old", "average", "new"]
TRUE = {"old": B.KW_OLD_TRUE, "average": B.KW_AVG_TRUE, "new": B.KW_NEW_TRUE}

cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
C_all = cache["C_all"]
ALL_NODES = list(cache["all_nodes"])
mon_pos = list(cache["mon_pos"])
truth_mon = cache["truth_all"][:, mon_pos]            # (73, 6)
S = {"old": cache["S_old"], "average": cache["S_avg"], "new": cache["S_new"]}
C_all_mon = C_all[:, :, mon_pos]
C_MIN = 0.2

BIAS_NODE = "15"                                       # informative old-zone monitor
bcol = B.MONITOR_NODES.index(BIAS_NODE)
OFFSETS = [0.0, 0.025, 0.05, 0.10]
N_NOISE = 30
SEEDS = list(range(42, 42 + N_NOISE))
thr = B.RMSE_THR                                       # 0.107


def glue_means(obs_post):
    rmse = np.sqrt(((C_all_mon - obs_post[None]) ** 2).mean(axis=(1, 2)))
    w = np.exp(-0.5 * (rmse / B.SIGMA_OBS) ** 2) * (rmse < thr)
    if w.sum() == 0:
        return None, None, None
    w = w / w.sum()
    means = {z: float(np.sum(w * S[z])) for z in ZKEYS}
    sds = {z: float(np.sqrt(np.sum(w * (S[z] - means[z]) ** 2))) for z in ZKEYS}
    below = (C_all < C_MIN)
    P = np.tensordot(w, below.astype(float), axes=(0, 0)).mean(axis=0)
    rank = [ALL_NODES[i] for i in np.argsort(P)[::-1][:6]]
    return means, sds, rank


def med(a):
    return float(np.median(a))


rows = []
base_old = None
for off in OFFSETS:
    old_means, old_sds, avg_means, new_means, ranks = [], [], [], [], []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        obs = truth_mon + rng.normal(0, B.SIGMA_OBS, truth_mon.shape)
        obs[:, bcol] += off                            # inject systematic bias at node 15
        obs = np.clip(obs, 0, None)[B.WARMUP_H:]
        means, sds, rank = glue_means(obs)
        if means is None:
            continue
        old_means.append(means["old"]); old_sds.append(sds["old"])
        avg_means.append(means["average"]); new_means.append(means["new"])
        ranks.append(tuple(rank))
    row = {"offset": off,
           "old_mean_med": med(old_means), "old_sd_med": med(old_sds),
           "avg_mean_med": med(avg_means), "new_mean_med": med(new_means),
           "risk_rank_mode": max(set(ranks), key=ranks.count)}
    rows.append(row)

base_old = rows[0]["old_mean_med"]
base_sd = rows[0]["old_sd_med"]
for r in rows:
    r["old_shift"] = r["old_mean_med"] - base_old
    r["shift_over_sd"] = r["old_shift"] / base_sd

print("=== Step 8: systematic bias at node 15 (old zone), threshold 0.107 ===")
print(f"baseline old behavioural SD (random spread) = {base_sd:.3f}\n")
print(f"{'offset':>7} | {'old mean':>9} | {'old shift':>10} | {'shift/SD':>9} | "
      f"{'avg mean':>9} | {'new mean':>9} | top-3 risk")
for r in rows:
    print(f"{r['offset']:>7} | {r['old_mean_med']:>9.3f} | {r['old_shift']:>+10.3f} | "
          f"{r['shift_over_sd']:>+9.2f} | {r['avg_mean_med']:>9.3f} | {r['new_mean_med']:>9.3f} | "
          f"{list(r['risk_rank_mode'][:3])}")

# concavity: does halving 0.05 -> 0.025 keep > 50% of the shift?
s025 = next(r["old_shift"] for r in rows if r["offset"] == 0.025)
s050 = next(r["old_shift"] for r in rows if r["offset"] == 0.05)
print(f"\nconcavity: shift(0.025)/shift(0.05) = {s025 / s050 * 100:.0f}%  "
      f"(50% would be linear; >50% = concave, halving the offset keeps most of the bias)")

report = {"bias_node": BIAS_NODE, "threshold": thr, "n_noise": N_NOISE,
          "baseline_old_sd": base_sd, "rows": rows,
          "concavity_shift025_over_shift050": s025 / s050}


def _jsafe(o):
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, tuple):
        return list(o)
    return str(o)


with open(os.path.join(HERE, "baseline_cache", "step8_sensor_bias.json"), "w") as f:
    json.dump(report, f, indent=2, default=_jsafe)

# ---- figure: old behavioural mean vs bias offset (± behavioural SD) ----
fig, ax = plt.subplots(figsize=(8, 5))
offs = [r["offset"] for r in rows]
means = [r["old_mean_med"] for r in rows]
sds = [r["old_sd_med"] for r in rows]
ax.errorbar(offs, means, yerr=sds, marker="o", capsize=4, color="steelblue",
            label="GLUE old mean ± behavioural SD")
ax.axhline(TRUE["old"], color="red", ls="--", lw=1.5, label="true k_w,old = -1.0")
ax.set_xlabel("systematic bias at node 15 (mg/L)")
ax.set_ylabel("GLUE behavioural mean of k_w,old (m/day)")
ax.set_title("Step 8 — a systematic sensor bias pushes the calibrated coefficient\n"
             "(only the coefficient that node informs; shift is super-linear/convex here)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
figpath = os.path.join(FIGDIR, "step8_sensor_bias.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")
print("figure saved to", figpath)
