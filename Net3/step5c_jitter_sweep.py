"""Step 5b (LOG): within-zone heterogeneity magnitude sweep -> precise-but-biased.

For jitter in {0.20, 0.35, 0.50}: truth has per-pipe k_w,p = zone_mean*(1+delta_p),
delta_p ~ U(-jitter, jitter) (seed 12345; jitter=0.20 reproduces Step 5a). The three-zone
HOMOGENEOUS model is calibrated against the (noisy) heterogeneous observations.

The homogeneous candidate predictions do NOT depend on the truth, so the 2000 GLUE candidate
predictions are reused from the frozen baseline cache (baseline.npz); only the observations
change with the truth. A 343-point grid (built here) gives the noise-free structural residual
and the grid best fit.

Because C = exp(k t) is convex in k, symmetric within-zone heterogeneity makes the true mean
concentration exceed the value at the arithmetic-mean k, so the best homogeneous coefficient is
pulled toward stronger decay: a precise fit but a biased coefficient, with the bias growing with
the heterogeneity magnitude.
"""
import os
import json
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import wntr

import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figures")

ZKEYS = ["old", "average", "new"]
ZONE_MEAN = {"old": B.KW_OLD_TRUE, "average": B.KW_AVG_TRUE, "new": B.KW_NEW_TRUE}
JITTER_SEED = 12345
JITTERS = [0.20, 0.35, 0.50]
C_MIN = 0.2

# reuse baseline GLUE candidate predictions (independent of the truth)
cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
C_all = cache["C_all"]                                   # (2000, 49, 92) homogeneous candidates
ALL_NODES = list(cache["all_nodes"])
mon_pos = list(cache["mon_pos"])
S = {"old": cache["S_old"], "average": cache["S_avg"], "new": cache["S_new"]}
C_all_mon = C_all[:, :, mon_pos]                          # (2000, 49, 6)

wn0 = wntr.network.WaterNetworkModel(B.PRACTICE_INP)
PIPE_LEN = {p: wn0.get_link(p).length for p in wn0.pipe_name_list}
zone_pipes = {z: [p for p in wn0.pipe_name_list if B.MATERIAL_ZONES[p] == z] for z in ZKEYS}

# homogeneous 3-zone grid library at monitors (for structural residual + grid fit)
kw_old_grid = np.round(np.linspace(-0.2, -1.5, 7), 3)
kw_avg_grid = np.round(np.linspace(-0.04, -0.2, 7), 3)
kw_new_grid = np.round(np.linspace(-0.005, -0.10, 7), 3)
GRID = {}
t0 = time.time()
for kwo in kw_old_grid:
    for kwa in kw_avg_grid:
        for kwn in kw_new_grid:
            GRID[(float(kwo), float(kwa), float(kwn))] = B.simulate_chlorine(
                B.KB_FIXED, 0.0, pre_run=B.make_kw_hook(kwo, kwa, kwn),
            ).values[B.WARMUP_H:]
print(f"grid library {len(GRID)} sims ({time.time() - t0:.1f}s)")


def wstats(w, x):
    m = float(np.sum(w * x))
    return m, float(np.sqrt(np.sum(w * (x - m) ** 2)))


rows = []
for jit in JITTERS:
    rng_j = np.random.default_rng(JITTER_SEED)
    kw_pipe = {p: ZONE_MEAN[B.MATERIAL_ZONES[p]] * (1.0 + rng_j.uniform(-jit, jit))
               for p in wn0.pipe_name_list}

    def hook(wn, _kw=kw_pipe):
        for p in wn.pipe_name_list:
            wn.get_link(p).wall_coeff = B.per_day_to_per_second(_kw[p])

    truth_all = B.simulate_chlorine(B.KB_FIXED, 0.0, pre_run=hook,
                                    monitor_nodes=ALL_NODES).values
    truth_mon = truth_all[:, mon_pos]
    truth_post_mon = truth_mon[B.WARMUP_H:]

    # noise-free structural residual + grid best fit (vs noise-free truth)
    struct = min(np.sqrt(((sim - truth_post_mon) ** 2).mean()) for sim in GRID.values())

    # noisy observations (same process: seed 42)
    rng_n = np.random.default_rng(B.NOISE_SEED)
    obs = np.clip(truth_mon + rng_n.normal(0, B.SIGMA_OBS, truth_mon.shape), 0, None)[B.WARMUP_H:]
    noise_rmse = float(np.sqrt(((truth_post_mon - obs) ** 2).mean()))

    # GLUE reusing cached candidate predictions
    RMSE = np.sqrt(((C_all_mon - obs[None]) ** 2).mean(axis=(1, 2)))
    L = np.exp(-0.5 * (RMSE / B.SIGMA_OBS) ** 2)
    beh = RMSE < B.RMSE_THR
    w = L * beh
    w = w / w.sum() if w.sum() > 0 else w

    # per-zone true arithmetic mean and bias
    zstats = {}
    for z in ZKEYS:
        kws = np.array([kw_pipe[p] for p in zone_pipes[z]])
        arith = float(kws.mean())
        m, sd = wstats(w, S[z])
        zstats[z] = {"arith": arith, "glue_mean": m, "glue_sd": sd,
                     "bias": m - arith, "bias_in_sd": (m - arith) / sd if sd > 0 else np.nan}

    # risk ranking
    below = (C_all < C_MIN)
    P_glue = np.tensordot(w, below.astype(float), axes=(0, 0)).mean(axis=0)
    P_true = (truth_all[B.WARMUP_H:] < C_MIN).mean(axis=0)
    rank_glue = [ALL_NODES[i] for i in np.argsort(P_glue)[::-1][:6]]
    rank_true = [ALL_NODES[i] for i in np.argsort(P_true)[::-1][:6]]

    rows.append({"jitter": jit, "struct_residual": float(struct),
                 "noise_rmse": noise_rmse, "behavioural": int(beh.sum()),
                 "rmse_min": float(RMSE.min()), "zones": zstats,
                 "rank_glue": rank_glue, "rank_true": rank_true})

# ---- report ----
print("\n=== within-zone heterogeneity sweep (precise-but-biased) ===")
print(f"{'jit':>4} {'structRes':>9} {'behav':>6} {'rmseMin':>7} | "
      f"{'old bias(SD)':>14} {'avg bias(SD)':>14} {'new bias(SD)':>14}")
for r in rows:
    z = r["zones"]
    def fmt(zz):
        return f"{z[zz]['bias']:+.3f}({z[zz]['bias_in_sd']:+.2f})"
    print(f"{r['jitter']:>4} {r['struct_residual']:>9.4f} {r['behavioural']:>6} "
          f"{r['rmse_min']:>7.4f} | {fmt('old'):>14} {fmt('average'):>14} {fmt('new'):>14}")
for r in rows:
    print(f"  jit={r['jitter']} risk GLUE {r['rank_glue']}  | TRUE {r['rank_true']}")


def _jsafe(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    return str(o)


with open(os.path.join(HERE, "baseline_cache", "step5c_jitter_sweep.json"), "w") as f:
    json.dump(rows, f, indent=2, default=_jsafe)

# ---- figure: |bias| vs jitter per zone (+ bias in SD units) ----
fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
jits = [r["jitter"] * 100 for r in rows]
for ax, z in zip(axes, ZKEYS):
    bias = [r["zones"][z]["bias"] for r in rows]
    sd = [r["zones"][z]["glue_sd"] for r in rows]
    ax.errorbar(jits, bias, yerr=sd, marker="o", capsize=4, color="steelblue",
                label="GLUE bias ± behavioural SD")
    ax.axhline(0, color="gray", lw=1)
    ax.set_xlabel("within-zone jitter (%)")
    ax.set_ylabel("bias = GLUE mean − true arith. mean (m/day)")
    ax.set_title(f"{z} zone")
    ax.grid(alpha=0.3)
    for xi, r in zip(jits, rows):
        ax.annotate(f"{r['zones'][z]['bias_in_sd']:+.1f}σ",
                    (xi, r["zones"][z]["bias"]), textcoords="offset points",
                    xytext=(6, 6), fontsize=8)
axes[0].legend(fontsize=8)
fig.suptitle("Symmetric within-zone heterogeneity (±20–50%): the fitted grouped coefficient stays "
             "within <0.6 SD of the true field average — grouped model is robust (no useful bias)",
             y=1.02)
plt.tight_layout()
figpath = os.path.join(FIGDIR, "step5c_jitter_sweep.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")
print("figure saved to", figpath)
