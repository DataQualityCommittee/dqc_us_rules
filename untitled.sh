#!/bin/bash
# Run DQC Conformance Suite tests
TESTCASESROOT=/Users/jasonleinbach/Downloads/DQC_Testcases_v66
OUTPUTLOGFILE=/Users/jasonleinbach/DQC-v70-log.xml
OUTPUTERRFILE=/Users/jasonleinbach/DQC-v70-err.txt
OUTPUTCSVFILE=/Users/jasonleinbach/DQC-v70-report.csv
TESTCASESINDEXFILE="$TESTCASESROOT/index.xml"
rm $OUTPUTLOGFILE $OUTPUTERRFILE
python3.4 -m arelle.CntlrCmdLine --file "$TESTCASESINDEXFILE" --validate --plugins '~/workspaces/wf/dqc_us_rules/dqc_us_rules|validate/EFM|logging/dqcParameters.py' --csvTestReport "$OUTPUTCSVFILE"  --logFile "$OUTPUTLOGFILE" --disclosureSystem efm-pragmatic-all-years --logCodeFilter '(?!EFM)' 2>  "$OUTPUTERRFILE"