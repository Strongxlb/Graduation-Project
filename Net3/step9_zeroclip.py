"""Step 9 (PRIMARY): does treating the paper's zero-clipped observations as EXACT RMSE points bias
the calibration? — the reviewer's actual request.

The paper generates observations as  C_obs = max(0, C_true + ε)  (lower bound L = 0), then calibrates
with unweighted RMSE that treats every clipped 0 as an exact measurement of 0. The statistically
correct treatment of a clipped point is left-censored: "the latent value Y* ≤ 0", contributing
Φ(−μ/σ) to the likelihood, not (0 − μ)². We compare the two on IDENTICAL data at L = 0.

  naive  (paper):   every point Gaussian, clipped zeros treated as exact 0  →  −½((0 − μ)/σ)²
  censored (L=0):   uncensored points Gaussian;  clipped-0 points →  log Φ(−μ/σ)   [log_ndtr]

Reported: (1) how many calibration points are clipped and where; (2) k_w,old/avg/new median [IQR]
over 30 noise realisations; (3) node-15 risk; (4) high-risk ranking; (5) the old profile curve.
The positive-detection-limit sweep (L = 0.1/0.2/0.3) is the OPTIONAL extension in step9_censored.py.
"""
import os
import json
import numpy as np
from scipy.special import log_ndtr
import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figures")
ZKEYS = ["old", "average", "new"]
TRUE = {"old": B.KW_OLD_TRUE, "average": B.KW_AVG_TRUE, "new": B.KW_NEW_TRUE}
ZONE_OF = {"107": "new", "113": "new", "15": "old", "145": "old", "209": "average", "231": "average"}
sigma = B.SIGMA_OBS
C_MIN = 0.2

cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
C_all = cache["C_all"].astype(np.float64)                 # (2000, 49, 92)
ALL_NODES = list(cache["all_nodes"])
mon_pos = list(cache["mon_pos"])
truth_full = cache["truth_all"][:, mon_pos]               # (73, 6)
noisy = cache["noisy"]                                     # (73, 6) baseline clipped obs (seed 42)
S = {"old": cache["S_old"], "average": cache["S_avg"], "new": cache["S_new"]}
C_all_mon = C_all[:, :, mon_pos]                          # (2000, 49, 6)
idx15 = ALL_NODES.index("15")

# ---------- 1) count clipped zeros in the ACTUAL calibration data ----------
full_zero = (noisy == 0.0)
cal_zero = full_zero[B.WARMUP_H:]                          # (49, 6) = the 294 calibration points
print("=== Step 9 (L=0): clipped-zero census ===")
print(f"full record  : {int(full_zero.sum())} / {full_zero.size}  (6 monitors x 73 h)")
print(f"calibration  : {int(cal_zero.sum())} / {cal_zero.size}  (6 monitors x 49 post-warm-up h)")
zeros_by_node = {}
for j, node in enumerate(B.MONITOR_NODES):
    zeros_by_node[node] = int(cal_zero[:, j].sum())
    print(f"   node {node:>4} ({ZONE_OF[node]:>7}): {int(cal_zero[:, j].sum()):>3} clipped hours")
by_zone = {z: sum(v for n, v in zeros_by_node.items() if ZONE_OF[n] == z) for z in ZKEYS}
print(f"   by zone: old {by_zone['old']}, average {by_zone['average']}, new {by_zone['new']}")


def behav_means(loglik):
    w = np.exp(loglik - loglik.max())
    w = w / w.sum()
    m = {z: float(np.sum(w * S[z])) for z in ZKEYS}
    sd = {z: float(np.sqrt(np.sum(w * (S[z] - m[z]) ** 2))) for z in ZKEYS}
    frac15 = float(np.sum(w * (C_all[:, :, idx15] < C_MIN).mean(axis=1)))
    frac_all = np.tensordot(w, (C_all < C_MIN).mean(axis=1), axes=(0, 0))
    top3 = [ALL_NODES[i] for i in np.argsort(frac_all)[::-1][:3]]
    return m, sd, frac15, top3


# ---------- 2) naive-exact-0 vs censored-at-0 over 30 noise realisations ----------
SEEDS = list(range(42, 72))
res = {"naive": {z: [] for z in ZKEYS}, "cens": {z: [] for z in ZKEYS},
       "naive_f15": [], "cens_f15": [], "naive_rank": [], "cens_rank": []}
for seed in SEEDS:
    rng = np.random.default_rng(seed)
    raw = truth_full + rng.normal(0, sigma, truth_full.shape)
    obs = np.clip(raw, 0.0, None)[B.WARMUP_H:]            # (49, 6) clipped at 0
    zmask = (obs == 0.0)                                  # clipped points

    r = (obs[None] - C_all_mon) / sigma
    ll_naive = (-0.5 * r ** 2).sum(axis=(1, 2))           # zeros treated as exact
    term_cen = log_ndtr((0.0 - C_all_mon) / sigma)        # log Φ(−μ/σ)
    ll_cens = np.where(zmask[None], term_cen, -0.5 * r ** 2).sum(axis=(1, 2))

    mn, _, f15n, rkn = behav_means(ll_naive)
    mc, _, f15c, rkc = behav_means(ll_cens)
    for z in ZKEYS:
        res["naive"][z].append(mn[z]); res["cens"][z].append(mc[z])
    res["naive_f15"].append(f15n); res["cens_f15"].append(f15c)
    res["naive_rank"].append(tuple(rkn)); res["cens_rank"].append(tuple(rkc))


def q(a):
    return float(np.median(a)), float(np.percentile(a, 25)), float(np.percentile(a, 75))


print("\n=== k_w estimates: naive-exact-0 vs censored-at-0  (median [IQR] over 30 noise) ===")
print(f"{'coef':>8} | {'truth':>6} | {'naive median [IQR]':>26} | {'censored median [IQR]':>26} | Δmedian")
report = {"sigma": sigma, "full_zero": int(full_zero.sum()), "cal_zero": int(cal_zero.sum()),
          "zeros_by_node": zeros_by_node, "zeros_by_zone": by_zone, "coef": {}}
for z in ZKEYS:
    nm, nlo, nhi = q(res["naive"][z]); cm, clo, chi = q(res["cens"][z])
    report["coef"][z] = {"naive": [nm, nlo, nhi], "cens": [cm, clo, chi],
                         "naive_bias": nm - TRUE[z], "cens_bias": cm - TRUE[z], "delta_median": cm - nm}
    print(f"{z:>8} | {TRUE[z]:>6.3f} | {nm:>8.3f} [{nlo:.3f},{nhi:.3f}] | "
          f"{cm:>8.3f} [{clo:.3f},{chi:.3f}] | {cm-nm:>+.3f}")

f15n, f15c = q(res["naive_f15"]), q(res["cens_f15"])
print(f"\nnode-15 fraction of hours < {C_MIN}:  naive {f15n[0]:.3f} [{f15n[1]:.3f},{f15n[2]:.3f}] | "
      f"censored {f15c[0]:.3f} [{f15c[1]:.3f},{f15c[2]:.3f}]")
rank_n = max(set(res["naive_rank"]), key=res["naive_rank"].count)
rank_c = max(set(res["cens_rank"]), key=res["cens_rank"].count)
print(f"top-3 risk ranking:  naive {list(rank_n)} | censored {list(rank_c)}")
report["node15_frac_below"] = {"naive": f15n, "cens": f15c}
report["top3"] = {"naive": list(rank_n), "cens": list(rank_c)}

# ---------- 3) old profile curve at L=0 (baseline seed 42) via the residual grid ----------
NG = 21
go = np.linspace(*B.PRIOR["old"], NG)
E = np.load(os.path.join(HERE, "baseline_cache", "step7c_resid_grid.npy"))   # (21,21,21,294) node-major
obs_flat = noisy[B.WARMUP_H:].T.ravel()                    # node-major, matches E build
zmask_flat = (obs_flat == 0.0)
mu = E + obs_flat[None, None, None, :]                     # sim, node-major
naive_nll = 0.5 * ((E / sigma) ** 2).sum(axis=3)
cens_nll = (0.5 * ((E / sigma) ** 2) * (~zmask_flat)).sum(axis=3) - (log_ndtr(-mu / sigma) * zmask_flat).sum(axis=3)


def profile_interval(nll_grid):
    prof = nll_grid.min(axis=(1, 2))
    d = prof - prof.min()
    below = np.where(d <= 1.92)[0]
    lo, hi = go[below.min()], go[below.max()]
    return prof, d, {"lo": float(lo), "hi": float(hi), "half_width": float((hi - lo) / 2),
                     "argmin": float(go[int(np.argmin(prof))])}


prof_n, d_n, iv_n = profile_interval(naive_nll)
prof_c, d_c, iv_c = profile_interval(cens_nll)
print(f"\nold profile 95% (baseline): naive [{iv_n['lo']:.3f},{iv_n['hi']:.3f}] (min {iv_n['argmin']:.3f}) | "
      f"censored [{iv_c['lo']:.3f},{iv_c['hi']:.3f}] (min {iv_c['argmin']:.3f})")
report["old_profile"] = {"naive": iv_n, "cens": iv_c}

with open(os.path.join(HERE, "baseline_cache", "step9_zeroclip.json"), "w") as f:
    json.dump(report, f, indent=2)
print("\nsaved step9_zeroclip.json")

# ---------- figure ----------
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, (axA, axB) = plt.subplots(1, 2, figsize=(13.5, 4.8))

axA.bar([f"{n}\n({ZONE_OF[n]})" for n in B.MONITOR_NODES],
        [zeros_by_node[n] for n in B.MONITOR_NODES],
        color=["firebrick" if ZONE_OF[n] == "old" else ("goldenrod" if ZONE_OF[n] == "average" else "steelblue")
               for n in B.MONITOR_NODES])
axA.set_ylabel("clipped-to-zero hours (of 49)")
axA.set_title(f"(a) Zero-clipping census: {int(cal_zero.sum())}/{cal_zero.size} calibration points\n"
              "(all in the low-chlorine old zone)")
axA.grid(alpha=0.3, axis="y")

axB.plot(go, d_n, "o-", color="crimson", label=f"naive exact-0  95% [{iv_n['lo']:.2f},{iv_n['hi']:.2f}]")
axB.plot(go, d_c, "s-", color="seagreen", label=f"censored L=0  95% [{iv_c['lo']:.2f},{iv_c['hi']:.2f}]")
axB.axhline(1.92, color="0.4", ls=":", label="ΔNLL = 1.92 (95%)")
axB.axvline(TRUE["old"], color="k", ls="--", lw=1.2, label="true = -1.0")
axB.set_ylim(0, 15)
axB.set_xlabel("k_w,old (m/day)")
axB.set_ylabel("ΔNLL")
axB.set_title("(b) old profile likelihood at L=0:\nnaive exact-0 vs censored (baseline)")
axB.legend(fontsize=8)
axB.grid(alpha=0.3)

plt.tight_layout()
figpath = os.path.join(FIGDIR, "step9_zeroclip.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")
print("figure saved to", figpath)
