"""Step 8c: does the sensor-bias location matter? Inject the SAME offset at each of the six monitors
in turn and compare (answers "why node 15, and would other nodes differ?").

Monitors are two-per-zone: new 107/113 | old 15/145 | average 209/231. A constant offset is added
to one monitor's column, GLUE is re-run (cache reused, threshold 0.107, 30 noise realisations), and
we report the shift of every coefficient's behavioural mean relative to its own baseline SD.
"""
import os
import json
import numpy as np
import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
ZKEYS = ["old", "average", "new"]
ZONE_OF = {"107": "new", "113": "new", "15": "old", "145": "old", "209": "average", "231": "average"}

cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
C_all = cache["C_all"]
ALL_NODES = list(cache["all_nodes"])
mon_pos = list(cache["mon_pos"])
truth_mon = cache["truth_all"][:, mon_pos]
S = {"old": cache["S_old"], "average": cache["S_avg"], "new": cache["S_new"]}
C_all_mon = C_all[:, :, mon_pos]
C_MIN, thr = 0.2, B.RMSE_THR
OFFSETS = [0.05, 0.10]
SEEDS = list(range(42, 72))


def glue(obs_post):
    rmse = np.sqrt(((C_all_mon - obs_post[None]) ** 2).mean(axis=(1, 2)))
    w = np.exp(-0.5 * (rmse / B.SIGMA_OBS) ** 2) * (rmse < thr)
    if w.sum() == 0:
        return None, None, None
    w = w / w.sum()
    means = {z: float(np.sum(w * S[z])) for z in ZKEYS}
    sds = {z: float(np.sqrt(np.sum(w * (S[z] - means[z]) ** 2))) for z in ZKEYS}
    below = (C_all < C_MIN)
    P = np.tensordot(w, below.astype(float), axes=(0, 0)).mean(axis=0)
    rank = [ALL_NODES[i] for i in np.argsort(P)[::-1][:3]]
    return means, sds, rank


def run(bcol, off):
    ms = {z: [] for z in ZKEYS}
    ranks = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        obs = truth_mon + rng.normal(0, B.SIGMA_OBS, truth_mon.shape)
        if bcol is not None:
            obs[:, bcol] += off
        obs = np.clip(obs, 0, None)[B.WARMUP_H:]
        means, sds, rank = glue(obs)
        if means is None:
            continue
        for z in ZKEYS:
            ms[z].append(means[z])
        ranks.append(tuple(rank))
    return ({z: float(np.median(ms[z])) for z in ZKEYS},
            max(set(ranks), key=ranks.count))


# unbiased baseline (means + per-coefficient SD)
base_means, base_rank = run(None, 0.0)
base_sd = {}
for z in ZKEYS:
    vals = []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        obs = np.clip(truth_mon + rng.normal(0, B.SIGMA_OBS, truth_mon.shape), 0, None)[B.WARMUP_H:]
        m, s, _ = glue(obs)
        if s:
            vals.append(s[z])
    base_sd[z] = float(np.median(vals))

print("=== Step 8c: bias location sweep (threshold 0.107, 30 noise) ===")
print(f"unbiased baseline means: old {base_means['old']:.3f}  avg {base_means['average']:.3f}  "
      f"new {base_means['new']:.3f}")
print(f"baseline behavioural SDs: old {base_sd['old']:.3f}  avg {base_sd['average']:.3f}  "
      f"new {base_sd['new']:.3f}\n")

report = {"threshold": thr, "base_means": base_means, "base_sd": base_sd, "base_rank": list(base_rank),
          "offsets": OFFSETS, "rows": []}
for off in OFFSETS:
    print(f"--- offset = +{off} mg/L ---")
    print(f"{'node':>5} {'zone':>8} | {'Δold':>7} {'Δavg':>7} {'Δnew':>7} | "
          f"{'own-coef shift/SD':>17} | top-3 risk")
    for node in B.MONITOR_NODES:
        bcol = B.MONITOR_NODES.index(node)
        means, rank = run(bcol, off)
        d = {z: means[z] - base_means[z] for z in ZKEYS}
        own = ZONE_OF[node]
        s_over_sd = d[own] / base_sd[own]
        rank_same = "same" if tuple(rank) == tuple(base_rank) else str(list(rank))
        report["rows"].append({"node": node, "zone": own, "offset": off,
                               "d_old": d["old"], "d_avg": d["average"], "d_new": d["new"],
                               "own_shift_over_sd": s_over_sd, "rank": list(rank)})
        print(f"{node:>5} {own:>8} | {d['old']:>+7.3f} {d['average']:>+7.3f} {d['new']:>+7.3f} | "
              f"{s_over_sd:>+17.2f} | {rank_same}")
    print()

with open(os.path.join(HERE, "baseline_cache", "step8c_bias_bynode.json"), "w") as f:
    json.dump(report, f, indent=2)
print("saved step8c_bias_bynode.json")
