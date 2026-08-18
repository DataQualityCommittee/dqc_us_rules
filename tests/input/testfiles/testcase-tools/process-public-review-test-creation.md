# Process: Public Review Test Creation (v31.csv → .travis.yml)

## Overview

This document describes the process used to turn a public-exposure findings export (`v31.csv`) for a new DQC rule into runnable `.travis.yml` test coverage, using a dedicated per-version staging line (`# V{version}`) as the landing zone before the pairs are later redistributed by taxonomy/year during routine matrix maintenance (see [process-travis-matrix-maintenance.md](process-travis-matrix-maintenance.md)).

Steps:
1. Empty and relabel the prior version's staging line (e.g. `# V30` → `# V31`), after its pairs have been redistributed into the correct taxonomy/year lines.
2. Parse `v31.csv` and resolve each filer's ticker via SEC EDGAR CIK lookup (the export has no ticker column).
3. Build `- INFILES` pairs and `$EXPECTED` filenames, and write them into the (now empty) `# V31` line.
4. Generate one Arelle command per report to produce each `$EXPECTED` `log.xml`-equivalent output file.

---

## Background: Emptying the Prior Staging Line

Before `v31.csv` existed, `.travis.yml`'s `# V30` line held 6 pairs — one-off entries staged there ahead of a rule's inclusion in the normal per-taxonomy-year lines. As part of this process those 6 pairs were redistributed:

- Pairs whose `$EXPECTED` filename ended `-US-2026.xml` were appended (in ascending `DQC.US.nnnn.nnnnn` order) to the end of the `# US GAAP 2026` line.
- Pairs ending `-US-2025.xml` were appended to the end of the **last** `# US GAAP 2025` chunk (the matrix splits `US GAAP 2025` across three `- INFILES` lines by ascending rule-code range; new codes higher than any existing code in all three chunks belong at the tail of the last one).
- The now-empty `# V30` line was relabeled `# V31` and its `- INFILES` reset to `INFILES='[]' EXFILES=`, ready to receive the next batch of new-rule test pairs.

This relabeled, emptied line is what `v31.csv` populates in the steps below.

---

## Inputs

| File | Location | Description |
|------|----------|-------------|
| `v31.csv` | `testcase-tools/` | Public-review/exposure findings export — one row per filing that triggered the new rule |
| `.travis.yml` | repo root | CI test matrix — the `# V31` line is the write target |

### v31.csv Column Reference (columns used)

| Column | Description |
|--------|-------------|
| `entry_url` | SEC `.htm` filing URL — becomes the INFILES `"file"` value |
| `error_code` | DQC rule code, e.g. `DQC.US.0245.10947` — becomes `"xule_run_only"` |
| `base_taxonomy` | Taxonomy used, e.g. `US GAAP 2024` — last 4 characters give the year for the `$EXPECTED` filename |
| `entity_code` | SEC CIK — used to resolve a ticker (see Step 1) |
| `entity_name` | Company name — informational only, not used in file naming |
| `document_type` | SEC form type, e.g. `10-K`, `10-Q`, `S-1` — informational; only affects naming if a code+ticker+year collision occurs (none did in this run) |

Unlike `missing-dqc-test.csv` (see [process-missing-dqc-test.md](process-missing-dqc-test.md)), `v31.csv` has **no ticker column** — Step 1 exists specifically to fill that gap.

---

## Step 1: Resolve Tickers via SEC EDGAR

### What

For each unique `entity_code` (CIK) in `v31.csv`, look up the company's ticker.

### How

Use the SEC EDGAR company-search tool (or equivalent `https://data.sec.gov/submissions/CIK##########.json` lookup) with the zero-padded CIK as the query, `include_filings=false`. The response's `tickers` list gives the resolution.

**Fallback rule:** If a CIK has no public ticker (e.g. a pre-IPO `S-1` filer), or if the CIK **already has an established `CIK{10-digit}` naming convention elsewhere in `.travis.yml`** for a different rule, use `CIK{10-digit CIK}` instead of a ticker — to keep all `$EXPECTED` filenames for the same underlying entity/filing consistent across rules. Do not switch an entity to a newly-discovered ticker if an existing `.travis.yml` entry for the same CIK already uses the `CIK########` form; grep `.travis.yml` for the CIK first.

### Result (this run)

| CIK | Entity | Resolved identifier | Note |
|-----|--------|----------------------|------|
| 1789832 | Hess Midstream LP | `HESM` | — |
| 1176948 | Ares Management Corp | `ARES` | — |
| 99780 | Trinity Industries Inc | `TRN` | — |
| 1793497 | VS Trust | `UVIX` | Matches ticker already used for this CIK elsewhere in `.travis.yml` (`DQC.US.0212.10737_UVIX-US-2025.xml` etc.) |
| 1938571 | Adaptin Bio, Inc. | `CIK0001938571` | EDGAR resolves ticker `APTN`, but an existing entry (`DQC.US.0238.10937_CIK0001938571-US-2025.xml`) for this same filing already used the CIK form — kept for consistency rather than switching to `APTN` |
| 1847345 | Aspire Biopharma Holdings, Inc. | `ASBP` | — |

---

## Step 2: Build INFILES Pairs and EXFILES Names

### What

For each `v31.csv` row, construct:
- an INFILES pair: `{"file": entry_url, "xule_run_only": error_code}`
- an EXFILES entry: `$EXPECTED/{error_code}_{ticker-or-CIK}-US-{year}.xml`, where `{year}` is the last 4 characters of `base_taxonomy`

### How

```python
import csv, json, re

ticker_map = {
    '1789832': 'HESM',
    '1176948': 'ARES',
    '99780':   'TRN',
    '1793497': 'UVIX',
    '1938571': 'CIK0001938571',   # kept consistent with existing DQC.US.0238.10937 entry
    '1847345': 'ASBP',
}

with open('v31.csv', encoding='utf-8') as f:
    rows = list(csv.DictReader(f))

pairs, exfiles = [], []
for r in rows:
    ident = ticker_map[r['entity_code']]
    year  = r['base_taxonomy'].strip()[-4:]
    code  = r['error_code'].strip()
    pairs.append({'file': r['entry_url'].strip(), 'xule_run_only': code})
    exfiles.append(f'$EXPECTED/{code}_{ident}-US-{year}.xml')
```

Rows are kept in `v31.csv` order (no re-sort needed — all rows shared the same rule code in this run).

---

## Step 3: Write Pairs into the `# V31` Line

### What

Locate the `# V31` comment line, find its associated `- INFILES` line immediately below, and replace its (empty) `INFILES='[]' EXFILES=` with the pairs/exfiles built in Step 2.

### How

```python
import re, json

with open('.travis.yml', encoding='utf-8') as f:
    lines = f.readlines()

v31_idx = next(i for i, l in enumerate(lines) if l.strip() == '# V31') + 1

m = re.search(r"(INFILES=')(\[.*\])('\s+EXFILES=)", lines[v31_idx])
prefix = lines[v31_idx][:m.start(1)]
infiles_json = json.dumps(pairs, separators=(',', ':'))
lines[v31_idx] = f"{prefix}INFILES='{infiles_json}' EXFILES={','.join(exfiles)}\n"

with open('.travis.yml', 'w', encoding='utf-8') as f:
    f.writelines(lines)
```

After writing, validate with `yaml.safe_load()` to confirm the file still parses.

### Result (last run: 2026-08-17)

- `# V31` line: **6** pairs written (all `DQC.US.0245.10947`)
- 3 pairs taxonomy year 2024 (`HESM`, `ARES`, `ASBP`), 3 pairs year 2025 (`TRN`, `UVIX`, `CIK0001938571`)

---

## Step 4: Generate Arelle Validation Commands

### What

For each pair written in Step 3, generate one single-filing Arelle command that reproduces the `$EXPECTED` output referenced in its EXFILES entry — for local review/regeneration of the golden test files before they're trusted as the `compare.py` baseline.

### Command Template

Follows the same single-filing pattern used in `commands.sh` and [process-missing-dqc-test.md](process-missing-dqc-test.md):

```bat
.\arellecmdline.exe --plugins 'validate/DQC|EDGAR/transform|inlineXbrlDocumentSet' -f {entry_url} -v --xule-run-only {error_code} --xule-time .005 --xule-debug --noCertificateCheck --logFile {repo}/tests/output/{LOGNAME} --xule-rule-set {repo}/dqc_us_rules/dqc-us-{YEAR}-V31-ruleset.zip --httpuseragent {contact_email}
```

Where `{LOGNAME}` is the basename of the EXFILES entry from Step 2, and `{YEAR}` selects the ruleset matching each row's `base_taxonomy` year (`dqc-us-2024-V31-ruleset.zip` or `dqc-us-2025-V31-ruleset.zip`).

**Output:** `testcase-tools/run_v31_dqc.bat` — 6 commands, one per pair.

### Verify LOGNAME Uniqueness

```python
import re
from collections import Counter

with open('run_v31_dqc.bat', encoding='utf-8') as f:
    lines = f.readlines()
logfiles = [re.search(r'--logFile\s+(\S+\.xml)', l).group(1).split('/')[-1]
            for l in lines if '--logFile' in l]
dupes = {k: v for k, v in Counter(logfiles).items() if v > 1}
print('Duplicates:', dupes if dupes else 'None')
```

### Result

- Commands generated: **6**
- `--logFile` collisions: **none**

---

## Key Files Summary

| File | Location | Purpose |
|------|----------|---------|
| `v31.csv` | `testcase-tools/` | Source public-review findings export (one row per filing/rule match, no ticker column) |
| `run_v31_dqc.bat` | `testcase-tools/` | Arelle validation commands, one per new pair, to (re)generate `$EXPECTED` output |
| `.travis.yml` | repo root | `# V31` line — CI matrix entry populated by this process |

---

## Notes

- The `# V31` staging line is **active** (not commented), so until `$EXPECTED` files exist at the paths referenced in its EXFILES list, the corresponding Travis job will fail on missing-file comparison. Run `run_v31_dqc.bat` and commit the resulting output to `tests/output/` before relying on CI green for this line.
- Naming consistency takes priority over ticker availability: if a CIK already appears elsewhere in `.travis.yml` under a `CIK{10-digit}` identifier (because no ticker was known when that entry was created), continue using that form for new entries for the same CIK rather than switching to a newly-resolved ticker — grep `.travis.yml` for the CIK before deciding.
- This staging-line pattern (`V{n}` → populate from a CSV → later redistribute by taxonomy/year) is intended to repeat each time a new rule accumulates public-review findings ahead of formal per-year test placement; see [process-travis-matrix-maintenance.md](process-travis-matrix-maintenance.md) for the redistribution half of the cycle.
