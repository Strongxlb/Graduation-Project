import os, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import wntr

INP = os.path.join(os.path.dirname(wntr.__file__), "library", "networks", "Net3.inp")
wn = wntr.network.WaterNetworkModel(INP)
MON = ["10", "15", "20", "35", "40", "60"]

# --- print tank locations + what connects to them ---
print("TANKS:")
for t in wn.tank_name_list:
    xy = wn.get_node(t).coordinates
    links = [l for l in wn.link_name_list
             if t in (wn.get_link(l).start_node_name, wn.get_link(l).end_node_name)]
    nbrs = []
    for l in links:
        lk = wn.get_link(l)
        other = lk.end_node_name if lk.start_node_name == t else lk.start_node_name
        nbrs.append(f"{l}->{other}")
    print(f"  tank {t}: coord={xy}, connects via {nbrs}")
print("RESERVOIRS:")
for r in wn.reservoir_name_list:
    print(f"  {r}: coord={wn.get_node(r).coordinates}")

# --- plot ---
fig, ax = plt.subplots(figsize=(11, 9))
wntr.graphics.plot_network(wn, node_size=12,
                           title="Net3 - tank & source locations", ax=ax, show_plot=False)

def mark(names, marker, color, size, label):
    xs = [wn.get_node(n).coordinates[0] for n in names]
    ys = [wn.get_node(n).coordinates[1] for n in names]
    ax.scatter(xs, ys, marker=marker, s=size, c=color, edgecolors="black",
               linewidths=1.2, zorder=6, label=label)
    for n in names:
        x, y = wn.get_node(n).coordinates
        ax.annotate(n, (x, y), xytext=(6, 6), textcoords="offset points",
                    fontsize=11, fontweight="bold", color=color, zorder=7)

mark(wn.tank_name_list, "s", "tab:blue", 200, "tanks (1/2/3)")
mark(wn.reservoir_name_list, "^", "tab:green", 240, "reservoirs (River/Lake)")
# monitors for context (small, no bold labels)
mx = [wn.get_node(n).coordinates[0] for n in MON]
my = [wn.get_node(n).coordinates[1] for n in MON]
ax.scatter(mx, my, marker="o", s=60, facecolors="none", edgecolors="red",
           linewidths=1.5, zorder=5, label="monitors")

ax.legend(loc="best", fontsize=9)
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "_tankloc.png")
plt.savefig(out, dpi=130)
print("saved", out)
