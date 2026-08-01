"""Step 7: a-priori identifiability via Fisher information / CRLB, with nuisance parameters.

Sensitivity (Jacobian) of monitored chlorine to each grouped wall coefficient at the truth, then
the Fisher information and the Cramér–Rao lower bound (CRLB = smallest achievable standard error).
The CRLB is computed for the three k_w under three nested models, adding the confounders the
reviewer flagged:

  Case A  k_w only              (k_b known, no sensor bias)          — idealised best case
  Case B  k_w + k_b             (k_b unknown; trades off with k_w)   — Priority-2 #5
  Case C  k_w + k_b + 6 offsets (per-monitor systematic bias)        — Priority-2 #1

Marginal CRLB for k_w uses the Schur complement  F_pp − F_pn F_nn⁻¹ F_np.
Independent Gaussian noise is assumed (AR(1) autocorrelation would inflate further, Priority-2 #4).

The idealised Case A shows the observations DO contain information about all three coefficients
(so GLUE's "avg/new uninformed" is partly the inefficiency of its informal likelihood — the
Stedinger 2008 / Mantovan & Todini 2006 critique). Adding the realistic confounders (Case C)
inflates the avg/new CRLB above their prior width, reconciling Fisher with GLUE.
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
TRUTH = [B.KW_OLD_TRUE, B.KW_AVG_TRUE, B.KW_NEW_TRUE]
KB = B.KB_FIXED
PRIOR_SD = {"old": (1.5 - 0.2) / np.sqrt(12), "average": (0.2 - 0.04) / np.sqrt(12),
            "new": (0.10 - 0.005) / np.sqrt(12)}
H, HKB = 0.02, 0.05
SIGMA = 0.10
NMON = len(B.MONITOR_NODES)


def sim(kb, kwo, kwa, kwn):
    return B.simulate_chlorine(kb, 0.0, pre_run=B.make_kw_hook(kwo, kwa, kwn)).values[B.WARMUP_H:]


# ---- Jacobian columns: old, avg, new, kb (finite differences), then 6 sensor offsets ----
def col(idx, h):
    kwp, kwm, kbp, kbm = list(TRUTH), list(TRUTH), KB, KB
    if idx < 3:
        kwp[idx] += h; kwm[idx] -= h
    else:
        kbp += h; kbm -= h
    return ((sim(kbp, *kwp) - sim(kbm, *kwm)) / (2 * h)).ravel()   # (294,) row = hour*6 + node


phys = [col(0, H), col(1, H), col(2, H), col(3, HKB)]              # old,avg,new,kb
n_obs = phys[0].size
node_of_row = np.arange(n_obs) % NMON                              # row -> monitor index
offsets = [(node_of_row == m).astype(float) for m in range(NMON)] # per-monitor additive bias
J_full = np.column_stack(phys + offsets)                          # (294, 4+6)
JtJ = J_full.T @ J_full
LABELS = ["old", "average", "new", "kb"] + [f"off_{n}" for n in B.MONITOR_NODES]


def marginal(idx_all, sigma):
    """Marginal CRLB (σ units) and eigenvalues for the 3 k_w within the column subset idx_all."""
    sub = JtJ[np.ix_(idx_all, idx_all)]
    p = [0, 1, 2]                                                 # kw are always the first three
    n = [i for i in range(len(idx_all)) if i not in p]
    Fpp = sub[np.ix_(p, p)]
    if n:
        Fpn = sub[np.ix_(p, n)]
        Fnn = sub[np.ix_(n, n)]
        marg = Fpp - Fpn @ np.linalg.pinv(Fnn) @ Fpn.T
    else:
        marg = Fpp
    cov = np.linalg.pinv(marg)
    crlb = sigma * np.sqrt(np.clip(np.diag(cov), 0, None))
    eig = np.linalg.eigvalsh(marg) / sigma ** 2
    return crlb, eig


cases = {"A: kw only": [0, 1, 2],
         "B: kw+kb": [0, 1, 2, 3],
         "C: kw+kb+6 offsets": list(range(J_full.shape[1]))}

# GLUE behavioural SD (empirical) at the primary threshold 0.107
cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
RMSE = cache["RMSE"]
S = {"old": cache["S_old"], "average": cache["S_avg"], "new": cache["S_new"]}
w = np.exp(-0.5 * (RMSE / B.SIGMA_OBS) ** 2) * (RMSE < B.RMSE_THR)
w = w / w.sum()
glue_sd = {z: float(np.sqrt(np.sum(w * (S[z] - np.sum(w * S[z])) ** 2))) for z in ZKEYS}

report = {"sigma": SIGMA, "prior_sd": PRIOR_SD, "glue_sd_0.107": glue_sd, "cases": {}}
print("=== Step 7: Fisher / CRLB with nuisance parameters (σ = 0.10) ===\n")
print(f"{'case':>22} | {'coef':>7} | {'CRLB':>7} | {'priorSD':>7} | {'CRLB/prior':>10} | identif.? | cond#")
for cname, idx in cases.items():
    crlb, eig = marginal(idx, SIGMA)
    cond = float(eig.max() / eig.min())
    report["cases"][cname] = {"condition_number": cond, "eigenvalues": [float(e) for e in eig[::-1]],
                              "coef": {}}
    for j, z in enumerate(ZKEYS):
        ratio = crlb[j] / PRIOR_SD[z]
        report["cases"][cname]["coef"][z] = {"crlb": float(crlb[j]), "crlb_over_prior": float(ratio),
                                             "identifiable": bool(ratio < 1.0)}
        print(f"{cname:>22} | {z:>7} | {crlb[j]:7.3f} | {PRIOR_SD[z]:7.3f} | {ratio:10.2f} | "
              f"{str(ratio < 1.0):>9} | {cond:8.1f}")
    print()

print(f"GLUE behavioural SD (0.107): " + ", ".join(f"{z} {glue_sd[z]:.3f}" for z in ZKEYS))
print(f"prior SD: " + ", ".join(f"{z} {PRIOR_SD[z]:.3f}" for z in ZKEYS))

# CRLB(C) vs sigma (scales linearly)
crlbC_unit, _ = marginal(cases["C: kw+kb+6 offsets"], 1.0)
report["crlbC_vs_sigma"] = {f"{s:.2f}": {z: float(s * crlbC_unit[j]) for j, z in enumerate(ZKEYS)}
                            for s in [0.05, 0.10, 0.15]}


def _jsafe(o):
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.integer):
        return int(o)
    return str(o)


with open(os.path.join(HERE, "baseline_cache", "step7_fisher.json"), "w") as f:
    json.dump(report, f, indent=2, default=_jsafe)

# ---- figure: CRLB/prior for cases A/B/C per coefficient (log; >1 = unidentifiable) ----
fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(ZKEYS))
wid = 0.25
for k, cname in enumerate(cases):
    vals = [report["cases"][cname]["coef"][z]["crlb_over_prior"] for z in ZKEYS]
    ax.bar(x + (k - 1) * wid, vals, wid, label=cname)
ax.axhline(1.0, color="crimson", ls="--", lw=1.5, label="CRLB = prior (identifiable below)")
ax.set_yscale("log")
ax.set_xticks(x)
ax.set_xticklabels(ZKEYS)
ax.set_ylabel("CRLB / prior SD (log; <1 identifiable, >1 not)")
ax.set_title("Step 7 — Fisher/CRLB: adding k_b and sensor offsets pushes avg/new above the prior\n"
             "(idealised A: all identifiable → realistic C: only old survives)")
ax.legend(fontsize=8)
ax.grid(alpha=0.3, axis="y")
plt.tight_layout()
figpath = os.path.join(FIGDIR, "step7_fisher.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")
print("\nfigure saved to", figpath)
