#!/bin/bash
set -x
echo $INFILES > infiles.json
sed -i "s|https://github.com/DataQualityCommittee/dqc_us_rules/.*/dqc_us_rules/|dqc_us_rules/|" $CURDIR/plugin/xule/rulesetMap.json
sed -i "s|\?raw=true||" $CURDIR/plugin/xule/rulesetMap.json
cp -r $CURDIR/plugin/xule /home/travis/virtualenv/python3.5.5/src/arelle/arelle/plugin/
cp $CURDIR/plugin/validate/DQC.py /home/travis/virtualenv/python3.5.5/src/arelle/arelle/plugin/validate/
python3.5 -m arelle.CntlrCmdLine --plugin "validate/DQC|transforms/SEC" -v --xule-filing-list infiles.json --logFile log.xml -v --xule-debug
python3.5 compare.py --compare-file report.txt --test-files log.xml --expected-results $EXFILES 
