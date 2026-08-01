"""Step 6: noise / sensor-accuracy sensitivity in the three-zone setup.

Re-runs the GLUE calibration against the SAME three-zone truth for a range of observation
noise levels σ = {0.02, 0.05, 0.10, 0.15} mg/L (foundation's 0.02/0.05/0.10 plus the
supervisor's requested ±0.05 / ±0.10 / ±0.15). σ is interpreted as ONE standard deviation.

Two choices are made consistently:
  - the likelihood scale equals the observation σ (L = exp(-0.5 (RMSE/σ)^2));
  - the behavioural threshold scales with σ as the ~95% acceptance band of the objective,
    threshold(σ) = σ (1 + 1.645/√(2N))  (0.107 at σ=0.1), via wq_common.threshold_for_sigma.

Everything reuses the frozen baseline cache (candidate predictions are noise-independent), so no
EPANET is re-run. Each σ is repeated over 30 independent noise realisations; results are reported
as median [IQR]. This answers §3.5 (how the behavioural width of each grouped coefficient scales
with σ) and the email question (required sensor accuracy for useful chlorine predictions).
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

cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
C_all = cache["C_all"]                              # (2000, 49, 92), noise-independent candidates
ALL_NODES = list(cache["all_nodes"])
mon_pos = list(cache["mon_pos"])
truth_mon = cache["truth_all"][:, mon_pos]          # (73, 6) three-zone truth at monitors
S = {"old": cache["S_old"], "average": cache["S_avg"], "new": cache["S_new"]}
C_all_mon = C_all[:, :, mon_pos]
C_MIN = 0.2

ZKEYS = ["old", "average", "new"]
PRIOR_OF = {"old": B.PRIOR["old"], "average": B.PRIOR["avg"], "new": B.PRIOR["new"]}
PRIOR_SD = {z: (PRIOR_OF[z][1] - PRIOR_OF[z][0]) / np.sqrt(12) for z in ZKEYS}
SIGMAS = [0.02, 0.05, 0.10, 0.15]
N_NOISE = 30
NOISE_SEEDS = list(range(42, 42 + N_NOISE))
NODE_BAND = "15"                                    # old-zone downstream node for the predictive band
kk = ALL_NODES.index(NODE_BAND)


def weighted_quantile(vals, w, q):
    o = np.argsort(vals)
    cw = np.cumsum(w[o])
    cw /= cw[-1]
    return vals[o][np.searchsorted(cw, min(q, 1.0))]


def med_iqr(a):
    a = np.asarray(a, float)
    return float(np.median(a)), float(np.percentile(a, 25)), float(np.percentile(a, 75))


rows = []
for sigma in SIGMAS:
    thr = B.threshold_for_sigma(sigma)
    per = {z: {"sd_ret": [], "sd": []} for z in ZKEYS}
    ret, band = [], []
    for seed in NOISE_SEEDS:
        rng = np.random.default_rng(seed)
        obs = np.clip(truth_mon + rng.normal(0, sigma, truth_mon.shape), 0, None)[B.WARMUP_H:]
        rmse = np.sqrt(((C_all_mon - obs[None]) ** 2).mean(axis=(1, 2)))
        L = np.exp(-0.5 * (rmse / sigma) ** 2)
        beh = rmse < thr
        w = L * beh
        if w.sum() == 0:
            continue
        w = w / w.sum()
        ret.append(float(beh.mean()))
        for z in ZKEYS:
            m = np.sum(w * S[z])
            sd = np.sqrt(np.sum(w * (S[z] - m) ** 2))
            per[z]["sd"].append(float(sd))
            per[z]["sd_ret"].append(float(sd / PRIOR_SD[z]))
        bidx = np.where(beh)[0]
        wb = w[bidx] / w[bidx].sum()
        lo = np.array([weighted_quantile(C_all[bidx, t, kk], wb, 0.05) for t in range(C_all.shape[1])])
        hi = np.array([weighted_quantile(C_all[bidx, t, kk], wb, 0.95) for t in range(C_all.shape[1])])
        band.append(float(np.mean(hi - lo)))
    row = {"sigma": sigma, "threshold": thr,
           "retention_med": med_iqr(ret)[0],
           "band_node15_med": med_iqr(band)[0]}
    for z in ZKEYS:
        m, lo, hi = med_iqr(per[z]["sd_ret"])
        sm = med_iqr(per[z]["sd"])[0]
        row[z] = {"sd_ret_med": m, "sd_ret_iqr": [lo, hi], "sd_med": sm}
    rows.append(row)

# ---- report ----
print("=== Step 6: noise / sensor-accuracy sensitivity (three-zone, threshold scales with σ) ===")
print(f"{'σ':>5} {'thr':>6} {'ret':>5} {'band15':>7} | "
      f"{'old SDret':>18} {'avg SDret':>18} {'new SDret':>18}")
for r in rows:
    def f(z):
        s = r[z]
        return f"{s['sd_ret_med']*100:4.0f}% [{s['sd_ret_iqr'][0]*100:.0f}-{s['sd_ret_iqr'][1]*100:.0f}]"
    print(f"{r['sigma']:>5} {r['threshold']:>6.3f} {r['retention_med']*100:>4.0f}% "
          f"{r['band_node15_med']:>7.3f} | {f('old'):>18} {f('average'):>18} {f('new'):>18}")


def _jsafe(o):
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.integer):
        return int(o)
    return str(o)


with open(os.path.join(HERE, "baseline_cache", "step6_noise_sensitivity.json"), "w") as f:
    json.dump(rows, f, indent=2, default=_jsafe)

# ---- figure: SD retained (%) vs σ for the three coefficients ----
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.6))
sig = [r["sigma"] for r in rows]
colors = {"old": "tab:red", "average": "tab:orange", "new": "tab:green"}
for z in ZKEYS:
    y = [r[z]["sd_ret_med"] * 100 for r in rows]
    lo = [r[z]["sd_ret_iqr"][0] * 100 for r in rows]
    hi = [r[z]["sd_ret_iqr"][1] * 100 for r in rows]
    ax1.plot(sig, y, marker="o", color=colors[z], label=f"{z}")
    ax1.fill_between(sig, lo, hi, color=colors[z], alpha=0.15)
ax1.axhline(70, color="gray", ls="--", lw=1, label="70% (identifiable below)")
for r in rows:                                      # flag sampling-limited σ (retention < 5%)
    if r["retention_med"] < 0.05:
        ax1.axvspan(r["sigma"] - 0.006, r["sigma"] + 0.006, color="red", alpha=0.08)
        ax1.annotate("sampling-\nlimited", (r["sigma"], 30), fontsize=7, ha="center", color="crimson")
ax1.set_xlabel("observation σ (mg/L)")
ax1.set_ylabel("behavioural SD retained (% of prior)")
ax1.set_title("Coefficient identifiability vs sensor noise")
ax1.legend(fontsize=8)
ax1.grid(alpha=0.3)

ax2.plot(sig, [r["band_node15_med"] for r in rows], marker="s", color="steelblue")
ax2.set_xlabel("observation σ (mg/L)")
ax2.set_ylabel("5–95% predictive band at node 15 (mg/L)")
ax2.set_title("Prediction uncertainty vs sensor noise")
ax2.grid(alpha=0.3)
fig.suptitle("Step 6 — sensor-accuracy sensitivity (three-zone; behavioural threshold scales with σ)",
             y=1.02)
plt.tight_layout()
figpath = os.path.join(FIGDIR, "step6_noise_sensitivity.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")
print("figure saved to", figpath)
