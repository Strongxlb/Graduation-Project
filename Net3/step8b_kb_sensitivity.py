"""Step 8b: GLUE calibration under a misspecified k_b (± 20%) — Priority-2 #5.

The observations are generated with the true k_b = -0.5. We then re-run GLUE while FIXING k_b at
-0.4, -0.5, -0.6 (±20%) and see how the three grouped k_w behavioural means move to compensate
(the bulk–wall trade-off). This is the empirical partner to Fisher Case B.

k_b = -0.5 reuses the baseline cache; k_b = -0.4 / -0.6 are simulated here (all nodes, for risk).
Primary threshold 0.107; 30 noise realisations, median reported.
"""
import os
import json
import time
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
FIGDIR = os.path.join(HERE, "figures")
ZKEYS = ["old", "average", "new"]
TRUE = {"old": B.KW_OLD_TRUE, "average": B.KW_AVG_TRUE, "new": B.KW_NEW_TRUE}
C_MIN = 0.2

cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
ALL_NODES = list(cache["all_nodes"])
mon_pos = list(cache["mon_pos"])
truth_mon = cache["truth_all"][:, mon_pos]                # true field (k_b=-0.5) at monitors
S = {"old": cache["S_old"], "average": cache["S_avg"], "new": cache["S_new"]}
N_MC = B.N_MC
Tn = cache["obs_glue"].shape[0]

KBS = [-0.4, -0.5, -0.6]
N_NOISE = 30
SEEDS = list(range(42, 42 + N_NOISE))

# candidate predictions per k_b (all nodes); reuse baseline cache for k_b = -0.5
preds = {-0.5: cache["C_all"]}
for kb in [-0.4, -0.6]:
    Ck = np.empty((N_MC, Tn, len(ALL_NODES)), dtype=np.float32)
    t0 = time.time()
    for s in range(N_MC):
        Ck[s] = B.simulate_chlorine(kb, 0.0,
                                    pre_run=B.make_kw_hook(S["old"][s], S["average"][s], S["new"][s]),
                                    monitor_nodes=ALL_NODES).values[B.WARMUP_H:].astype(np.float32)
        if (s + 1) % 1000 == 0:
            print(f"  kb={kb}: {s+1}/{N_MC} ({time.time()-t0:.0f}s)")
    preds[kb] = Ck


def med(a):
    return float(np.median(a))


rows = []
for kb in KBS:
    Cmon = preds[kb][:, :, mon_pos]
    om, am, nm, sdo = [], [], [], []
    for seed in SEEDS:
        rng = np.random.default_rng(seed)
        obs = np.clip(truth_mon + rng.normal(0, B.SIGMA_OBS, truth_mon.shape), 0, None)[B.WARMUP_H:]
        rmse = np.sqrt(((Cmon - obs[None]) ** 2).mean(axis=(1, 2)))
        w = np.exp(-0.5 * (rmse / B.SIGMA_OBS) ** 2) * (rmse < B.RMSE_THR)
        if w.sum() == 0:
            continue
        w = w / w.sum()
        mo = float(np.sum(w * S["old"]))
        om.append(mo); am.append(float(np.sum(w * S["average"]))); nm.append(float(np.sum(w * S["new"])))
        sdo.append(float(np.sqrt(np.sum(w * (S["old"] - mo) ** 2))))
    # risk ranking at this kb (baseline obs, seed 42)
    rng = np.random.default_rng(42)
    obs0 = np.clip(truth_mon + rng.normal(0, B.SIGMA_OBS, truth_mon.shape), 0, None)[B.WARMUP_H:]
    rmse0 = np.sqrt(((Cmon - obs0[None]) ** 2).mean(axis=(1, 2)))
    w0 = np.exp(-0.5 * (rmse0 / B.SIGMA_OBS) ** 2) * (rmse0 < B.RMSE_THR)
    w0 = w0 / w0.sum()
    P = np.tensordot(w0, (preds[kb] < C_MIN).astype(float), axes=(0, 0)).mean(axis=0)
    rank = [ALL_NODES[i] for i in np.argsort(P)[::-1][:6]]
    rows.append({"kb": kb, "old": med(om), "avg": med(am), "new": med(nm),
                 "old_sd": med(sdo), "risk_top6": rank})

base = next(r for r in rows if r["kb"] == -0.5)
print("\n=== Step 8b: GLUE under misspecified k_b (obs generated at k_b=-0.5) ===")
print(f"{'k_b':>5} | {'old':>8} {'shift':>7} | {'avg':>8} | {'new':>8} | top-3 risk")
for r in rows:
    print(f"{r['kb']:>5} | {r['old']:>8.3f} {r['old']-base['old']:>+7.3f} | {r['avg']:>8.3f} | "
          f"{r['new']:>8.3f} | {list(r['risk_top6'][:3])}")
print(f"\nbaseline old behavioural SD = {base['old_sd']:.3f}")
print(f"old shift for ±20% k_b: {rows[0]['old']-base['old']:+.3f} (k_b=-0.4), "
      f"{rows[2]['old']-base['old']:+.3f} (k_b=-0.6)")

report = {"kbs": KBS, "rows": rows, "baseline_old_sd": base["old_sd"]}


def _jsafe(o):
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.integer):
        return int(o)
    return str(o)


# shift of each coefficient relative to the reference k_b, which is what the log tabulates
ref = next(r for r in rows if r["kb"] == B.KB_FIXED)
for r in rows:
    r["shift_vs_kb_ref"] = {k: r[k] - ref[k] for k in ("old", "avg", "new")}

with open(os.path.join(HERE, "baseline_cache", "step8b_kb_sensitivity.json"), "w") as f:
    json.dump(report, f, indent=2, default=_jsafe)

# ---- figure: kw behavioural means vs fixed k_b ----
fig, ax = plt.subplots(figsize=(8, 5))
kbs = [r["kb"] for r in rows]
KEY = {"old": "old", "average": "avg", "new": "new"}
for z, c in zip(ZKEYS, ["tab:red", "tab:orange", "tab:green"]):
    ax.plot(kbs, [r[KEY[z]] for r in rows], marker="o", color=c, label=f"{z}")
    ax.axhline(TRUE[z], color=c, ls=":", lw=1)
ax.axvline(-0.5, color="gray", ls="--", lw=1, label="true k_b")
ax.set_xlabel("fixed k_b in calibration (1/day)")
ax.set_ylabel("GLUE behavioural mean of k_w (m/day)")
ax.set_title("Step 8b — bulk–wall compensation: misspecifying k_b (±20%) shifts the k_w estimates\n"
             "(dotted = true k_w; risk ranking checked separately)")
ax.legend()
ax.grid(alpha=0.3)
plt.tight_layout()
figpath = os.path.join(FIGDIR, "step8b_kb_sensitivity.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")
print("figure saved to", figpath)
