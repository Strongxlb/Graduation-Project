import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import wntr

INP = os.path.join(os.path.dirname(wntr.__file__), "library", "networks", "Net3.inp")
wn = wntr.network.WaterNetworkModel(INP)

print("=" * 60)
print("NET3 COMPOSITION")
print("=" * 60)
print("junctions (需水节点):", len(wn.junction_name_list))
print("pipes (管段)       :", len(wn.pipe_name_list))
print("reservoirs (水源)  :", wn.reservoir_name_list)
print("tanks (水箱)       :", wn.tank_name_list)
print("pumps (泵)         :", wn.pump_name_list)
print("valves (阀)        :", wn.valve_name_list)
print("patterns (模式)    :", wn.pattern_name_list)

print("\n--- TANKS (水箱) ---")
for t in wn.tank_name_list:
    tk = wn.get_node(t)
    print(f"  tank {t}: elevation={tk.elevation:.1f} m, init_level={tk.init_level:.2f} m, "
          f"min={tk.min_level:.2f}, max={tk.max_level:.2f}, diameter={tk.diameter:.1f} m")

print("\n--- a few JUNCTIONS: base demand + pattern ---")
for j in wn.junction_name_list[:6]:
    nd = wn.get_node(j)
    dts = nd.demand_timeseries_list[0] if len(nd.demand_timeseries_list) else None
    base = dts.base_value if dts is not None else 0.0
    pat = dts.pattern_name if (dts is not None and dts.pattern_name) else "(none)"
    print(f"  junction {j}: base_demand={base*1000:.2f} L/s, pattern={pat}")

print("\n--- DEMAND PATTERN multipliers (diurnal) ---")
for pn in wn.pattern_name_list:
    mult = wn.get_pattern(pn).multipliers
    print(f"  pattern {pn} ({len(mult)} steps): {np.round(mult,2).tolist()}")

# ---- plot: demand pattern + tank levels over time ----
wn.options.time.duration = 72 * 3600
sim = wntr.sim.EpanetSimulator(wn).run_sim()
head = sim.node["head"]

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 8))

# panel 1: the diurnal demand multiplier (pattern '1')
pstep_h = wn.options.time.pattern_timestep / 3600.0
m = wn.get_pattern("1").multipliers
hrs = np.arange(len(m)) * pstep_h
ax1.step(hrs, m, where="post", lw=2.0, color="tab:green")
ax1.axhline(1.0, color="grey", ls="--", lw=0.8, label="mean = 1.0")
ax1.set_xlabel("hour of day"); ax1.set_ylabel("demand multiplier")
ax1.set_title("Net3 diurnal demand pattern '1'  (actual demand = base x multiplier)")
ax1.legend(fontsize=8); ax1.grid(alpha=0.3)

# panel 2: tank water level over 72 h
for t in wn.tank_name_list:
    level = head[t] - wn.get_node(t).elevation
    ax2.plot(level.index / 3600.0, level, lw=1.8, label=f"tank {t}")
ax2.set_xlabel("hours"); ax2.set_ylabel("tank water level (m)")
ax2.set_title("Net3 tank levels over time (fill / drain)")
ax2.legend(fontsize=8); ax2.grid(alpha=0.3)

plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "_net3data.png")
plt.savefig(out, dpi=130)
print("\nsaved", out)
