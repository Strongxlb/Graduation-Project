"""
Week 1 Step 3 - WNTR minimal hydraulic + chlorine demo on Net1.

Goal: confirm the EPANET / WNTR toolchain works end-to-end before we touch
any real calibration logic. We deliberately keep the model trivial (Net1,
single bulk decay coefficient, single chlorine source at the reservoir) and
focus on producing four reference figures:

    01_network.png            - network topology with elevations
    02_pressure_timeseries.png - junction pressures over 24 h
    03_chlorine_timeseries.png - chlorine at a few sample junctions
    04_chlorine_spatial.png   - spatial chlorine map at end of simulation

Run from the repository root:

    python src/01_demo_wntr.py

Outputs (figures + CSVs) go to results/week1_demo/ so we can inspect numbers
without re-running the simulation.
"""

from __future__ import annotations

import os
import shutil
import tempfile
import warnings
from importlib import resources
from pathlib import Path

# ---------------------------------------------------------------------------
# Environment hardening
#
# (1) Some user homes have a non-writable ~/.matplotlib (permission issue or
#     filesystem ACL); point matplotlib at a guaranteed-writable cache dir
#     BEFORE importing matplotlib.
# (2) wntr 1.4.x still does `from pkg_resources import resource_filename`,
#     which emits a noisy DeprecationWarning under setuptools<81. Silence it.
# ---------------------------------------------------------------------------

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

import matplotlib.pyplot as plt  # noqa: E402  (after MPLCONFIGDIR setup)
import pandas as pd               # noqa: E402
import wntr                       # noqa: E402

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parents[1]
MODELS_DIR = REPO_ROOT / "models"
OUT_DIR = REPO_ROOT / "results" / "week1_demo"

OUT_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)


# ---------------------------------------------------------------------------
# Locate Net1.inp
# ---------------------------------------------------------------------------

def locate_net1_inp() -> Path:
    """Return the path to Net1.inp, copying it into ``models/`` on first run.

    WNTR ships its example networks inside the installed package. We copy
    Net1.inp into our repo so that (a) the demo is self-contained and (b)
    the model file is version-controlled alongside the code.

    The exact location of Net1.inp inside the installed wntr package has
    moved across versions:
        - wntr <= 1.3:  wntr/examples/networks/Net1.inp
        - wntr >= 1.4:  wntr/library/networks/Net1.inp

    We try ``importlib.resources`` first (works regardless of layout), then
    fall back to a few well-known paths, then fall back to a recursive
    search inside the installed package.
    """
    local_copy = MODELS_DIR / "Net1.inp"
    if local_copy.exists():
        return local_copy

    src: Path | None = None

    for pkg in ("wntr.library.networks",      # wntr >= 1.4
                "wntr.examples.networks"):    # wntr <= 1.3
        try:
            ref = resources.files(pkg).joinpath("Net1.inp")
            if ref.is_file():
                src = Path(str(ref))
                break
        except (ModuleNotFoundError, AttributeError):
            continue

    if src is None:
        wntr_dir = Path(wntr.__file__).resolve().parent
        for cand in [
            wntr_dir / "library" / "networks" / "Net1.inp",
            wntr_dir / "examples" / "networks" / "Net1.inp",
            wntr_dir / "tests" / "networks_for_testing" / "Net1.inp",
        ]:
            if cand.exists():
                src = cand
                break

    if src is None:
        wntr_dir = Path(wntr.__file__).resolve().parent
        matches = list(wntr_dir.rglob("Net1.inp"))
        if matches:
            src = matches[0]

    if src is None:
        raise FileNotFoundError(
            f"Could not locate Net1.inp inside the installed wntr package "
            f"(version {getattr(wntr, '__version__', 'unknown')}). "
            "Please drop a copy into models/Net1.inp manually."
        )

    shutil.copy(src, local_copy)
    print(f"[setup] Copied Net1.inp from {src} -> {local_copy}")
    return local_copy


# ---------------------------------------------------------------------------
# Build / configure the model
# ---------------------------------------------------------------------------

def build_model(inp_file: Path) -> wntr.network.WaterNetworkModel:
    """Load Net1 and configure a 24-hour chlorine simulation."""
    wn = wntr.network.WaterNetworkModel(str(inp_file))

    # Time options: 24-hour run with 1-hour reporting.
    wn.options.time.duration = 24 * 3600           # seconds
    wn.options.time.hydraulic_timestep = 3600      # 1 h
    wn.options.time.quality_timestep = 300         # 5 min (finer for transport)
    wn.options.time.report_timestep = 3600         # 1 h

    # Tell EPANET we are tracking a chemical called Chlorine.
    # Default `inpfile_units` is "mg/L" in wntr >= 1.4, so we don't set it.
    wn.options.quality.parameter = "CHEMICAL"
    wn.options.quality.chemical_name = "Chlorine"

    # First-order bulk decay. EPANET interprets the coefficient with units
    # of 1/day (negative => decay). -0.5/day is a common chlorine baseline.
    wn.options.reaction.bulk_coeff = -0.5
    wn.options.reaction.wall_coeff = 0.0           # ignore wall decay for now
    wn.options.reaction.bulk_order = 1.0
    wn.options.reaction.wall_order = 1.0

    # Chlorine source: reservoir water enters at 1.0 mg/L.
    # IMPORTANT: WNTR stores `initial_quality` in SI units (kg/m^3) when
    # set via the Python API; .inp values are auto-converted on load.
    # 1.0 mg/L  ==  0.001 kg/m^3.
    for res_name in wn.reservoir_name_list:
        wn.get_node(res_name).initial_quality = 0.001  # 1.0 mg/L

    # Junction nodes start clean; chlorine arrives as the network fills.
    for j_name in wn.junction_name_list:
        wn.get_node(j_name).initial_quality = 0.0

    return wn


# WNTR returns simulation results in SI (kg/m^3).  Convert to mg/L for
# every downstream plot, print and CSV so that figure labels match reality.
KGM3_TO_MGL = 1000.0


# ---------------------------------------------------------------------------
# Plotting helpers
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


def plot_network(wn: wntr.network.WaterNetworkModel) -> None:
    fig, ax = plt.subplots(figsize=(7, 6))
    wntr.graphics.plot_network(
        wn,
        node_attribute="elevation",
        node_size=40,
        title="Net1 - elevation (m)",
        ax=ax,
        show_plot=False,
    )
    annotate_node_ids(ax, wn)
    fig.savefig(OUT_DIR / "01_network.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


def plot_pressure(results: wntr.sim.results.SimulationResults,
                  wn: wntr.network.WaterNetworkModel) -> None:
    pressure = results.node["pressure"][wn.junction_name_list]
    hours = pressure.index / 3600.0
    fig, ax = plt.subplots(figsize=(8, 4))
    for node in wn.junction_name_list:
        ax.plot(hours, pressure[node], alpha=0.7)
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Pressure (m)")
    ax.set_title("Junction pressures over 24 h")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "02_pressure_timeseries.png", dpi=150)
    plt.close(fig)


def plot_chlorine_timeseries(chlorine: pd.DataFrame,
                             sample_nodes: list[str]) -> None:
    fig, ax = plt.subplots(figsize=(8, 4))
    hours = chlorine.index / 3600.0
    for node in sample_nodes:
        ax.plot(hours, chlorine[node], label=f"node {node}")
    ax.axhline(0.2, color="red", linestyle="--", linewidth=1,
               label="0.2 mg/L threshold")
    ax.set_xlabel("Time (hours)")
    ax.set_ylabel("Free chlorine (mg/L)")
    ax.set_title("Chlorine timeseries at sample junctions")
    ax.legend(loc="best", fontsize=8)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(OUT_DIR / "03_chlorine_timeseries.png", dpi=150)
    plt.close(fig)


def plot_chlorine_spatial(wn: wntr.network.WaterNetworkModel,
                          chlorine: pd.DataFrame) -> None:
    final_t = chlorine.index[-1]
    chlorine_final = chlorine.loc[final_t].to_dict()

    fig, ax = plt.subplots(figsize=(7, 6))
    wntr.graphics.plot_network(
        wn,
        node_attribute=chlorine_final,
        node_size=60,
        node_colorbar_label="Cl (mg/L)",
        title=f"Chlorine spatial distribution at t = {final_t/3600:.0f} h",
        ax=ax,
        show_plot=False,
    )
    annotate_node_ids(ax, wn)
    fig.savefig(OUT_DIR / "04_chlorine_spatial.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    inp_file = locate_net1_inp()
    print(f"[setup] Using model: {inp_file}")

    wn = build_model(inp_file)
    print(f"[setup] Junctions: {len(wn.junction_name_list)} | "
          f"Pipes: {len(wn.pipe_name_list)} | "
          f"Reservoirs: {len(wn.reservoir_name_list)} | "
          f"Tanks: {len(wn.tank_name_list)}")

    print("[run]   Starting EPANET simulation ...")
    sim = wntr.sim.EpanetSimulator(wn)
    results = sim.run_sim()
    print("[run]   Simulation finished.")

    pressure = results.node["pressure"][wn.junction_name_list]
    chlorine = results.node["quality"][wn.junction_name_list] * KGM3_TO_MGL  # -> mg/L

    # Sanity checks: pressures should be positive at junctions for Net1.
    n_neg = (pressure < 0).sum().sum()
    print(f"[check] Negative-pressure samples at junctions: {n_neg}")
    print(f"[check] Chlorine range (mg/L): "
          f"min={chlorine.values.min():.3f}, max={chlorine.values.max():.3f}")

    sample_nodes = wn.junction_name_list[: min(5, len(wn.junction_name_list))]

    plot_network(wn)
    plot_pressure(results, wn)
    plot_chlorine_timeseries(chlorine, sample_nodes)
    plot_chlorine_spatial(wn, chlorine)
    print(f"[out]   Outputs written to {OUT_DIR}")

    chlorine.to_csv(OUT_DIR / "chlorine_junctions.csv")
    pressure.to_csv(OUT_DIR / "pressure_junctions.csv")


if __name__ == "__main__":
    # Headless backend so the script also works on remote machines / CI.
    os.environ.setdefault("MPLBACKEND", "Agg")
    main()
