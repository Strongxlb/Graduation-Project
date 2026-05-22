"""
02_demo_wntr_original.py — run Net1 with the ORIGINAL .inp settings
=======================================================================

Goal: contrast the "minimal-friction debug demo" in 01 against the
unmodified .inp baseline, to make the cost of the demo-1 simplifications
visible.

Demo-1 (`01_demo_wntr.py`) deviated from Net1.inp in exactly two places:

    1. junction initial chlorine     0.5 mg/L  -->  0.0 mg/L
    2. Global Wall decay coefficient -1 m/day  -->  0      (wall reaction OFF)

This script:
    (a) loads Net1.inp untouched (no quality overrides),
    (b) re-runs the same 24 h simulation,
    (c) writes parallel outputs to results/week1_original/,
    (d) reads results from results/week1_demo/ (the modified version) and
        produces side-by-side comparison plots and summary tables under
        results/week1_compare/.

Run from the repo root:
    python src/02_demo_wntr_original.py
"""

from __future__ import annotations

import os
import shutil
import tempfile
import warnings
from importlib import resources
from pathlib import Path

_MPL_CACHE = Path.home() / ".cache" / "matplotlib"
try:
    _MPL_CACHE.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(_MPL_CACHE))
except OSError:
    os.environ.setdefault("MPLCONFIGDIR",
                          str(Path(tempfile.gettempdir()) / "matplotlib"))

warnings.filterwarnings(
    "ignore",
    message="pkg_resources is deprecated.*",
    category=UserWarning,
)

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np               # noqa: E402
import pandas as pd              # noqa: E402
import wntr                      # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = REPO_ROOT / "models"
OUT_ORIG = REPO_ROOT / "results" / "week1_original"
OUT_CMP = REPO_ROOT / "results" / "week1_compare"
RES_MOD = REPO_ROOT / "results" / "week1_demo"

for d in (OUT_ORIG, OUT_CMP, MODELS_DIR):
    d.mkdir(parents=True, exist_ok=True)

# WNTR stores / returns concentrations in SI (kg/m^3). The .inp uses mg/L.
# We multiply by 1000 everywhere in this script so labels / thresholds /
# CSVs all read in mg/L for human consumption.
KGM3_TO_MGL = 1000.0


# ---------------------------------------------------------------------------
# Locate Net1.inp (same logic as 01_demo_wntr.py)
# ---------------------------------------------------------------------------

def locate_net1_inp() -> Path:
    local_copy = MODELS_DIR / "Net1.inp"
    if local_copy.exists():
        return local_copy

    src: Path | None = None
    for pkg in ("wntr.library.networks", "wntr.examples.networks"):
        try:
            ref = resources.files(pkg).joinpath("Net1.inp")
            if ref.is_file():
                src = Path(str(ref))
                break
        except (ModuleNotFoundError, AttributeError):
            continue

    if src is None:
        wntr_dir = Path(wntr.__file__).resolve().parent
        matches = list(wntr_dir.rglob("Net1.inp"))
        if matches:
            src = matches[0]

    if src is None:
        raise FileNotFoundError("Net1.inp not found in wntr install.")

    shutil.copy(src, local_copy)
    return local_copy


# ---------------------------------------------------------------------------
# Original-config run (no overrides whatsoever)
# ---------------------------------------------------------------------------

def run_original(inp_file: Path) -> tuple[pd.DataFrame, pd.DataFrame,
                                          wntr.network.WaterNetworkModel]:
    """Load Net1.inp untouched and run the 24 h simulation."""
    wn = wntr.network.WaterNetworkModel(str(inp_file))

    # Sanity-print: what does the .inp actually say?
    # WNTR stores reaction coefficients in 1/s and m/s (SI); convert
    # for display so the user sees the familiar 1/day and m/day units
    # that match the .inp file.
    print("[orig]  Reading Net1.inp quality settings:")
    print(f"        bulk_coeff  = "
          f"{wn.options.reaction.bulk_coeff * 86400:.4f} 1/day")
    print(f"        wall_coeff  = "
          f"{wn.options.reaction.wall_coeff * 86400:.4f} m/day")
    print(f"        bulk_order  = {wn.options.reaction.bulk_order}")
    print(f"        wall_order  = {wn.options.reaction.wall_order}")
    print(f"        duration    = "
          f"{wn.options.time.duration/3600:.1f} h")

    j0 = wn.junction_name_list[0]
    print(f"        junction {j0} initial_quality = "
          f"{wn.get_node(j0).initial_quality * KGM3_TO_MGL:.3f} mg/L")
    for r in wn.reservoir_name_list:
        print(f"        reservoir {r} initial_quality = "
              f"{wn.get_node(r).initial_quality * KGM3_TO_MGL:.3f} mg/L")
    for t in wn.tank_name_list:
        print(f"        tank {t}      initial_quality = "
              f"{wn.get_node(t).initial_quality * KGM3_TO_MGL:.3f} mg/L")

    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    pressure = results.node["pressure"][wn.junction_name_list]
    chlorine = results.node["quality"][wn.junction_name_list] * KGM3_TO_MGL  # mg/L
    return pressure, chlorine, wn


# ---------------------------------------------------------------------------
# Standalone plots for the ORIGINAL run (mirror of 01_demo_wntr.py outputs)
# ---------------------------------------------------------------------------

def annotate_node_ids(ax: plt.Axes,
                      wn: wntr.network.WaterNetworkModel,
                      *,
                      fontsize: int = 9) -> None:
    """Label each network node with its EPANET ID (junctions 10–32, tank 2, etc.)."""
    for name in wn.node_name_list:
        node = wn.get_node(name)
        x, y = node.coordinates
        ax.annotate(
            name,
            (x, y),
            textcoords="offset points",
            xytext=(5, 5),
            fontsize=fontsize,
            fontweight="bold",
            color="0.1",
            ha="left",
            va="bottom",
            zorder=10,
            clip_on=False,
        )


def plot_original_outputs(wn: wntr.network.WaterNetworkModel,
                          pressure: pd.DataFrame,
                          chlorine: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    wntr.graphics.plot_network(
        wn, node_attribute="elevation", node_size=40,
        title="Net1 - elevation (m)", ax=ax, show_plot=False,
    )
    annotate_node_ids(ax, wn)
    fig.savefig(OUT_ORIG / "01_network.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    hours = pressure.index / 3600.0
    for node in wn.junction_name_list:
        ax.plot(hours, pressure[node], alpha=0.7)
    ax.set(xlabel="Time (hours)", ylabel="Pressure (m)",
           title="Junction pressures over 24 h (original .inp)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_ORIG / "02_pressure_timeseries.png", dpi=150)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4))
    hours = chlorine.index / 3600.0
    for node in wn.junction_name_list:
        ax.plot(hours, chlorine[node], label=f"node {node}", alpha=0.8)
    ax.axhline(0.2, color="red", linestyle="--", linewidth=1,
               label="0.2 mg/L threshold")
    ax.set(xlabel="Time (hours)", ylabel="Free chlorine (mg/L)",
           title="Chlorine timeseries — ORIGINAL .inp (bulk=-0.5/day, wall=-1 m/day)")
    ax.legend(loc="best", fontsize=8, ncol=2)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_ORIG / "03_chlorine_timeseries.png", dpi=150)
    plt.close(fig)

    final_t = chlorine.index[-1]
    fig, ax = plt.subplots(figsize=(7, 6))
    wntr.graphics.plot_network(
        wn, node_attribute=chlorine.loc[final_t].to_dict(),
        node_size=60, node_colorbar_label="Cl (mg/L)",
        title=f"Chlorine at t={final_t/3600:.0f} h — ORIGINAL .inp",
        ax=ax, show_plot=False,
    )
    annotate_node_ids(ax, wn)
    fig.savefig(OUT_ORIG / "04_chlorine_spatial.png",
                dpi=150, bbox_inches="tight")
    plt.close(fig)

    chlorine.to_csv(OUT_ORIG / "chlorine_junctions.csv")
    pressure.to_csv(OUT_ORIG / "pressure_junctions.csv")


# ---------------------------------------------------------------------------
# Side-by-side comparison ORIGINAL vs MODIFIED
# ---------------------------------------------------------------------------

def make_comparison(chlorine_orig: pd.DataFrame,
                    wn: wntr.network.WaterNetworkModel) -> None:
    mod_csv = RES_MOD / "chlorine_junctions.csv"
    if not mod_csv.exists():
        raise FileNotFoundError(
            f"Cannot find {mod_csv}. Run `python src/01_demo_wntr.py` first."
        )
    chlorine_mod = pd.read_csv(mod_csv, index_col=0)
    chlorine_mod.index = chlorine_mod.index.astype(float)
    chlorine_mod.columns = chlorine_mod.columns.astype(str)

    hours_o = chlorine_orig.index / 3600.0
    hours_m = chlorine_mod.index / 3600.0

    # --- Plot 1: side-by-side 9 junctions ---
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for node in wn.junction_name_list:
        axes[0].plot(hours_o, chlorine_orig[node], label=f"node {node}",
                     alpha=0.8)
        axes[1].plot(hours_m, chlorine_mod[node], label=f"node {node}",
                     alpha=0.8)
    for ax, title in zip(axes,
                         ["ORIGINAL .inp\n(junctions=0.5 mg/L, wall=-1 m/day)",
                          "MODIFIED demo 1\n(junctions=0.0 mg/L, wall=0)"]):
        ax.axhline(0.2, color="red", linestyle="--", linewidth=1,
                   label="0.2 mg/L")
        ax.set(xlabel="Time (hours)", ylabel="Free chlorine (mg/L)",
               title=title)
        ax.grid(alpha=0.3)
        ax.set_ylim(-0.05, 1.15)
    axes[1].set_ylabel("")
    axes[0].legend(loc="upper right", fontsize=7, ncol=2)
    fig.suptitle("Chlorine at 9 junctions — ORIGINAL vs MODIFIED",
                 fontsize=11, y=1.02)
    fig.tight_layout()
    fig.savefig(OUT_CMP / "chlorine_timeseries_side_by_side.png",
                dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Plot 2: spatial at t = 24 h, both configs ---
    final_o = chlorine_orig.iloc[-1].to_dict()
    final_m = chlorine_mod.iloc[-1].to_dict()
    vmin = 0.0
    vmax = max(max(final_o.values()), max(final_m.values()), 1.0)

    fig, axes = plt.subplots(1, 2, figsize=(14, 6), constrained_layout=True)
    wntr.graphics.plot_network(
        wn, node_attribute=final_o, node_size=70,
        node_colorbar_label="Cl (mg/L)",
        title="ORIGINAL .inp at t = 24 h", ax=axes[0],
        node_range=[vmin, vmax], show_plot=False,
    )
    annotate_node_ids(axes[0], wn)
    wntr.graphics.plot_network(
        wn, node_attribute=final_m, node_size=70,
        node_colorbar_label="Cl (mg/L)",
        title="MODIFIED demo 1 at t = 24 h", ax=axes[1],
        node_range=[vmin, vmax], show_plot=False,
    )
    annotate_node_ids(axes[1], wn)
    fig.savefig(OUT_CMP / "spatial_at_24h.png", dpi=150, bbox_inches="tight")
    plt.close(fig)

    # --- Numerical summary table ---
    rows = []
    threshold = 0.2
    for node in wn.junction_name_list:
        co = chlorine_orig[node]
        cm = chlorine_mod[node]
        rows.append({
            "node": node,
            "orig_mean": co.mean(),
            "orig_min":  co.min(),
            "orig_max":  co.max(),
            "orig_below_0.2_pct": float((co < threshold).mean() * 100),
            "mod_mean":  cm.mean(),
            "mod_min":   cm.min(),
            "mod_max":   cm.max(),
            "mod_below_0.2_pct": float((cm < threshold).mean() * 100),
            "abs_diff_mean":     co.mean() - cm.mean(),
        })
    df = pd.DataFrame(rows).set_index("node")
    df.to_csv(OUT_CMP / "summary_per_node.csv", float_format="%.4f")

    print("\n[cmp]   Per-junction summary (mg/L; below_0.2 in %):")
    print(df.round(3).to_string())

    # --- Overall summary printed ---
    overall = pd.DataFrame({
        "mean": [chlorine_orig.values.mean(), chlorine_mod.values.mean()],
        "min":  [chlorine_orig.values.min(),  chlorine_mod.values.min()],
        "max":  [chlorine_orig.values.max(),  chlorine_mod.values.max()],
        "below_0.2_pct": [
            float((chlorine_orig.values < threshold).mean() * 100),
            float((chlorine_mod.values  < threshold).mean() * 100),
        ],
    }, index=["original", "modified"])
    print("\n[cmp]   Overall network summary:")
    print(overall.round(3).to_string())
    overall.to_csv(OUT_CMP / "summary_overall.csv", float_format="%.4f")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    inp_file = locate_net1_inp()
    print(f"[setup] Using model: {inp_file}\n")

    pressure, chlorine, wn = run_original(inp_file)
    print(f"\n[orig]  Chlorine range: "
          f"min={chlorine.values.min():.3f}, "
          f"max={chlorine.values.max():.3f} mg/L")
    print(f"        Negative-pressure samples: "
          f"{int((pressure < 0).sum().sum())}")

    plot_original_outputs(wn, pressure, chlorine)
    print(f"[orig]  Outputs written to {OUT_ORIG}\n")

    print("[cmp]   Building original vs modified comparison ...")
    make_comparison(chlorine, wn)
    print(f"\n[cmp]   Outputs written to {OUT_CMP}")


if __name__ == "__main__":
    os.environ.setdefault("MPLBACKEND", "Agg")
    main()
