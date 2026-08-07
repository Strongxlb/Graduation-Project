#!/bin/bash
# Build the Research Paper: paper.md -> paper.docx, and report the word count on the
# official rule (abstract + body + figure/table captions count; references and table
# content do not).
set -euo pipefail
cd "$(dirname "$0")"

CSL="${CSL:-$HOME/Zotero/styles/harvard-cite-them-right.csl}"
[ -f "$CSL" ] || { echo "CSL not found: $CSL" >&2; exit 1; }

# Splice artifact-generated tables into a working copy, so no table body is ever hand-typed:
# {{TABLE2}} pulls the pipe table straight out of what paper_figs.py wrote.
python3 - <<'SPLICE'
import re
src  = open('paper.md').read()
tabs = open('../Net3/Figures/paper/tables.md').read()
blocks = {}
for m in re.finditer(r'^## Table (\d+) .*?$(.*?)(?=^## Table |\Z)', tabs, re.M | re.S):
    body, run = [], []
    for l in m.group(2).split('\n'):
        if l.strip().startswith('|'):
            run.append(l)
        elif run:
            body.append('\n'.join(run)); run = []
    if run:
        body.append('\n'.join(run))
    blocks[m.group(1)] = '\n\n'.join(body)
def sub(m):
    if m.group(1) not in blocks:
        raise SystemExit('TABLE%s not found in tables.md' % m.group(1))
    return blocks[m.group(1)]

DEFTABLE = r"""| Symbol | Definition | Section |
|---|---|---|
| $R_{\mathrm{SD},j}$ | $\sigma_{\mathrm{post},j}/\sigma_{\mathrm{prior},j}$, reported as SD retained | 2.4.1 |
| $G_j$ | $(\mu_{\mathrm{post},j}-m_{\mathrm{disp},j})/(k_{\mathrm{true},j}-m_{\mathrm{disp},j})$, fraction of an imposed prior displacement recovered | 2.4.2 |
| $\mathrm{ESS}$ | $1/\sum_i w_i^2$, effective sample size of the normalised weights | 2.3.1 |
| $Z_{\Delta,j}$ | standardised displacement: median perturbed minus median reference posterior mean, divided by the median within-realisation reference posterior SD | 2.5 |
| $\Delta k_{\mathrm{raw}}$ | $\hat{k}-k_{\mathrm{arith}}$, raw bias against the arithmetic zone mean | 2.6.3 |
| $\Delta k_{\mathrm{struct}}$ | $\Delta k_{\mathrm{raw}}-\Delta k_{\mathrm{hom}}$, bias net of the paired homogeneous control | 2.6.3 |
| $f_j$ | $(\hat{k}_j-k_{\mathrm{arith},j})/(k_{\mathrm{length},j}-k_{\mathrm{arith},j})$, raw position between the two candidate targets | 2.6.3 |
| $\lambda$ | length-structure modulation amplitude in $k_{w,p}=\bar{k}_{w,z}(1+\lambda s_p)$; not a correlation coefficient | 2.6.2 |
| $D_{i,n}$ | $\int \mathbf{1}[C_{i,n}(t)<C_{\mathrm{crit}}] \mathrm{d}t$, member duration below threshold | 2.8.1 |
| $A_{i,n}$ | $\int \max[0,\ C_{\mathrm{crit}}-C_{i,n}(t)] \mathrm{d}t$, member cumulative deficit | 2.8.1 |
| $M_{i,n}$ | $\min_t C_{i,n}(t)$, member window minimum | 2.8.1 |
| $E[D_n]$, $E[A_n]$ | $\sum_i w_i D_{i,n}$ and $\sum_i w_i A_{i,n}$, weighted expectations | 2.8.1 |
| $\bar{P}_n$ | $E[D_n]/48$, time-averaged below-threshold probability | 2.8.1 |
| $P_{\min,n}$ | $\sum_i w_i \mathbf{1}[M_{i,n}<C_{\mathrm{crit}}]$, probability of at least one breach in the window | 2.8.1 |
| $J_k$ | $|S_k^{\mathrm{pert}}\cap S_k^{\mathrm{ref}}|/|S_k^{\mathrm{pert}}\cup S_k^{\mathrm{ref}}|$, top-$k$ shortlist overlap | 2.8.3 |
"""
src = src.replace('{{DEFTABLE}}', DEFTABLE)
open('paper.gen.md', 'w').write(re.sub(r'\{\{TABLE(\d+)\}\}', sub, src))
SPLICE

pandoc paper.gen.md -o paper.docx \
    --reference-doc=reference.docx \
    --citeproc --bibliography=refs.bib --csl="$CSL" \
    --resource-path=.:figures/paper


# Word's math font shows U+200B as a missing-glyph box. Pandoc emits one after every n-ary
# operator subscript, and turns LaTeX spacing macros into exotic space characters. Both are
# cosmetic, so strip them from the generated equations.
python3 - <<'CLEAN'
import zipfile, shutil, re
src, tmp = 'paper.docx', 'paper.docx.tmp'
zin = zipfile.ZipFile(src)
items = {n: zin.read(n) for n in zin.namelist()}
zin.close()
xml = items['word/document.xml'].decode('utf8')
xml = xml.replace('\u200b', '')
for ch in ('\u2001', '\u2002', '\u2003', '\u2005', '\u2009'):
    xml = xml.replace(ch, ' ')
items['word/document.xml'] = xml.encode('utf8')
z = zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED)
for n, d in items.items():
    z.writestr(n, d)
z.close()
shutil.move(tmp, src)
CLEAN

python3 - <<'PY'
import re
raw = open('paper.md').read()
src = re.sub(r'<!--.*?-->', '', raw, flags=re.S)
src = re.split(r'^#+\s*References\s*$', src, flags=re.M)[0]

def wc(t):
    t = re.sub(r'`[^`]*`', ' ', t)
    t = re.sub(r'\$\$.*?\$\$', ' EQ ', t, flags=re.S)   # display maths -> one word
    t = re.sub(r'\$[^$]*\$', ' EQ ', t)                 # inline maths  -> one word
    t = re.sub(r'\[@[^\]]*\]|@[A-Za-z0-9_]+', ' ', t)   # citations resolve at build time
    return len(re.sub(r'[#*_>|\[\]()-]', ' ', t).split())

body, caps, rows = [], [], 0
for blk in src.split('\n\n'):
    st = blk.strip()
    if not st:
        continue
    if st.startswith('|'):                              # table content: never counted
        rows += st.count('\n') + 1
    elif st.startswith('!['):                           # figure caption: counted
        caps.append(re.match(r'!\[(.*?)\]\(', st, re.S).group(1))
    elif re.match(r'^Table \d+\.', st):                 # table caption: counted
        caps.append(st)
    elif st.startswith('{{'):
        pass
    else:
        body.append(st)

b, c = wc('\n'.join(body)), wc('\n'.join(caps))
print('body %s + captions %s (%d caption(s)) = %s counted'
      % (format(b, ','), format(c, ','), len(caps), format(b + c, ',')))
print('remaining to 12,000: %s   (table rows excluded: %d)'
      % (format(12000 - b - c, ','), rows))

keys = set(re.findall(r'@([A-Za-z][A-Za-z0-9_]*)', raw))
have = set(re.findall(r'@\w+\{([^,]+),', open('refs.bib').read()))
gap = sorted(k for k in keys if k not in have)
if gap:
    print('citation keys not yet in refs.bib:', ', '.join(gap))
PY

echo "wrote paper.docx"
