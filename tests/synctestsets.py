"""
Sync sec-validation-tests.json with the matrix entries in .travis.yml.

Parses all active and single-commented matrix rows from .travis.yml,
compares them against the existing test sets in the JSON config. When
an entry's name already exists but its content (filings) has changed,
the existing entry is updated in place. Truly new entries are prepended.

Also structurally validates each matrix row: every {file, xule_run_only}
object in INFILES must have both fields populated, INFILES and EXFILES
must have the same number of entries (they're paired positionally), and
each entry's xule_run_only code should appear in its paired EXFILES name.

Usage:
    python tests/synctestsets.py [--dry-run] [--summary-json PATH]
"""

import argparse
import copy
import json
import re
import sys


DEFAULT_TRAVIS_FILE = ".travis.yml"
DEFAULT_TESTS_JSON = "tests/secvalidationtests.json"


def parse_travis_matrix(path):
    with open(path) as f:
        lines = f.readlines()

    entries = []
    current_label = ""
    label_counts = {}

    for line in lines:
        stripped = line.strip()

        m = re.match(r"^#\s*(.+)", stripped)
        if m and "OK as fail" not in m.group(1) and "INFILES" not in m.group(1):
            current_label = m.group(1).strip()

        is_active = stripped.startswith("- INFILES=")
        is_commented = stripped.startswith("#- INFILES=") and not stripped.startswith("##- INFILES=")

        if not (is_active or is_commented):
            continue

        clean = stripped.lstrip("#").lstrip().lstrip("-").strip()
        infiles_match = re.search(r"INFILES='(\[.*?\])'", clean)
        exfiles_match = re.search(r"EXFILES=(.*)$", clean)

        if not (infiles_match and exfiles_match):
            continue

        infiles_raw = infiles_match.group(1)
        exfiles_raw = exfiles_match.group(1).strip().replace("$EXPECTED", "./tests/output")

        base = current_label
        label_counts[base] = label_counts.get(base, 0) + 1
        if label_counts[base] > 1:
            name = f"{base} ({label_counts[base]})"
        else:
            name = base

        try:
            infiles = json.loads(infiles_raw)
        except json.JSONDecodeError:
            # Structurally broken row — validate_travis_structure() already reports
            # this; skip it here rather than crashing the whole sync.
            continue

        if not isinstance(infiles, list) or not all(
            isinstance(e, dict) and "file" in e and "xule_run_only" in e for e in infiles
        ):
            # Missing/extra keys, non-object entries, etc. — also already reported
            # by validate_travis_structure(); skip rather than crashing downstream
            # (fingerprint() and the sync diff assume both keys are present).
            continue

        entries.append({
            "name": name,
            "infiles": infiles,
            "exfiles": exfiles_raw,
        })

    return entries


def validate_travis_structure(path):
    """Structurally validate each matrix row's INFILES/EXFILES pairing.

    Every {file, xule_run_only} object must have both fields populated,
    the INFILES count must match the EXFILES count (they're paired
    positionally by the validation workflow, not by name), and each
    entry's xule_run_only code should appear in its positionally-paired
    expected-results filename.

    :param path: Path to .travis.yml
    :return: list of issue dicts: {"row": name, "line": lineno, "issue": message}
    """
    with open(path) as f:
        lines = f.readlines()

    issues = []
    current_label = ""
    label_counts = {}

    for lineno, line in enumerate(lines, start=1):
        stripped = line.strip()

        m = re.match(r"^#\s*(.+)", stripped)
        if m and "OK as fail" not in m.group(1) and "INFILES" not in m.group(1):
            current_label = m.group(1).strip()

        is_active = stripped.startswith("- INFILES=")
        is_commented = stripped.startswith("#- INFILES=") and not stripped.startswith("##- INFILES=")
        if not (is_active or is_commented):
            continue

        clean = stripped.lstrip("#").lstrip().lstrip("-").strip()
        infiles_match = re.search(r"INFILES='(\[.*?\])'", clean)
        exfiles_match = re.search(r"EXFILES=(.*)$", clean)

        base = current_label
        label_counts[base] = label_counts.get(base, 0) + 1
        row_name = base if label_counts[base] == 1 else f"{base} ({label_counts[base]})"

        if not infiles_match:
            issues.append({"row": row_name, "line": lineno, "issue": "Could not find INFILES='[...]' on this row"})
            continue
        if not exfiles_match:
            issues.append({"row": row_name, "line": lineno, "issue": "Could not find EXFILES=... on this row"})
            continue

        try:
            infiles = json.loads(infiles_match.group(1))
        except json.JSONDecodeError as e:
            issues.append({"row": row_name, "line": lineno, "issue": f"INFILES is not valid JSON: {e}"})
            continue

        exfiles_raw = exfiles_match.group(1).strip().replace("$EXPECTED", "./tests/output")
        exfiles = [x for x in exfiles_raw.split(",") if x.strip()]

        if len(infiles) != len(exfiles):
            issues.append({
                "row": row_name,
                "line": lineno,
                "issue": f"{len(infiles)} INFILES entries vs {len(exfiles)} EXFILES entries (must match 1:1)",
            })
            if len(infiles) > len(exfiles):
                # file/xule_run_only entries with no corresponding $EXPECTED entry
                for i in range(len(exfiles), len(infiles)):
                    entry = infiles[i]
                    rule = entry.get("xule_run_only", "?") if isinstance(entry, dict) else "?"
                    issues.append({
                        "row": row_name,
                        "line": lineno,
                        "issue": f"INFILES[{i}] ({rule}) has no matching EXFILES/$EXPECTED entry — an entry was removed from EXFILES without removing the matching INFILES entry",
                    })
            else:
                # $EXPECTED entries left behind after their file/xule_run_only was removed
                for i in range(len(infiles), len(exfiles)):
                    exname = exfiles[i].rsplit("/", 1)[-1]
                    issues.append({
                        "row": row_name,
                        "line": lineno,
                        "issue": f"EXFILES[{i}] ('{exname}') has no matching INFILES entry — file/xule_run_only was removed but its $EXPECTED entry remains",
                    })

        for i, entry in enumerate(infiles):
            if not isinstance(entry, dict):
                issues.append({"row": row_name, "line": lineno, "issue": f"INFILES[{i}] is not an object: {entry!r} (invalid structure)"})
                continue

            has_pair = i < len(exfiles)
            suffix = " while its EXFILES/$EXPECTED entry remains" if has_pair else ""

            missing_keys = {"file", "xule_run_only"} - set(entry.keys())
            extra_keys = set(entry.keys()) - {"file", "xule_run_only"}
            if missing_keys:
                issues.append({
                    "row": row_name,
                    "line": lineno,
                    "issue": f"INFILES[{i}] missing key(s) {sorted(missing_keys)}{suffix}",
                })
            if extra_keys:
                issues.append({"row": row_name, "line": lineno, "issue": f"INFILES[{i}] has unexpected key(s): {sorted(extra_keys)} (invalid structure)"})
            if "file" in entry and not entry.get("file", "").strip():
                issues.append({"row": row_name, "line": lineno, "issue": f"INFILES[{i}] has an empty 'file'{suffix}"})
            if "xule_run_only" in entry and not entry.get("xule_run_only", "").strip():
                issues.append({"row": row_name, "line": lineno, "issue": f"INFILES[{i}] has an empty 'xule_run_only'{suffix}"})

            if i < len(exfiles):
                rule = entry.get("xule_run_only", "")
                exname = exfiles[i].rsplit("/", 1)[-1]
                if rule and rule not in exname:
                    issues.append({
                        "row": row_name,
                        "line": lineno,
                        "issue": f"INFILES[{i}] xule_run_only '{rule}' does not appear in its paired EXFILES name '{exname}'",
                    })

    return issues


def fingerprint(entry):
    infiles_sorted = sorted(
        (f["file"], f.get("xule_run_only", "")) for f in entry["infiles"]
    )
    exfiles_sorted = ",".join(sorted(entry["exfiles"].split(",")))
    return json.dumps(infiles_sorted) + "|" + exfiles_sorted


def sync(dry_run=False, travis_file=None, tests_json=None, summary_json=None):
    travis_file = travis_file or DEFAULT_TRAVIS_FILE
    tests_json = tests_json or DEFAULT_TESTS_JSON

    structural_issues = validate_travis_structure(travis_file)
    if structural_issues:
        print(f"\nFound {len(structural_issues)} structural issue(s) in {travis_file}:")
        for issue in structural_issues:
            print(f"  ! [{issue['row']}] line {issue['line']}: {issue['issue']}")
    else:
        print(f"\n{travis_file} structure OK — every INFILES entry has a matching EXFILES entry.")

    travis_entries = parse_travis_matrix(travis_file)

    try:
        with open(tests_json) as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = []

    existing_fps = {fingerprint(e) for e in existing}
    existing_by_name = {e["name"]: i for i, e in enumerate(existing)}

    added = []
    updated = []
    added_details = []
    updated_details = []
    new_entries = []
    for entry in travis_entries:
        fp = fingerprint(entry)
        if fp in existing_fps:
            continue
        if entry["name"] in existing_by_name:
            idx = existing_by_name[entry["name"]]
            before = {
                "infiles": copy.deepcopy(existing[idx]["infiles"]),
                "exfiles": existing[idx]["exfiles"],
            }
            existing[idx]["infiles"] = entry["infiles"]
            existing[idx]["exfiles"] = entry["exfiles"]
            after = {"infiles": entry["infiles"], "exfiles": entry["exfiles"]}
            existing_fps.add(fp)
            updated.append(entry["name"])
            updated_details.append({"name": entry["name"], "before": before, "after": after})
        else:
            new_entry = {
                "name": entry["name"],
                "infiles": entry["infiles"],
                "exfiles": entry["exfiles"],
            }
            new_entries.append(new_entry)
            existing_fps.add(fp)
            added.append(entry["name"])
            added_details.append({"name": entry["name"], "entry": new_entry})

    existing = new_entries + existing
    has_changes = bool(added or updated)

    if summary_json:
        with open(summary_json, "w") as f:
            json.dump({
                "structural_issues": structural_issues,
                "added": added,
                "updated": updated,
                "added_details": added_details,
                "updated_details": updated_details,
                "has_changes": has_changes,
            }, f, indent=2)

    if not has_changes:
        print("No new test sets found. JSON is already in sync.")
        return False

    if updated:
        print(f"Updated {len(updated)} existing test set(s):")
        for name in updated:
            print(f"  ~ {name}")
    if added:
        print(f"Found {len(added)} new test set(s):")
        for name in added:
            print(f"  + {name}")

    if dry_run:
        print("\nDry run — no changes written.")
        return True

    with open(tests_json, "w") as f:
        json.dump(existing, f, indent=2)
        f.write("\n")

    print(f"\nUpdated {tests_json}")
    return True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sync test sets from .travis.yml")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be added without writing")
    parser.add_argument("--travis", default=None, help="Path to .travis.yml (default: .travis.yml)")
    parser.add_argument("--tests", default=None, help="Path to sec-validation-tests.json (default: .github/workflows/sec-validation-tests.json)")
    parser.add_argument("--summary-json", default=None, help="Write a machine-readable summary (structural issues, added/updated names) to this path")
    args = parser.parse_args()
    changed = sync(dry_run=args.dry_run, travis_file=args.travis, tests_json=args.tests, summary_json=args.summary_json)
    sys.exit(0 if not changed else 2 if args.dry_run else 0)
