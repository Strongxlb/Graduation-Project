"""Cross-check RESULTS_LOG.md, the figures and the JSON artifacts against each other.

RESULTS_LOG.md claims that every number in it comes from a script, but the numbers are copied in by
hand, so they drift whenever a script is re-run. This script detects that drift until the log is
generated from the artifacts directly.

The number check works on a simple asymmetry: a log number that matches no JSON value but sits
within STALE_REL_TOL of one is almost certainly a copy of an older run, whereas a log number that
is nowhere near any JSON value is usually prose (a threshold, a count of monitors, a citation year).
So near-misses fail the run and are listed; unmatched numbers are only counted, and listed under
--verbose.

Usage:
    python validate_artifacts.py            # summary; exit 1 if any check fails
    python validate_artifacts.py --verbose  # also list unmatched (probably prose) numbers
"""
import bisect
import json
import os
import re
import sys

import provenance

HERE = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(HERE, "baseline_cache")
LOG = os.path.join(HERE, "RESULTS_LOG.md")

# figures/ and Figures/ are the same directory on a case-insensitive filesystem; resolve whichever
# name exists so the check also works on Linux.
FIGDIR = next((os.path.join(HERE, d) for d in ("figures", "Figures")
               if os.path.isdir(os.path.join(HERE, d))), os.path.join(HERE, "figures"))

STALE_REL_TOL = 0.02      # a near-miss this close to a JSON value is treated as a stale copy
MIN_INT_TO_CHECK = 10     # below this, integers are too ambiguous to match usefully
MAX_DP = 6                # deepest rounding compared; a percent form needs two more than written

# Canonical section label -> the artifacts whose numbers that section may quote.
# The labels are also the reference for the numbering check: a "## Step X" heading in the log must
# appear here, which is what keeps section labels and script filenames aligned.
SECTIONS = {
    "Step 0": ["step0_warmup_convergence.json"],
    "Step 1": ["baseline_meta.json"],
    "Step 2": ["baseline_meta.json", "step3_threshold.json"],
    # Step 3 tabulates the formal-likelihood row from Step 1 for contrast, so it legitimately
    # quotes that artifact as well; declaring it keeps the strict table rule usable.
    "Step 3": ["step3_threshold.json", "baseline_meta.json"],
    "Step 4": ["step4_displaced_prior.json"],
    "Step 4b": ["step4b_sensitivity.json"],
    "Step 4d": ["step4d_displaced_robust.json"],
    "Step 5": ["step5_structural_error.json"],
    "Step 5a": ["step5_structural_error.json"],
    "Step 5c": ["step5c_jitter_sweep.json"],
    "Step 5c-ensemble": ["step5c_jitter_sweep.json"],
    "Step 5d": ["step5d_structured.json"],
    "Step 5d-dose": ["step5d_structured.json"],
    "Step 5e": ["step5d_structured.json"],   # grid geometry is recorded there
    "Step 6": ["step6_noise_sensitivity.json"],
    "Step 7": ["step7_fisher.json"],
    "Step 7b": ["step7b_profile.json"],
    "Step 7c": ["step7c_ar1.json", "step7c_profile_ar1.json"],
    # the bias-location sweep table lives inside the Step 8 section
    "Step 8": ["step8_sensor_bias.json", "step8c_bias_bynode.json"],
    "Step 8b": ["step8b_kb_sensitivity.json"],
    "Step 8c": ["step8c_bias_bynode.json"],
    "Step 9": ["step9_zeroclip.json"],
    "Step 10": ["step10_risk_metrics.json"],
    "Step 11": ["step11_loo.json"],
    "Step 11b": ["step11_loo.json"],
    "Step 11c": ["step11_loo.json"],
    "Step 11d": ["step11_loo.json"],
    "Step 12": ["step12_scenarios.json"],
    "Step 13": ["step13_known_answer.json"],
}

FIGURE_SOURCE = {
    "step0_warmup_convergence.png": "step0_warmup_convergence.json",
    "step4b_sensitivity_curves.png": "step4b_sensitivity.json",
    "step4d_displaced_robust.png": "step4d_displaced_robust.json",
    "step5_structural_error.png": "step5_structural_error.json",
    "step5c_jitter_sweep.png": "step5c_jitter_sweep.json",
    "step5d_structured.png": "step5d_structured.json",
    "step6_noise_sensitivity.png": "step6_noise_sensitivity.json",
    "step7_fisher.png": "step7_fisher.json",
    "step7b_profile.png": "step7b_profile.json",
    "step8_sensor_bias.png": "step8_sensor_bias.json",
    "step8b_kb_sensitivity.png": "step8b_kb_sensitivity.json",
    "step9_zeroclip.png": "step9_zeroclip.json",
    "step10_risk_metrics.png": "step10_risk_metrics.json",
    "step11_loo.png": "step11_loo.json",
    "step12_summary.png": "step12_scenarios.json",
    "step12_scenario_maps.png": "step12_scenarios.json",
    "step12_ageing_delta.png": "step12_scenarios.json",
}
FIGURE_STALE_S = 60      # a figure written in the same script run may predate its JSON by seconds

# Numbers that legitimately appear as prose constants anywhere in the log.
CONSTANTS = {
    0.02, 0.025, 0.05, 0.1, 0.107, 0.11, 0.12, 0.15, 0.2, 0.4, 0.5, 0.6, 0.9, 0.95, 1.0, 1.645,
    1.92, 1.96, 2.0, 6.0, 12.0, 16.0, 20.0, 24.0, 30.0, 48.0, 49.0, 72.0, 92.0, 120.0, 168.0,
    294.0, 2000.0,
}
# Quantile/percentile labels ("5-95% band", "25/75 IQR") read as bare integers.
PERCENTILES = {1, 5, 10, 25, 50, 68, 75, 90, 95, 99, 100}
# Junction names in Net3 are numeric strings, so they collide with measurements unless excluded.
NODE_IDS = {float(n) for n in provenance.B.all_junctions()}
CITATION_YEARS = range(1900, 2101)

# (regex, why it is wrong). Kept narrow on purpose: a broad unit scan is all false positives.
UNIT_RULES = [
    (re.compile(r"(?i)(coefficient|k_?w).{0,80}SD.{0,20}\(mg/L\)"),
     "wall coefficients are m/day, not mg/L"),
    (re.compile(r"(?i)k_?b.{0,40}\(mg/L\)"),
     "the bulk coefficient is per day, not mg/L"),
]
PATH_RULES = [
    (re.compile(r"/opt/anaconda3|/Users/|C:\\\\"), "machine-specific absolute path"),
]

HEADING = re.compile(r"^#{2,4}\s+(Step\s+[\w.]+?)\s*(?:—|-|–|$)", re.M)
NUMBER = re.compile(r"(?<![\w.])(-?\d+(?:\.\d+)?)(?![\w.]*\d)")
# Lines that deliberately quote a superseded run cannot be checked: no current artifact holds those
# numbers, and that is the point of the sentence. The phrasing is the opt-out.
SUPERSEDED = re.compile(r"(?i)\b(an? earlier (run|version)|draft'?s earlier|earlier single-window|"
                        r"superseded|previously reported|before the fix)\b")


# ---------------------------------------------------------------- helpers
def walk_numbers(obj):
    """Every numeric leaf in a JSON structure, including numbers embedded in strings."""
    if isinstance(obj, bool):
        return
    if isinstance(obj, (int, float)):
        yield float(obj)
    elif isinstance(obj, dict):
        for k, v in obj.items():
            for n in walk_numbers(k):
                yield n
            for n in walk_numbers(v):
                yield n
    elif isinstance(obj, (list, tuple)):
        for v in obj:
            for n in walk_numbers(v):
                yield n
    elif isinstance(obj, str):
        for m in NUMBER.finditer(obj):
            try:
                yield float(m.group(1))
            except ValueError:
                pass


def value_set(paths):
    """Sorted absolute values of every numeric leaf in the given artifacts.

    Matching is done by interval rather than by equality of roundings: a log number written to d
    decimals is consistent with any artifact value within half a unit in the last place. Comparing
    rounded values instead misfires on ties (1755/2000 = 0.8775 prints as 87.8% but rounds to 0.877).
    Signs are dropped because the log writes negatives with U+2212, which does not parse.
    """
    vals = set()
    for p in paths:
        full = os.path.join(CACHE, p)
        if not os.path.exists(full):
            continue
        with open(full) as f:
            data = json.load(f)
        vals.update(abs(v) for v in walk_numbers(data))
    return sorted(vals)


def log_sections():
    """[(label, body, first_line_no)] for each Step heading in the log, in order."""
    text = open(LOG).read()
    marks = [(m.start(), m.group(1).strip()) for m in HEADING.finditer(text)]
    out = []
    for i, (pos, label) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(text)
        line_no = text.count("\n", 0, pos) + 1
        out.append((re.sub(r"\s+", " ", label), text[pos:end], line_no))
    return out, text


def num_f(num_str):
    return float(num_str)


def is_excluded(num_str):
    """Numbers that cannot be compared against artifacts: labels, identifiers, constants."""
    v = float(num_str)
    if abs(v) in CONSTANTS:
        return True
    if "." not in num_str:                       # bare integers carry the ambiguous cases
        iv = int(v)
        return (abs(v) < MIN_INT_TO_CHECK or iv in PERCENTILES or iv in CITATION_YEARS
                or abs(v) in NODE_IDS)
    return False


def _dp(num_str):
    return len(num_str.split(".")[1]) if "." in num_str else 0


def candidates(num_str):
    """(|value|, half-width) intervals a log number may occupy relative to the stored value.

    Two rescalings are routine in the log and neither is an error: fractions are stored (0.6611) and
    quoted as percentages (66.1%), and SI quantities are stored in base units but quoted with a
    prefix (activation energies in J/mol, quoted in kJ/mol). Each form carries its own half-width,
    so a percentage is compared at the precision it implies for the fraction, not at its own.
    """
    v, dp = abs(float(num_str)), _dp(num_str)
    half = 0.5 * 10 ** -dp
    return [(v, half),
            (v / 100.0, half / 100.0), (v * 100.0, half * 100.0),
            (v / 1000.0, half / 1000.0), (v * 1000.0, half * 1000.0)]


def matches(num_str, pools):
    """True if some artifact value could have been rounded to the number as written.

    The interval is widened by a relative epsilon because rescaling introduces representation
    error: 87.8/100 is 0.8780000000000001, whose exact lower bound would exclude a stored 0.8775.
    """
    for v, half in candidates(num_str):
        half += abs(v) * 1e-9 + 1e-12
        for vals in pools:
            i = bisect.bisect_left(vals, v - half)
            if i < len(vals) and vals[i] <= v + half:
                return True
    return False


def nearest(num_str, pools):
    """Nearest artifact value to the number as written, ignoring sign (the log uses U+2212)."""
    v = abs(float(num_str))
    best = None
    for vals in pools:
        for x in vals:
            if best is None or abs(x - v) < abs(best - v):
                best = x
    return best


# ---------------------------------------------------------------- checks
def check_artifacts_exist():
    missing = sorted({p for ps in SECTIONS.values() for p in ps
                      if not os.path.exists(os.path.join(CACHE, p))})
    fig_missing = sorted(f for f in FIGURE_SOURCE if not os.path.exists(os.path.join(FIGDIR, f)))
    problems = [f"missing artifact: baseline_cache/{p}" for p in missing]
    problems += [f"missing figure: {os.path.basename(FIGDIR)}/{f}" for f in fig_missing]
    referenced = {p for ps in SECTIONS.values() for p in ps} | {"cache_manifest.json"}
    orphans = sorted(f for f in os.listdir(CACHE)
                     if f.endswith(".json") and f not in referenced
                     and not f.endswith(".npy.key.json"))   # provenance sidecars, not results
    notes = [f"artifact not mapped to any log section: {o}" for o in orphans]
    return problems, notes


def check_manifest():
    bad = provenance.check_manifest()
    return [f"manifest field {k!r}: cache={o!r} now={n!r}" for k, o, n in bad], []


def check_figure_freshness():
    problems = []
    for fig, src in FIGURE_SOURCE.items():
        fp, sp = os.path.join(FIGDIR, fig), os.path.join(CACHE, src)
        if not (os.path.exists(fp) and os.path.exists(sp)):
            continue
        lag = os.path.getmtime(sp) - os.path.getmtime(fp)
        if lag > FIGURE_STALE_S:
            problems.append(f"{fig} is {lag / 60:.1f} min older than {src} — regenerate it")
    return problems, []


def check_numbering(sections):
    problems = []
    scripts = os.listdir(HERE)
    for label, _, _ in sections:
        if label not in SECTIONS:
            problems.append(f"log heading {label!r} is not a known section "
                            f"(known: {', '.join(sorted(SECTIONS))})")
            continue
        stem = label.replace("Step ", "step").replace(" ", "")
        # sub-sections that a single script produces rather than having a file of their own
        if not any(s.startswith(stem + "_") for s in scripts) and stem not in (
                "step2", "step5a", "step5e", "step11b", "step11c",
                "step5c-ensemble", "step5d-dose", "step11d"):
            problems.append(f"log heading {label!r} has no matching {stem}_*.py script")
    return problems, []


def check_log_numbers(sections, verbose=False):
    """Compare each section's numbers with its own artifacts, then with all artifacts.

    The global fallback matters because the log legitimately cross-references numbers between
    sections (a prior SD quoted in Step 2 lives in the Step 7 artifact). Only a number that matches
    NOWHERE, yet sits within STALE_REL_TOL of some artifact value, is reported as stale.
    """
    problems, notes = [], []
    global_pool = value_set(sorted({p for ps in SECTIONS.values() for p in ps}))
    total_ok = total_un = total_xref = 0
    for label, body, first_line in sections:
        if label not in SECTIONS:
            continue
        own_pool = value_set(SECTIONS[label])
        if not own_pool:
            notes.append(f"{label}: no artifact values available, numbers unchecked")
            continue
        stale, unmatched, exempt, global_only = [], [], 0, []
        # The exemption is scoped to the markdown paragraph, not the line: prose wraps, so the
        # marker phrase and the superseded numbers it introduces often land on different lines.
        para_exempt = False
        for offset, line in enumerate(body.splitlines()):
            line_no = first_line + offset
            if not line.strip():
                para_exempt = False
                continue
            if line.lstrip().startswith("#"):     # headings carry sub-section numbers, not results
                continue
            if SUPERSEDED.search(line):
                para_exempt = True
            if para_exempt:
                exempt += 1
                continue
            # A markdown table row is where results are reported; prose is where other sections get
            # cross-referenced. Table cells are therefore held to the section's OWN artifact — the
            # global pool let a whole stale results table survive a change of weighting scheme on
            # coincidental hits. The rule applies only from three decimals up: with thousands of
            # values in the pool, a two-decimal cell matches somewhere no matter what, so demanding
            # provenance for it would be a guess dressed up as a check.
            in_table = line.lstrip().startswith("|")
            for m in NUMBER.finditer(line):
                num = m.group(1)
                if is_excluded(num):
                    continue
                if matches(num, [own_pool]):
                    total_ok += 1
                    continue
                strict = in_table and _dp(num) >= 3
                if not strict and matches(num, [global_pool]):
                    # Legal in prose, but with thousands of values a coincidental hit is possible,
                    # so these are surfaced for eyeballing rather than silently counted as verified.
                    total_ok += 1
                    global_only.append(num)
                    continue
                near = nearest(num, [own_pool, global_pool])
                if near is not None and 0 < abs(near - num_f(num)) / max(abs(near), 1e-12) \
                        <= STALE_REL_TOL:
                    stale.append((num, near, line_no))
                else:
                    unmatched.append(num)
        total_un += len(unmatched)
        for got, near, line_no in stale:
            problems.append(f"RESULTS_LOG.md:{line_no} ({label}): log says {got}; "
                            f"no artifact has it, nearest artifact value is {near:g}")
        if verbose and unmatched:
            notes.append(f"{label}: {len(unmatched)} unmatched (likely prose): "
                         f"{', '.join(sorted(set(unmatched))[:20])}")
        if verbose and exempt:
            notes.append(f"{label}: {exempt} line(s) exempt as describing a superseded run")
        if verbose and global_only:
            notes.append(f"{label}: {len(global_only)} number(s) match another section's artifact "
                         f"but not this one — check they are intended cross-references: "
                         f"{', '.join(sorted(set(global_only))[:12])}")
        total_xref += len(global_only)
    notes.append(f"numbers matched to artifacts: {total_ok} (of which {total_xref} matched only "
                 f"another section's artifact; --verbose lists them); unmatched (likely prose): "
                 f"{total_un}")
    return problems, notes


def check_text_rules(text):
    problems = []
    for i, line in enumerate(text.splitlines(), 1):
        for rx, why in UNIT_RULES + PATH_RULES:
            if rx.search(line):
                problems.append(f"RESULTS_LOG.md:{i}: {why} -> {line.strip()[:90]}")
    return problems, []


def check_env_claims(text):
    problems = []
    with open(os.path.join(CACHE, "cache_manifest.json")) as f:
        man = json.load(f)
    m = re.search(r"conda env `([\w.-]+)`", text)
    if m and m.group(1) != man["conda_env"]:
        problems.append(f"log claims conda env `{m.group(1)}` but the cache was produced in "
                        f"`{man['conda_env']}`")
    for pkg in ("numpy", "wntr", "scipy"):
        for got in re.findall(rf"(?i){pkg}\s+([0-9]+\.[0-9]+(?:\.[0-9]+)?)", text):
            if not man[pkg].startswith(got) and not got.startswith(man[pkg]):
                problems.append(f"log claims {pkg} {got} but the cache was produced with "
                                f"{pkg} {man[pkg]}")
    return problems, []


# ---------------------------------------------------------------- driver
def main(verbose=False):
    sections, text = log_sections()
    checks = [
        ("artifacts exist", lambda: check_artifacts_exist()),
        ("cache manifest", lambda: check_manifest()),
        ("figure freshness", lambda: check_figure_freshness()),
        ("section numbering", lambda: check_numbering(sections)),
        ("log numbers vs artifacts", lambda: check_log_numbers(sections, verbose)),
        ("units and paths", lambda: check_text_rules(text)),
        ("environment claims", lambda: check_env_claims(text)),
    ]
    failed = 0
    for name, fn in checks:
        problems, notes = fn()
        status = "FAIL" if problems else "pass"
        print(f"[{status}] {name}" + (f" — {len(problems)} problem(s)" if problems else ""))
        for p in problems:
            print(f"         {p}")
        for n in notes:
            print(f"         note: {n}")
        failed += bool(problems)
    print(f"\n{len(checks) - failed}/{len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(verbose="--verbose" in sys.argv))
