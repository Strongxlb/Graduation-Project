"""Provenance of the cached results: what code, model file and library versions produced them.

`baseline_cache/*.json` and `baseline.npz` are only meaningful together with the network file, the
frozen configuration, THE SOURCE CODE, and the library versions that ran EPANET. This module writes
those facts to `baseline_cache/cache_manifest.json` and can check a later environment against them,
so a stale cache is detected instead of silently reused.

What is hashed, and why each is needed:

  config_sha256      every baseline choice (monitors, seeds, priors, timing, truth) serialised and
                     hashed, so a changed experiment definition is one field
  net3_inp_sha256    the frozen network file
  wq_common_sha256   the module that defines the model AND the likelihoods. Config alone is not
                     enough: rewriting the likelihood implementation without touching a single
                     configuration value changes every weighted number while leaving the config hash
                     identical. That gap is why this field is CRITICAL.
  step_scripts_sha256  one hash per step script plus a combined hash, so it is possible to say which
                     scripts have changed since the cache was written. Not critical, because editing
                     one step's prose must not invalidate another step's cache.
  git.tree_sha256    a hash over the CONTENT of every tracked file, i.e. an identifier for the
                     working tree rather than for the commit. A commit id says nothing about a dirty
                     tree; this does.
  git.dirty_files    which tracked files are modified, so a dirty result set names its own gap
  numpy/scipy        exact versions, not just python's minor version

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

# Fields that must match for a cache to be reusable. Everything else in the manifest is recorded for
# the record only (the timestamp, the commit id, the per-script hashes). `wq_common_sha256` is here
# because that module defines both the forward model and the likelihoods: a change there can move
# every cached number without moving the config hash. numpy/scipy are exact, because the weights come
# from log_ndtr and the design from scipy.stats.qmc.
CRITICAL = ["config_sha256", "net3_inp_sha256", "wq_common_sha256",
            "wntr", "numpy", "scipy", "python_minor"]

STEP_GLOB = "step"


def _run_git(*args):
    try:
        r = subprocess.run(["git", *args], cwd=HERE, capture_output=True, text=True, timeout=20)
        return r.stdout if r.returncode == 0 else ""
    except (OSError, subprocess.SubprocessError):
        return ""


def git_info():
    """Commit id plus a content hash of the whole tracked tree.

    `git rev-parse HEAD` identifies a commit, which is not the same thing as identifying the code
    that ran: with uncommitted edits the commit id is a link to something else. `git ls-files -s`
    lists the staged blob id of every tracked file, and hashing that listing gives a stable
    fingerprint for the tree; `git diff` covers what is modified but not yet staged.
    """
    ls = _run_git("ls-files", "-s")
    status = _run_git("status", "--porcelain")
    diff = _run_git("diff", "HEAD")
    dirty_files = sorted(line[3:].strip() for line in status.splitlines() if line.strip())
    return {
        "commit": _run_git("rev-parse", "HEAD").strip(),
        "dirty": bool(dirty_files),
        "dirty_files": dirty_files,
        "tree_sha256": hashlib.sha256(ls.encode()).hexdigest() if ls else None,
        # hash of the uncommitted diff, so a dirty result set is at least identified rather than
        # merely flagged; None when the tree is clean, which is the state a release should be in
        "uncommitted_diff_sha256": (hashlib.sha256(diff.encode()).hexdigest() if diff.strip()
                                    else None),
    }


def source_hashes():
    """Hash wq_common.py and every step script, plus a combined hash over the step scripts."""
    steps = sorted(f for f in os.listdir(HERE)
                   if f.startswith(STEP_GLOB) and f.endswith(".py"))
    per_step = {f: sha256_of_file(os.path.join(HERE, f)) for f in steps}
    blob = json.dumps(per_step, sort_keys=True, separators=(",", ":")).encode()
    return {
        "wq_common_sha256": sha256_of_file(os.path.join(HERE, "wq_common.py")),
        "provenance_sha256": sha256_of_file(os.path.join(HERE, "provenance.py")),
        "step_scripts_sha256": per_step,
        "step_scripts_combined_sha256": hashlib.sha256(blob).hexdigest(),
    }


def sha256_of_file(path):
    return B.sha256_of(path) if os.path.exists(path) else None


def changed_step_scripts(path=None):
    """[(script, recorded, current)] for each step script whose hash differs from the manifest.

    Not part of CRITICAL: editing one step's prose must not invalidate another step's cache. It is
    reported separately so "which results predate which edit?" has an answer.
    """
    path = MANIFEST if path is None else path
    if not os.path.exists(path):
        return []
    with open(path) as f:
        old = json.load(f)
    rec = (old.get("code") or {}).get("step_scripts_sha256", {})
    now = source_hashes()["step_scripts_sha256"]
    out = []
    for name in sorted(set(rec) | set(now)):
        if rec.get(name) != now.get(name):
            out.append((name, rec.get(name), now.get(name)))
    return out


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
        # The concentration unit is part of the experiment definition, not an implementation
        # detail. Before the kg/m^3 correction the same "inlet_mgl: 1.0" meant a 1000 mg/L source,
        # so a config hash that omitted the convention would have declared two physically different
        # caches identical. The solver tolerance is here for the same reason: it is an ABSOLUTE
        # concentration, so it only means anything alongside the unit it is measured in.
        "concentration_unit": "mg/L at every interface; kg/m^3 inside WNTR, converted in "
                              "wq_common.build_model / run_model / simulate_chlorine",
        "quality_tolerance_mg_L": B.QUALITY_TOLERANCE,
    }


def config_sha256(cfg=None):
    cfg = frozen_config() if cfg is None else cfg
    blob = json.dumps(cfg, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(blob).hexdigest()


def manifest():
    cfg = frozen_config()
    code = source_hashes()
    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "git": git_info(),
        "net3_inp": os.path.relpath(B.NET3_INP, os.path.dirname(HERE)),
        "net3_inp_sha256": B.sha256_of(B.NET3_INP),
        "config": cfg,
        "config_sha256": config_sha256(cfg),
        # promoted to the top level so it can be a CRITICAL field; the rest of `code` is a record
        "wq_common_sha256": code["wq_common_sha256"],
        "code": code,
        "critical_fields": list(CRITICAL),
        "scope": ("These hashes identify the code and environment that produced the cache. They do "
                  "NOT make the results reconstructible from the manifest alone when "
                  "git.uncommitted_diff_sha256 is non-null: the diff itself is not stored, only "
                  "identified. A release should be tagged from a clean tree, where that field is "
                  "null and git.tree_sha256 fully determines the source."),
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
        drift = changed_step_scripts()
        if bad:
            print("MANIFEST MISMATCH")
            for k, o, n in bad:
                print(f"  {k}\n    cache : {o}\n    now   : {n}")
        if drift:
            print(f"step scripts changed since the manifest was written ({len(drift)}); the "
                  f"artifacts they write may predate the edit:")
            for name, o, n in drift:
                print(f"  {name}: {'(new file)' if o is None else o[:12]} -> "
                      f"{'(deleted)' if n is None else n[:12]}")
        if bad:
            sys.exit(1)
        print("manifest OK — current environment matches the cached results"
              + (" (but see the step-script drift above)" if drift else ""))
    else:
        m = write_manifest()
        g = m["git"]
        print(f"wrote {os.path.relpath(MANIFEST, os.path.dirname(HERE))}")
        print(f"  config_sha256  {m['config_sha256']}")
        print(f"  wq_common      {m['wq_common_sha256'][:16]}...")
        print(f"  step scripts   {m['code']['step_scripts_combined_sha256'][:16]}... "
              f"({len(m['code']['step_scripts_sha256'])} files)")
        print(f"  net3_inp       {m['net3_inp']}  {m['net3_inp_sha256'][:16]}...")
        print(f"  git commit     {g['commit'][:12]}{' (DIRTY)' if g['dirty'] else ' (clean)'}")
        print(f"  git tree       {g['tree_sha256'][:16] if g['tree_sha256'] else '—'}...")
        if g["uncommitted_diff_sha256"]:
            print(f"  uncommitted    diff {g['uncommitted_diff_sha256'][:16]}... over "
                  f"{len(g['dirty_files'])} file(s) — the diff is identified but NOT stored, so "
                  f"this manifest does not by itself reconstruct the code that ran")
        print(f"  env            {m['conda_env']}  python {m['python']}  "
              f"numpy {m['numpy']}  scipy {m['scipy']}  wntr {m['wntr']}")
