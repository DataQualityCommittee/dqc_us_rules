# Process: Rolling Test Cases Forward to a New Taxonomy Year and Updating .travis.yml

## Overview

This document describes the end-to-end process used to:
1. Identify pending test case entries for a source year (e.g. 2024) in `.travis.yml` or a candidate list
2. Query the XBRL US API to get company namespace (fact) data
3. Generate a batch file (`run_{fromYear}_roll{toYear}.bat`) to create rolled instance `.xml` files using Arelle + xule + xodel
4. Generate a batch file (`run_validate_roll.bat`) to validate rolled instances against DQC rules
5. Update `.travis.yml` with the new roll test entries, removing any original entries it supersedes

Examples below use a `2024 → 2025` roll, but the year and ruleset version (`V29`, `V31`, ...) are always parameters, not fixed values — substitute whatever source/target year and current ruleset version you're actually working with.

---

## Inputs

| File | Location | Description |
|------|----------|-------------|
| `.travis.yml` | repo root | Source of active INFILES/EXFILES test entries |
| `original.csv` | `testcase-tools/` | Table of `$EXPECTED`, `file:`, and `updated` (converted URL) columns — derived from `.travis.yml` entries for the source year |
| `results.csv` | `testcase-tools/` | XBRL US API report lookup results — columns: `report.entry-url`, `entity.ticker`, `report.entity-name`, `fact` (dts.target-namespace), etc. |
| `final.csv` | `testcase-tools/` | Merged table of `original.csv` + `results.csv` on `file:` = `report.entry-url` |

---

## Local Environment Setup

The `arelleCmdLine.exe` on `PATH` is a plain `pip install`-ed Arelle. It does **not** come with the `xule` plugin family pre-registered the way CI's `travis-run.sh` sets it up (CI clones the `xule` repo fresh each run and moves `plugin/xule`, `plugin/validate/DQC.py`, etc. directly into Arelle's own `site-packages/arelle/plugin/` folder so bare plugin names like `"xule"` resolve). Locally, you must either:
- **Mirror CI**: copy/symlink `xule/plugin/xule`, `xule/plugin/xodel`, `xule/plugin/SimpleXBRLModel`, `xule/plugin/serializer`, and `xule/plugin/validate/DQC.py` into Arelle's own plugin directory once, so short names work as written in the command templates below, **or**
- **Reference full local paths** in every `--plugins` argument, e.g. `--plugins "D:/.../xule/plugin/xule|D:/.../xule/plugin/SimpleXBRLModel|D:/.../xule/plugin/xodel|D:/.../xule/plugin/serializer"`.

**Required plugin set per stage** (this is the part that's easy to get wrong — omitting any of these produces a crash deep inside `xodel`/`serializer`, not an obvious "plugin not found" error):
- **Instance creation (Step 4/5):** `xule` + `SimpleXBRLModel` + `xodel` + `serializer`. All four are required even though the command only ever references `xodel`-specific flags — `xodel.py` does plain (non-plugin) Python imports of `SimpleXBRLModel` and `serializer` as a fallback, but those modules only initialize correctly (e.g. the shared `_SXM` reference inside `serializer`) when Arelle's plugin loader fires their `__pluginInfo__` mount points, which only happens if they're also listed in `--plugins`.
- **Validation (Step 6/7):** `xule` alone is sufficient. `validate/DQC` and `EDGAR/transform` (used by CI) are **not** required for validating an already-rolled instance, because the rolled instance is a plain XBRL file, not inline XBRL — `EDGAR/transform`'s SEC-specific inline transforms don't apply, and `validate/DQC` is just a convenience wrapper around `xule` for auto-selecting a ruleset, which you're bypassing anyway by passing `--xule-rule-set` explicitly.

**Python dependency:** the `xule` plugin requires `aniso8601`, which is not a default Arelle dependency. If you see `ModuleNotFoundError: No module named 'aniso8601'`, install it into the same Python environment `arelleCmdLine.exe` resolves to (check with `pip show Arelle-release` or by inspecting the shebang/launcher).

---

## Step 1: Extract Source-Year Entries from .travis.yml

Parse `.travis.yml` matrix section for all active (non-`##`) INFILES entries where `$EXPECTED` ends in `{fromYear}.xml`. For each `{file: "...", xule_run_only: "..."}` block, capture:

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

## Step 4: Generate run_{fromYear}_roll{toYear}.bat (Instance Creation)

For each MATCHED row in `final.csv`, generate one Arelle command using the `file:` column (original `.htm` SEC URL) to fetch the filing and produce a rolled instance `.xml`.

**Command template:**
```bat
arelleCmdLine.exe --plugins "{xule_path}|{SimpleXBRLModel_path}|{xodel_path}|{serializer_path}" -f "{file:}" --xule-time .005 --xule-debug --noCertificateCheck --logFile "D:/DJT/.../tests/input/testfiles/{fromYear}-roll-{toYear}/roll{$EXPECTED}" --xule-rule-set "D:/DJT/.../tests/input/{fromYear}-roll-{toYear}-V{ver}-test-ruleset.zip" --xodel-location "D:/DJT/.../tests/input/testfiles/{fromYear}-roll-{toYear}/" --xodel-show-xule-log --xince-file-type=xml --xule-arg TAXONOMY_DATE="{ROLL_YEAR}{MMDD}" --xule-arg PUBLISH_TAXONOMY={entity.ticker}_taxonomy_{fromYear}_{toYear} --xule-arg TICKER={entity.ticker} --xule-arg OLD_CO_NAMESPACE={fact} --xule-arg INSTANCE_NAME={entity.ticker}_instance_{fromYear}_{toYear} --xule-arg NEW_CO_NAMESPACE={FACTDOMAIN}{ROLL_YEAR}{MMDD}
```

See **Local Environment Setup** above for what `{xule_path}` etc. resolve to and why all four plugins are needed — a bare `--plugins "xodel"` will fail with `ModuleNotFoundError: No module named 'SimpleXBRLModel'` or (if `SimpleXBRLModel` is present but `serializer` isn't) `AttributeError: 'NoneType' object has no attribute 'SXMType'`.

**Column mappings:**
| Placeholder | Source column |
|-------------|--------------|
| `{file:}` | `file:` (original `.htm` SEC URL) |
| `{$EXPECTED}` | `$EXPECTED` (e.g. `DQC.US.0208.10727_WHF-US-2024.xml`) |
| `{entity.ticker}` | `entity.ticker` |
| `{fact}` | `fact` (full namespace URI, first value if multiple) |
| `{FACTDOMAIN}` | `fact` truncated to 3rd `/` inclusive (e.g. `http://henryschein.com/`) |
| `{ROLL_YEAR}` | The ending year of the roll forward — e.g. `{toYear}` |
| `{MMDD}` | The 4-digit month+day extracted from `fact` (last 4 digits of the date segment in the namespace URI, e.g. `1231` from `http://henryschein.com/20241231`) |
| `{ver}` | The current ruleset version under test (e.g. `V31`) — **do not hardcode a version**; use whatever `{fromYear}-roll-{toYear}-V{ver}-test-ruleset.zip` currently exists in `tests/input/` |

**Notes:**
- Use forward slashes throughout paths — backslashes with `\t`, `\2` etc. are misinterpreted by Python string literals
- `TAXONOMY_DATE` value uses double quotes; all other `--xule-arg` values are unquoted
- `TAXONOMY_DATE` and `NEW_CO_NAMESPACE` date suffix = `{ROLL_YEAR}` + `{MMDD}` derived from `fact`: replace the year in the namespace date with the roll's ending year, preserving the original mmdd (e.g. `http://henryschein.com/20241231` → `MMDD=1231`, `ROLL_YEAR=2025` → `20251231`)
- **Edge case — namespace date already in roll year:** If the year extracted from `fact` equals `{ROLL_YEAR}` (e.g. the filing has a 2025 period-end date but is a 2024 report), `OLD_CO_NAMESPACE` and `NEW_CO_NAMESPACE` would be identical. In this case, increment `{ROLL_YEAR}` by one additional year for `TAXONOMY_DATE` and `NEW_CO_NAMESPACE` only (e.g. use `2026` instead of `2025`), so the rolled instance has a distinct namespace.
- **Edge case — missing ticker:** If `entity.ticker` is empty in `final.csv` for a row, `PUBLISH_TAXONOMY`, `TICKER`, and `INSTANCE_NAME` will be blank in the generated command (appearing as `PUBLISH_TAXONOMY=_taxonomy_...`, `TICKER=`, `INSTANCE_NAME=_instance_...`). After generating the bat file, scan for any command where `PUBLISH_TAXONOMY=_` or `INSTANCE_NAME=_` appears and fill in the missing ticker by extracting it from the `$EXPECTED` filename in the `--logFile` argument (the token between the last `_` of the rule number and the first `-` or `_` separator before `us-20XX`).
- **Ticker drift:** the token embedded in a roll candidate's filename (e.g. `ABQQ` in `rollDQC.US.0014_ABQQ-us-2024.xml`) reflects the ticker *at the time the candidate list was compiled*. Companies rename/rebrand/change ticker between then and when you actually run the roll. Always trust the `entity.ticker` value actually resolved by the API lookup (and used as `TICKER=` in the generated command) over the filename token — don't assume the small "known overrides" table below is exhaustive; treat any mismatch between filename token and `entity.ticker` as expected and normal, not an error.

**Output files per run:**
- `{TICKER}_instance_{fromYear}_{toYear}.xml` — the rolled XBRL instance
- `{TICKER}_taxonomy_{fromYear}_{toYear}.zip` — the rolled taxonomy package
- `roll{$EXPECTED}` — the Arelle log file, written to `{fromYear}-roll-{toYear}/` and left there permanently (see **Notes on File Differences** — there is no later "move to tests/output" step for this file; a *separate* validation log of the same name is written to `tests/output/` in Step 7)

**Before running — delete any pre-existing file at the `--logFile` path.** Arelle opens `--logFile` in **append** mode, not truncate. If the target path already has content (a pre-existing stub committed to git, or leftover output from a previous failed attempt at this same ticker), the new run's log gets concatenated onto the old content instead of replacing it — silently producing a file with two full `<?xml ...><log>...</log>` documents back to back. See **Troubleshooting** for how to detect and fix this if you didn't catch it in advance.

---

## Step 5: Run run_{fromYear}_roll{toYear}.bat

Run each command individually rather than as one big batch, so a crash on one ticker doesn't obscure whether earlier tickers in the batch actually succeeded. `arelleCmdLine.exe` needs to be on `PATH` or referenced by full path.

**Verify each run before moving on:**
1. Check the process actually exited 0 — if you're piping output through another command (e.g. `| tail`), the reported exit code reflects the *pipe's* last command, not `arelleCmdLine.exe`'s. Redirect to a file and check `$?` directly instead.
2. Confirm both output files exist and are non-trivial size: `{TICKER}_instance_{fromYear}_{toYear}.xml` and `{TICKER}_taxonomy_{fromYear}_{toYear}.zip`. A `.zip` of ~20 bytes means the taxonomy serialization crashed after creating an empty archive — check the log for a `serializer` traceback (see Troubleshooting).
3. Confirm the `--logFile` output has exactly one `<?xml version=` declaration: `grep -c '<?xml version=' <logfile>` should be `1`. If it's `2` or more, the append-mode issue above occurred — strip everything before the last `<?xml ...>` and keep only the final `<log>...</log>` block.

If a ticker's instance creation fails and can't be quickly fixed, abandon it cleanly: `git checkout -- <path>` for any pre-existing tracked file that got modified or deleted, `rm` for any newly-created file, so it leaves no diff and doesn't get mistaken for a completed roll.

---

## Step 6: Generate run_validate_roll.bat (DQC Rule Validation)

For each `roll*.xml` file in `tests/input/testfiles/{fromYear}-roll-{toYear}/`, find the corresponding `{TICKER}_instance_{fromYear}_{toYear}.xml` and generate a validation command.

**Ticker mapping:** Derive from `final.csv` `entity.ticker` column matched via `$EXPECTED`. This table is a non-exhaustive sample of overrides seen so far — expect to encounter more (see "Ticker drift" note in Step 4):

| Roll filename token | Actual ticker / instance |
|--------------------|--------------------------|
| TENNX | TENX |
| IMII | BSAI |
| DEFE | DTII |
| UNIO | UCC |
| ABQQ | AERA |
| ACCR | ASII |
| BLAC | BDCC |

**Command template:**
```bat
arelleCmdLine.exe --plugins "{xule_path}" -f "./tests/input/testfiles/{fromYear}-roll-{toYear}/{TICKER}_instance_{fromYear}_{toYear}.xml" -v --xule-run-only {RULE} --xule-time .005 --xule-debug --noCertificateCheck --logFile "./tests/output/{ROLL}" --xule-rule-set "./dqc_us_rules/dqc-us-{toYear}-V{ver}-ruleset.zip"
```

Only the `xule` plugin is needed here — see **Local Environment Setup** for why `validate/DQC` and `EDGAR/transform` (used by CI's `travis-run.sh`) aren't required for a local, already-rolled, non-inline instance.

**Placeholder mappings:**
| Placeholder | Value |
|-------------|-------|
| `{TICKER}_instance_{fromYear}_{toYear}.xml` | The rolled instance produced in Step 4/5 |
| `{RULE}` | Extracted from the `--logFile` filename: the substring between `roll` and the first `_` (e.g. `rollDQC.US.0208.10727_WHF-US-2024.xml` → `DQC.US.0208.10727`). Only one space before and after this value in the command. |
| `{ROLL}` | Full roll filename (e.g. `rollDQC.US.0208.10727_WHF-US-2024.xml`) |

**Skip** any roll file with no matching instance file — instance creation failed for that ticker (e.g. SAH, XRX, EXC, NVVE, TECTP, ACRS, ADTX had no instance generated). See **Troubleshooting** for common crash signatures.

**Missing ticker check:** After generating the bat file, scan for any command where the instance path contains `/_instance_` (i.e. the ticker segment before `_instance_` is empty). For each such line, extract the ticker from the roll filename in `--logFile` (the token between the last `_` of the rule number and the first `-` or `_` separator before `us-20XX`) and insert it into the instance path.

**Delete any pre-existing file at the `--logFile` path before running**, for the same append-mode reason as Step 4.

---

## Step 7: Run run_validate_roll.bat

Execute from repo root. Each command validates the rolled instance against the specified DQC rule and writes the log to `tests/output/roll{$EXPECTED}`.

**A clean exit is not sufficient — confirm the rule actually fired.** A ticker can create and validate without any error yet still be useless as a regression fixture, if the roll process didn't preserve whatever fact pattern originally triggered the rule. After each run, check:
```
grep -c 'code="{RULE}' tests/output/roll{$EXPECTED}
```
This must be **greater than 0**. If it's `0`, treat the ticker the same as a hard failure — do not add it to `.travis.yml` in Step 8 (abandon it per the cleanup note in Step 5). A useful sanity check when a rule family covers many sub-numbered variants (e.g. `DQC.US.0014.2791`) is to grep for the *family* prefix (`DQC.US.0014`) rather than an exact match, since `--xule-run-only` with a bare family id will fire whichever specific sub-rule applies to that filer.

---

## Step 8: Update .travis.yml

### 8a. Make a working copy
```
.travis.yml → .travis_copy.yml
```

### 8b. Replace $EXPECTED entries with roll prefix
For each `roll*.xml` present in `tests/output/`, replace:
```
$EXPECTED/DQC.US.xxxx_TICKER-us-{fromYear}.xml
```
with:
```
$EXPECTED/rollDQC.US.xxxx_TICKER-us-{fromYear}.xml
```

### 8c. Extract roll pairs into new INFILES block
Scan the matrix section for mixed blocks containing both roll and non-roll EXFILES entries. For each matched roll `file:`/`xule_run_only` pair:
- Update `file:` from the original `.htm` SEC URL to the local `./tests/input/testfiles/{fromYear}-roll-{toYear}/{TICKER}_instance_{fromYear}_{toYear}.xml` path
- Move all roll pairs into a single new `- INFILES` entry at the bottom of the matrix

Non-roll pairs remain in their original blocks.

**`INFILES` and `EXFILES` are positionally paired arrays on the same line** — the Nth object in the `INFILES` JSON array corresponds to the Nth comma-separated token in `EXFILES`. Any manual edit must keep them in lockstep (add/remove at the same index in both), or — safer — edit programmatically by matching on content (the `file:` URL or `xule_run_only` rule id) rather than by position, and re-serialize both arrays together.

### 8d. Handle unmatched roll files
Any roll files in `tests/output/` that are NOT referenced in the main active INFILES block go into a commented `##- INFILES` entry at the top of the matrix section.

### 8e. Remove the superseded original entry
**This step is easy to skip and has no error if you skip it — verify it explicitly.** For every ticker/rule pair you just rolled forward, the *original* (non-rolled) entry for that exact pair — testing the original filing against the original year's taxonomy — almost certainly still exists somewhere else in the matrix (it does not have to be adjacent to, or in the same block as, the roll entry you just added). Find it by matching on the same `file:` URL and `xule_run_only` rule id used to generate the roll command, and remove that INFILES/EXFILES pair from wherever it lives.

**Verification (required, not optional):** for every ticker just rolled, run:
```
grep -o "[^,\"']*<TICKER>-us-{fromYear}[^,\"']*" .travis.yml
```
This should return **exactly one match** — the `roll`-prefixed entry. If it returns two (a `roll...` and a non-`roll...` match), the original entry wasn't removed.

**Definition of done for the whole Step 8 edit:** re-parse the edited line(s) and confirm `INFILES` is still valid JSON and its length equals the number of comma-separated `EXFILES` tokens:
```python
import re, json
m = re.search(r"INFILES='(\[.*?\])' EXFILES=(\S+)", line)
infiles = json.loads(m.group(1))
exfiles = m.group(2).split(",")
assert len(infiles) == len(exfiles)
```

### 8f. Creation-stage log files are kept permanently, not moved to "unused/"
Unlike the taxonomy/rule set files, the `roll*.xml` creation logs in `{fromYear}-roll-{toYear}/` are left in place indefinitely once a ticker is successfully rolled and added to `.travis.yml` — there is no cleanup/archival step that moves them elsewhere. (An `unused/` subfolder convention was previously documented here but does not reflect actual practice — it does not get used even for tickers processed months ago.)

If a ticker is **abandoned** (failed creation, or validated with zero rule hits per Step 7), leave no trace: `git checkout -- <path>` to restore any pre-existing tracked file (creation log stub, etc.) that got modified or deleted during the attempt, and `rm` any newly-created file (`{TICKER}_instance_...xml`, `{TICKER}_taxonomy_...zip`, `tests/output/roll...xml`, any ticker-specific scratch `.bat`). Do not add it to `.travis.yml`.

---

## Troubleshooting

Errors observed in practice, and what they actually mean:

| Error | Cause | Fix |
|---|---|---|
| `arelleCmdLine: error: no such option: --xule-time` | `xule` plugin isn't loaded at all — usually `--plugins "xodel"` alone, with no `xule` path | Add the full path to `xule/plugin/xule` to `--plugins` |
| `ModuleNotFoundError: No module named 'aniso8601'` | Missing Python dependency for `xule` | `pip install aniso8601` into the Python env backing `arelleCmdLine.exe` |
| `ModuleNotFoundError: No module named 'xodel.SimpleXBRLModel'` / `No module named 'SimpleXBRLModel'` | `SimpleXBRLModel` plugin folder not on the loader's path | Add `xule/plugin/SimpleXBRLModel` to `--plugins` |
| `AttributeError: 'NoneType' object has no attribute 'SXMType'` (inside `serializer/__init__.py`) | `serializer` plugin not registered — its `Serializer.Init` hook is what populates the shared `_SXM` module reference; a plain `import serializer` inside `xodel.py` gets a module whose hooks never fired | Add `xule/plugin/serializer` to `--plugins` |
| Taxonomy `.zip` output is ~20 bytes | Same root cause as above — taxonomy serialization crashed after creating an empty archive | Check the crash trace; almost always the `serializer`/`SimpleXBRLModel` plugin issue |
| `XodelException: There is no content for the label. Rule: labels` (or similar `XodelException`) | Genuine data issue in that filer's facts/labels — not an environment problem | Skip this ticker (Step 5 abandonment) |
| `...concept {X} is not in the taxonomy` | Local Arelle taxonomy cache is missing the target year's full US-GAAP taxonomy and couldn't resolve a concept referenced during the roll | Confirm network access to fetch `xbrl.fasb.org`/`taxonomies.xbrl.us`; may require a long first-time taxonomy download |
| A rolled instance validates cleanly but the target rule shows 0 hits | The roll process didn't preserve the fact pattern that originally triggered the rule | Not a fixable error — abandon the ticker per Step 7/Step 8f, it's not a useful regression fixture |
| A `--logFile` output contains two `<?xml ...><log>...</log>` documents | `--logFile` was opened in append mode against a path that already had content (pre-existing git stub, or leftover from a prior failed attempt at the same ticker) | Delete the target path before rerunning (see Step 4/6); if already corrupted, keep only the content from the last `<?xml version=` onward |

---

## Key Files Summary

| File | Location | Purpose |
|------|----------|---------|
| `original.csv` | `testcase-tools/` | Source table from `.travis.yml` entries for the source year |
| `results.csv` | `testcase-tools/` | XBRL US API report data |
| `final.csv` | `testcase-tools/` | Merged working table |
| `run_{fromYear}_roll{toYear}.bat` | `testcase-tools/` | Creates rolled instance + taxonomy files |
| `run_validate_roll.bat` | `testcase-tools/` | Validates instances against DQC rules |
| `us{fromYear}_entries.csv` | `testcase-tools/` | Non-roll DQC.US `*-us-{fromYear}` entries still in .travis.yml |
| `.travis_copy.yml` | `testcase-tools/` | Working copy of .travis.yml with roll updates applied |
| `{TICKER}_instance_{fromYear}_{toYear}.xml` | `{fromYear}-roll-{toYear}/` | Rolled XBRL instance files |
| `{TICKER}_taxonomy_{fromYear}_{toYear}.zip` | `{fromYear}-roll-{toYear}/` | Rolled taxonomy packages |
| `rollDQC.US.*-us-{fromYear}.xml` | `tests/output/` | Validation log files (test expected output) |

---

## Notes on File Differences

The `roll*.xml` files in `{fromYear}-roll-{toYear}/` are **instance creation logs** (xule/xodel plugin, large — tens of MB for a big filer).
The `roll*.xml` files in `tests/output/` are **validation logs** (xule DQC validation, much smaller — under 1 MB typically).
They share the same filename but are not duplicates — they serve different pipeline stages and both are kept permanently once a ticker is committed.

---

## Ruleset Paths

| Ruleset | Path pattern | Notes |
|---------|------|-------|
| Instance creation | `tests/input/{fromYear}-roll-{toYear}-V{ver}-test-ruleset.zip` | `{ver}` must match the current ruleset version under test — check `tests/input/` for what actually exists rather than assuming a version |
| DQC validation | `dqc_us_rules/dqc-us-{toYear}-V{ver}-ruleset.zip` | Same version as above; note this lives in the **inner** `dqc_us_rules/` folder (the repo root is also named `dqc_us_rules`, which is easy to confuse) |
