# Process: Rolling 2024 Test Cases to 2025 and Updating .travis.yml

## Overview

This document describes the end-to-end process used to:
1. Identify 2024 test case entries in `.travis.yml`
2. Query the XBRL US API to get company namespace (fact) data
3. Generate a batch file (`run_2024_roll2025.bat`) to create rolled instance `.xml` files using Arelle + xodel
4. Generate a batch file (`run_validate_roll.bat`) to validate rolled instances against DQC rules
5. Update `.travis.yml` with the new roll test entries

---

## Inputs

| File | Location | Description |
|------|----------|-------------|
| `.travis.yml` | repo root | Source of active INFILES/EXFILES test entries |
| `original.csv` | `testcase-tools/` | Table of `$EXPECTED`, `file:`, and `updated` (converted URL) columns — derived from `.travis.yml` 2024 entries |
| `results.csv` | `testcase-tools/` | XBRL US API report lookup results — columns: `report.entry-url`, `entity.ticker`, `report.entity-name`, `fact` (dts.target-namespace), etc. |
| `final.csv` | `testcase-tools/` | Merged table of `original.csv` + `results.csv` on `file:` = `report.entry-url` |

---

## Step 1: Extract 2024 Entries from .travis.yml

Parse `.travis.yml` matrix section for all active (non-`##`) INFILES entries where `$EXPECTED` ends in `2024.xml`. For each `{file: "...", xule_run_only: "..."}` block, capture:

- `file:` — the SEC `.htm` URL
- `xule_run_only` — the rule identifier (e.g. `DQC.US.0208.10727`)
- `$EXPECTED` — the expected output XML filename

Filter to `DQC.US.*` entries only (exclude `DQC.IFRS.*` and local TestCo files).

**Result:** `original.csv` with columns `$EXPECTED`, `file:`, `updated`

The `updated` column converts the `.htm` URL to `_htm.xml` format:
- `http://.../whf-20241231x10k.htm` → `http://.../whf-20241231x10k_htm.xml`

---

## Step 2: Query XBRL US API for Company Data

For each SEC URL in `original.csv`, query the XBRL US API report lookup endpoint to retrieve:
- `report.entry-url` — matches `file:` column (join key)
- `entity.ticker`
- `report.entity-name`
- `fact` — the `dts.target-namespace` value (company namespace URI, e.g. `http://henryschein.com/20241231`)

**Result:** `results.csv`

Clean the `fact` column by stripping the API dict wrapper, leaving only the namespace URL value(s). Preserve duplicate namespace values as comma-separated strings (do not deduplicate).

---

## Step 3: Merge to final.csv

Merge `original.csv` (left) with `results.csv` (right) on `file:` = `report.entry-url`.

Rules:
- All rows preserved — do NOT deduplicate rows where URL appears multiple times
- Add `match_status` column: `MATCHED`, `UNMATCHED-results`, or `UNMATCHED-original`
- Local TestCo file entry will be `UNMATCHED-original` (no SEC URL)

**Result:** `final.csv` with all columns from both sources plus `match_status`

---

## Step 4: Generate run_2024_roll2025.bat (Instance Creation)

For each MATCHED row in `final.csv`, generate one Arelle command using the `file:` column (original `.htm` SEC URL) to fetch the filing and produce a rolled instance `.xml`.

**Command template:**
```bat
./arelleCmdLine.exe --plugins "xodel" -f "{file:}" --xule-time .005 --xule-debug --noCertificateCheck --logFile "D:/DJT/.../tests/input/testfiles/2024-roll-2025/roll{$EXPECTED}" --xule-rule-set "D:/DJT/.../tests/input/2024-roll-2025-V29-test-ruleset.zip" --xodel-location "D:/DJT/.../tests/input/testfiles/2024-roll-2025/" --xodel-show-xule-log --xince-file-type=xml --xule-arg TAXONOMY_DATE="{ROLL_YEAR}{MMDD}" --xule-arg PUBLISH_TAXONOMY={entity.ticker}_taxonomy_2024_2025 --xule-arg TICKER={entity.ticker} --xule-arg OLD_CO_NAMESPACE={fact} --xule-arg INSTANCE_NAME={entity.ticker}_instance_2024_2025 --xule-arg NEW_CO_NAMESPACE={FACTDOMAIN}{ROLL_YEAR}{MMDD}
```

**Column mappings:**
| Placeholder | Source column |
|-------------|--------------|
| `{file:}` | `file:` (original `.htm` SEC URL) |
| `{$EXPECTED}` | `$EXPECTED` (e.g. `DQC.US.0208.10727_WHF-US-2024.xml`) |
| `{entity.ticker}` | `entity.ticker` |
| `{fact}` | `fact` (full namespace URI, first value if multiple) |
| `{FACTDOMAIN}` | `fact` truncated to 3rd `/` inclusive (e.g. `http://henryschein.com/`) |
| `{ROLL_YEAR}` | The ending year of the roll forward — e.g. `2025` for a `2024_roll2025` process |
| `{MMDD}` | The 4-digit month+day extracted from `fact` (last 4 digits of the date segment in the namespace URI, e.g. `1231` from `http://henryschein.com/20241231`) |

**Notes:**
- Use double quotes around `"xodel"` for the plugins value
- Use forward slashes throughout paths — backslashes with `\t`, `\2` etc. are misinterpreted by Python string literals
- `TAXONOMY_DATE` value uses double quotes; all other `--xule-arg` values are unquoted
- `TAXONOMY_DATE` and `NEW_CO_NAMESPACE` date suffix = `{ROLL_YEAR}` + `{MMDD}` derived from `fact`: replace the year in the namespace date with the roll's ending year, preserving the original mmdd (e.g. `http://henryschein.com/20241231` → `MMDD=1231`, `ROLL_YEAR=2025` → `20251231`)
- **Edge case — namespace date already in roll year:** If the year extracted from `fact` equals `{ROLL_YEAR}` (e.g. the filing has a 2025 period-end date but is a 2024 report), `OLD_CO_NAMESPACE` and `NEW_CO_NAMESPACE` would be identical. In this case, increment `{ROLL_YEAR}` by one additional year for `TAXONOMY_DATE` and `NEW_CO_NAMESPACE` only (e.g. use `2026` instead of `2025`), so the rolled instance has a distinct namespace.
- **Edge case — missing ticker:** If `entity.ticker` is empty in `final.csv` for a row, `PUBLISH_TAXONOMY`, `TICKER`, and `INSTANCE_NAME` will be blank in the generated command (appearing as `PUBLISH_TAXONOMY=_taxonomy_...`, `TICKER=`, `INSTANCE_NAME=_instance_...`). After generating the bat file, scan for any command where `PUBLISH_TAXONOMY=_` or `INSTANCE_NAME=_` appears and fill in the missing ticker by extracting it from the `$EXPECTED` filename in the `--logFile` argument (the token between the last `_` of the rule number and the first `-` or `_` separator before `us-20XX`).

**Output files per run:**
- `{TICKER}_instance_2024_2025.xml` — the rolled XBRL instance
- `{TICKER}_taxonomy_2024_2025.zip` — the rolled taxonomy package
- `roll{$EXPECTED}` — the Arelle log file (written to `2024-roll-2025/` folder initially, later moved to `tests/output/` after validation)

---

## Step 5: Run run_2024_roll2025.bat

Execute from the directory containing `arelleCmdLine.exe`. Each command fetches the SEC filing via `_htm.xml` URL and produces the instance and taxonomy files in `tests/input/testfiles/2024-roll-2025/`.

---

## Step 6: Generate run_validate_roll.bat (DQC Rule Validation)

For each `roll*.xml` file in `tests/input/testfiles/2024-roll-2025/`, find the corresponding `{TICKER}_instance_2024_2025.xml` and generate a validation command.

**Ticker mapping:** Derive from `final.csv` `entity.ticker` column matched via `$EXPECTED`. Known overrides where roll filename ticker differs from entity.ticker:

| Roll filename token | Actual ticker / instance |
|--------------------|--------------------------|
| TENNX | TENX |
| IMII | BSAI |
| DEFE | DTII |
| UNIO | UCC |

**Command template:**
```bat
.\arellecmdline.exe --plugins "validate/DQC|EDGAR/transform" -f D:/DJT/.../tests/{INSTANCE} -v --xule-run-only {RULE} --xule-time .005 --xule-debug --noCertificateCheck --logFile D:/DJT/.../tests/output/{ROLL} --xule-rule-set D:/DJT/.../dqc_us_rules/dqc-US-2025-V29-ruleset.zip
```

**Placeholder mappings:**
| Placeholder | Value |
|-------------|-------|
| `{INSTANCE}` | `./tests/input/testfiles/2024-roll-2025/{TICKER}_instance_2024_2025.xml` |
| `{RULE}` | Extracted from the `--logFile` filename: the substring between `roll` and the first `_` (e.g. `rollDQC.US.0208.10727_WHF-US-2024.xml` → `DQC.US.0208.10727`). Only one space before and after this value in the command. |
| `{ROLL}` | Full roll filename (e.g. `rollDQC.US.0208.10727_WHF-US-2024.xml`) |

**Skip** any roll file with no matching instance file (e.g. SAH, XRX, EXC, NVVE, TECTP, ACRS had no instance generated).

**Missing ticker check:** After generating the bat file, scan for any command where the instance path contains `/_instance_` (i.e. the ticker segment before `_instance_` is empty). For each such line, extract the ticker from the roll filename in `--logFile` (the token between the last `_` of the rule number and the first `-` or `_` separator before `us-20XX`) and insert it into the instance path.

---

## Step 7: Run run_validate_roll.bat

Execute from repo root. Each command validates the rolled instance against the specified DQC rule and writes the log to `tests/output/roll{$EXPECTED}`.

---

## Step 8: Update .travis.yml

### 8a. Make a working copy
```
.travis.yml → .travis_copy.yml
```

### 8b. Replace $EXPECTED entries with roll prefix
For each `roll*.xml` present in `tests/output/`, replace:
```
$EXPECTED/DQC.US.xxxx_TICKER-us-2024.xml
```
with:
```
$EXPECTED/rollDQC.US.xxxx_TICKER-us-2024.xml
```

**Expected replacements: 40** (one per roll file in `tests/output/`)

### 8c. Extract roll pairs into new INFILES block
Scan the matrix section for mixed blocks containing both roll and non-roll EXFILES entries. For each matched roll `file:`/`xule_run_only` pair:
- Update `file:` from the original `.htm` SEC URL to the local `./tests/input/testfiles/2024-roll-2025/{TICKER}_instance_2024_2025.xml` path
- Move all roll pairs into a single new `- INFILES` entry at the bottom of the matrix

Non-roll pairs remain in their original blocks.

### 8d. Handle unmatched roll files
Any roll files in `tests/output/` that are NOT referenced in the main active INFILES block go into a commented `##- INFILES` entry at the top of the matrix section.

### 8e. Clean up unused files
Files in `tests/input/testfiles/2024-roll-2025/` NOT referenced on the active line 22 entry move to `tests/input/testfiles/2024-roll-2025/unused/`:
- `{TICKER}_instance_2024_2025.xml`
- `{TICKER}_taxonomy_2024_2025.zip`
- `roll*.xml` log files (from the creation step, distinct from `tests/output/` validation logs)

---

## Key Files Summary

| File | Location | Purpose |
|------|----------|---------|
| `original.csv` | `testcase-tools/` | Source table from `.travis.yml` 2024 entries |
| `results.csv` | `testcase-tools/` | XBRL US API report data |
| `final.csv` | `testcase-tools/` | Merged working table |
| `run_2024_roll2025.bat` | `testcase-tools/` | Creates rolled instance + taxonomy files |
| `run_validate_roll.bat` | `testcase-tools/` | Validates instances against DQC rules |
| `us2024_entries.csv` | `testcase-tools/` | Non-roll DQC.US *-us-2024 entries still in .travis.yml |
| `.travis_copy.yml` | `testcase-tools/` | Working copy of .travis.yml with roll updates applied |
| `{TICKER}_instance_2024_2025.xml` | `2024-roll-2025/` | Rolled XBRL instance files |
| `{TICKER}_taxonomy_2024_2025.zip` | `2024-roll-2025/` | Rolled taxonomy packages |
| `rollDQC.US.*-us-2024.xml` | `tests/output/` | Validation log files (test expected output) |

---

## Notes on File Differences

The `roll*.xml` files in `2024-roll-2025/` are **instance creation logs** (xodel/Xince plugin, large, ~22k lines).
The `roll*.xml` files in `tests/output/` are **validation logs** (DQC Rules Validator plugin, small, ~1k lines).
They are not duplicates — they serve different pipeline stages.

---

## Ruleset Paths

| Ruleset | Path |
|---------|------|
| Instance creation | `tests/input/2024-roll-2025-V29-test-ruleset.zip` |
| DQC validation | `dqc_us_rules/dqc-US-2025-V29-ruleset.zip` |
