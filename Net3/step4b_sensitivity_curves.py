"""Step 4b: single-parameter identifiability curves (why old is one-sided, avg/new flat).

For each coefficient, sweep it across (and a little beyond) its prior range while holding
the other two at their TRUE values, and compute the monitored RMSE against the baseline
noisy observations. This visualises the shape of the GLUE objective:
  - old  : an asymmetric valley (steep on the weak side, flat/saturated on the strong side)
  - avg  : nearly flat across its whole prior (objective insensitive)
  - new  : nearly flat across its whole prior (objective insensitive)

Cheap (~200 monitor-only EPANET runs). Outputs a figure + a JSON summary.
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
os.makedirs(FIGDIR, exist_ok=True)

cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
obs_glue = cache["obs_glue"]                       # (49, 6) baseline noisy observations
TRUE = {"old": B.KW_OLD_TRUE, "avg": B.KW_AVG_TRUE, "new": B.KW_NEW_TRUE}
PRIOR = {"old": B.PRIOR["old"], "avg": B.PRIOR["avg"], "new": B.PRIOR["new"]}

# RMSE at the truth (noise floor reference)
truth_sim = B.simulate_chlorine(
    B.KB_FIXED, 0.0,
    pre_run=B.make_kw_hook(TRUE["old"], TRUE["avg"], TRUE["new"]),
).values[B.WARMUP_H:]
NOISE_FLOOR = float(np.sqrt(((truth_sim - obs_glue) ** 2).mean()))


def rmse_for(kw_old, kw_avg, kw_new):
    sim = B.simulate_chlorine(
        B.KB_FIXED, 0.0,
        pre_run=B.make_kw_hook(kw_old, kw_avg, kw_new),
    ).values[B.WARMUP_H:]
    return float(np.sqrt(((sim - obs_glue) ** 2).mean()))


# display sweep ranges (wider than the prior so the valley shape is visible)
SWEEP = {
    "old": np.linspace(-2.2, -0.05, 80),
    "avg": np.linspace(-0.30, -0.005, 80),
    "new": np.linspace(-0.15, -0.002, 80),
}

results = {}
for g in ["old", "avg", "new"]:
    xs = SWEEP[g]
    rmse = np.empty(len(xs))
    for i, v in enumerate(xs):
        kw = dict(TRUE)
        kw[g] = float(v)
        rmse[i] = rmse_for(kw["old"], kw["avg"], kw["new"])
    a, b = PRIOR[g]
    in_prior = (xs >= min(a, b)) & (xs <= max(a, b))
    results[g] = {
        "x": xs.tolist(),
        "rmse": rmse.tolist(),
        "prior_range": [a, b],
        "truth": TRUE[g],
        "prior_rmse_min": float(rmse[in_prior].min()),
        "prior_rmse_max": float(rmse[in_prior].max()),
        "prior_rmse_swing": float(rmse[in_prior].max() - rmse[in_prior].min()),
    }

# ---- figure ----
fig, axes = plt.subplots(1, 3, figsize=(15, 4.2))
labels = {"old": "k_w,old", "avg": "k_w,avg", "new": "k_w,new"}
for ax, g in zip(axes, ["old", "avg", "new"]):
    xs = np.array(results[g]["x"])
    rmse = np.array(results[g]["rmse"])
    a, b = results[g]["prior_range"]
    ax.plot(xs, rmse, color="steelblue", lw=2)
    ax.axvspan(min(a, b), max(a, b), color="0.85", label="prior range")
    ax.axvline(results[g]["truth"], color="red", lw=2, label="true value")
    ax.axhline(B.RMSE_THR, color="crimson", ls="--", lw=1, label="threshold 0.12")
    ax.axhline(0.107, color="darkorange", ls=":", lw=1, label="threshold 0.107")
    ax.axhline(NOISE_FLOOR, color="green", ls="-.", lw=1, label="noise floor")
    ax.set_xlabel(f"{labels[g]} (m/day)")
    ax.set_ylabel("monitored RMSE (mg/L)")
    ax.set_title(f"{labels[g]}: RMSE swing over prior = "
                 f"{results[g]['prior_rmse_swing']:.3f} mg/L")
    ax.grid(alpha=0.3)
axes[0].legend(fontsize=7, loc="upper center")
fig.suptitle("Single-parameter objective: old is an asymmetric valley; avg/new are flat "
             "(other two held at truth)", y=1.02)
plt.tight_layout()
figpath = os.path.join(FIGDIR, "step4b_sensitivity_curves.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")

summary = {
    "hold_others_at": "true values",
    "observations": "baseline noisy (seed 42)",
    "noise_floor_rmse": NOISE_FLOOR,
    "threshold": B.RMSE_THR,
    "prior_rmse_swing": {g: results[g]["prior_rmse_swing"] for g in ["old", "avg", "new"]},
    "figure": os.path.relpath(figpath, HERE),
}
with open(os.path.join(HERE, "baseline_cache", "step4b_sensitivity.json"), "w") as f:
    json.dump({"summary": summary, "sweeps": results}, f, indent=2)

print("noise floor RMSE =", round(NOISE_FLOOR, 4))
print("RMSE swing across each prior (others at truth):")
for g in ["old", "avg", "new"]:
    print(f"  {labels[g]:>9}: min {results[g]['prior_rmse_min']:.4f} -> "
          f"max {results[g]['prior_rmse_max']:.4f}  (swing {results[g]['prior_rmse_swing']:.4f} mg/L)")
print("figure saved to", figpath)
