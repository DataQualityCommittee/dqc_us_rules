# Process: Consolidating Invalid Roll Test Case Files

This document describes the two-step process for identifying and consolidating invalid validation logs, instance files, and taxonomy archives into the `invalid` directory.

**Destination:** `tests/input/testfiles/testcase-tools/invalid/`

---

## Step 1 — Identify Invalid Validation Logs

### What
Evaluate each `roll*.xml` output file in `tests/output/` to confirm it contains at least one DQC rule finding. A valid roll output file must contain at least one occurrence of:

```
<entry code="DQC.US
```

Any roll file that lacks this string produced no DQC.US findings and is considered an invalid test case.

### How

Run the following Python snippet:

```python
import os, glob, shutil

output_dir  = "tests/output"
invalid_dir = "tests/input/testfiles/testcase-tools/invalid"
search_str  = '<entry code="DQC.US'

for path in sorted(glob.glob(os.path.join(output_dir, "roll*.xml"))):
    with open(path, encoding="utf-8", errors="replace") as f:
        content = f.read()
    if search_str not in content:
        basename   = os.path.basename(path)
        new_name   = "invalid-" + basename
        # Rename in place, then move to invalid directory
        new_path   = os.path.join(output_dir, new_name)
        os.rename(path, new_path)
        shutil.move(new_path, os.path.join(invalid_dir, new_name))
        print(f"Moved: {new_name}")
```

### Result
- Files are renamed with the `invalid-` prefix (e.g., `invalid-rollDQC.US.0077.7654_MTEX-us-2023.xml`).
- Renamed files are moved to the `invalid/` directory.

---

## Step 2 — Identify Instance Files with No Valid Roll Match

### What
After Step 1, compare the remaining (valid) roll output files against the instance files in the roll input folder. Any instance file that has no corresponding valid roll file is an invalid test case — its instance `.xml` and taxonomy `.zip` are moved to `invalid/`.

Roll filenames encode the company ticker in this format:

```
rollDQC.US.{rule}_{TICKER}-us-2023.xml      (e.g. rollDQC.US.0001.57_TOL-us-2023.xml)
rollDQC.US.{rule}_{TICKER}_US-2023.xml      (e.g. rollDQC.US.0204.10706_LEVI_US-2023.xml)
```

Instance filenames follow:

```
{TICKER}_instance_2023_2025.xml
{TICKER}_taxonomy_2023_2025.zip
```

A dot-suffix ticker in a roll file (e.g., `AGM.A`) is treated as a match for the base ticker (`AGM`).

### How

Run the following Python snippet:

```python
import os, re, shutil

roll_dir    = "tests/output"
inst_dir    = "tests/input/testfiles/2023-roll-2025"
invalid_dir = "tests/input/testfiles/testcase-tools/invalid"

def extract_ticker(filename):
    """Extract company ticker from a roll output filename."""
    name = filename.replace(".xml", "")
    name = re.sub(r'^rollDQC\.(US|IFRS)\.\d+(\.\d+)?_', '', name)
    name = re.sub(r'[-_][Uu][Ss]-2023$', '', name)
    return name.upper()

# Collect tickers from remaining valid roll files
roll_files   = [f for f in os.listdir(roll_dir) if f.startswith("roll") and f.endswith(".xml")]
roll_tickers = set(extract_ticker(f) for f in roll_files)

# Collect instance tickers
inst_files   = [f for f in os.listdir(inst_dir) if f.endswith("_instance_2023_2025.xml")]
inst_tickers = {f.split("_")[0].upper(): f for f in inst_files}

# Move instance + taxonomy pairs with no matching roll ticker
for ticker, inst_file in sorted(inst_tickers.items()):
    matched = ticker in roll_tickers or any(
        rt == ticker or rt.startswith(ticker + ".") for rt in roll_tickers
    )
    if not matched:
        for suffix in [f"{ticker}_instance_2023_2025.xml", f"{ticker}_taxonomy_2023_2025.zip"]:
            src = os.path.join(inst_dir, suffix)
            dst = os.path.join(invalid_dir, suffix)
            if os.path.exists(src):
                shutil.move(src, dst)
                print(f"Moved: {suffix}")
```

### Result
- Instance `.xml` and taxonomy `.zip` file pairs with no valid roll match are moved to `invalid/`.
- Reasons an instance file may lack a valid roll match:
  - No roll file was ever generated for that ticker.
  - The roll file was moved to `invalid/` in Step 1 (produced no DQC.US findings).
  - The ticker in the roll filename does not exactly match the instance filename ticker.

---

## Directory Inventory After Both Steps

The `invalid/` directory will contain:

| File type | Naming pattern | Origin |
|---|---|---|
| Invalid validation log | `invalid-roll*.xml` | Step 1 — renamed from `tests/output/` |
| Invalid instance file | `{TICKER}_instance_2023_2025.xml` | Step 2 — moved from roll input folder |
| Invalid taxonomy archive | `{TICKER}_taxonomy_2023_2025.zip` | Step 2 — moved from roll input folder |
