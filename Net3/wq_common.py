"""Frozen three-zone baseline configuration and WNTR/EPANET helpers.

This module fixes every choice of the main calibration experiment (originally in
03_pipeline_net3_02.ipynb) so that all follow-up experiments (threshold sensitivity,
displaced prior, structural error, noise sweep, Fisher information, sensor bias) run
against exactly the same synthetic truth, monitoring array, seeds and priors.

sigma = 0.1 mg/L is interpreted as ONE standard deviation of the Gaussian
observation error.
"""
import os
import numpy as np
import wntr

PRACTICE_INP = os.path.join(os.path.dirname(wntr.__file__),
                            "library", "networks", "Net3.inp")

# ---- monitoring array: two nodes per zone (new 107/113 | old 15/145 | average 209/231) ----
MONITOR_NODES = ["107", "113", "15", "145", "209", "231"]

# ---- boundary / initial conditions ----
INLET_CHLORINE_MGL = 1.0
TANK_INIT_MGL = 0.5
SECONDS_PER_DAY = 24 * 3600

# ---- simulation timing ----
DURATION_H = 72
WARMUP_H = 24
HYDRAULIC_TIMESTEP_S = 3600
REPORT_TIMESTEP_S = 3600
QUALITY_TIMESTEP_S = 300

# ---- fixed / true parameters (m/day for wall, 1/day for bulk) ----
KB_FIXED = -0.5
KW_OLD_TRUE, KW_AVG_TRUE, KW_NEW_TRUE = -1.0, -0.1, -0.05

# ---- GLUE configuration ----
PRIOR = {"old": (-1.5, -0.2), "avg": (-0.2, -0.04), "new": (-0.10, -0.005)}
N_MC = 2000
SIGMA_OBS = 0.1          # one standard deviation of the Gaussian observation error (mg/L)
RMSE_THR = 0.12
NOISE_SEED = 42          # seed for the baseline noisy observation set
SAMPLE_SEED = 0          # seed for the 2000 uniform-prior parameter draws

# ---- three contiguous zones by node coordinates ----
ZONE_Y_LOW = 10.0
ZONE_X_MID = 26.0
ZONE_RANK = {"new": 0, "average": 1, "old": 2}


def per_day_to_per_second(v):
    return v / SECONDS_PER_DAY


def zone_of(x, y):
    """Bottom band (y <= 10) = average; otherwise left (x <= 26) = new, right = old."""
    if y <= ZONE_Y_LOW:
        return "average"
    return "new" if x <= ZONE_X_MID else "old"


def assign_materials_zones(inp_file=PRACTICE_INP):
    """Assign each pipe to a zone; a cross-zone pipe is given the weaker (newer) side."""
    wn = wntr.network.WaterNetworkModel(inp_file)
    mat = {}
    for p in wn.pipe_name_list:
        lk = wn.get_link(p)
        zs = zone_of(*wn.get_node(lk.start_node_name).coordinates)
        ze = zone_of(*wn.get_node(lk.end_node_name).coordinates)
        mat[p] = zs if zs == ze else (zs if ZONE_RANK[zs] <= ZONE_RANK[ze] else ze)
    return mat


MATERIAL_ZONES = assign_materials_zones()


def make_kw_hook(kw_old, kw_avg, kw_new, material=None):
    """Return a pre_run hook that sets per-pipe wall_coeff by zone."""
    mat = MATERIAL_ZONES if material is None else material
    kwz = {"old": kw_old, "average": kw_avg, "new": kw_new}

    def _hook(wn):
        for p in wn.pipe_name_list:
            wn.get_link(p).wall_coeff = per_day_to_per_second(kwz[mat[p]])
    return _hook


def simulate_chlorine(kb_per_day, kw_per_day, monitor_nodes=None, inp_file=PRACTICE_INP,
                      inlet_mgl=INLET_CHLORINE_MGL, tank_mgl=TANK_INIT_MGL,
                      duration_hours=DURATION_H, bulk_order=1, wall_order=1, pre_run=None):
    """Single chlorine simulation. Returns a DataFrame (index = hours, cols = nodes)."""
    if monitor_nodes is None:
        monitor_nodes = MONITOR_NODES
    wn = wntr.network.WaterNetworkModel(inp_file)
    wn.options.time.duration = duration_hours * 3600
    wn.options.time.hydraulic_timestep = HYDRAULIC_TIMESTEP_S
    wn.options.time.report_timestep = REPORT_TIMESTEP_S
    wn.options.time.quality_timestep = QUALITY_TIMESTEP_S
    wn.options.quality.parameter = "CHEMICAL"
    wn.options.quality.chemical_name = "Chlorine"
    wn.options.quality.inpfile_units = "mg/L"
    wn.options.reaction.bulk_order = bulk_order
    wn.options.reaction.wall_order = wall_order
    wn.options.reaction.bulk_coeff = per_day_to_per_second(kb_per_day)
    wn.options.reaction.wall_coeff = per_day_to_per_second(kw_per_day)
    for r in wn.reservoir_name_list:
        wn.get_node(r).initial_quality = inlet_mgl
    for t in wn.tank_name_list:
        wn.get_node(t).initial_quality = tank_mgl
    if pre_run is not None:
        pre_run(wn)
    res = wntr.sim.EpanetSimulator(wn).run_sim()
    q = res.node["quality"][monitor_nodes]
    q.index = q.index / 3600.0
    q.index.name = "hours"
    return q


def all_junctions(inp_file=PRACTICE_INP):
    return wntr.network.WaterNetworkModel(inp_file).junction_name_list
