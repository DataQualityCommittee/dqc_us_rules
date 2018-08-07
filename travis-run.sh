#!/bin/bash
set -x
echo $INFILES > infiles.json
python3.5 -m arelle.CntlrCmdLine --plugin validate/DQC -v --xule-filing-list infiles.json --logFile log.xml --xule-run
