"""Step 7c: error autocorrelation (AR(1)) — Priority-2 #4, done properly.

Instead of mechanically multiplying every CRLB by the scalar ESS factor √[(1+ρ)/(1−ρ)], we build
the full AR(1) observation covariance and recompute the Fisher information:

  per-sensor 49×49 block   Σ_block[t,s] = σ² · ρ^|t−s|      (hourly AR(1), ρ = 0.4)
  full covariance          Σ = block_diag(6 sensor blocks)  (sensors independent)
  Fisher (AR(1))           F = Jᵀ Σ⁻¹ J     vs     independent  F = JᵀJ / σ²
  CRLB_j = sqrt[(F⁻¹)_jj]

Each coefficient's CRLB widens by its own factor (not a single 1.53), because J varies across
nodes and time. This is the idealised Case A (k_w only, k_b known, no bias) plus autocorrelation.
"""
import os
import json
import numpy as np
from scipy.linalg import block_diag
import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
ZKEYS = ["old", "average", "new"]
TRUTH = [B.KW_OLD_TRUE, B.KW_AVG_TRUE, B.KW_NEW_TRUE]
PRIOR_SD = {"old": (1.5 - 0.2) / np.sqrt(12), "average": (0.2 - 0.04) / np.sqrt(12),
            "new": (0.10 - 0.005) / np.sqrt(12)}
H = 0.02
SIGMA = 0.10
RHO = 0.40
NT = B.DURATION_H - B.WARMUP_H + 1          # 49 post-warm-up hours
NMON = len(B.MONITOR_NODES)


def sim_mon(kwo, kwa, kwn):
    return B.simulate_chlorine(B.KB_FIXED, 0.0,
                               pre_run=B.make_kw_hook(kwo, kwa, kwn)).values[B.WARMUP_H:]  # (49,6)


# ---- Jacobian in NODE-MAJOR order (so Σ is block-diagonal per sensor) ----
cols = []
for j in range(3):
    kp, km = list(TRUTH), list(TRUTH)
    kp[j] += H
    km[j] -= H
    dC = (sim_mon(*kp) - sim_mon(*km)) / (2 * H)        # (49, 6)
    cols.append(dC.T.ravel())                            # node-major: node0 h0..48, node1 ...
J = np.column_stack(cols)                                # (294, 3)

# ---- AR(1) covariance ----
tt = np.arange(NT)
block = SIGMA ** 2 * RHO ** np.abs(tt[:, None] - tt[None, :])   # 49×49
Sigma = block_diag(*[block for _ in range(NMON)])               # 294×294
Sigma_inv = np.linalg.inv(Sigma)

# ---- Fisher + CRLB, independent vs AR(1) ----
F_indep = (J.T @ J) / SIGMA ** 2
F_ar1 = J.T @ Sigma_inv @ J
crlb_indep = np.sqrt(np.diag(np.linalg.inv(F_indep)))
crlb_ar1 = np.sqrt(np.diag(np.linalg.inv(F_ar1)))

ess_factor = np.sqrt((1 + RHO) / (1 - RHO))              # scalar reference 1.53
n_eff = NT * NMON * (1 - RHO) / (1 + RHO)

print(f"=== Step 7c: AR(1) autocorrelation (ρ={RHO}) — Case A (k_w only) ===")
print(f"scalar ESS reference: inflation √[(1+ρ)/(1−ρ)] = {ess_factor:.2f}; "
      f"N_eff ≈ {n_eff:.0f} of {NT*NMON}\n")
print(f"{'coef':>8} | {'CRLB indep':>10} | {'CRLB AR(1)':>10} | {'widening':>8} | "
      f"{'CRLB/prior indep':>16} | {'CRLB/prior AR(1)':>16}")
report = {"rho": RHO, "ess_factor": float(ess_factor), "n_eff": float(n_eff), "coef": {}}
for j, z in enumerate(ZKEYS):
    wf = crlb_ar1[j] / crlb_indep[j]
    report["coef"][z] = {"crlb_indep": float(crlb_indep[j]), "crlb_ar1": float(crlb_ar1[j]),
                         "widening": float(wf),
                         "crlb_over_prior_indep": float(crlb_indep[j] / PRIOR_SD[z]),
                         "crlb_over_prior_ar1": float(crlb_ar1[j] / PRIOR_SD[z])}
    print(f"{z:>8} | {crlb_indep[j]:10.3f} | {crlb_ar1[j]:10.3f} | {wf:8.2f}x | "
          f"{crlb_indep[j]/PRIOR_SD[z]:16.2f} | {crlb_ar1[j]/PRIOR_SD[z]:16.2f}")

with open(os.path.join(HERE, "baseline_cache", "step7c_ar1.json"), "w") as f:
    json.dump(report, f, indent=2)
print("\nsaved step7c_ar1.json")
