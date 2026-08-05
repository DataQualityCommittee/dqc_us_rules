"""
Sync sec-validation-tests.json with the matrix entries in .travis.yml.

Parses all active and single-commented matrix rows from .travis.yml,
compares them against the existing test sets in the JSON config, and
adds any missing entries with enabled=false. Existing entries are
never modified or removed.

Usage:
    python tests/synctestsets.py [--dry-run]
"""

import argparse
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

        entries.append({
            "name": name,
            "infiles": json.loads(infiles_raw),
            "exfiles": exfiles_raw,
        })

    return entries


def fingerprint(entry):
    infiles_sorted = sorted(
        (f["file"], f.get("xule_run_only", "")) for f in entry["infiles"]
    )
    exfiles_sorted = ",".join(sorted(entry["exfiles"].split(",")))
    return json.dumps(infiles_sorted) + "|" + exfiles_sorted


def sync(dry_run=False, travis_file=None, tests_json=None):
    travis_file = travis_file or DEFAULT_TRAVIS_FILE
    tests_json = tests_json or DEFAULT_TESTS_JSON

    travis_entries = parse_travis_matrix(travis_file)

    try:
        with open(tests_json) as f:
            existing = json.load(f)
    except FileNotFoundError:
        existing = []

    existing_fps = {fingerprint(e) for e in existing}

    added = []
    new_entries = []
    for entry in travis_entries:
        fp = fingerprint(entry)
        if fp not in existing_fps:
            new_entries.append({
                "name": entry["name"],
                "infiles": entry["infiles"],
                "exfiles": entry["exfiles"],
            })
            existing_fps.add(fp)
            added.append(entry["name"])

    existing = new_entries + existing

    if not added:
        print("No new test sets found. JSON is already in sync.")
        return False

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
    args = parser.parse_args()
    changed = sync(dry_run=args.dry_run, travis_file=args.travis, tests_json=args.tests)
    sys.exit(0 if not changed else 2 if args.dry_run else 0)
