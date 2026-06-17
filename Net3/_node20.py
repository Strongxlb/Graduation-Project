import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import wntr

SECONDS_PER_DAY = 24 * 3600
p2s = lambda v: v / SECONDS_PER_DAY
INP = os.path.join(os.path.dirname(wntr.__file__), "library", "networks", "Net3.inp")
MON = ["10", "15", "20", "35", "40", "60"]

def simulate_chlorine(kb, kw, duration_hours=72, bulk_order=1, wall_order=1):
    wn = wntr.network.WaterNetworkModel(INP)
    wn.options.time.duration = duration_hours * 3600
    wn.options.time.hydraulic_timestep = 3600
    wn.options.time.report_timestep = 3600
    wn.options.time.quality_timestep = 300
    wn.options.quality.parameter = "CHEMICAL"; wn.options.quality.inpfile_units = "mg/L"
    wn.options.reaction.bulk_order = bulk_order; wn.options.reaction.wall_order = wall_order
    wn.options.reaction.bulk_coeff = p2s(kb); wn.options.reaction.wall_coeff = p2s(kw)
    for r in wn.reservoir_name_list: wn.get_node(r).initial_quality = 1.0
    res = wntr.sim.EpanetSimulator(wn).run_sim()
    q = res.node["quality"][MON]; q.index = q.index / 3600.0
    return q

def simulate_age(duration_hours=72):
    wn = wntr.network.WaterNetworkModel(INP)
    wn.options.time.duration = duration_hours * 3600
    wn.options.time.report_timestep = 3600
    wn.options.quality.parameter = "AGE"
    res = wntr.sim.EpanetSimulator(wn).run_sim()
    age = res.node["quality"][MON] / 3600.0; age.index = age.index / 3600.0
    return age

ts_zero = simulate_chlorine(kb=-0.3, kw=0.0, bulk_order=0, wall_order=0, duration_hours=72)
age = simulate_age(72)

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 7), sharex=True)
ax1.plot(ts_zero.index, ts_zero["20"], color="tab:blue", lw=1.8)
ax1.set_ylabel("C at node 20 (mg/L)")
ax1.set_title("Node 20 — concentration over time (zero-order)")
ax1.grid(alpha=0.3)

ax2.plot(age.index, age["20"], color="tab:red", lw=1.8)
ax2.set_ylabel("water age at node 20 (h)")
ax2.set_xlabel("hours")
ax2.set_title("Node 20 — water age over time")
ax2.grid(alpha=0.3)

plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "_node20.png")
plt.savefig(out, dpi=130)
print("saved", out)
print("C range:", round(ts_zero["20"].min(), 3), "to", round(ts_zero["20"].max(), 3))
print("age range:", round(age["20"].min(), 2), "to", round(age["20"].max(), 2))
