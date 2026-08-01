"""Step 4d: robust displaced-prior experiment (option d = a + b).

Two displacement designs, each keeping prior width fixed and the truth inside the range:
  DOWN    : all three midpoints set to  truth - 1 prior SD  (into the strong-decay regime)
  UP_OLD  : old midpoint set to  truth + 1 prior SD  (weaker/steep side; upper bound capped
            at -0.005 to stay non-positive); avg/new kept at their baseline (centred) priors.

For each design the 2000 forward simulations are run ONCE (monitors only) and cached; then the
gap-closing statistic is recomputed over N_NOISE independent noisy observation sets and two
behavioural thresholds. Robustness is reported as median [IQR] across the noise realisations.

gap_closed = (behavioural_mean - displaced_mid) / (truth - displaced_mid)
  0  = behavioural mean stayed at the displaced prior midpoint (data uninformative)
  1  = behavioural mean pulled all the way to the truth (data fully informative)
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
os.makedirs(FIGDIR, exist_ok=True)

cache = np.load(os.path.join(HERE, "baseline_cache", "baseline.npz"), allow_pickle=True)
ALL_NODES = list(cache["all_nodes"])
mon_pos = list(cache["mon_pos"])
truth_mon = cache["truth_all"][:, mon_pos]          # (73, 6) noise-free monitor truth

TRUE = {"old": B.KW_OLD_TRUE, "avg": B.KW_AVG_TRUE, "new": B.KW_NEW_TRUE}
GROUPS = ["old", "avg", "new"]
THRESHOLDS = [0.107, 0.12]
N_NOISE = 30
NOISE_SEEDS = list(range(42, 42 + N_NOISE))
UPPER_CAP = -0.005


def prior_sd(rng):
    a, b = rng
    return (b - a) / np.sqrt(12)


def down_range(orig, truth):
    a, b = orig
    w = b - a
    mid = truth - w / np.sqrt(12)
    return (mid - w / 2, mid + w / 2)


def up_range(orig, truth, cap=UPPER_CAP):
    a, b = orig
    w = b - a
    mid = truth + w / np.sqrt(12)
    lo, hi = mid - w / 2, mid + w / 2
    if hi > cap:                       # shift window down to keep it non-positive
        shift = hi - cap
        lo, hi = lo - shift, hi - shift
    return (lo, hi)


def run_design(name, priors):
    """priors: dict group -> (a,b). Returns cached monitor predictions + midpoints."""
    rng = np.random.default_rng(B.SAMPLE_SEED)
    S = {g: rng.uniform(*priors[g], B.N_MC) for g in GROUPS}
    preds = np.empty((B.N_MC, truth_mon.shape[0] - B.WARMUP_H, len(B.MONITOR_NODES)),
                     dtype=np.float32)
    t0 = time.time()
    for s in range(B.N_MC):
        preds[s] = B.simulate_chlorine(
            B.KB_FIXED, 0.0,
            pre_run=B.make_kw_hook(S["old"][s], S["avg"][s], S["new"][s]),
        ).values[B.WARMUP_H:].astype(np.float32)
        if (s + 1) % 500 == 0:
            print(f"  [{name}] {s + 1}/{B.N_MC} ({time.time() - t0:.1f}s)")
    mids = {g: 0.5 * (priors[g][0] + priors[g][1]) for g in GROUPS}
    return S, preds, mids


def evaluate(S, preds, mids, priors):
    """Return per-threshold, per-group arrays of gap_closed / sd_retained / retention
    across the N_NOISE noisy observation sets."""
    out = {thr: {g: {"gap": [], "sd_ret": []} for g in GROUPS} for thr in THRESHOLDS}
    out_ret = {thr: [] for thr in THRESHOLDS}
    psd = {g: prior_sd(priors[g]) for g in GROUPS}
    for seed in NOISE_SEEDS:
        rng = np.random.default_rng(seed)
        obs = np.clip(truth_mon + rng.normal(0, B.SIGMA_OBS, truth_mon.shape), 0, None)
        obs = obs[B.WARMUP_H:]
        rmse = np.sqrt(((preds - obs[None]) ** 2).mean(axis=(1, 2)))
        L = np.exp(-0.5 * (rmse / B.SIGMA_OBS) ** 2)
        for thr in THRESHOLDS:
            beh = rmse < thr
            w = L * beh
            if w.sum() == 0:
                continue
            w = w / w.sum()
            out_ret[thr].append(float(beh.mean()))
            for g in GROUPS:
                m = float(np.sum(w * S[g]))
                sd = float(np.sqrt(np.sum(w * (S[g] - m) ** 2)))
                denom = TRUE[g] - mids[g]
                gap = (m - mids[g]) / denom if abs(denom) > 1e-9 else np.nan
                out[thr][g]["gap"].append(gap)
                out[thr][g]["sd_ret"].append(sd / psd[g])
    return out, out_ret


def med_iqr(a):
    a = np.asarray(a, float)
    a = a[~np.isnan(a)]
    if len(a) == 0:
        return (np.nan, np.nan, np.nan)
    return (float(np.median(a)), float(np.percentile(a, 25)), float(np.percentile(a, 75)))


# ---- designs (both displace all three so every gap-closed is valid) ----
#   DOWN  : old down, avg down, new down (all into the strong-decay regime)
#   OLDUP : old up (weak/steep side), avg down, new down
PRIORS_DOWN = {g: down_range(B.PRIOR[g], TRUE[g]) for g in GROUPS}
PRIORS_OLDUP = {"old": up_range(B.PRIOR["old"], TRUE["old"]),
                "avg": down_range(B.PRIOR["avg"], TRUE["avg"]),
                "new": down_range(B.PRIOR["new"], TRUE["new"])}
DESIGNS = [("DOWN", PRIORS_DOWN), ("OLDUP", PRIORS_OLDUP)]
for name, pr in DESIGNS:
    for g in GROUPS:
        a, b = pr[g]
        assert b <= 1e-9, f"{name}/{g} upper bound positive"
        assert a <= TRUE[g] <= b, f"{name}/{g} truth not in range"

report = {"n_noise": N_NOISE, "thresholds": THRESHOLDS, "designs": {}}
box = {thr: {} for thr in THRESHOLDS}   # for the figure

for name, priors in DESIGNS:
    S, preds, mids = run_design(name, priors)
    ev, ret = evaluate(S, preds, mids, priors)
    report["designs"][name] = {"priors": {g: list(priors[g]) for g in GROUPS},
                               "midpoints": mids, "thresholds": {}}
    for thr in THRESHOLDS:
        gstats = {}
        for g in GROUPS:
            gm, glo, ghi = med_iqr(ev[thr][g]["gap"])
            sm, slo, shi = med_iqr(ev[thr][g]["sd_ret"])
            gstats[g] = {"gap_med": gm, "gap_iqr": [glo, ghi],
                         "sd_ret_med": sm, "sd_ret_iqr": [slo, shi]}
            box[thr][f"{g}\n({name})"] = [x for x in ev[thr][g]["gap"] if not np.isnan(x)]
        rm, rlo, rhi = med_iqr(ret[thr])
        report["designs"][name]["thresholds"][str(thr)] = {
            "retention_med": rm, "retention_iqr": [rlo, rhi], "groups": gstats}

with open(os.path.join(HERE, "baseline_cache", "step4d_displaced_robust.json"), "w") as f:
    json.dump(report, f, indent=2)

# ---- print summary ----
for name in ["DOWN", "OLDUP"]:
    print(f"\n=== {name} ===  priors: " +
          ", ".join(f"{g}[{report['designs'][name]['priors'][g][0]:.3f},"
                    f"{report['designs'][name]['priors'][g][1]:.3f}]" for g in GROUPS))
    for thr in THRESHOLDS:
        d = report["designs"][name]["thresholds"][str(thr)]
        print(f"  thr={thr} retention {d['retention_med']*100:.0f}% :")
        for g in GROUPS:
            s = d["groups"][g]
            print(f"    {g:>3}: gap closed {s['gap_med']*100:5.0f}% "
                  f"[{s['gap_iqr'][0]*100:.0f}-{s['gap_iqr'][1]*100:.0f}%]  "
                  f"SD retained {s['sd_ret_med']*100:4.0f}%")

# ---- figure: boxplots of gap_closed over noise realisations ----
fig, axes = plt.subplots(1, len(THRESHOLDS), figsize=(15, 4.8), sharey=True)
series_order = ["old\n(DOWN)", "old\n(OLDUP)", "avg\n(DOWN)", "avg\n(OLDUP)",
                "new\n(DOWN)", "new\n(OLDUP)"]
for ax, thr in zip(axes, THRESHOLDS):
    data = [box[thr][k] for k in series_order]
    ax.boxplot(data, labels=[k.replace("\n", " ") for k in series_order], showmeans=True)
    ax.axhline(0.0, color="gray", ls=":", lw=1, label="0% (stayed at prior mid)")
    ax.axhline(1.0, color="green", ls="--", lw=1, label="100% (reached truth)")
    ax.set_title(f"threshold {thr}")
    ax.set_ylabel("gap to truth closed")
    ax.tick_params(axis="x", labelrotation=20)
    ax.grid(alpha=0.3, axis="y")
axes[0].legend(fontsize=8, loc="upper left")
fig.suptitle(f"Displaced-prior pull-back over {N_NOISE} noise realisations "
             "(all three displaced; old recovered only from the weak/steep side)", y=1.02)
plt.tight_layout()
figpath = os.path.join(FIGDIR, "step4d_displaced_robust.png")
plt.savefig(figpath, dpi=130, bbox_inches="tight")
print("\nfigure saved to", figpath)
