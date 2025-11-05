#!/bin/bash
pip show Arelle-release
set -x

# Copy xule files to the appropriate directory
mkdir $CURDIR/temp
git clone --depth=1 --branch $XULE_VERSION --single-branch https://github.com/$XULE_REPO/xule.git $CURDIR/temp/xule
mv $CURDIR/temp/xule/plugin/xule $VIRTUAL_ENV/lib/$PYTHON_VERSION/site-packages/arelle/plugin
mv $CURDIR/temp/xule/plugin/semanticHash.py $VIRTUAL_ENV/lib/$PYTHON_VERSION/site-packages/arelle/plugin
mv $CURDIR/temp/xule/plugin/validate/DQC.py $VIRTUAL_ENV/lib/$PYTHON_VERSION/site-packages/arelle/plugin/validate
rm -fR $CURDIR/temp
mkdir $CURDIR/EDGAR
git clone --quiet --depth=1 --branch $TRANSFORM_VERSION --single-branch https://github.com/Arelle/EDGAR.git $CURDIR/EDGAR
mv $CURDIR/EDGAR $VIRTUAL_ENV/lib/$PYTHON_VERSION/site-packages/arelle/plugin
rm -fR $CURDIR/EDGAR

echo $INFILES > infiles.json
sed -i "s|https://github.com/DataQualityCommittee/dqc_us_rules/.*/dqc_us_rules/|$GH_SLUG/raw/$PR_BR/dqc_us_rules/|" $CURDIR/rulesetMap.json
sed -i "s|\?raw=true||" $CURDIR/rulesetMap.json
cat $CURDIR/plugin/xule/version.json
$PYTHON_VERSION -m arelle.CntlrCmdLine --httpUserAgent "DQC-Arelle (xbrl.us; dqc@xbrl.us)" --plugin "validate/DQC|EDGAR/transform|inlineXbrlDocumentSet" -v --dqc-replace-rule-set-map $CURDIR/rulesetMap.json --xule-filing-list infiles.json --logFile $CURDIR/log.xml -v --xule-debug
cat /home/travis/.config/arelle/plugin/xule/rulesetMap.json
$PYTHON_VERSION compare.py --compare-file $CURDIR/report.txt --test-files $CURDIR/log.xml --expected-results $EXFILES --html-file report.html
