"""Step 5d: STRUCTURED within-zone heterogeneity -> precise-but-biased.

Location-consistent design (addresses the critique of the length-based five-group truth):
the truth keeps the three LOCATION zones, but WITHIN each zone the wall coefficient is
correlated with pipe length (a proxy for residence/flow contribution): longer pipes decay more
strongly. The per-zone ARITHMETIC mean is held exactly at the zone mean, but the
LENGTH-weighted (≈ residence-weighted, i.e. effective) mean is shifted stronger. A three-zone
homogeneous fit therefore recovers the length-weighted value, not the arithmetic mean — a precise
fit but a biased coefficient.

Contrast with Step 5a/5b (random, uncorrelated jitter): there length-weighted ≈ arithmetic, so
no bias. Here the correlation is what breaks it.

Reuses the frozen baseline GLUE candidate predictions (truth-independent); primary threshold 0.107.
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
C_MIN = 0.2
CORR = 0.5                       # strength of the length-correlation (factor 1 + CORR*s, s in [-1,1])

cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
C_all = cache["C_all"]
ALL_NODES = list(cache["all_nodes"])
mon_pos = list(cache["mon_pos"])
S = {"old": cache["S_old"], "average": cache["S_avg"], "new": cache["S_new"]}
C_all_mon = C_all[:, :, mon_pos]

wn0 = wntr.network.WaterNetworkModel(B.PRACTICE_INP)
PIPE_LEN = {p: wn0.get_link(p).length for p in wn0.pipe_name_list}
zone_pipes = {z: [p for p in wn0.pipe_name_list if B.MATERIAL_ZONES[p] == z] for z in ZKEYS}

# ---- build the structured (length-correlated) truth ----
KW_PIPE = {}
for z in ZKEYS:
    ps = zone_pipes[z]
    lens = np.array([PIPE_LEN[p] for p in ps])
    order = np.argsort(lens)                     # shortest -> longest
    rank = np.empty(len(ps))
    rank[order] = np.arange(len(ps))
    s = 2.0 * (rank / (len(ps) - 1) - 0.5) if len(ps) > 1 else np.zeros(len(ps))  # in [-1,1], mean 0
    for p, sp in zip(ps, s):
        KW_PIPE[p] = ZONE_MEAN[z] * (1.0 + CORR * sp)   # longer pipe -> stronger decay


def hook(wn):
    for p in wn.pipe_name_list:
        wn.get_link(p).wall_coeff = B.per_day_to_per_second(KW_PIPE[p])


true_ref = {}
for z in ZKEYS:
    ps = zone_pipes[z]
    kws = np.array([KW_PIPE[p] for p in ps])
    lens = np.array([PIPE_LEN[p] for p in ps])
    true_ref[z] = {"n": len(ps), "arith": float(kws.mean()),
                   "lenwt": float((kws * lens).sum() / lens.sum()),
                   "min": float(kws.min()), "max": float(kws.max())}

truth_all = B.simulate_chlorine(B.KB_FIXED, 0.0, pre_run=hook, monitor_nodes=ALL_NODES).values
truth_mon = truth_all[:, mon_pos]
truth_post_mon = truth_mon[B.WARMUP_H:]

# grid library for structural residual + grid fit
kw_old_grid = np.round(np.linspace(-0.2, -1.5, 7), 3)
kw_avg_grid = np.round(np.linspace(-0.04, -0.2, 7), 3)
kw_new_grid = np.round(np.linspace(-0.005, -0.10, 7), 3)
GRID = {}
t0 = time.time()
for kwo in kw_old_grid:
    for kwa in kw_avg_grid:
        for kwn in kw_new_grid:
            GRID[(float(kwo), float(kwa), float(kwn))] = B.simulate_chlorine(
                B.KB_FIXED, 0.0, pre_run=B.make_kw_hook(kwo, kwa, kwn)).values[B.WARMUP_H:]
struct = min(np.sqrt(((sim - truth_post_mon) ** 2).mean()) for sim in GRID.values())
print(f"grid {len(GRID)} sims ({time.time()-t0:.1f}s); structural residual {struct:.4f}")

# noisy obs + GLUE (reuse cached candidates), primary threshold 0.107
rng_n = np.random.default_rng(B.NOISE_SEED)
obs = np.clip(truth_mon + rng_n.normal(0, B.SIGMA_OBS, truth_mon.shape), 0, None)[B.WARMUP_H:]
RMSE = np.sqrt(((C_all_mon - obs[None]) ** 2).mean(axis=(1, 2)))
L = np.exp(-0.5 * (RMSE / B.SIGMA_OBS) ** 2)
beh = RMSE < B.RMSE_THR
w = L * beh
w = w / w.sum()
GRIDFIT = None
best_rmse = np.inf
for kw, sim in GRID.items():
    r = np.sqrt(((sim - obs) ** 2).mean())
    if r < best_rmse:
        best_rmse, GRIDFIT = r, kw
gf = {"old": GRIDFIT[0], "average": GRIDFIT[1], "new": GRIDFIT[2]}

glue = {}
for z in ZKEYS:
    m = float(np.sum(w * S[z]))
    sd = float(np.sqrt(np.sum(w * (S[z] - m) ** 2)))
    glue[z] = {"mean": m, "sd": sd}

# risk
below = (C_all < C_MIN)
P_glue = np.tensordot(w, below.astype(float), axes=(0, 0)).mean(axis=0)
P_true = (truth_all[B.WARMUP_H:] < C_MIN).mean(axis=0)
rank_glue = [ALL_NODES[i] for i in np.argsort(P_glue)[::-1][:6]]
rank_true = [ALL_NODES[i] for i in np.argsort(P_true)[::-1][:6]]

report = {"design": "within-zone length-correlated heterogeneity (CORR=%.2f)" % CORR,
          "threshold": B.RMSE_THR, "structural_residual": float(struct),
          "behavioural": int(beh.sum()), "rmse_min": float(RMSE.min()),
          "grid_fit": GRIDFIT, "zones": {}, "rank_glue": rank_glue, "rank_true": rank_true}
print("\n=== Step 5d: structured (length-correlated) within-zone heterogeneity, thr=0.107 ===")
print(f"behavioural {int(beh.sum())}/{B.N_MC}, min RMSE {RMSE.min():.4f}")
print(f"{'zone':>8} | {'arith':>7} {'lenwt':>7} | {'GLUE mean±sd':>15} | {'gridfit':>8} | "
      f"{'bias(GLUE-arith)':>16} | {'lenwt-arith':>11}")
for z in ZKEYS:
    tr = true_ref[z]
    bias = glue[z]["mean"] - tr["arith"]
    report["zones"][z] = {**tr, "glue_mean": glue[z]["mean"], "glue_sd": glue[z]["sd"],
                          "grid_fit": gf[z], "bias": bias, "lenwt_minus_arith": tr["lenwt"] - tr["arith"]}
    print(f"{z:>8} | {tr['arith']:7.3f} {tr['lenwt']:7.3f} | {glue[z]['mean']:7.3f}±{glue[z]['sd']:.3f} "
          f"| {gf[z]:8.3f} | {bias:+16.3f} | {tr['lenwt']-tr['arith']:+11.3f}")
print(f"risk GLUE {rank_glue}\nrisk TRUE {rank_true}")


def _jsafe(o):
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.integer):
        return int(o)
    return str(o)


with open(os.path.join(HERE, "baseline_cache", "step5d_structured.json"), "w") as f:
    json.dump(report, f, indent=2, default=_jsafe)

# figure: kw vs pipe length per zone + arith/lenwt/GLUE lines
fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
for ax, z in zip(axes, ZKEYS):
    ps = zone_pipes[z]
    lens = np.array([PIPE_LEN[p] for p in ps])
    kws = np.array([KW_PIPE[p] for p in ps])
    ax.scatter(lens, kws, s=18, color="0.5", label="true pipe k_w")
    ax.axhline(true_ref[z]["arith"], color="black", lw=2, label="true arith. mean")
    ax.axhline(true_ref[z]["lenwt"], color="green", lw=2, ls="-.", label="length-weighted mean")
    ax.axhline(glue[z]["mean"], color="steelblue", lw=2, ls="--", label="GLUE behavioural mean")
    ax.set_xlabel("pipe length")
    ax.set_ylabel("k_w (m/day)")
    ax.set_title(f"{z} zone")
    ax.grid(alpha=0.3)
axes[0].legend(fontsize=7)
fig.suptitle("Step 5d — structured (length-correlated) heterogeneity: GLUE tracks the "
             "length-weighted mean, biased from the arithmetic mean (precise-but-biased)", y=1.02)
plt.tight_layout()
figpath = os.path.join(FIGDIR, "step5d_structured.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")
print("figure saved to", figpath)
