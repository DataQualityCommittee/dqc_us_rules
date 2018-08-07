#!/bin/bash
set -x
echo $INFILES > infiles.json
sed -i "s|LOCATION|$CURDIR/dqc_us_rules|" $CURDIR/plugin/xule/rulesetMap.json
cp -r $CURDIR/plugin/xule /home/travis/virtualenv/python3.5.5/src/arelle/arelle/plugin/
cp $CURDIR/plugin/validate/DQC.py /home/travis/virtualenv/python3.5.5/src/arelle/arelle/plugin/validate/
python3.5 -m arelle.CntlrCmdLine --plugin validate/DQC -v --xule-filing-list infiles.json --logFile log.xml -v
echo '===== START LOG FILE =====' && cat log.xml && echo '===== END LOG FILE ====='