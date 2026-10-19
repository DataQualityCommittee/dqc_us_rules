# Process: Generating Validation Commands from missing-dqc-test.csv

## Overview

This document describes the process used to:
1. Query the XBRL US API for DQC assertion data and save to a `missing-dqc-test*.csv` file
2. Generate a batch file (`run_missing_dqc.bat`) to validate filings against DQC rules
3. Generate a `.travis.yml`-compatible `- INFILES` block (`run_missing_dqc_infiles.txt`), inserted as **temporary** standalone blocks grouped by taxonomy year
4. Prune `missing-test.txt` by removing codes already covered in `.travis.yml`
5. Validate output files for DQC findings; rename/delete invalid outputs and re-add their codes to `missing-test.txt`
6. Merge the surviving valid entries from the temporary blocks into the matching existing `# US GAAP {YEAR}` `- INFILES` block(s), in ascending `DQC.US.major.minor` order, then delete the temporary blocks so no new blocks are left over

---

## Inputs

| File | Location | Description |
|------|----------|-------------|
| `missing-dqc-test*.csv` | `testcase-tools/` | XBRL US API assertion query results — one row per filing/assertion match. May be suffixed per release cycle (e.g. `missing-dqc-test-v31.csv`) rather than the single cumulative `missing-dqc-test.csv`, if starting a fresh batch for a new ruleset version |
| `assertions-public-exposure.ipynb` | `testcase-tools/` | Jupyter notebook used to query the XBRL US API and append results to the CSV (Cell 13 sets the exact output path) |

### missing-dqc-test.csv Column Reference

The CSV has **no header row** (columns are positional). After a leading pandas row-index column, the columns are:

| Column | Description |
|--------|-------------|
| `report.base-taxonomy` | Taxonomy used (e.g. `US GAAP 2025`) |
| `report.filing-date` | Filing date (`YYYY-MM-DD` or `M/D/YYYY`) |
| `report.entry-url` | SEC `.htm` filing URL |
| `assertion.code` | DQC rule code (e.g. `DQC.US.0177.10133`) |
| `report.document-type` | SEC form type (e.g. `10-K`, `10-Q`, `DEF 14A`) |
| `report.accession` | SEC accession number |
| `entity.code` | SEC CIK |
| `entity.ticker` | Company ticker symbol (occasionally contains non-alphanumeric characters, e.g. `AUKF/33`) |
| `entity.name` | Company name |
| `assertion.type` | Numeric rule identifier |

---

## Step 1: Query the XBRL US API (assertions-public-exposure.ipynb)

The notebook queries the XBRL US `assertion` endpoint for DQC findings using a list of `XBRL_Elements` (rule codes) and a set of `report_year` values.

**Key notebook parameters (Cell 3):**
- `endpoint = 'assertion'`
- `XBRL_Elements` — list of `DQC.US.nnnn.nnnnn` codes to query (4-part codes only), typically sourced from `missing-test.txt`
- `report_year` — list of taxonomy years to search (e.g. `['us gaap 2026', 'us gaap 2025']`)

**Output cell (near the end of the notebook):**
```python
filtered_df.to_csv(r"D:\...\testcase-tools\missing-dqc-test-v31.csv", sep=",", mode="a", header=False)
```
Results are **appended** to the CSV (not overwritten), so the notebook can be run incrementally for batches of rules. Confirm the exact output filename/path in the notebook before running Step 2 — it may point at a version-suffixed file rather than the base `missing-dqc-test.csv`.

---

## Step 2: Generate run_missing_dqc.bat (Validation Commands)

For each **unique combination of `assertion.code` + `report.document-type`**, select the row with the **latest `report.filing-date`**. Generate one Arelle command per selected row.

**Primary-level rules:** `DQC.US.0011`, `DQC.US.0013`, and `DQC.US.0014` are processed at the primary rule level — strip the secondary numeric code from `assertion.code` before generating commands (e.g. `DQC.US.0011.6820` → `DQC.US.0011`). After stripping, re-deduplicate by `(effective_code, document-type)` keeping the latest `report.filing-date`.

**Command template:**
```bat
.\arellecmdline.exe --plugins 'validate/DQC|EDGAR/transform|inlineXbrlDocumentSet' -f {report.entry-url} -v --xule-run-only {assertion.code} --xule-time .005 --xule-debug --noCertificateCheck --logFile D:/DJT/.../tests/output/{LOGNAME} --xule-rule-set D:/DJT/.../dqc_us_rules/dqc-us-{YEAR}-V{RULESET_VERSION}-ruleset.zip --httpuseragent {your-email}
```

Notes on the ruleset path: filenames use **lowercase** `us` and the current ruleset version tag (e.g. `V31`), not a fixed `V29` — check `dqc_us_rules/dqc-us-*-ruleset.zip` for what's actually present before generating the batch file. The `--httpuseragent` flag is required for current Arelle/SEC EDGAR behavior; use the querying user's email.

**Log filename rules (`{LOGNAME}`):**

The document-type is included in the log filename **only** when the combination of `assertion.code` + `entity.ticker` + `YEAR` is **not unique** (i.e. the same ticker appears more than once for that code and year with different document-types):

| Condition | Filename pattern |
|-----------|-----------------|
| `assertion.code` + `ticker` + `YEAR` is unique | `{assertion.code}_{entity.ticker}_US-{YEAR}.xml` |
| `assertion.code` + `ticker` + `YEAR` is not unique | `{assertion.code}_{entity.ticker}-{DOCTYPE}_US-{YEAR}.xml` |

Where `{DOCTYPE}` is `report.document-type` with **all non-alphanumeric characters removed** (e.g. `DEF 14A` → `DEF14A`, `10-K` → `10K`, `10-Q/A` → `10QA`, `20-F/A` → `20FA`, `S-1/A` → `S1A`, `POS AM` → `POSAM`).

**`{entity.ticker}` also needs sanitizing** — apply the same non-alphanumeric stripping to the ticker itself before using it in a filename, not just the doctype (e.g. `AUKF/33` → `AUKF33`). A literal `/` in a ticker would otherwise be read as a path separator.

**Placeholder mappings:**

| Placeholder | Source |
|-------------|--------|
| `{report.entry-url}` | `report.entry-url` column |
| `{assertion.code}` | `assertion.code` column (or the 3-part `effective_code` for 0011/0013/0014) |
| `{entity.ticker}` | `entity.ticker` column, non-alphanumeric characters stripped |
| `{YEAR}` | Last 4 characters of `report.base-taxonomy` (e.g. `US GAAP 2025` → `2025`) |
| `{DOCTYPE}` | `report.document-type` with all non-alphanumeric characters removed (only when `assertion.code` + `ticker` + `YEAR` is not unique) |

**Notes:**
- Use **single quotes** around the `--plugins` value (not double quotes)
- Commands sorted ascending by `DQC.US.nnnn.nnnnn`, then by `report.document-type`
- Entries with `DQC.US.0011`, `DQC.US.0013`, or `DQC.US.0014` use only the 3-part code in `--xule-run-only` and in the log filename
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

## Step 3: Generate run_missing_dqc_infiles.txt (Travis CI INFILES) — temporary blocks

Using the same unique rows selected in Step 2, generate `- INFILES` blocks for `.travis.yml`, grouped by taxonomy year and sorted ascending by `DQC.US.nnnn.nnnnn` within each year.

**INFILES entry template:**
```yaml
    # US GAAP {YEAR}
    - INFILES='[{"file":"{report.entry-url}","xule_run_only":"{assertion.code}"}]' EXFILES=$EXPECTED/{LOGNAME}
```

Where `{LOGNAME}` follows the same conditional filename rule as Step 2 (document-type included only when multiple doc-types exist for the same code+ticker+year).

**Output:** `testcase-tools/run_missing_dqc_infiles.txt` — one `# US GAAP {YEAR}` comment + `- INFILES` line pair per year present in the batch.

Paste these blocks into `.travis.yml` as **temporary, standalone** entries (e.g. immediately after any version-tag block like `# V31`). They exist only so Steps 4–5 can validate against real filings; Step 6 merges the surviving entries into the permanent per-year blocks and deletes these temporary ones. Do not treat them as the final destination.

---

## Step 4: Prune missing-test.txt

After inserting the temporary INFILES blocks from Step 3 into `.travis.yml`, remove any `DQC.US.nnnn.nnnnn` / `DQC.IFRS.nnnn.nnnnn` code from `missing-test.txt` that already appears on any `- INFILES` line in `.travis.yml` — whether active or commented out.

### What
Scan every line in `.travis.yml` that contains `INFILES=` (regardless of leading `#` or `##`) and collect all `DQC.(US|IFRS).nnnn.nnnnn` codes found. Remove any line in `missing-test.txt` that consists solely of one of those codes.

### How

```python
import re

travis_codes = set()
with open('.travis.yml', encoding='utf-8') as f:
    for line in f:
        if 'INFILES=' in line:
            for code in re.findall(r'DQC\.(?:US|IFRS)\.\d+\.\d+', line):
                travis_codes.add(code)

with open('tests/input/testfiles/testcase-tools/missing-test.txt', encoding='utf-8') as f:
    txt_lines = f.readlines()

kept = [
    line for line in txt_lines
    if not (re.fullmatch(r'DQC\.(?:US|IFRS)\.\d+\.\d+', line.strip()) and line.strip() in travis_codes)
]

with open('tests/input/testfiles/testcase-tools/missing-test.txt', 'w', encoding='utf-8') as f:
    f.writelines(kept)
```

Run this once right after Step 3's temporary blocks are pasted in (so the batch's own codes get pruned), and again after Step 6 has nothing new to add (it should be a no-op the second time, since the codes were already covered by the temporary blocks).

### Result (last run: 2026-08-18)
- Unique DQC codes across all `.travis.yml` INFILES lines (after inserting Step 3's temporary blocks): **372**
- Lines removed from `missing-test.txt`: **18**
- Lines remaining in `missing-test.txt`: **275**

---

## Step 5: Validate Output Files, Mark Invalids

After running `run_missing_dqc.bat` (requires `arellecmdline.exe` and live network access to SEC EDGAR — this step is typically run by the user outside of an assistant session), check each `--logFile` output in `tests/output/` to confirm it contains at least one DQC finding. Files with no findings are invalid test cases.

### What
For each `--logFile` name listed in `run_missing_dqc.bat`:
1. Check whether `tests/output/{LOGNAME}` contains the string `<entry code="DQC` at least once
2. If not, prepend `invalid-` to the filename
3. For each invalid file: add its `DQC.US.nnnn.nnnnn` code to `missing-test.txt` if not already present — **except** `DQC.US.0011`, `DQC.US.0013`, and `DQC.US.0014` (processed at primary rule level, not tracked by secondary code). A code with *some* valid rows and *some* invalid rows for different tickers still gets re-added — the invalid row is dropped in Step 6 regardless of its siblings.
4. Delete the `invalid-*.xml` file from `tests/output/`

Invalid rows are **not** separately stripped out of the temporary `.travis.yml` blocks in this step — Step 6 handles that by construction, since it only merges the surviving valid rows and then deletes the temporary blocks outright.

**Scope restriction:** Only process files matching logfile names in `run_missing_dqc.bat`. Do not rename, remove, or edit any other files or `.travis.yml` entries.

### How

```python
import re, os

output_dir  = 'tests/output'
txt_path    = 'tests/input/testfiles/testcase-tools/missing-test.txt'
bat_path    = 'tests/input/testfiles/testcase-tools/run_missing_dqc.bat'
search_str  = '<entry code="DQC'
PRIMARY_ONLY = {'DQC.US.0011', 'DQC.US.0013', 'DQC.US.0014'}

with open(bat_path, encoding='utf-8') as f:
    bat_lines = [l for l in f if l.strip()]
logfiles = [re.search(r'--logFile\s+\S+/(\S+\.xml)', l).group(1) for l in bat_lines]

invalid_entries = []
for fname in logfiles:
    fpath = os.path.join(output_dir, fname)
    with open(fpath, encoding='utf-8', errors='replace') as f:
        content = f.read()
    if search_str not in content:
        new_name = 'invalid-' + fname
        os.rename(fpath, os.path.join(output_dir, new_name))
        m = re.match(r'(DQC\.US\.\d+(?:\.\d+)?)_', fname)
        invalid_entries.append({'invalid': new_name, 'original': fname,
                                 'code': m.group(1) if m else None})

with open(txt_path, encoding='utf-8') as f:
    txt_lines = f.readlines()
existing = set(l.strip() for l in txt_lines)
new_codes = sorted(
    set(e['code'] for e in invalid_entries
        if e['code'] and e['code'] not in PRIMARY_ONLY and e['code'] not in existing),
    key=lambda x: [int(p) for p in re.findall(r'\d+', x)]
)
# Insert new_codes into the --- DQC.US --- section of missing-test.txt, in numeric order

for e in invalid_entries:
    os.remove(os.path.join(output_dir, e['invalid']))
```

### Result (last run: 2026-08-18)
- Files checked: **29**
- Valid (contain `<entry code="DQC`): **25**
- Invalid (renamed, deleted): **4**
  - `DQC.US.0117.10093` × 2 (NATL, BULLW — third row for this code, APAM, was valid)
  - `DQC.US.0234.10928` × 1 (AQUNF — sibling row for AMCR/AUKF33 was valid)
  - `DQC.US.0241.10942` × 1 (VRIAC — only row for this code)
- Codes re-added to `missing-test.txt`: **3** (`DQC.US.0117.10093`, `DQC.US.0234.10928`, `DQC.US.0241.10942`)

---

## Step 6: Merge Valid Entries into Existing INFILES Blocks

Take the rows that survived Step 5 (i.e. everything in the temporary blocks minus the invalid rows) and merge each `{file, xule_run_only}` / `$EXPECTED/{LOGNAME}` triple into the **existing** `- INFILES` block(s) sharing that row's `# US GAAP {YEAR}` heading, then delete the temporary blocks entirely. The goal is that `.travis.yml` ends up with no leftover standalone blocks from this run — every surviving row lives inside a pre-existing block.

### What
1. For each taxonomy year present in the temporary blocks, find the existing `- INFILES` block(s) under the matching `# US GAAP {YEAR}` heading.
2. **If there is exactly one existing block for that heading**, insert each new triple at the position that keeps the block's `xule_run_only` codes in ascending `DQC.US.major.minor` order (ties: insert after the last existing row with the same code).
3. **If there are multiple existing blocks sharing the same heading**, they are not independent — check first whether they form one contiguous ascending sequence (the last code of block *N* is ≤ the first code of block *N+1*). If so, treat them as one long sorted sequence split across blocks, and route each new row to whichever block's numeric range it falls into: the first block where the new code is ≤ that block's own max code, or falls in the gap before the next block's first code; the last block is the catch-all for anything higher than every existing code. If the blocks are *not* a contiguous sequence (e.g. genuinely unrelated batches), stop and ask which block should receive the new rows rather than guessing.
4. Rebuild each modified `- INFILES` line's JSON array and its matching `EXFILES=` comma list together, in the same order, so `file`/`xule_run_only`/`EXFILES` triples stay aligned.
5. Delete the temporary block(s) (comment + `- INFILES` line) inserted in Step 3.
6. Validate: re-parse `.travis.yml` as YAML, and confirm for each modified block that the `INFILES` array length equals the `EXFILES` entry count and that codes are sorted ascending.

### How

```python
import re, json

def parse_infiles_line(line):
    m = re.search(r"INFILES='(\[.*?\])'\s+EXFILES=(.+)$", line.strip())
    infiles = json.loads(m.group(1))
    exfiles = m.group(2).split(',')
    indent = re.match(r'(\s*)', line).group(1)
    return infiles, exfiles, indent

def rebuild_infiles_line(indent, infiles, exfiles):
    infiles_str = json.dumps(infiles, separators=(',', ':'))
    return f"{indent}- INFILES='{infiles_str}' EXFILES=" + ",".join(exfiles) + "\n"

def sort_key(code):
    return [int(p) for p in re.findall(r'\d+', code)]

def insert_sorted(infiles, exfiles, codes, triple, exfile, key):
    pos = len(codes)
    for i, c in enumerate(codes):
        if sort_key(c) > key:
            pos = i
            break
    infiles.insert(pos, triple)
    exfiles.insert(pos, exfile)
    codes.insert(pos, triple['xule_run_only'])

# For a single-block heading (e.g. one "# US GAAP 2026" block):
#   insert_sorted(infiles, exfiles, codes, triple, exfile, sort_key(row['effective_code']))
#
# For a multi-block heading (e.g. three "# US GAAP 2025" blocks forming one
# contiguous sequence): walk the blocks in file order, and for each new row pick
# the first block where key <= block's own last code, or key < the next block's
# first code; fall back to the last block for anything higher than everything.
```

### Result (last run: 2026-08-18)
- `# US GAAP 2026`: 1 existing block, 49 → 67 entries (18 valid rows merged)
- `# US GAAP 2025`: 3 existing blocks forming one contiguous sequence, 62/64/77 → 63/67/80 entries (7 valid rows merged, distributed by numeric range)
- Temporary blocks removed: 2 (the `# US GAAP 2025` / `# US GAAP 2026` pairs inserted in Step 3)
- `.travis.yml` matrix entries after cleanup: 15 (down from 17 with the temporary blocks in place), still valid YAML

---

## Key Files Summary

| File | Location | Purpose |
|------|----------|---------|
| `missing-dqc-test*.csv` | `testcase-tools/` | Source assertion data from XBRL US API (may be version-suffixed per cycle) |
| `assertions-public-exposure.ipynb` | `testcase-tools/` | Notebook to query API and append to CSV |
| `run_missing_dqc.bat` | `testcase-tools/` | Arelle validation commands (one per unique assertion+doctype) |
| `run_missing_dqc_infiles.txt` | `testcase-tools/` | Temporary `- INFILES` entries grouped by year, later merged into existing blocks (Step 6) |
| `missing-test.txt` | `testcase-tools/` | Remaining DQC codes with no test coverage in `.travis.yml` |

---

## Ruleset Paths

Ruleset filenames use **lowercase** `us`/`ifrs`/`esef` and the current ruleset version tag. Verify against `dqc_us_rules/dqc-*-ruleset.zip` before generating commands — do not assume a fixed version. As of the 2026-08-18 run:

| Year | Ruleset path |
|------|-------------|
| 2023 | `dqc_us_rules/dqc-us-2023-V31-ruleset.zip` |
| 2024 | `dqc_us_rules/dqc-us-2024-V31-ruleset.zip` |
| 2025 | `dqc_us_rules/dqc-us-2025-V31-ruleset.zip` |
| 2026 | `dqc_us_rules/dqc-us-2026-V31-ruleset.zip` |

---

## Notes

- The source CSV is cumulative within a version/cycle — each notebook run appends new rows. Duplicate `(assertion.code, document-type)` combinations across runs are resolved at bat/INFILES generation time by always selecting the latest `report.filing-date`.
- The `XBRL_Elements` list in the notebook is maintained separately in `missing-test.txt` and is updated as new DQC rules are identified that lack test coverage in `.travis.yml`.
- Full cycle order: query (Step 1) → bat (Step 2) → temporary INFILES blocks (Step 3) → paste into `.travis.yml` → prune `missing-test.txt` (Step 4) → run the bat externally → validate outputs and re-add invalid codes (Step 5) → merge surviving rows into the existing per-year blocks and delete the temporary ones (Step 6) → prune `missing-test.txt` again (should be a no-op).
- The `inlineXbrlDocumentSet` plugin is included in `--plugins` to support inline XBRL filings.
- Tickers can contain non-alphanumeric characters (e.g. `AUKF/33`); sanitize them the same way as document-types before using them in filenames.
