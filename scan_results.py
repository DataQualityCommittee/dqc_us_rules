import os
import csv
import sys
import argparse

_EXCLUDED_TESTS = [
]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('csv_file', help='CSV Test Report File name')
    args = parser.parse_args()

    with open(args.csv_file, 'rt') as f:
        reader = csv.reader(f)
        # skip header
        next(reader, None)
        failed_rows = []
        for row in reader:
            if len(row) > 5:
                if row[2] not in _EXCLUDED_TESTS:
                    if row[5] != 'pass':
                        failed_rows.append(row)
    if len(failed_rows) > 0:
        print('Tests failed: {}'.format(failed_rows))
        sys.exit(1)
    else:
        print('All included tests pass')
        sys.exit(0)

if __name__ == "__main__":
    main()
