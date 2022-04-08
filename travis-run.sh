#!/bin/bash
set -x
svn export https://github.com/xbrlus/xule/trunk/plugin/xule $CURDIR/plugin/xule
svn export https://github.com/xbrlus/xule/trunk/plugin/validate $CURDIR/plugin/validate
cp -R $CURDIR/plugin/xule $VIRTUAL_ENV/src/arelle/arelle/plugin/xule
cp $CURDIR/plugin/validate/DQC.py $VIRTUAL_ENV/src/arelle/arelle/plugin/validate/DQC.py
echo $INFILES > infiles.json
#cat $CURDIR/rulesetMap.json
sed -i "s|https://github.com/DataQualityCommittee/dqc_us_rules/.*/dqc_us_rules/|$GH_SLUG/raw/$PR_BR/dqc_us_rules/|" $CURDIR/plugin/xule/rulesetMap.json
sed -i "s|\?raw=true||" $CURDIR/plugin/xule/rulesetMap.json
cat $CURDIR/plugin/xule/rulesetMap.json
python3.9 -m arelle.CntlrCmdLine --httpUserAgent "Tauriello david.tauriello@xbrl.us" --plugin "validate/DQC|transforms/SEC" -v --dqc-replace-rule-set-map $CURDIR/plugin/xule/rulesetMap.json --xule-filing-list infiles.json --logFile $CURDIR/log.xml -v --xule-debug
#cat /home/travis/.config/arelle/plugin/xule/rulesetMap.json
python3.9 compare.py --compare-file $CURDIR/report.txt --test-files $CURDIR/log.xml --expected-results $EXFILES --html-file report.html