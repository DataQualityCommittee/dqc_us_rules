#!/bin/bash
set -x
$ARELLE_DIR=$(which arellecmdline)
echo "Arelle Dir"
echo $ARELLE_DIR
echo $INFILES > infiles.json
sed -i "s|https://github.com/DataQualityCommittee/dqc_us_rules/.*/dqc_us_rules/|dqc_us_rules/|" $CURDIR/plugin/xule/rulesetMap.json
sed -i "s|\?raw=true||" $CURDIR/plugin/xule/rulesetMap.json
cp -r $CURDIR/plugin/xule $HOME/virtualenv/$TRAVIS_PYTHON_VERSION/src/arelle/arelle/plugin/
cp $CURDIR/plugin/validate/DQC.py $HOME/virtualenv/$TRAVIS_PYTHON_VERSION/src/arelle/arelle/plugin/validate/
python3.5 -m arelle.CntlrCmdLine --plugin "validate/DQC|transforms/SEC" -v --xule-filing-list infiles.json --logFile log.xml -v --xule-debug
python3.5 compare.py --compare-file report.txt --test-files log.xml --expected-results $EXFILES 
