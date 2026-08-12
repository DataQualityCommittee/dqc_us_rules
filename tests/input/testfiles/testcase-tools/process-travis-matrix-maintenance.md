# Process: .travis.yml Matrix Maintenance

## Overview

This document describes the two-stage process for keeping the `.travis.yml` matrix section clean and actionable:

1. **Deduplicate** — prune `- INFILES` pairs whose `xule_run_only` value is a 4-part `DQC.US.nnnn.nnnnn` or `DQC.IFRS.nnnn.nnnnn` code that already appeared in an earlier pair. Collect the removed pairs into a holding `- INFILES` line for review.
2. **Triage failing pairs** — read Travis CI build results, identify which specific `$EXPECTED` files failed, and move those pairs to a commented `#- INFILES` line so they are excluded from the next run without being lost.

---

## Inputs

| File | Location | Description |
|------|----------|-------------|
| `.travis.yml` | repo root | CI test matrix — source for all read/write operations |
| Travis CI build URL | `https://app.travis-ci.com/github/davidtauriello/dqc_us_rules/builds/{BUILD_ID}` | Build results identifying failing jobs |

---

## .travis.yml Matrix Structure

Each active `- INFILES` line corresponds to one Travis CI job. Commented lines (`##-`, `#-`) are skipped by Travis CI but preserved for reference. Lines run in the order they appear; job numbers are assigned left-to-right through active lines only.

**Current ordering convention (after last maintenance run):**

| Line | Prefix | Label | Pairs |
|------|--------|-------|-------|
| 20 | `#-` | Failing pairs (triage hold) | 7 |
| 22 | `#-` | Duplicated US rule tests (dedup hold) | 46 |
| 24 | `-` | OK as fail | 3 |
| 26 | `-` | US GAAP 2026 | 5 |
| 28 | `-` | US GAAP 2025 | 39 |
| 30 | `-` | US GAAP roll to 2025 (roll 1) | 98 |
| 32 | `-` | US GAAP roll to 2025 (roll 2) | 92 |
| 34 | `-` | US GAAP 2024 | 114 |
| 36 | `-` | US GAAP 2023 | 9 |
| 38 | `-` | IFRS 2025 | 1 |
| 40 | `-` | IFRS 2024 | 37 |
| 42 | `-` | IFRS 2023 | 27 |

---

## Step 1: Deduplicate 4-Part DQC Codes

### What

Scan all `- INFILES` lines in the matrix (including commented lines) in document order. For each `xule_run_only` value that is a **4-part code** (`DQC.US.nnnn.nnnnn` or `DQC.IFRS.nnnn.nnnnn`):

- **Always keep** any pair whose `$EXPECTED` filename contains an amendment/doctype suffix (characters between the ticker and `_US-YEAR.xml` or `-us-YEAR.xml`) — e.g., `-10KA`, `-10QA`, `-DEFC14A`, `-10K`, `-10Q`. These represent distinct document types and are never considered duplicates.
- For **standard pairs** (no amendment suffix): keep the first occurrence in document order; remove all subsequent occurrences of the same code.
- Amendment pairs do **not** register the code as "seen" — a later standard pair for the same code is still eligible to be the first standard occurrence.
- 3-part codes (`DQC.US.nnnn`, `DQC.IFRS.nnnn`) and `DQC.IFRS.*` codes (when running a DQC.US dedup pass) are left untouched.

### Amendment Suffix Detection

```python
import re

def has_amendment_suffix(exfile):
    """Return True if $EXPECTED filename has a doctype/amendment suffix
    between the ticker and _US/IFRS-YEAR.xml."""
    basename = exfile.strip().split('/')[-1]
    basename = re.sub(r'^roll', '', basename)          # strip roll prefix
    m = re.match(r'DQC\.[A-Z]+\.\d+(?:\.\d+)?_(.+)$', basename)
    if not m:
        return False
    rest = m.group(1)                                   # e.g. 'TCX-DEFC14A_US-2026.xml'
    rest = re.sub(r'[_-](?:US|us|ifrs|IFRS)-\d{4}\.xml$', '', rest)
    return '-' in rest                                  # hyphen = amendment suffix present
```

### How

```python
import re, json

travis = '.travis.yml'

with open(travis, encoding='utf-8') as f:
    lines = f.readlines()

seen_standard = set()    # 4-part codes seen as standard (non-amendment) pairs
removed_pairs   = []     # (pair_json, exfile) collected for holding line
removed_exfiles = []
new_lines = list(lines)

for i, line in enumerate(lines):
    if 'INFILES=' not in line:
        continue
    m = re.search(r"(INFILES='(\[.*\])'\s+EXFILES=(.+?))\n?$", line)
    if not m:
        continue
    prefix      = line[:m.start(1)]
    newline     = '\n' if line.endswith('\n') else ''
    pairs       = json.loads(m.group(2))
    exfiles     = m.group(3).strip().split(',')

    kept_pairs, kept_exfiles = [], []
    for pair, exfile in zip(pairs, exfiles):
        code     = pair.get('xule_run_only', '')
        is_4part = bool(re.match(r'DQC\.(US|IFRS)\.\d+\.\d+$', code))
        amend    = has_amendment_suffix(exfile)

        if not is_4part or amend:
            kept_pairs.append(pair)
            kept_exfiles.append(exfile)
        elif code in seen_standard:
            removed_pairs.append(pair)
            removed_exfiles.append(exfile.strip())
        else:
            seen_standard.add(code)
            kept_pairs.append(pair)
            kept_exfiles.append(exfile)

    infiles_json = json.dumps(kept_pairs, separators=(',', ':'))
    new_lines[i] = f"{prefix}INFILES='{infiles_json}' EXFILES={','.join(kept_exfiles)}{newline}"

with open(travis, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
```

### Result (last run: 2026-04-30)

- Lines scanned: all 10 active + commented INFILES lines
- 4-part DQC.US codes evaluated: **305 unique**
- Amendment pairs preserved (always kept): **9**
- Standard duplicate pairs removed: **46**

---

## Step 2: Collect Removed Pairs into a Holding `- INFILES` Line

After deduplication, insert a new `- INFILES` line at **line 20** (before all other matrix entries) containing the removed pairs. This line can be used to re-examine and re-validate removed pairs without losing the `{file: xule_run_only:}` and `$EXPECTED` information.

The removed pairs and exfiles are already held in `removed_pairs` / `removed_exfiles` from Step 1.

```python
# After running Step 1 script — removed_pairs and removed_exfiles are populated

with open(travis, encoding='utf-8') as f:
    lines = f.readlines()

indent = '    '    # 4-space indent matching all other matrix entries

infiles_json = json.dumps(removed_pairs, separators=(',', ':'))
exfiles_str  = ','.join(removed_exfiles)
new_line = f"{indent}- INFILES='{infiles_json}' EXFILES={exfiles_str}\n"

lines.insert(19, new_line)   # insert at index 19 → becomes line 20

with open(travis, 'w', encoding='utf-8') as f:
    f.writelines(lines)
```

**Note:** If running Steps 1 and 2 in one pass, collect `removed_pairs` / `removed_exfiles` during the Step 1 loop, then perform the insert after writing the pruned file.

---

## Step 3: Identify Failing Pairs from Travis CI Build

### What

After a CI run, identify which jobs failed and which specific `$EXPECTED` files within each job produced a test count / expected count mismatch.

### How — Get Job States via Travis CI API

```python
import json, urllib.request

BUILD_ID = '278037588'    # replace with actual build ID

def api_get(path):
    req = urllib.request.Request(
        f'https://api.travis-ci.com{path}',
        headers={'Travis-API-Version': '3'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())

build   = api_get(f'/build/{BUILD_ID}')
job_ids = [job['id'] for job in build['jobs']]

for idx, job_id in enumerate(job_ids, 1):
    job = api_get(f'/job/{job_id}')
    print(f'Job {idx} (id={job_id}): {job["state"]}')
```

### How — Extract Failing `$EXPECTED` Files from Job Logs

The Travis CI HTML report embeds one table row per test pair. A row where **test count ≠ expected count** is a failure. Rows that name an `Expected file:` are mismatches against a specific `$EXPECTED` file.

```python
import re, json, urllib.request

def fetch_log(job_id):
    req = urllib.request.Request(
        f'https://api.travis-ci.com/job/{job_id}/log',
        headers={'Travis-API-Version': '3'}
    )
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())['content']

# Pattern: <td>CODE<br/><br/>Expected file:<br/>FILENAME</td>...<td>TEST</td><td>EXPECTED</td>
pat = re.compile(
    r"<td[^>]*>[^<]+<br\s*/><br\s*/>Expected file:\s*<br\s*/>([^<]+)</td>"
    r".*?<td[^>]*>(\d+)</td><td[^>]*>(\d+)</td>",
    re.DOTALL
)

failing_job_ids = [639133850, 639133852, 639133853, 639133856]   # jobs 3,5,6,9

for job_id in failing_job_ids:
    log = fetch_log(job_id)
    for m in pat.finditer(log):
        exfile, test_cnt, exp_cnt = m.group(1).strip(), int(m.group(2)), int(m.group(3))
        if test_cnt != exp_cnt:
            print(f'  FAIL: {exfile}  (test={test_cnt}, expected={exp_cnt})')
```

### Result (build 278037588, run 2026-04-30)

| Job | Label | Failing `$EXPECTED` file |
|-----|-------|--------------------------|
| 3 | US GAAP 2025 | `DQC.US.0209.10730_STON-US-2025.xml` |
| 3 | US GAAP 2025 | `DQC.US.0209.10731_STON-US-2025.xml` |
| 3 | US GAAP 2025 | `DQC.US.0209.10732_STON-US-2025.xml` |
| 5 | US GAAP roll 2 | `rollDQC.US.0180.10154_GHI_US-2024.xml` |
| 6 | US GAAP 2024 | `DQC.US.0013_CODI-10Q_US-2024.xml` |
| 6 | US GAAP 2024 | `DQC.US.0013_CODI-K-us-2024.xml` |
| 9 | IFRS 2024 | `DQC.IFRS.0130.9725_DZZ-ifrs-2024.xml` |

---

## Step 4: Move Failing Pairs to a Commented `#- INFILES` Line

### What

For each `$EXPECTED` filename identified in Step 3:
1. Locate the pair in `.travis.yml` by matching the basename of the `EXFILES` entry.
2. Remove it from its current INFILES line.
3. Collect all removed pairs into a new `#- INFILES` line inserted at **line 20**.
4. All other matrix lines shift down by one.

### How

```python
import re, json

travis = '.travis.yml'

failing_basenames = {
    'DQC.US.0209.10730_STON-US-2025.xml',
    'DQC.US.0209.10731_STON-US-2025.xml',
    'DQC.US.0209.10732_STON-US-2025.xml',
    'rollDQC.US.0180.10154_GHI_US-2024.xml',
    'DQC.US.0013_CODI-10Q_US-2024.xml',
    'DQC.US.0013_CODI-K-us-2024.xml',
    'DQC.IFRS.0130.9725_DZZ-ifrs-2024.xml',
}

with open(travis, encoding='utf-8') as f:
    lines = f.readlines()

extracted_pairs, extracted_exfiles = [], []
new_lines = list(lines)

for i, line in enumerate(lines):
    if 'INFILES=' not in line:
        continue
    m = re.search(r"(INFILES='(\[.*\])'\s+EXFILES=(.+?))\n?$", line)
    if not m:
        continue
    prefix  = line[:m.start(1)]
    newline = '\n' if line.endswith('\n') else ''
    pairs   = json.loads(m.group(2))
    exfiles = m.group(3).strip().split(',')

    kept_pairs, kept_exfiles = [], []
    for pair, exfile in zip(pairs, exfiles):
        if exfile.strip().split('/')[-1] in failing_basenames:
            extracted_pairs.append(pair)
            extracted_exfiles.append(exfile.strip())
        else:
            kept_pairs.append(pair)
            kept_exfiles.append(exfile)

    infiles_json = json.dumps(kept_pairs, separators=(',', ':'))
    new_lines[i] = f"{prefix}INFILES='{infiles_json}' EXFILES={','.join(kept_exfiles)}{newline}"

# Build and insert the #- INFILES line at line 20 (index 19)
infiles_json = json.dumps(extracted_pairs, separators=(',', ':'))
exfiles_str  = ','.join(extracted_exfiles)
new_infiles  = f"    #- INFILES='{infiles_json}' EXFILES={exfiles_str}\n"
new_lines.insert(19, new_infiles)

with open(travis, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)
```

### Result (last run: 2026-04-30)

- Failing pairs extracted: **7** (from jobs 3, 5, 6, 9)
- New `#- INFILES` inserted at line 20
- Source lines adjusted: US GAAP 2025 (−3), roll 2 (−1), US GAAP 2024 (−2), IFRS 2024 (−1)

---

## Key Files Summary

| File | Location | Purpose |
|------|----------|---------|
| `.travis.yml` | repo root | CI matrix — read and written by all steps |
| `process-travis-matrix-maintenance.md` | `testcase-tools/` | This document |

---

## Notes

- **Line 20 convention**: Both the dedup holding line (`- INFILES`) and the triage hold line (`#- INFILES`) are inserted at line 20 in sequence. The triage `#-` line is always topmost (excluded from CI). The dedup `- INFILES` is active and included in CI runs.
- **Amendment pairs** are never deduplicated — a ticker that filed multiple form types (10-K and 10-K/A, or 10-Q and 10-Q/A) provides genuinely distinct test coverage.
- **`DQC.US.0011`, `DQC.US.0013`, `DQC.US.0014`** are 3-part codes and are excluded from deduplication. Multiple INFILES entries for these rules with different `$EXPECTED` files are expected and correct.
- **Travis CI API**: The public API at `https://api.travis-ci.com` (with header `Travis-API-Version: 3`) can retrieve build job states and log content without authentication for public repositories. The `/job/{id}/log` endpoint returns full log content in a JSON `content` field.
- **Ordering**: Within the dedup pass, document order determines which occurrence is "first". The order is: US GAAP 2026 → US GAAP 2025 → roll lines → US GAAP 2024 → US GAAP 2023 → IFRS years. A 2026 test always wins over a 2025 duplicate, and 2025 wins over 2024.
- After addressing failing pairs (debugging or replacing `$EXPECTED` files), move the `#- INFILES` pairs back into the appropriate active `- INFILES` line and remove the `#-` holding entry.
