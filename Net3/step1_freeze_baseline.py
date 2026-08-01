"""Step 1: freeze and cache the three-zone baseline.

Reproduces the main experiment of 03_pipeline_net3_02 exactly and caches every
candidate model prediction so that later experiments (threshold sensitivity, noise
sweep, sensor bias, ...) can recompute RMSE / weights WITHOUT re-running EPANET.

Outputs (in Net3/baseline_cache/):
  baseline.npz       - S_old/S_avg/S_new, RMSE, weights, behavioural, C_all (2000 x Tn x nodes),
                       truth_all, obs_glue, node lists, monitor positions
  baseline_meta.json - full config + verification summary
"""
import os
import json
import time
import numpy as np

import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "baseline_cache")
os.makedirs(OUT, exist_ok=True)

ALL_NODES = B.all_junctions()
mon_pos = [ALL_NODES.index(m) for m in B.MONITOR_NODES]

# 1) synthetic truth over the whole network (monitors are a subset)
truth_all_df = B.simulate_chlorine(
    B.KB_FIXED, 0.0,
    pre_run=B.make_kw_hook(B.KW_OLD_TRUE, B.KW_AVG_TRUE, B.KW_NEW_TRUE),
    monitor_nodes=ALL_NODES,
)
truth_all = truth_all_df.values                       # (73, 92)
truth_index = np.asarray(truth_all_df.index, dtype=float)
truth_mon = truth_all_df[B.MONITOR_NODES].values      # (73, 6)

# 2) baseline noisy observations: Gaussian(0, sigma) added to monitor truth, clipped >= 0
rng_noise = np.random.default_rng(B.NOISE_SEED)
raw = truth_mon + rng_noise.normal(0.0, B.SIGMA_OBS, size=truth_mon.shape)
n_clip = int((raw < 0).sum())
noisy = np.clip(raw, 0.0, None)                       # (73, 6)
obs_glue = noisy[B.WARMUP_H:]                          # (49, 6)
noise_rmse = float(np.sqrt(((noisy - truth_mon) ** 2).mean()))

# 3) 2000 uniform-prior parameter draws (seed 0), same order as the notebook
rng = np.random.default_rng(B.SAMPLE_SEED)
S_old = rng.uniform(*B.PRIOR["old"], B.N_MC)
S_avg = rng.uniform(*B.PRIOR["avg"], B.N_MC)
S_new = rng.uniform(*B.PRIOR["new"], B.N_MC)

# 4) forward each draw over the whole network; cache predictions and RMSE at monitors
Tn = obs_glue.shape[0]
C_all = np.empty((B.N_MC, Tn, len(ALL_NODES)), dtype=np.float32)
RMSE = np.empty(B.N_MC)
t0 = time.time()
for s in range(B.N_MC):
    cs = B.simulate_chlorine(
        B.KB_FIXED, 0.0,
        pre_run=B.make_kw_hook(S_old[s], S_avg[s], S_new[s]),
        monitor_nodes=ALL_NODES,
    ).values[B.WARMUP_H:]                              # (49, 92)
    C_all[s] = cs.astype(np.float32)
    d = cs[:, mon_pos] - obs_glue
    RMSE[s] = np.sqrt((d ** 2).mean())
    if (s + 1) % 500 == 0:
        print(f"  {s + 1}/{B.N_MC} forward runs ({time.time() - t0:.1f}s)")

# 5) informal Gaussian likelihood, behavioural filter, normalised weights
L = np.exp(-0.5 * (RMSE / B.SIGMA_OBS) ** 2)
behavioural = RMSE < B.RMSE_THR_DRAFT      # Step 1 reproduces the draft, which used 0.12
weights = L * behavioural
weights = weights / weights.sum()


def wmean(x):
    return float(np.sum(weights * x))


def wstd(x):
    m = wmean(x)
    return float(np.sqrt(np.sum(weights * (x - m) ** 2)))


summary = {
    "behavioural_count": int(behavioural.sum()),
    "retention_rate": float(behavioural.mean()),
    "rmse_min": float(RMSE.min()),
    "noise_rmse": noise_rmse,
    "n_clip": n_clip,
    "Tn": int(Tn),
    "n_nodes": len(ALL_NODES),
    "kw_old_mean_sd": [wmean(S_old), wstd(S_old)],
    "kw_avg_mean_sd": [wmean(S_avg), wstd(S_avg)],
    "kw_new_mean_sd": [wmean(S_new), wstd(S_new)],
    "true": [B.KW_OLD_TRUE, B.KW_AVG_TRUE, B.KW_NEW_TRUE],
    "runtime_s": round(time.time() - t0, 1),
}

config = {
    "monitor_nodes": B.MONITOR_NODES,
    "inlet_mgl": B.INLET_CHLORINE_MGL, "tank_mgl": B.TANK_INIT_MGL,
    "duration_h": B.DURATION_H, "warmup_h": B.WARMUP_H,
    "hydraulic_timestep_s": B.HYDRAULIC_TIMESTEP_S,
    "report_timestep_s": B.REPORT_TIMESTEP_S,
    "quality_timestep_s": B.QUALITY_TIMESTEP_S,
    "kb_fixed": B.KB_FIXED,
    "kw_true": [B.KW_OLD_TRUE, B.KW_AVG_TRUE, B.KW_NEW_TRUE],
    "prior": B.PRIOR, "n_mc": B.N_MC, "sigma_obs": B.SIGMA_OBS,
    "rmse_thr": B.RMSE_THR_DRAFT, "noise_seed": B.NOISE_SEED, "sample_seed": B.SAMPLE_SEED,
    "sigma_convention": "sigma = 0.1 mg/L is one standard deviation of the Gaussian observation error",
}

np.savez_compressed(
    os.path.join(OUT, "baseline.npz"),
    S_old=S_old, S_avg=S_avg, S_new=S_new,
    RMSE=RMSE, weights=weights, behavioural=behavioural,
    C_all=C_all, truth_all=truth_all, truth_index=truth_index,
    obs_glue=obs_glue, noisy=noisy,
    all_nodes=np.asarray(ALL_NODES), monitor_nodes=np.asarray(B.MONITOR_NODES),
    mon_pos=np.asarray(mon_pos),
)
with open(os.path.join(OUT, "baseline_meta.json"), "w") as f:
    json.dump({"config": config, "summary": summary}, f, indent=2)

print("\n=== baseline frozen ===")
print(json.dumps(summary, indent=2))
print("\nDraft reported for cross-check: behavioural 1685/2000, RMSE_min 0.098,")
print("kw_old -0.96+/-0.32, kw_avg -0.12+/-0.045, kw_new -0.053+/-0.027")
print("cache saved to", OUT)
