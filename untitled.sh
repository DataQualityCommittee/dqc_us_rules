#!/bin/bash
# Run DQC Conformance Suite tests
TESTCASESROOT=./DQC_Testcases_v66
OUTPUTLOGFILE=./DQC-v70-log.xml
OUTPUTERRFILE=./DQC-v70-err.txt
OUTPUTCSVFILE=./DQC-v70-report.csv
TESTCASESINDEXFILE="$TESTCASESROOT/index.xml"
python3.4 -m arelle.CntlrCmdLine --file "$TESTCASESINDEXFILE" --validate --plugins './dqc_us_rules/dqc_us_rules|validate/EFM|logging/dqcParameters.py' --csvTestReport "$OUTPUTCSVFILE"  --logFile "$OUTPUTLOGFILE" --disclosureSystem efm-pragmatic-all-years --logCodeFilter '(?!EFM)' 2>  "$OUTPUTERRFILE"