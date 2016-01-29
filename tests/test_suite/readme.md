# Test Suite

## Overview

This suite contains a number of individual XBRL filings which represent pass and fail cases for each of the rules published by the Data Quality Committee.

A pass case specifies an XBRL instance document for a given rule that will pass the rule without raising any DQC error.

A fail case is expected to raise the error condition of the  rule and return the specified error message (or equivalent) to the user.

A user can take a given test case XBRL file and run it in a DQC rules-aware XBRL processor and compare the result against the expected result.

## Test Suite Contents

The test suite includes the following:

### Excel Spreadsheet

An excel spreadsheet listing the rules and related test cases and whether a pass or fail case is expected. 

The spreadsheet has the following columns:

1. Rule_Element_ID:  Unique identifier of the element(s) that is tested within a rule

2. Rule_ID:  DQC rule number, a unique identifier of the code that is used to process a rule.  For example the test of negative values will only have one rule-ID (i.e. DQC_0015) but will have multiple Rule_Element_ID’s

3. Rule_Description: Short description of what the rule is testing

4. Primary_Element: The primary element is provided to give the reader an idea of the element that is being tested.  If more than one element is tested in a rule, such as comparing the values of two elements, only one of the elements is entered into this field.

5. TestCase: Test case identifier.  There may be multiple test case variations associated with a given rule. The identifier corresponds to the folder containing the test case.

6. t=error: If a test case defines a pass condition this will have a value of false.  If the test case returns an error condition this field will have a value of true.  

7. Test_Case_Description: Describes what the test case is testing for.

In addition to the Excel spreadsheet, there are a number of directories that contain the individual test cases. To open a test case the user should open the xml instance file in the folder that is not a linkbase.

A listing of the entry points is in included in the excel spreadsheet. To open these files the user will need to use a standard XBRL processor.

### Variations Files

A variation file specifies the test case variations for a rule. The suite contains a separate folder for every rule.  Within this folder (DQC_XXXX)  is the variation file and the associated test case variations.  There is at least one pass case and one fail case per rule. The variation file documents the entry point (loadable XBRL instance document) of each test case variation. The variation file also includes information about the expected results.

The variation file includes the following information.

1. Rule Number (i.e DQC_0036.1)

2. Description of the Rule

3. Rule Message. This is the message template from the "Rule Submission Form" which shows the format for any error messages returned to the user and the parameters of the detected error to return.

4. Name of the test case

5. Description of the test case

6. Location of the test case for both the schema and the instance.  These are contained in the <data> element. Each test case represents a single variation corresponding to the single instance, which is identified with the attribute readMeFirst="true” in the <instance> element.

7. Results for the test case.  This contains the following:

    1. error code

    2. error severity

    3. count of errors

    4. element impacted

    5. value of the fact impacted (If applicable)

    6. period of the fact (start date and end date)

    7. associated dimensions

    8. error message

    9. list of any blocked error codes for contrived testing circumstances which would raise other error codes in performing the indicated error check.

### Index File

Included in the directory is an index file listing the location of the variation file.  The variation file can be read to determine which test cases to run with for a rule.

### Test Cases

Each test case is contained in a directory called CASE_xxx. Each file contains  a set of XBRL files that represent an individual test case. These test cases are XBRL 2.1 valid.

## Run the Test Cases using Arelle

To run the test cases using Arelle (current version):

* Copy the zip file onto a machine that has arelle installed.

* Unzip the files into the directory {PATH TO TESTCASE}/DQC_Testcases

* Ln -s the plugin (src subdirectory) to arelle's plugin/validate subdirectory/DQC

* Here is a sample  bash file "runDQCTests.sh" for Mac/Linux.

```
#!/bin/bash
TESTCASESROOT={PATH TO TESTCASE}/DQC_Testcases"
OUTPUTLOGFILE={PATH TO WHERE OUTPUT SHOULD GO}/DQC-log.txt
OUTPUTERRFILE={PATH TO WHERE OUTPUT SHOULD GO}/DQC-err.txt
OUTPUTCSVFILE={PATH TO WHERE OUTPUT SHOULD GO}/DQC-report.csv
TESTCASESINDEXFILE="$TESTCASESROOT/index.xml"
ARELLEDIR={PATH TO WHERE ARELLE IS}
PYTHONPATH=$ARELLEDIR

rm $OUTPUTLOGFILE $OUTPUTERRFILE

python3.4 -m arelle.CntlrCmdLine --file "$TESTCASESINDEXFILE" --validate --plugins '{PATH TO DQC PLUGIN}|logging/dqcParameters.py' --disclosureSystem efm-pragmatic --logCodeFilter '(?!EFM)' --csvTestReport "$OUTPUTCSVFILE"  --logFile "$OUTPUTLOGFILE" 2>  "$OUTPUTERRFILE"
```

* Run the bash file nohup scripts/runDQCTests.sh > log/nohup.out &

* On Windows, if the binary distribution is installed, to run as above, modifying for your installation locations (test-suite-index-file for where you installed the test suite, dqc-plugin-dir for where you installed the src dir of DQC distribution, and output file locations:

"c:\program files\arelle\arelleCmdLine" --file "test-suite-index-file" --validate --plugins "dqc-plugin-dir|logging\dqcParameters.py" --disclosureSystem efm-pragmatic --logCodeFilter "(?!EFM)"

 --csvTestReport "output-csv-file"  --logFile "output-log-file" 2>  "output-err-file"

Note that this could take several hours to run.  The OUTPUTLOGFILE can be inspected to show progress (such as with the linux "tail" command).  (You can shorten the run to a few minutes for testing purposes for all rules other than 0015, by temporarily commenting out rule 0015 in the test suite index file.)

Review the DQC-report.csv file to see the results of the test cases against the expected result.  This file is written at completion of all of the test suite's processing.


© Copyright 2015 - 2016, XBRL US Inc. All rights reserved.   
See [License](../../License.md) for license information.  
See [Patent Notice](../../PatentNotice.md) for patent infringement notice.
