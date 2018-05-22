# XBRL US Data Quality Committee Rules

**This Data Quality Committee (DQC) repository contains:**

* Final rules that the XBRL US Data Quality Committee approved for public release
* Draft rules that the XBRL US Data Quality Committee approved to expose for public comment
* Python-based reference implementation of the rules, using Arelle as an XBRL processor
* Unit tests for the reference implementation
* Test suite documentation

## About the DQC Arelle plugin (v5 and later)

The DQC rules are run using an Arelle plugin written in python-based syntax (called xule) that requires the [Arelle XBRL processor](http://arelle.org/download/) on a local computer or server. The DQC Arelle plugin reads a specified ruleset and the assertions defined in the ruleset are evaluated against an XBRL instance, a taxonomy or an extension taxonomy, creating validation messages.

The ruleset is comprised of compiled rule files representing rule submission forms that define the rules in a human readable syntax. Both the compiled rule files and the human readable rule submission forms are included in the distribution.

#### On this page: [Deploying the DQC Arelle Plugin](#deploying) || [Usage and Results - DQC Rules with Arelle](#using) || [Change Management](#versioning) || [License and Patent](#licensing)

## <a name="deploying"></a>Deploying the DQC Arelle Plugin
### Windows/Mac/Linux Application Install
* Download the latest version of [Arelle](http://arelle.org/download/) to your environment and install. 
* Download the latest release of the [DQC plugin (v5.1 or later)](https://github.com/DataQualityCommittee/dqc_us_rules/releases) 
* Extract the archive and copy the "xule" folder and its contents from the archive to the plugin directory of Arelle in your environment. In a Windows environment, this would be located on a path similar to C:\Program Files\Arelle\plugin; on a Mac, the location would be at /Applications/Arelle.app/Contents/MacOS/plugin.
* Copy the "aniso8601" to the root of the Arelle install in your environment. In a Windows environment, this would be located on a path similar to C:\Program FIles\Arelle; on a Mac, the location would be at /Applications/Arelle.app/Contents/MacOS/.

### Source Install
* Download the latest version of [Arelle](http://arelle.org/download/) to your environment and install. 
* Install the following modules to python:
  * isodate
  * aniso8601
  * numpy
  * \*regex  (If you are using python 3.4)
* Extract the xule.zip file.  Copy the xule folder to the Arelle plugin folder.  The default directory under linux is [arelle_root]/arelle/plugins.

## <a name="using"></a>Usage and Results - DQC Rules with Arelle

*  [from the graphic user interface (GUI)](usage_Arelle_GUI.md) - **version 5.2.0 or later**
*  [from a command prompt](usage_command_prompt.md)
*  [Managing Rulesets](usage_rulesets.md)

### Results
The DQC Arelle plugin produces validation messages using standard Arelle output. In the GUI, results will appear in the bottom window as the filing is processed and can be exported to text for review. From a command prompt, the option `--logFile` specifies the output location of the file. The format of the output is specified by the extension of the file. For example `--logFile DQC-output.`**`xml`**` will create an xml formatted file whereas `--logFile DQC-output.json will create a json formatted file. **Output to a file is appended** to an existing file - the existing file is not overwritten. An example of an XML output is shown below:

```
<entry code="DQC.US.0001.75" level="error">
<message severity="error" cid="4508053008" filing_url="https://www.sec.gov/Archives/edgar/data/1606698/000109690617000244/0001096906-17-000244-xbrl.zip/alpine-20161231.xml">[DQC.US.0001.75] The concept SharesIssued with a value of 21,474,481 is dimensionally qualified with the StatementEquityComponentsAxis and the base taxonomy member CommonClassAMember. Only extension members and the elements defined as children of this axis in the US GAAP taxonomy should be used with the axis StatementEquityComponentsAxis.
The properties of the fact for SharesIssued are:
Period: 2016-12-31
Dimensions: us-gaap:StatementEquityComponentsAxis=us-gaap:CommonClassAMember
Unit: shares

Rule Element Id:75
Rule Version: 2.0 'https://www.sec.gov/Archives/edgar/data/1606698/000109690617000244/0001096906-17-000244-xbrl.zip/alpine-20161231.xml’, 320</message>
<ref href="('https://www.sec.gov/Archives/edgar/data/1606698/000109690617000244/0001096906-17-000244-xbrl.zip/alpine-20161231.xml#element(/1/317)', 320)"/></entry>
```

In the XML example above, **the message portion starts with *[DQC.US.0001.75]* and ends with the instance filename and line number at the end of the message**. 

The message portion of the log file output can be controlled by using the `--logFormat` option. The default format is specified as the following:

`"[%(messageCode)s] %(message)s - %(file)s"`

To *exclude the rule number, filename and line number from the message*, use the command prompt `--logFormat  "%(message)s"`.

## <a name="versioning"></a>Change Management

The rule definition index is [here](docs/README.md) with links to the human-readable versions and status of each Data Quality Committee rule.

The dqc_us_rules library follows a standard semantic versioning system of MAJOR.MINOR.FIX format. Major releases are specified when a new set of rules have been approved, coded, and accepted by the DQC after a public comment period.

The MAJOR version specified by each individual rule is the most-recent release version in which the rule was altered. For example, a rule being marked as v2.0.0 would have last been functionally modified during the 2.0.0 release of the DQC library. See [summary of rules](/docs/README.md) for current rule version detail (which is [also found in each rule's code](https://github.com/DataQualityCommittee/dqc_us_rules/search?q=_RULE_VERSION)).

Similarly, the entire set of rules is versioned. MAJOR release is specified at the beginning of each public comment period, suffixed with Release Candidate subversions (RC) to denote revisions prior to the approved release.

### Proposed Changes

We actively accept, and encourage, pull requests for code changes. A list of the requirements for a pull request follows, and the request will be reviewed by the technical leads of the project. If the request is accepted it will be merged into the appropriate branch. Some requests may require Committee approval which may take longer to implement. If the request is found to be missing parts or is otherwise incomplete, comments will be noted regarding the missing or incomplete parts.

### Development of Rules that are "Ready for Coding":

When new rules that have been approved for coding are released by the DQC, the rules will be developed on a branch named `next_q#_YY` where the `#` is the quarter, and the `YY` is replaced by the current year. All new coding for the proposed rules will target this branch on the root DataQualityCommittee fork. Periodically, this branch will be tagged <!--and released on the global pypi index -->as a release candidate (RC). Once final approval for the rules is complete, the RC versions of the library will be removed from the index, the next branch wil be merged into master, and a new major version of the library will be released<!-- on the [global pypi index](https://pypi.python.org/simple/dqc-us-rules/)-->.
### Requirements for a Pull Request (PR):

  - Branch off master, develop on your independent fork, PR back to master or other appropriate branch on the root fork.
  - Your code should pass [flake8](https://flake8.readthedocs.org/en/latest/).
  - Unit test coverage is required or an explanation for why the change is already covered or not coverable.
  - Good [Docstrings](https://github.com/Workiva/styleguide/blob/master/python/style.rst) are required.
  - Good [commit messages](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html) are required.
  - The pull request must go through the review process described below.

### Pull Request Review Process:

  - Each pull request must have at least one `+1` comment from another community member.
  - For code changes, you must have a second `+1` comment from a second community member.
  - The request will need to go through the Quality Assurance process defined below and receive a `+10` comment. This can be from any other community member, including one of the reviewers.
  - At this point, the request can be submitted to one of the project maintainers to be merged.

### Quality Assurance (QA) of a Pull Request:
  - Verify that the code passes flake8 on both the code and tests.
  - Verify that the code passes unit tests.
  - Verify that tests were added or updated to reflect the changes made. If tests were not added, check for a reasoning in the pull request to justify the absence.
  - This template contains all the steps, and can be used as a step-by-step guide.

#### QA Steps:
- Manual testing: <Enter Manual testing notes here.>
- Flake8 on dqc_us_rules: <Paste output of flake8 on the dqc_us_rules directory here.>
- Flake8 on tests: <Paste output of flake8 on the tests directory here.>
- Nosetest result: <Paste output of nose tests here.>
#### Result: <Put result here.>

The result will be any of a few things. For example a +10 for passing, or just a comment like "sent back for rework", or whatever else is needed to be done before another pass at QA.

## <a name="licensing"></a>License and Patent

See [License](https://xbrl.us/dqc-license) for license information.  
See [Patent Notice](https://xbrl.us/dqc-patent) for patent infringement notice.

Copyright 2015 - 2018 XBRL US, Inc. All rights reserved.