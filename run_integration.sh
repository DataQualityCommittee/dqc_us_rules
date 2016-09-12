#!/bin/bash
# Run DQC Conformance Suite tests
TESTCASESROOT=./DQC_Testcases
OUTPUTLOGFILE=./DQC-log.xml
OUTPUTERRFILE=./DQC-err.txt
OUTPUTCSVFILE=./DQC-report.csv
CURRDIR=$(pwd)
TESTCASESINDEXFILE="$TESTCASESROOT/index.xml"
python3.4 -m arelle.CntlrCmdLine --file "$TESTCASESINDEXFILE" --validate --plugins "$CURRDIR/dqc_us_rules|validate/EFM|logging/dqcParameters.py" --csvTestReport "$OUTPUTCSVFILE"  --logFile "$OUTPUTLOGFILE" --disclosureSystem efm-pragmatic-all-years --logCodeFilter '(?!EFM)' 2>  "$OUTPUTERRFILE"
python3.4 -m tests.integration.run_integration
