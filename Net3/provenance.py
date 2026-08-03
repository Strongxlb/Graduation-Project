"""Provenance of the cached results: what code, model file and library versions produced them.

The point is that `baseline_cache/*.json` and `baseline.npz` are only meaningful together with the
network file, the frozen configuration in `wq_common.py` and the library versions that ran EPANET.
This module writes those facts to `baseline_cache/cache_manifest.json` and can check a later
environment against them, so a stale cache is detected instead of silently reused.

Usage:
    python provenance.py            # write/refresh the manifest
    python provenance.py --check    # compare the current environment against the manifest
"""
import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone

import numpy as np

import wq_common as B

HERE = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(HERE, "baseline_cache", "cache_manifest.json")

# Fields that must match for a cache to be reusable. Everything else in the manifest is recorded
# for the record only (e.g. the timestamp, or the git commit, which changes on every commit).
CRITICAL = ["config_sha256", "net3_inp_sha256", "wntr", "python_minor"]


def git_info():
    def run(*args):
        try:
            return subprocess.run(["git", *args], cwd=HERE, capture_output=True,
                                  text=True, timeout=10).stdout.strip()
        except (OSError, subprocess.SubprocessError):
            return ""
    return {"commit": run("rev-parse", "HEAD"),
            "dirty": bool(run("status", "--porcelain"))}


def versions():
    import scipy
    import wntr
    v = {"python": sys.version.split()[0],
         "python_minor": ".".join(sys.version.split()[0].split(".")[:2]),
         "numpy": np.__version__, "scipy": scipy.__version__, "wntr": wntr.__version__,
         # from sys.prefix, not CONDA_DEFAULT_ENV: the variable is inherited from the calling
         # shell and lies whenever the interpreter is invoked by full path
         "conda_env": os.path.basename(sys.prefix),
         "sys_prefix": sys.prefix}
    try:
        import pandas
        v["pandas"] = pandas.__version__
    except ImportError:
        v["pandas"] = None
    return v


def frozen_config():
    """Every baseline choice that a cached result depends on, in a canonical form.

    Hashing this dict means one field detects any change to the experiment definition — a moved
    monitor, a different seed, a new prior or a changed warm-up all invalidate the cache.
    """
    return {
        "monitor_nodes": list(B.MONITOR_NODES),
        "inlet_mgl": B.INLET_CHLORINE_MGL,
        "tank_init_mgl": B.TANK_INIT_MGL,
        "duration_h": B.DURATION_H,
        "warmup_h": B.WARMUP_H,
        "hydraulic_timestep_s": B.HYDRAULIC_TIMESTEP_S,
        "report_timestep_s": B.REPORT_TIMESTEP_S,
        "quality_timestep_s": B.QUALITY_TIMESTEP_S,
        "kb_fixed": B.KB_FIXED,
        "kw_true": [B.KW_OLD_TRUE, B.KW_AVG_TRUE, B.KW_NEW_TRUE],
        "prior": {k: list(v) for k, v in B.PRIOR.items()},
        "n_mc": B.N_MC,
        "sigma_obs": B.SIGMA_OBS,
        "rmse_thr_primary": B.RMSE_THR,
        "rmse_thr_draft": B.RMSE_THR_DRAFT,
        "n_resid": B.N_RESID,
        "noise_seed": B.NOISE_SEED,
        "sample_seed": B.SAMPLE_SEED,
        "zone_rule": {"y_low": B.ZONE_Y_LOW, "x_mid": B.ZONE_X_MID,
                      "cross_zone": "weaker (newer) side wins"},
    }


def config_sha256(cfg=None):
    cfg = frozen_config() if cfg is None else cfg
    blob = json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def manifest():
    cfg = frozen_config()
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git": git_info(),
        "net3_inp": os.path.relpath(B.NET3_INP, os.path.dirname(HERE)),
        "net3_inp_sha256": B.sha256_of(B.NET3_INP),
        "config": cfg,
        "config_sha256": config_sha256(cfg),
        **versions(),
    }


def write_manifest(path=MANIFEST):
    m = manifest()
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(m, f, indent=2)
    return m


def check_manifest(path=MANIFEST):
    """Return a list of (field, recorded, current) for every CRITICAL field that disagrees."""
    if not os.path.exists(path):
        return [("manifest", "missing", "run provenance.py to create it")]
    with open(path) as f:
        old = json.load(f)
    new = manifest()
    return [(k, old.get(k), new.get(k)) for k in CRITICAL if old.get(k) != new.get(k)]


def _key_path(path):
    return path + ".key.json"


def save_keyed_array(path, arr, **extra):
    """Save an intermediate array together with the configuration that produced it.

    Grids over the prior box are expensive to rebuild, so they are cached — but a cache keyed only
    on file existence silently survives a change of warm-up or timing, which is exactly how a stale
    profile-likelihood grid can be reused against a rebuilt baseline.
    """
    np.save(path, arr)
    key = {"config_sha256": config_sha256(), "shape": list(np.shape(arr)),
           "net3_inp_sha256": B.sha256_of(B.NET3_INP), **extra}
    with open(_key_path(path), "w") as f:
        json.dump(key, f, indent=2)


def load_keyed_array(path, **expect):
    """Load an array saved by save_keyed_array, or None if missing or built under another config."""
    if not (os.path.exists(path) and os.path.exists(_key_path(path))):
        return None
    with open(_key_path(path)) as f:
        key = json.load(f)
    if key.get("config_sha256") != config_sha256():
        return None
    if key.get("net3_inp_sha256") != B.sha256_of(B.NET3_INP):
        return None
    if any(key.get(k) != v for k, v in expect.items()):
        return None
    return np.load(path)


def require_keyed_array(path, what, **expect):
    """Like load_keyed_array but raises, for consumers that cannot rebuild the array themselves."""
    arr = load_keyed_array(path, **expect)
    if arr is None:
        raise RuntimeError(
            f"{what} at {os.path.basename(path)} is missing or was built under a different "
            f"configuration. Rebuild it (run the step that writes it) before using this script; "
            f"reusing it would silently mix results from two different baselines.")
    return arr


def require_fresh_cache(path=MANIFEST):
    """Raise if the cache was produced under a different configuration. For use by step scripts."""
    bad = check_manifest(path)
    if bad:
        lines = "\n".join(f"  {k}: cache={o!r} now={n!r}" for k, o, n in bad)
        raise RuntimeError("cached results were produced under a different setup:\n" + lines +
                           "\nRebuild the cache (step1) or check out the matching commit.")


if __name__ == "__main__":
    if "--check" in sys.argv:
        bad = check_manifest()
        if bad:
            print("MANIFEST MISMATCH")
            for k, o, n in bad:
                print(f"  {k}\n    cache : {o}\n    now   : {n}")
            sys.exit(1)
        print("manifest OK — current environment matches the cached results")
    else:
        m = write_manifest()
        print(f"wrote {os.path.relpath(MANIFEST, os.path.dirname(HERE))}")
        print(f"  config_sha256  {m['config_sha256']}")
        print(f"  net3_inp       {m['net3_inp']}  {m['net3_inp_sha256'][:16]}...")
        print(f"  git            {m['git']['commit'][:12]}"
              f"{' (dirty)' if m['git']['dirty'] else ''}")
        print(f"  env            {m['conda_env']}  python {m['python']}  "
              f"numpy {m['numpy']}  scipy {m['scipy']}  wntr {m['wntr']}")
