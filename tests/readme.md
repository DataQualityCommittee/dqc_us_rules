# Test Suite

## Overview

This suite contains a number of individual XBRL filings which represent pass and fail cases for each of the rules published by the Data Quality Committee.

A pass case specifies an XBRL instance document for a given rule that will pass the rule without raising any DQC error.

A fail case is expected to raise the error condition of the  rule and return the specified error message (or equivalent) to the user.

A user can take a given test case XBRL file and run it in a DQC rules-aware XBRL processor and compare the result against the expected result.

#### The test suite includes URLs to instance files (xml) listed in the "matrix" section of the [.travis.yml](/.travis.yml) and synced with the [secvalidationtests.json](secvalidationtests.json) (used by GitHub Actions) for this branch or release. 

#### Sample JSON test case structure for [GitHub Actions workflow](/.github/workflows/compileandvalidatedqc.yml):

[
  {
    "name": "V30",
    "infiles": [
      {
        "file": "http://www.sec.gov/Archives/edgar/data/889609/000168316826001856/cps_i10k-123125.htm",
        "xule_run_only": "DQC.US.0234.10930"
      }
    ],
    "exfiles": "./tests/output/DQC.US.0234.10930_CPSS-US-2026.xml
  }
]

For each DQC Release, the workflow compiles ruleset .zip files and runs all test cases listed for the current branch-named version. 

[The workflow validation process](/.github/workflows/compileandvalidatedqc.yml#L821): 

  1.  runs xule with the corresponding ruleset.zip for a specified rule (or rules) for the instance file
  2.  produces messaging that is captured to a log.xml file
  3.  runs a corresponding log from the release's [tests/output](./output/) folder with expected data
  4.  uses the [compare.py](/compare.py) routine to confirm both files produce identcal results
  5.  generates a table of discrepancies if any exist.  

As needed, the .travis.yml process supplements the GitHub workflow (confirming processing or testing build and/or test case variations).

© Copyright 2015 - 2026, XBRL US, Inc. All rights reserved.   
See [License](https://xbrl.us/dqc-license) for license information.  
See [Patent Notice](https://xbrl.us/dqc-patent) for patent infringement notice.
