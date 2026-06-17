import os, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import wntr

INP = os.path.join(os.path.dirname(wntr.__file__), "library", "networks", "Net3.inp")
MON = ["10", "15", "20", "35", "40", "60"]

wn = wntr.network.WaterNetworkModel(INP)
wn.options.time.duration = 96 * 3600
wn.options.time.report_timestep = 3600
wn.options.quality.parameter = "AGE"
res = wntr.sim.EpanetSimulator(wn).run_sim()
age = (res.node["quality"] / 3600.0).iloc[-24:].mean()   # steady-ish mean age (h)

cap = float(np.round(np.nanpercentile(age.values, 92)))   # clip scale to avoid stagnant outliers
print("age stats (h): min %.1f  median %.1f  max %.1f  -> colorbar cap %.0f"
      % (age.min(), age.median(), age.max(), cap))
print("oldest nodes:", age.sort_values(ascending=False).head(5).round(1).to_dict())

age_clip = age.clip(upper=cap)

fig, ax = plt.subplots(figsize=(11, 9))
wntr.graphics.plot_network(
    wn, node_attribute=age_clip, node_size=22, node_cmap="plasma",
    node_range=[0, cap], node_colorbar_label="water age (h)",
    title=f"Net3 - water age (hydraulic only; scale capped at {cap:.0f} h)",
    ax=ax, show_plot=False,
)

def mark(names, marker, color, size, label):
    xs = [wn.get_node(n).coordinates[0] for n in names]
    ys = [wn.get_node(n).coordinates[1] for n in names]
    ax.scatter(xs, ys, marker=marker, s=size, facecolors="none",
               edgecolors=color, linewidths=1.8, zorder=6, label=label)

mark(wn.tank_name_list, "s", "cyan", 160, "tanks")
mark(wn.reservoir_name_list, "^", "lime", 200, "reservoirs")
mark(MON, "o", "white", 80, "monitors")
ax.legend(loc="best", fontsize=8)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "_agemap.png")
plt.savefig(out, dpi=130)
print("saved", out)
