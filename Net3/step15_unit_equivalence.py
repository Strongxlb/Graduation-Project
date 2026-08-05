"""Step 15: what the chlorine concentration unit correction changed — measured, not asserted.

BACKGROUND. WNTR's Python API stores concentration internally in kg/m^3. `options.quality.
inpfile_units` governs only how the .inp is read and written, so assigning 1.0 to `initial_quality`
intending "1 mg/L" makes EPANET simulate 1000 mg/L, and reading `run_sim()` output as mg/L repeats
the error on the way out. Every concentration in this project was on that scale until it was fixed.

WHY IT WAS INVISIBLE. Under FIRST-order kinetics the field is linear in the source, and sigma and
the risk threshold were expressed on the same (wrong) scale, so every ratio the analysis depends on
was preserved. The reaction coefficients were never affected: k_b is 1/time and k_w is length/time,
so neither carries a mass unit — verified in step13 arm 2/3 and by the values WNTR writes into the
.inp (GLOBAL BULK -0.5000; WALL -3.2808 / -0.3281 / -0.1640 ft/day).

THE TRAP INSIDE THE FIX. EPANET's water-quality tolerance is an ABSOLUTE concentration. At the old
scale 0.01 was 1e-5 of the source; at the corrected scale it would be 1e-2 of it. Correcting the
units without scaling the tolerance therefore does not relabel the experiment, it coarsens it. That
is what arm C measures, and it is the reason wq_common.QUALITY_TOLERANCE exists.

THREE ARMS, same 256 leading Sobol candidates (a leading 2^k subset is itself a balanced design):

  legacy      initial_quality assigned raw (the superseded configuration), tolerance 0.01
              -> its raw output is exactly what the old cache stored and the log used to quote
  corrected   the current configuration: converted on the way in, mg/L on the way out, tol 1e-5
  units_only  converted, but tolerance left at 0.01 — the fix done wrong

`legacy` and `corrected` report the same quantity (what the log calls mg/L), so they are compared
directly. If the correction is a relabelling, they agree to floating point.

Reuses no cache and re-runs EPANET; ~3 x 256 runs.
"""
import json
import os

import numpy as np
import wntr

import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "baseline_cache")
N = 256
LEGACY_TOLERANCE = 0.01          # the EPANET default, and what the superseded configuration used
C_MIN = 0.2                      # mg/L, the operational threshold the risk map uses

ALL_NODES = B.all_junctions()
draws = B.prior_draws()
S = (draws["old"][:N], draws["avg"][:N], draws["new"][:N])


def simulate(kw, arm):
    """Post-warm-up field for one candidate under one arm, in the units that arm reports."""
    wn = B.build_model(B.KB_FIXED, 0.0, pre_run=B.make_kw_hook(*kw))
    if arm == "legacy":
        # undo the conversion build_model now applies, and restore the old absolute tolerance
        for r in wn.reservoir_name_list:
            wn.get_node(r).initial_quality = B.INLET_CHLORINE_MGL
        for t in wn.tank_name_list:
            wn.get_node(t).initial_quality = B.TANK_INIT_MGL
        wn.options.quality.tolerance = LEGACY_TOLERANCE
    elif arm == "units_only":
        wn.options.quality.tolerance = LEGACY_TOLERANCE
    elif arm != "corrected":
        raise ValueError(arm)
    res = wntr.sim.EpanetSimulator(wn).run_sim(file_prefix=f"s15_{arm}")
    q = res.node["quality"][ALL_NODES].values[B.WARMUP_H:]
    # legacy reported the raw internal array as if it were mg/L; the other two convert honestly
    return q if arm == "legacy" else B.internal_to_mgl(q)


ARMS = ("legacy", "corrected", "units_only")
field = {a: np.empty((N, B.DURATION_H - B.WARMUP_H + 1, len(ALL_NODES))) for a in ARMS}
print("=== Step 15: what the concentration-unit correction changed ===")
print(f"{N} leading Sobol candidates x {len(ARMS)} arms; legacy tolerance {LEGACY_TOLERANCE}, "
      f"corrected {B.QUALITY_TOLERANCE:g} kg/m^3\n")
for i in range(N):
    kw = (S[0][i], S[1][i], S[2][i])
    for a in ARMS:
        field[a][i] = simulate(kw, a)
    if (i + 1) % 64 == 0:
        print(f"  {i + 1}/{N}")


def compare(ref, other):
    d = np.abs(ref - other)
    rel = d / np.maximum(np.abs(ref), 1e-12)
    low = ref < C_MIN                                   # where the risk map is decided
    dur_ref = (ref < C_MIN).sum(axis=1)
    dur_oth = (other < C_MIN).sum(axis=1)
    return {
        "max_abs_diff_mg_L": float(d.max()),
        "max_rel_diff": float(rel.max()),
        "median_rel_diff": float(np.median(rel)),
        "max_rel_diff_below_threshold": float(rel[low].max()) if low.any() else None,
        "n_points_below_threshold_ref": int(low.sum()),
        "n_points_below_threshold_other": int((other < C_MIN).sum()),
        "n_cells_with_different_hours_below": int((dur_ref != dur_oth).sum()),
        "n_cells": int(dur_ref.size),
    }


res = {"corrected_vs_legacy": compare(field["legacy"], field["corrected"]),
       "units_only_vs_legacy": compare(field["legacy"], field["units_only"])}

for name, r in res.items():
    print(f"\n--- {name} ---")
    print(f"  max abs diff            {r['max_abs_diff_mg_L']:.3e} mg/L")
    print(f"  max rel diff            {r['max_rel_diff']:.3e}")
    print(f"  median rel diff         {r['median_rel_diff']:.3e}")
    print(f"  max rel diff below 0.2  {r['max_rel_diff_below_threshold']:.3e}")
    print(f"  points below 0.2        {r['n_points_below_threshold_ref']} -> "
          f"{r['n_points_below_threshold_other']}")
    print(f"  hours-below cells that differ  {r['n_cells_with_different_hours_below']} of "
          f"{r['n_cells']}")

verdict = ("the correction is a relabelling: the reported field is unchanged to floating point"
           if res["corrected_vs_legacy"]["max_rel_diff"] < 1e-5 else
           "the correction changes the reported field and must be treated as a new result")
print(f"\nVERDICT: {verdict}")
print("The units_only arm is the counterfactual: correcting the units WITHOUT scaling the absolute")
print("quality tolerance does change the answer, which is why the tolerance moves with the unit.")

report = {
    "weighting": "none — this step compares raw simulated fields, no ensemble is weighted",
    "n_candidates": N,
    "arms": {
        "legacy": f"initial_quality assigned raw (superseded), tolerance {LEGACY_TOLERANCE}; its "
                  f"output is what the pre-correction cache stored and the log quoted as mg/L",
        "corrected": f"current configuration: mg/L -> kg/m^3 on the way in, kg/m^3 -> mg/L on the "
                     f"way out, tolerance {B.QUALITY_TOLERANCE:g} kg/m^3",
        "units_only": f"units corrected but tolerance left at {LEGACY_TOLERANCE} — the fix done "
                      f"wrong, kept as the counterfactual",
    },
    "legacy_tolerance": LEGACY_TOLERANCE,
    "corrected_tolerance_kg_m3": B.QUALITY_TOLERANCE,
    "C_MIN_mg_L": C_MIN,
    "comparisons": res,
    "verdict": verdict,
    "coefficients_note": "k_b (1/time) and k_w (length/time) carry no mass unit and were never "
                         "affected; step13 arms 1-3 verify them against an analytic solution and "
                         "step13 arm 4 pins the concentration unit against WNTR's own to_si/from_si",
}
with open(os.path.join(OUT, "step15_unit_equivalence.json"), "w") as f:
    json.dump(report, f, indent=2)
print("\nsaved step15_unit_equivalence.json")
