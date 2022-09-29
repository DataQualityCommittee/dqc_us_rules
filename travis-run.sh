#!/bin/bash
set -x
svn export --quiet https://github.com/xbrlus/xule/trunk/plugin/xule $CURDIR/plugin/xule
svn export --quiet https://github.com/xbrlus/xule/trunk/plugin/validate $CURDIR/plugin/validate
cp -R $CURDIR/plugin/xule $VIRTUAL_ENV/src/arelle-release/arelle/plugin/xule
cp $CURDIR/plugin/validate/DQC.py $VIRTUAL_ENV/src/arelle-release/arelle/plugin/validate/DQC.py
echo $INFILES > infiles.json
sed -i "s|https://github.com/DataQualityCommittee/dqc_us_rules/.*/dqc_us_rules/|$GH_SLUG/raw/$PR_BR/dqc_us_rules/|" $CURDIR/rulesetMap.json
sed -i "s|\?raw=true||" $CURDIR/rulesetMap.json
cat $CURDIR/plugin/xule/rulesetCompatibility.json
python3.9 -m arelle.CntlrCmdLine --httpUserAgent "DQC-Arelle (xbrl.us; dqc@xbrl.us)" --plugin "validate/DQC|transforms/SEC" -v --dqc-replace-rule-set-map $CURDIR/rulesetMap.json --xule-filing-list infiles.json --logFile $CURDIR/log.xml -v --xule-debug
cat /home/travis/.config/arelle/plugin/xule/rulesetMap.json
python3.9 compare.py --compare-file $CURDIR/report.txt --test-files $CURDIR/log.xml --expected-results $EXFILES --html-file report.html