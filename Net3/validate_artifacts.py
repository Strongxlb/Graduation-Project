"""Cross-check RESULTS_LOG.md, README.md, the figures and the JSON artifacts against each other.

The prose numbers are copied in by hand, so they drift whenever a script is re-run. These checks
detect that drift until the documents are generated from the artifacts directly.

WHAT THIS SCRIPT DOES AND DOES NOT ESTABLISH — read before quoting a passing run.

  It establishes, for the numbers it covers:
    * a registered CLAIM (the list below) equals a named value at a named JSON path. This is the only
      check with real teeth, because both the sentence and the source are pinned;
    * every result artifact declares which weighting produced it, so a table cannot be read under the
      wrong inference rule;
    * no log number is a near-miss of a JSON value, which is the signature of a stale transcription;
    * no forbidden phrasing survives (superseded configurations, over-claimed wording);
    * the environment and the frozen model file match the ones that produced the cache.

  It does NOT establish:
    * that the artifacts themselves are correct. If a script computes the wrong thing, every check
      here confirms only that the prose faithfully reports a wrong number;
    * that an unregistered number in the prose came from anywhere. The general number check is a
      drift detector, not a provenance proof: with thousands of values in the pool, a two-decimal
      figure matches something by coincidence, which is why table cells are held to their own
      section's artifact from three decimals up and why the claim registry exists;
    * SEMANTIC consistency. Nothing here notices that two sections draw opposite conclusions, that a
      caveat has gone missing, or that a correct number is described with the wrong words;
    * that a figure shows what its caption says. Figure freshness is a file-timestamp comparison
      only.

A passing run therefore means "no detected drift in the covered numbers", not "the log is verified".

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
REPO = os.path.dirname(HERE)
CACHE = os.path.join(HERE, "baseline_cache")
LOG = os.path.join(HERE, "RESULTS_LOG.md")
DOCS = {"RESULTS_LOG.md": LOG,
        "README.md": os.path.join(REPO, "README.md"),
        "README.en.md": os.path.join(REPO, "README.en.md"),
        "REVISION_RESPONSE_MATRIX.md": os.path.join(REPO, "REVISION_RESPONSE_MATRIX.md")}

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
    "Step 8d": ["step8d_sensor_drift.json"],
    "Step 9": ["step9_zeroclip.json"],
    "Step 10": ["step10_risk_metrics.json"],
    "Step 11": ["step11_loo.json"],
    "Step 11b": ["step11_loo.json"],
    "Step 11c": ["step11_loo.json"],
    "Step 11d": ["step11_loo.json"],
    "Step 12": ["step12_scenarios.json"],
    "Step 13": ["step13_known_answer.json"],
    "Step 14": ["step14_repeated_noise.json"],
}

# Every result artifact must say which weighting produced it. Without this a table of numbers is
# only implicitly attached to an inference rule, which is how an informal-GLUE result ends up quoted
# under a formal heading. Accepted keys, in order of preference.
WEIGHTING_KEYS = ("primary_weighting", "weighting")
# Artifacts that hold no weighted ensemble and so have no weighting to declare: a warm-up
# convergence test, Fisher/profile geometry, and an analytic known-answer test.
WEIGHTING_EXEMPT = {"cache_manifest.json", "step0_warmup_convergence.json",
                    "step4b_sensitivity.json",   # single-parameter RMSE curves; no ensemble weights
                    "step7_fisher.json",         # a-priori Fisher/CRLB; ensemble SD is a side check
                    "step7b_profile.json", "step7c_ar1.json", "step7c_profile_ar1.json",
                    "step9_zeroclip.json",       # compares two formal likelihoods on one realisation
                    "step13_known_answer.json"}

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
    "step8d_sensor_drift.png": "step8d_sensor_drift.json",
    "step9_zeroclip.png": "step9_zeroclip.json",
    "step10_risk_metrics.png": "step10_risk_metrics.json",
    "step11_loo.png": "step11_loo.json",
    "step12_summary.png": "step12_scenarios.json",
    "step12_scenario_maps.png": "step12_scenarios.json",
    "step12_ageing_delta.png": "step12_scenarios.json",
    "step14_repeated_noise.png": "step14_repeated_noise.json",
}
FIGURE_STALE_S = 60      # a figure written in the same script run may predate its JSON by seconds

# ---------------------------------------------------------------- claim registry
# Each entry pins ONE sentence in ONE document to ONE value at ONE JSON path. This is the check with
# real teeth: the general number scan can only notice that a figure is near something, whereas a
# registered claim fails both when the number changes AND when the sentence is reworded so that the
# anchor disappears — which is the failure mode that let a whole stale table survive before.
#
# Fields: (document, regex with exactly one capture group, artifact, dotted JSON path, scale)
# `scale` multiplies the stored value before comparison, so a stored fraction can be claimed as a
# percentage. Precision is taken from the number as written.
CLAIMS = [
    # --- headline: how much prior width each weighting retains (the project's central contrast) ---
    ("RESULTS_LOG.md", r"formal censored[^\n]{0,120}?retains\s+([0-9.]+)\s*/\s*[0-9.]+\s*/\s*[0-9.]+\s*%",
     "baseline_meta.json", "summary/schemes/formal_censored/coef/old/sd_retained", 100),
    ("RESULTS_LOG.md", r"formal censored[^\n]{0,120}?retains\s+[0-9.]+\s*/\s*([0-9.]+)\s*/\s*[0-9.]+\s*%",
     "baseline_meta.json", "summary/schemes/formal_censored/coef/avg/sd_retained", 100),
    ("RESULTS_LOG.md", r"formal censored[^\n]{0,120}?retains\s+[0-9.]+\s*/\s*[0-9.]+\s*/\s*([0-9.]+)\s*%",
     "baseline_meta.json", "summary/schemes/formal_censored/coef/new/sd_retained", 100),
    ("README.md", r"censored 正式似然只保留\s*\*\*([0-9.]+)\s*/\s*[0-9.]+\s*/\s*[0-9.]+%\*\*",
     "baseline_meta.json", "summary/schemes/formal_censored/coef/old/sd_retained", 100),
    ("README.md", r"censored 正式似然只保留\s*\*\*[0-9.]+\s*/\s*([0-9.]+)\s*/\s*[0-9.]+%\*\*",
     "baseline_meta.json", "summary/schemes/formal_censored/coef/avg/sd_retained", 100),
    ("README.md", r"censored 正式似然只保留\s*\*\*[0-9.]+\s*/\s*[0-9.]+\s*/\s*([0-9.]+)%\*\*",
     "baseline_meta.json", "summary/schemes/formal_censored/coef/new/sd_retained", 100),
    ("README.md", r"informal GLUE（草稿阈值 `0.12`）保留了先验宽度的 \*\*([0-9.]+)\s*/\s*[0-9.]+\s*/\s*[0-9.]+%\*\*",
     "baseline_meta.json", "summary/schemes/informal_glue_draft_thr/coef/old/sd_retained", 100),
    # --- the a-priori bound the posterior width is compared with ---
    ("RESULTS_LOG.md", r"Case[- ]A CRLB[^\n]{0,80}?old\s+([0-9.]+)",
     "step7_fisher.json", "cases/A: kw only/coef/old/crlb", 1),
    # --- Step 14: the repeated-sampling claims that replace "the estimator is efficient" ---
    ("RESULTS_LOG.md", r"empirical SD / CRLB[^\n]{0,80}?([0-9.]+)\s*/\s*[0-9.]+\s*/\s*[0-9.]+",
     "step14_repeated_noise.json",
     "by_scheme/formal_censored/coef/old/empirical_sd_over_crlb", 1),
    ("RESULTS_LOG.md", r"nominal 90% intervals cover[^\n]{0,80}?([0-9.]+)\s*/\s*[0-9.]+\s*/\s*[0-9.]+",
     "step14_repeated_noise.json", "by_scheme/formal_censored/coef/old/coverage/q90", 1),
    # --- warm-up: the residual drift that stops "converged" from being sayable ---
    ("RESULTS_LOG.md", r"residual cycle-to-cycle drift[^\n]{0,90}?([0-9.]+)\s*%",
     "step0_warmup_convergence.json", "per_criterion/risk_rel_dDeficit/worst_by_cycle[5]", 100),
    ("RESULTS_LOG.md", r"water age[^\n]{0,90}?still\s+([0-9.]+)\s*h between the last two cycles",
     "step0_warmup_convergence.json", "per_criterion/age_p95_dAge/worst_by_cycle[5]", 1),
    # --- risk: the descriptive association, and that no p-value is claimed ---
    ("RESULTS_LOG.md", r"Spearman ρ = ([0-9.]+)[^\n]{0,40}descriptive",
     "step10_risk_metrics.json", "age_risk_association/spearman_dur", 1),
    # --- sensor bias: displacement in posterior-SD units, primary rule ---
    ("RESULTS_LOG.md", r"\+0\.10 mg/L at node 15 moves[^\n]{0,60}?([0-9.]+)\s*posterior SD",
     "step8_sensor_bias.json", "rows[6]/shift_over_sd", 1),
    # --- sensor drift: the ratio that decides whether a drift needs its own analysis at all ---
    ("RESULTS_LOG.md", r"the ratio reaches\s+\*\*([0-9.]+)\*\*\s+at D = \+0\.10",
     "step8d_sensor_drift.json", "equivalence/231/+0.100/drift_over_const_mean", 1),
    ("RESULTS_LOG.md", r"\| 15 \(old\) \| −0\.100 \| −([0-9.]+) \|",
     "step8d_sensor_drift.json", "rows[0]/own_shift_over_sd", -1),
    # --- sensor accuracy: the answer that changed when the primary rule changed ---
    ("RESULTS_LOG.md", r"σ = 0\.10[^\n]{0,90}?retains\s+([0-9.]+)\s*/\s*[0-9.]+\s*/\s*[0-9.]+\s*% of the prior",
     "step6_noise_sensitivity.json",
     "rows[2]/by_scheme/formal_censored/old/sd_ret_med", 100),
    # --- profile likelihood: the continuous interval, which is the one that may be quoted ---
    ("RESULTS_LOG.md", r"continuous 95% interval for `k_w,old` is \[−([0-9.]+),",
     "step7b_profile.json",
     "continuous_profile/by_likelihood/censored/coef/old/lo", -1),
    # --- scenarios: the node counts the Discussion leans on ---
    ("README.md", r"baseline ([0-9]+) nodes", "step12_scenarios.json",
     "scenario_summary[0]/P_min_gt_0.5_nodes", 1),
    ("README.md", r"heat \+ ageing ([0-9]+)", "step12_scenarios.json",
     "scenario_summary[3]/P_min_gt_0.5_nodes", 1),
]

# (document, regex, why it must not appear). These are the specific wordings a previous revision left
# behind: a superseded configuration, a claim stronger than its evidence, or a label naming the wrong
# inference rule. A number check cannot catch any of them, because each is a sentence about numbers
# that are themselves current.
FORBIDDEN = [
    (r"(?i)\b2000[- ](draw|sample|member|prior draw)", "the design is 8192 scrambled Sobol draws"),
    (r"(?i)2000 EPANET runs", "the baseline is 8192 EPANET runs"),
    (r"(?i)\b24 ?h warm-?up\b(?![^\n]{0,60}(draft|superseded|earlier|was ))",
     "the warm-up is 120 h; 24 h is the superseded draft value and must be marked as such"),
    (r"(?i)72 ?h simulation(?![^\n]{0,60}(draft|superseded|earlier))",
     "the horizon is 168 h; 72 h is the superseded draft value"),
    (r"(?i)≈\s*residence-weighted|residence-weighted[^\n]{0,20}\(i\.e\.|"
     r"recovers the residence-weighted",
     "length-weighted is an illustrative proxy, NOT the residence-weighted coefficient (Step 5d)"),
    (r"(?i)GLUE behavioural mean of|"
     r"(?<!informal )GLUE (behavioural )?(mean|posterior)(?![^\n]{0,40}comparator)",
     "name the rule: the primary results are formal censored posterior means, not GLUE means"),
    (r"(?i)p\s*[≈=]\s*1e-16|p\s*<\s*1e-1[0-9]",
     "no p-value is reported for the age-risk association; the junctions are not independent"),
    (r"(?i)(proven|demonstrably|shown to be) efficient|estimator is efficient|"
     r"(reached|reaches|attained|attains) the (Cramér–Rao|Cramer-Rao|CRLB)",
     "the formal posterior spread is LOCALLY CONSISTENT with the CRLB; efficiency needs the "
     "repeated-sampling test in Step 14"),
    (r"(?i)(complete|full) periodic steady state|water age had converged|has converged after 120",
     "120 h is a finite-horizon pragmatic choice; the deficit and water-age criteria never pass"),
    (r"(?i)all numbers are checked|every number is verified|7/7 checks passing",
     "the validator covers a subset of numbers and establishes no semantic consistency"),
]
# Documents where FORBIDDEN is enforced. The response matrix is included because that is where the
# over-claims lived.
FORBIDDEN_DOCS = ["RESULTS_LOG.md", "README.md", "README.en.md", "REVISION_RESPONSE_MATRIX.md"]

# Numbers that legitimately appear as prose constants anywhere in the log.
CONSTANTS = {
    0.02, 0.025, 0.05, 0.1, 0.107, 0.11, 0.12, 0.15, 0.2, 0.4, 0.5, 0.6, 0.9, 0.95, 1.0, 1.645,
    1.92, 1.96, 2.0, 6.0, 12.0, 16.0, 20.0, 24.0, 30.0, 48.0, 49.0, 72.0, 92.0, 100.0, 120.0,
    168.0, 294.0, 8192.0,
    # Algebraic consequences of N and sigma rather than outputs of any script, so no artifact holds
    # them and the drift check would otherwise match them against an unrelated value by proximity.
    17.15,      # sqrt(N) = sqrt(294), the factor by which the informal score inflates sigma
    1.71,       # sigma * sqrt(N) = the informal score's effective observation sd, mg/L
    0.0041,     # sigma / sqrt(2N), the sampling sd of the RMSE objective at the truth
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
# The second lookbehind drops numbers that are part of a hyphenated identifier (SHA-256, UTF-8,
# AR-1), which are names rather than measurements.
NUMBER = re.compile(r"(?<![\w.])(?<!\w-)(-?\d+(?:\.\d+)?)(?![\w.]*\d)")
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


# NOT IMPLEMENTED, deliberately: a number check on README.md.
#
# The README summarises every section, so it has no per-section artifact mapping and its comparison
# pool is the union of all artifacts — thousands of values at every rounding. A check against that
# pool cannot fail: injecting three realistic regressions (SD retained 86/98/98 -> 84/97/98, a CRLB
# ratio 1.06 -> 1.11, and the warm-up 120 h -> 96 h) was caught ZERO times out of three. A check in
# this list that cannot fail is worse than no check, because it turns an unverified document into a
# green light, so it was removed rather than shipped.
#
# The workable version is an explicit claim registry — each README figure mapped to a JSON path in a
# named artifact, roughly 40 entries — which is precise but is real work. Until that exists, the
# README's numbers are verified only by whoever transcribed them, i.e. exactly the position
# RESULTS_LOG.md was in before this tooling (93 stale numbers).


_PATH_STEP = re.compile(r"([^/\[\]]+)|\[(\d+)\]")


def json_at(data, path):
    """Value at a slash-separated path with optional [i] indices.

    Slash rather than dot because several JSON keys contain a dot ("P_min_gt_0.5_nodes"), and a
    separator that appears inside key names silently mis-parses instead of failing.
    """
    cur = data
    for key, idx in _PATH_STEP.findall(path):
        cur = cur[int(idx)] if idx else cur[key]
    return cur


def read_doc(name):
    p = DOCS[name]
    return open(p).read() if os.path.exists(p) else None


def check_claims():
    """Every registered claim: the anchor must exist and the number must equal its JSON source."""
    problems, notes = [], []
    loaded, checked = {}, 0
    for doc, pattern, artifact, path, scale in CLAIMS:
        text = read_doc(doc)
        if text is None:
            problems.append(f"claim document missing: {doc}")
            continue
        if artifact not in loaded:
            full = os.path.join(CACHE, artifact)
            loaded[artifact] = json.load(open(full)) if os.path.exists(full) else None
        data = loaded[artifact]
        if data is None:
            problems.append(f"claim source missing: baseline_cache/{artifact}")
            continue
        try:
            want = float(json_at(data, path)) * scale
        except (KeyError, IndexError, TypeError, ValueError):
            problems.append(f"claim path not found in {artifact}: {path}")
            continue
        found = re.findall(pattern, text)
        if not found:
            problems.append(f"{doc}: registered claim has no anchor — the sentence matching "
                            f"/{pattern}/ is gone, so {artifact}:{path} is no longer checked "
                            f"anywhere. Restore the wording or update CLAIMS.")
            continue
        for got in found:
            got = got if isinstance(got, str) else got[0]
            got = got.strip().rstrip(".,;:")
            half = 0.5 * 10 ** -_dp(got) + abs(want) * 1e-9 + 1e-12
            if abs(float(got) - want) > half:
                problems.append(f"{doc}: claims {got} but {artifact}:{path} is {want:g}")
            else:
                checked += 1
    notes.append(f"{checked} registered claim(s) verified against a named JSON path "
                 f"(of {len(CLAIMS)} registered)")
    return problems, notes


def check_weighting_declared():
    """Every result artifact must name the weighting that produced it."""
    problems, notes = [], []
    for fn in sorted(os.listdir(CACHE)):
        if not fn.endswith(".json") or fn.endswith(".npy.key.json") or fn in WEIGHTING_EXEMPT:
            continue
        with open(os.path.join(CACHE, fn)) as f:
            data = json.load(f)
        if not isinstance(data, dict):
            problems.append(f"{fn}: top level is a {type(data).__name__}, so it cannot carry a "
                            f"weighting declaration — wrap it in an object")
            continue
        if not any(k in data for k in WEIGHTING_KEYS):
            problems.append(f"{fn}: no {' or '.join(WEIGHTING_KEYS)} field — a table of weighted "
                            f"numbers whose weighting is only implied by the script that wrote it")
    notes.append(f"{len(WEIGHTING_EXEMPT)} artifact(s) exempt (no weighted ensemble): "
                 f"{', '.join(sorted(WEIGHTING_EXEMPT))}")
    return problems, notes


def check_forbidden():
    """Wordings that a previous revision left behind and that no number check can catch."""
    problems = []
    for doc in FORBIDDEN_DOCS:
        text = read_doc(doc)
        if text is None:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            if SUPERSEDED.search(line):
                continue
            for rx, why in FORBIDDEN:
                if re.search(rx, line):
                    problems.append(f"{doc}:{i}: {why}\n           -> {line.strip()[:110]}")
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
        ("weighting declared in every artifact", lambda: check_weighting_declared()),
        ("registered claims vs JSON paths", lambda: check_claims()),
        ("forbidden / superseded wording", lambda: check_forbidden()),
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
    print("Scope: this detects drift in the numbers it covers and the wordings it lists. It does not "
          "verify that the artifacts are correct, that unregistered numbers have a source, or that "
          "any two sections agree with each other. Read the docstring before quoting a pass.")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(verbose="--verbose" in sys.argv))
