import os
import csv
import sys

_EXCLUDED_TESTS = [
    'DQC_0001.58.2593',
    'DQC_0001.60.3062',
    'DQC_0001.64.3058',
    'DQC_0001.65.3057',
    'DQC_0001.72.3052',
    'DQC_0018.34.3452',
    'DQC_0018.34.2781'
]

_REPORT_OUTPUT_FILE = os.path.join(
    os.path.dirname(__file__),
    '..',
    '..',
    'DQC-v70-report.csv'
)


def main():
    with open(_REPORT_OUTPUT_FILE, 'rt') as f:
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
