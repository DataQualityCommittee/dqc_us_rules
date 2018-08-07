#!/bin/bash
python3.5 -m arelle.CntlrCmdLine --plugin validate/DQC -v --xule-filing-list $INFILES --logFile log.xml
