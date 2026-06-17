import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import wntr

SECONDS_PER_DAY = 24 * 3600
p2s = lambda v: v / SECONDS_PER_DAY
INP = os.path.join(os.path.dirname(wntr.__file__), "library", "networks", "Net3.inp")
MON = ["10", "15", "20", "35", "40", "60"]
KB_FIXED = -0.5
KW_OLD, KW_NEW = -1.0, -0.05      # stronger contrast

# --- contiguous "old DMA": all pipes within N hops of a seed node ---
def old_pipes_cluster(inp_file=INP, seed="15", n_hops=4):
    wn = wntr.network.WaterNetworkModel(inp_file)
    G = wn.get_graph().to_undirected()
    near = set(nx.single_source_shortest_path_length(G, seed, cutoff=n_hops).keys())
    old = set()
    for p in wn.pipe_name_list:
        lk = wn.get_link(p)
        if lk.start_node_name in near and lk.end_node_name in near:
            old.add(p)
    return old

OLD = old_pipes_cluster(seed="15", n_hops=4)

def sim(material_old):
    wn = wntr.network.WaterNetworkModel(INP)
    wn.options.time.duration = 72 * 3600
    wn.options.time.hydraulic_timestep = 3600
    wn.options.time.report_timestep = 3600
    wn.options.time.quality_timestep = 300
    wn.options.quality.parameter = "CHEMICAL"; wn.options.quality.inpfile_units = "mg/L"
    wn.options.reaction.bulk_order = 1; wn.options.reaction.wall_order = 1
    wn.options.reaction.bulk_coeff = p2s(KB_FIXED); wn.options.reaction.wall_coeff = p2s(0.0)
    for r in wn.reservoir_name_list: wn.get_node(r).initial_quality = 1.0
    for p in wn.pipe_name_list:
        wn.get_link(p).wall_coeff = p2s(KW_OLD if (material_old and p in OLD) else KW_NEW)
    res = wntr.sim.EpanetSimulator(wn).run_sim()
    q = res.node["quality"][MON]; q.index = q.index/3600.0
    return q.iloc[-24:].mean()

c_new = sim(False)   # all new
c_dma = sim(True)    # contiguous old DMA
print("old pipes in cluster: %d of 117 (%.0f%%)" % (len(OLD), 100*len(OLD)/117))
print(pd.DataFrame({"all new": c_new.round(3), "old DMA": c_dma.round(3),
                    "drop": (c_new - c_dma).round(3)}))
print("max drop: %.3f mg/L" % (c_new - c_dma).abs().max())

# --- map: which pipes are 'old' (the contiguous DMA) ---
wn = wntr.network.WaterNetworkModel(INP)
link_old = {p: (1.0 if p in OLD else 0.0) for p in wn.pipe_name_list}
fig, ax = plt.subplots(figsize=(11, 9))
wntr.graphics.plot_network(wn, link_attribute=link_old, link_width=2.0,
                           link_cmap=plt.cm.coolwarm, link_colorbar_label="old_CI (1) / new (0)",
                           node_size=8, title="Contiguous 'old DMA' (cluster around monitor 15)",
                           ax=ax, show_plot=False)
for n in MON:
    x, y = wn.get_node(n).coordinates
    ax.scatter([x], [y], s=70, facecolors="none", edgecolors="black", linewidths=1.5, zorder=6)
    ax.annotate(n, (x, y), xytext=(5, 5), textcoords="offset points", fontsize=9, fontweight="bold")
plt.tight_layout()
out = os.path.join(os.path.dirname(__file__), "_region.png")
plt.savefig(out, dpi=130); print("saved", out)
