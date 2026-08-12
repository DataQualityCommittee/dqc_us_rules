# Process: Generating Validation Commands from missing-dqc-test.csv

## Overview

This document describes the process used to:
1. Query the XBRL US API for DQC assertion data and save to `missing-dqc-test.csv`
2. Generate a batch file (`run_missing_dqc.bat`) to validate filings against DQC rules
3. Generate a `.travis.yml`-compatible `- INFILES` block (`run_missing_dqc_infiles.txt`) grouped by taxonomy year
4. Prune `missing-test.txt` by removing codes already covered in `.travis.yml`
5. Validate output files for DQC findings; remove invalid entries from `.travis.yml` and `tests/output/`

---

## Inputs

| File | Location | Description |
|------|----------|-------------|
| `missing-dqc-test.csv` | `testcase-tools/` | XBRL US API assertion query results — one row per filing/assertion match |
| `assertions-public-exposure.ipynb` | `testcase-tools/` | Jupyter notebook used to query the XBRL US API and append results to `missing-dqc-test.csv` |

### missing-dqc-test.csv Column Reference

| Column | Description |
|--------|-------------|
| `report.base-taxonomy` | Taxonomy used (e.g. `US GAAP 2025`) |
| `report.filing-date` | Filing date in `M/D/YYYY` format |
| `report.entry-url` | SEC `.htm` filing URL |
| `assertion.code` | DQC rule code (e.g. `DQC.US.0177.10133`) |
| `report.document-type` | SEC form type (e.g. `10-K`, `10-Q`, `DEF 14A`) |
| `report.accession` | SEC accession number |
| `entity.code` | SEC CIK |
| `entity.ticker` | Company ticker symbol |
| `entity.name` | Company name |
| `assertion.type` | Numeric rule identifier |

---

## Step 1: Query the XBRL US API (assertions-public-exposure.ipynb)

The notebook queries the XBRL US `assertion` endpoint for DQC findings using a list of `XBRL_Elements` (rule codes) and a set of `report_year` values.

**Key notebook parameters (Cell 3):**
- `endpoint = 'assertion'`
- `XBRL_Elements` — list of `DQC.US.nnnn.nnnnn` codes to query (4-part codes only)
- `report_year` — list of taxonomy years to search (e.g. `['us gaap 2026', 'us gaap 2025', 'us gaap 2024']`)

**Output cell (Cell 9):**
```python
df.to_csv(r"D:\DJT\...\testcase-tools\missing-dqc-test.csv", sep=",", mode="a", header=False)
```
Results are **appended** to the existing CSV (not overwritten), so the notebook can be run incrementally for batches of rules.

---

## Step 2: Generate run_missing_dqc.bat (Validation Commands)

For each **unique combination of `assertion.code` + `report.document-type`**, select the row with the **latest `report.filing-date`**. Generate one Arelle command per selected row.

**Primary-level rules:** `DQC.US.0011`, `DQC.US.0013`, and `DQC.US.0014` are processed at the primary rule level — strip the secondary numeric code from `assertion.code` before generating commands (e.g. `DQC.US.0011.6820` → `DQC.US.0011`). After stripping, re-deduplicate by `(effective_code, document-type)` keeping the latest `report.filing-date`.

**Command template:**
```bat
.\arellecmdline.exe --plugins 'validate/DQC|EDGAR/transform|inlineXbrlDocumentSet' -f {report.entry-url} -v --xule-run-only {assertion.code} --xule-time .005 --xule-debug --noCertificateCheck --logFile D:/DJT/.../tests/output/{LOGNAME} --xule-rule-set D:/DJT/.../dqc_us_rules/dqc-US-{YEAR}-V29-ruleset.zip
```

**Log filename rules (`{LOGNAME}`):**

The document-type is included in the log filename **only** when the combination of `assertion.code` + `entity.ticker` + `YEAR` is **not unique** (i.e. the same ticker appears more than once for that code and year with different document-types):

| Condition | Filename pattern |
|-----------|-----------------|
| `assertion.code` + `ticker` + `YEAR` is unique | `{assertion.code}_{entity.ticker}_US-{YEAR}.xml` |
| `assertion.code` + `ticker` + `YEAR` is not unique | `{assertion.code}_{entity.ticker}-{DOCTYPE}_US-{YEAR}.xml` |

Where `{DOCTYPE}` is `report.document-type` with **all non-alphanumeric characters removed** (e.g. `DEF 14A` → `DEF14A`, `10-K` → `10K`, `10-Q/A` → `10QA`, `20-F/A` → `20FA`, `S-1/A` → `S1A`, `POS AM` → `POSAM`).

**Placeholder mappings:**

| Placeholder | Source |
|-------------|--------|
| `{report.entry-url}` | `report.entry-url` column |
| `{assertion.code}` | `assertion.code` column |
| `{entity.ticker}` | `entity.ticker` column |
| `{YEAR}` | Last 4 characters of `report.base-taxonomy` (e.g. `US GAAP 2025` → `2025`) |
| `{DOCTYPE}` | `report.document-type` with all non-alphanumeric characters removed (only when `assertion.code` + `ticker` + `YEAR` is not unique) |

**Notes:**
- Use **single quotes** around the `--plugins` value (not double quotes)
- Commands sorted ascending by `DQC.US.nnnn.nnnnn`, then by `report.document-type`
- Total commands generated: **70** (after stripping 0011/0013/0014 secondary codes and re-deduplicating)
- Of 70 entries, entries with `DQC.US.0011`, `DQC.US.0013`, or `DQC.US.0014` use only the 3-part code in `--xule-run-only` and in the log filename
- After generating the bat file, verify that all `--logFile` names are unique. Duplicates indicate a collision in the filename logic and must be resolved before running. Use the following check:

```python
import re
from collections import Counter

with open('run_missing_dqc.bat', encoding='utf-8') as f:
    lines = f.readlines()

logfiles = [re.search(r'--logFile\s+(\S+\.xml)', l).group(1).split('/')[-1]
            for l in lines if '--logFile' in l]
dupes = {k: v for k, v in Counter(logfiles).items() if v > 1}
print("Duplicates:", dupes if dupes else "None — all unique")
```

**Output:** `testcase-tools/run_missing_dqc.bat`

---

## Step 3: Generate run_missing_dqc_infiles.txt (Travis CI INFILES)

Using the same unique rows selected in Step 2, generate `- INFILES` blocks for `.travis.yml`, grouped by taxonomy year and sorted ascending by `DQC.US.nnnn.nnnnn` within each year.

**INFILES entry template:**
```yaml
    - INFILES='[{"file":"{report.entry-url}","xule_run_only":"{assertion.code}"}]' EXFILES=$EXPECTED/{LOGNAME}
```

Where `{LOGNAME}` follows the same conditional filename rule as Step 2 (document-type included only when multiple doc-types exist for the same code+year, spaces removed).

**Year groupings (current run):**

| Year | Entries |
|------|---------|
| 2024 | 21 |
| 2025 | 44 |
| 2026 | 5 |
| **Total** | **70** |

**Output:** `testcase-tools/run_missing_dqc_infiles.txt` — three `- INFILES` lines, one per year, ready to paste into `.travis.yml`

---

## Step 4: Prune missing-test.txt

After generating the bat and INFILES files, remove any `DQC.US.nnnn.nnnnn` code from `missing-test.txt` that already appears on any `- INFILES` line in `.travis.yml` — whether active or commented out.

### What
Scan every line in `.travis.yml` that contains `INFILES=` (regardless of leading `#` or `##`) and collect all `DQC.US.nnnn.nnnnn` codes found. Remove any line in `missing-test.txt` that consists solely of one of those codes.

### How

```python
import re, os

# Collect all 4-part DQC codes from every INFILES line in .travis.yml
travis_codes = set()
with open('.travis.yml', encoding='utf-8') as f:
    for line in f:
        if 'INFILES=' in line:
            for code in re.findall(r'DQC\.US\.\d+\.\d+', line):
                travis_codes.add(code)

# Remove matching lines from missing-test.txt
with open('missing-test.txt', encoding='utf-8') as f:
    txt_lines = f.readlines()

kept = [
    line for line in txt_lines
    if not (re.fullmatch(r'DQC\.US\.\d+\.\d+', line.strip()) and line.strip() in travis_codes)
]

with open('missing-test.txt', 'w', encoding='utf-8') as f:
    f.writelines(kept)
```

### Result (last run: 2026-04-28)
- Unique DQC codes across all `.travis.yml` INFILES lines: **341**
- Lines removed from `missing-test.txt`: **161**
- Lines remaining in `missing-test.txt`: **281**

---

## Step 5: Validate Output Files and Clean Up Invalids

After running `run_missing_dqc.bat`, check each `--logFile` output in `tests/output/` to confirm it contains at least one DQC finding. Files with no findings are invalid test cases.

### What
For each `--logFile` name listed in `run_missing_dqc.bat`:
1. Check whether `tests/output/{LOGNAME}` contains the string `<entry code="DQC` at least once
2. If not, prepend `invalid-` to the filename
3. For each invalid file: add its `DQC.US.nnnn.nnnnn` code to `missing-test.txt` if not already present — **except** `DQC.US.0011`, `DQC.US.0013`, and `DQC.US.0014` (processed at primary rule level, not tracked by secondary code)
4. Remove the corresponding pair from `.travis.yml` lines 20–22 (the `- INFILES` entries created by this process)
5. Delete the `invalid-*.xml` file from `tests/output/`

**Scope restriction:** Only process files and `.travis.yml` entries created by this process (i.e. logfile names matching those in `run_missing_dqc.bat`). Do not rename, remove, or edit any other files or `.travis.yml` entries.

### How

```python
import re, os, json
from collections import Counter

output_dir  = 'tests/output'
travis_path = '.travis.yml'
txt_path    = 'testcase-tools/missing-test.txt'
bat_path    = 'testcase-tools/run_missing_dqc.bat'
search_str  = '<entry code="DQC'
PRIMARY_ONLY = {'DQC.US.0011', 'DQC.US.0013', 'DQC.US.0014'}

# 1. Get logfile names from bat
with open(bat_path, encoding='utf-8') as f:
    bat_lines = f.readlines()
logfiles = [re.search(r'--logFile\s+\S+/(\S+\.xml)', l).group(1)
            for l in bat_lines if '--logFile' in l]

# 2. Identify invalids and rename
invalid_entries = []
for fname in logfiles:
    fpath = os.path.join(output_dir, fname)
    if not os.path.exists(fpath):
        continue
    with open(fpath, encoding='utf-8', errors='replace') as f:
        content = f.read()
    if search_str not in content:
        new_name = 'invalid-' + fname
        os.rename(fpath, os.path.join(output_dir, new_name))
        m = re.match(r'(DQC\.US\.\d+(?:\.\d+)?)_', fname)
        invalid_entries.append({'invalid': new_name, 'original': fname,
                                 'code': m.group(1) if m else None})

# 3. Add codes to missing-test.txt (skip primary-only rules, skip duplicates)
with open(txt_path, encoding='utf-8') as f:
    txt_lines = f.readlines()
existing = set(l.strip() for l in txt_lines)
new_codes = sorted(
    set(e['code'] for e in invalid_entries
        if e['code'] and e['code'] not in PRIMARY_ONLY and e['code'] not in existing),
    key=lambda x: [int(p) for p in re.findall(r'\d+', x)]
)
# Insert into --- DQC.US --- section in numeric order
# ... (insert logic as per Step 2 sort key)

# 4. Remove invalid pairs from .travis.yml lines 20-22
with open(travis_path, encoding='utf-8') as f:
    travis_lines = f.readlines()
originals = set(e['original'] for e in invalid_entries)
for i in [19, 20, 21]:  # 0-indexed lines 20, 21, 22
    line = travis_lines[i]
    m = re.search(r"INFILES='(\[.*?\])'\s+EXFILES=(.+)$", line.strip())
    if not m:
        continue
    infiles = json.loads(m.group(1))
    exfiles = [ex.strip() for ex in m.group(2).split(',')]
    kept = [(inf, ex) for inf, ex in zip(infiles, exfiles)
            if ex.split('/')[-1] not in originals]
    indent = re.match(r'(\s*)', line).group(1)
    infiles_str = json.dumps([p[0] for p in kept], separators=(',', ':'))
    travis_lines[i] = indent + "- INFILES='" + infiles_str + "' EXFILES=" + ','.join(p[1] for p in kept) + '\n'
with open(travis_path, 'w', encoding='utf-8') as f:
    f.writelines(travis_lines)

# 5. Delete invalid files
for e in invalid_entries:
    fpath = os.path.join(output_dir, e['invalid'])
    if os.path.exists(fpath):
        os.remove(fpath)
```

### Notes
- Only logfile names from `run_missing_dqc.bat` are in scope — this prevents accidental removal of roll test output files or other unrelated entries
- If an invalid file's corresponding `.travis.yml` pair is found on a line **after line 22**, report it but do not remove it (it belongs to a different process)
- `DQC.US.0011`, `DQC.US.0013`, and `DQC.US.0014` are still removed from `.travis.yml` when invalid; they are simply not added to `missing-test.txt`

### Result (last run: 2026-04-28)
- Files checked: **70**
- Valid (contain `<entry code="DQC`): **58**
- Invalid (renamed, removed from travis, deleted): **12**
  - `DQC.US.0011` × 5 — no findings, primary-only rule, not added to `missing-test.txt`
  - `DQC.US.0117.10093` × 3
  - `DQC.US.0127.9591` × 1
  - `DQC.US.0198.10660` × 2
  - `DQC.US.0204.10704` × 1
- New codes added to `missing-test.txt`: **0** (all 4 unique codes already present)
- Entries found after line 22: **0**

---

## Key Files Summary

| File | Location | Purpose |
|------|----------|---------|
| `missing-dqc-test.csv` | `testcase-tools/` | Source assertion data from XBRL US API |
| `assertions-public-exposure.ipynb` | `testcase-tools/` | Notebook to query API and append to CSV |
| `run_missing_dqc.bat` | `testcase-tools/` | Arelle validation commands (one per unique assertion+doctype) |
| `run_missing_dqc_infiles.txt` | `testcase-tools/` | Travis CI `- INFILES` entries grouped by year |
| `missing-test.txt` | `testcase-tools/` | Remaining DQC codes with no test coverage in `.travis.yml` |

---

## Ruleset Paths

| Year | Ruleset path |
|------|-------------|
| 2024 | `dqc_us_rules/dqc-US-2024-V29-ruleset.zip` |
| 2025 | `dqc_us_rules/dqc-US-2025-V29-ruleset.zip` |
| 2026 | `dqc_us_rules/dqc-US-2026-V29-ruleset.zip` |

---

## Notes

- `missing-dqc-test.csv` is cumulative — each notebook run appends new rows. Duplicate `(assertion.code, document-type)` combinations across runs are resolved at bat/INFILES generation time by always selecting the latest `report.filing-date`.
- The `XBRL_Elements` list in the notebook is maintained separately in `missing-test.txt` and is updated as new DQC rules are identified that lack test coverage in `.travis.yml`.
- After each full cycle (query → bat → INFILES → prune), re-run Step 4 to keep `missing-test.txt` current. Codes added to `.travis.yml` from `run_missing_dqc_infiles.txt` should be pruned before the next notebook query run.
- The `inlineXbrlDocumentSet` plugin is included in `--plugins` to support inline XBRL filings.
