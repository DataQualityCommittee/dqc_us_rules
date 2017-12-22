# XBRL US Data Quality Committee Rules

**This Data Quality Committee (DQC) repository contains:**

* Final rules that the XBRL US Data Quality Committee approved for public release
* Draft rules that the XBRL US Data Quality Committee approved to expose for public comment
* Python-based reference implementation of the rules, using Arelle as an XBRL processor
* Unit tests for the reference implementation
* Test suite

## Running the DQC Arelle plugin (v5 and later)

### Overview

The DQC rules are run using an Arelle plugin written in python-based syntax (called xule) that requires the [Arelle XBRL processor](http://arelle.org/download/) on a local computer or server. The DQC Arelle plugin reads a specified ruleset and the assertions defined in the ruleset are evaluated against an XBRL instance, a taxonomy or an extension taxonomy, creating validation messages.

The ruleset is comprised of compiled rule files representing rule submission forms that define the rules in a human readable syntax. Both the compiled rule files and the human readable rule submission forms are included in the distribution.

## Deploying the DQC Arelle Plugin

* Download the latest version of [Arelle](http://arelle.org/download/) to your environment and install. 
* Download the latest release of the [DQC plugin (v5 or later)](https://github.com/DataQualityCommittee/dqc_us_rules/releases) 
* Extract the archive and copy the "xule" folder and its contents from the archive to the plugin directory of Arelle in your environment (In a Windows environment, this would be located on a path similar to C:\Program FIles\Arelle\plugin).
* Copy the "aniso8601" to the root of the Arelle install in your environment (In a Windows environment, this would be located on a path similar to C:\Program FIles\Arelle).
* Confirm the DQC Arelle plugin is installed by running `arelleCmdLine --plugins xule` to return:

`
[info] Activation of plug-in DQC XBRL rule processor (xule) successful, version 1.0. - xule
`

## Configuration and Use of the DQC Arelle Plugin

The DQC ruleset files are part of each [downloaded release archive (v5 or later)](https://github.com/DataQualityCommittee/dqc_us_rules/releases) as .zip files in the folder "dqc_us_rules". Copy the "dqc_us_rules" folder to your environment to run them locally, or reference them from the Internet using this format `https://github.com/DataQualityCommittee/dqc_us_rules/`***raw***`/`**vMajor.Minor.FixRelease**`/dqc_us_rules/dqc-us-`**TaxonomyYear**`-V`**MajorRelease**`-ruleset.zip` when running the plugin from the command line (see below). The extracted files for US GAAP Taxonomies from 2015, 2016 and 2017 are also in the "dqc_us_rules" folder as the reference implementation for the DQC rules.   
 
The minimum parameters that need to be passed are the following:
* **`--plugins xule`** : Loads the DQC plugin.
* **`-f`** : the location of the instance file to be evaluated. This will take a zip file, XML instance or inline XBRL file.
* **`--xule-rule-set`** : the location of the compiled ruleset
* **`--xule-run`** : Instructs the processor to run the rules

A typical command line syntax for Arelle is as follows (including optional parameters defined below:

`
arelleCmdLine --plugins xule -f {instance file or zip file} --xule-rule-set {ruleset file} --xule-run --noCertificateCheck --logFile {log file name}
`

**Examples:**  
`
arelleCmdLine --plugins xule -f https://www.sec.gov/Archives/edgar/data/xxx-20170930.xml  --xule-rule-set dqc-us-2017-V5-ruleset.zip --xule-run --noCertificateCheck --logFile DQC-output.xml
`  
or  
`
arelleCmdLine --plugins xule -f https://www.sec.gov/Archives/edgar/data/xxx-20170930.xml  --xule-rule-set https://github.com/DataQualityCommittee/dqc_us_rules/raw/v5.0.0/dqc_us_rules/dqc-us-2017-V5-ruleset.zip --xule-run --noCertificateCheck --logFile DQC-output.xml
`  

In addition the following optional parameters can be passed:

* **`--logFile`** : Specifies where the output of running the rules should be sent. To get an XML file the file needs to end with .xml. To get a json file it needs to end with .json. If a log file is not specified, output will be displayed in the command window.
* **`--noCertificateCheck`** : This is used to ensure that files from the internet are not rejected if there is no SSL certificate on the machine running the DQC plugin.
* **`--xule-bypass-packages`** : This option will ignore packages included in the ruleset. (See *Managing the Ruleset File* below)  
* **`--packages`** : This option will accept additional taxonomy packages

To get additional options use the option `--help` (eg. `arelleCmdLine --plugins xule --help`)

The DQC plugin options will be displayed at the bottom of the list under the title "Xule Business Rule". All DQC specific options start with `--xule`.

**Every XBRL instance has a specific taxonomy that it uses.** When running the DQC plugin the correct ruleset must be run against the XBRL instance. If the XBRL instance uses the US GAAP 2017 taxonomy then the dqc_us_rules that apply to the 2017 taxonomy must be used. 

There is a separate *dqc_us_rules* file for every *year* and *taxonomy* released. The format of the ruleset file is as follows:

`dqc-{`*`taxonomy`*`}-{`*`year`*`}-{`*`dqc_us_rules version`*`}-ruleset.zip`

For example, the ruleset for the 2017 us-gaap taxonomy for the version 5 release would be called:

`dqc-us-2017-V5-ruleset.zip`

The ruleset for the 2017 ifrs taxonomy for the version 6 release would be called:

`dqc-ifrs-2017-V6-ruleset.zip`

### Results
The DQC Arelle plugin produces validation messages using standard Arelle output. The option `--logFile` specifies the output location of the file. The format of the output is specified by the extension of the file. For example `--logFile DQC-output.`**`xml`**` will create an xml formatted file whereas `--logFile DQC-output.json will create a json formatted file. **Output to a file is appended** to an existing file - the existing file is not overwritten. An example of an XML output is shown below:

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

### Managing the Ruleset File

The ruleset file includes packages with local versions of files used by the DQC plugin. Using these resource files locally allows the plugin to be run without Internet access. These resource files are included by default in the ruleset as XBRL taxonomy packages. To ignore the packages included in the ruleset, use the option ```--xule-bypass-packages```. Using the plugin this way will generally take more time to run, as the plugin will use resources referenced in the dqc_us_rules repository as raw.githubusercontent.com. 

Mnage packages used in the ruleset with the following three options, which require ```--xule-rule-set```:

* `--xule-show-packages`
* `--xule-add-packages`
* `--xule-remove-packages`

All these options also require the --xule-rule-set option to be used.

**Example**
`arelleCmdLine --plugins xule --xule-show-packages --xule-rule-set dqc-us-2017-V5-ruleset.zip```

Will return the following:
```
Packages in rule set:
	dqc_15_concepts.csv and dqc_0011.csv (resources.zip)
```

**Usages and switches**
* **```--xule-add--packages```** followed by a ```|``` separated list of package files will add the packages to the rule set. If a package is already in the rule set it will overwrite it. It will attempt to activate the package in arelle to test that the package is valid.

* **```--xule-remove-packages```** followed by a ```|``` separated list of package file names (this is the zip file name). If a package is not in the rule set, it will report it, but not fail. Any other packages in the list will be removed.

* **```--xule-add--packages```** and **```--xule-remove-packages```** options modify the ruleset file and can only be used on a locally stored ruleset.

The format of the package zip file is based on the XBRL packages specification. It has a single directory in the zip file. Usually, the name of this top level directory is the same as the name of the zip file, but that is not required. Inside the top level directory, there is a directory named "META-INF". Inside the META-INF directory there are two files 'catalog.xml' and "taxonomyPackages.xml".

The **catalog.xml** file contains the remapping. The ```<rewriteURI>``` element in this file defines the map. It can map to a directory or a file. Several ```<rewriteURI>``` elements can used to define multiple mappings. The one in the example is:

```
<catalog xmlns="urn:oasis:names:tc:entity:xmlns:xml:catalog">
	<rewriteURI rewritePrefix="../" uriStartString="https://raw.githubusercontent.com/DataQualityCommittee/dqc_us_rules/master/dqc_us_rules/resources/DQC_US_0015/"/>
</catalog>
```

Note that ```rewritePrefix``` is mapping to the parent directory that the catalog.xml file is in.

Normally taxonomy packages are used to archive (zip) taxonomies and identity taxonomy entry points. Here the taxonomy package mechanism is used to remap csv files, which is out of scope for the taxonomy package spec. However, it does work and using taxonomy package handling built into Arelle. The XBRL spec working group is considering using taxonomy packages for other file types.

### Running the DQC plugin on a Server

#### Server Requirements

* Python 3.5 
* Arelle 1.6 (or greater is preferred)

When running an instance through the DQC Arelle server, a ruleset needs to be defined. However different rulesest may be required depending on the instance provided. Generally, a each taxonomy will have a different rule set associated with it.  For this reason, the user needs to identify the taxonomy used by the instance and then select the appropriate rule set to use. The DQC server version checks the taxonomy version of the instance and selects the appropriate rule set to use.

The server process also pre-caches the rulesets and the associated constants in the rule sets.  This means the server version can process filings significantly faster as constants such as taxonomies do not have to be loaded every time an instant document is processed.

## Rule Versioning

The dqc_us_rules library follows a standard semantic versioning system of MAJOR.MINOR.FIX format. Major releases are specified when a new set of rules have been approved, coded, and accepted by the DQC after a public comment period.

The MAJOR version specified by each individual rule is the most-recent release version in which the rule was altered. For example, a rule being marked as v2.0.0 would have last been functionally modified during the 2.0.0 release of the DQC library. See [summary of rules](/docs/README.md) for current rule version detail (which is [also found in each rule's code](https://github.com/DataQualityCommittee/dqc_us_rules/search?q=_RULE_VERSION)).

Similarly, the entire set of rules is versioned. MAJOR release is specified at the beginning of each public comment period, suffixed with Release Candidate subversions (RC) to denote revisions prior to the approved release.

## Rule Index

The rule definition index is [here](docs/README.md) with links to the human-readable versions and status of each Data Quality Committee rule.

## Proposed Changes

We actively accept, and encourage, pull requests for code changes. A list of the requirements for a pull request follows, and the request will be reviewed by the technical leads of the project. If the request is accepted it will be merged into the appropriate branch. Some requests may require Committee approval which may take longer to implement. If the request is found to be missing parts or is otherwise incomplete, comments will be noted regarding the missing or incomplete parts.

### Development of Rules that are "Ready for Coding":

When new rules that have been approved for coding are released by the DQC, the rules will be developed on a branch named ```next_q#_YY``` where the ```#``` is the quarter, and the ```YY``` is replaced by the current year. All new coding for the proposed rules will target this branch on the root DataQualityCommittee fork. Periodically, this branch will be tagged <!--and released on the global pypi index -->as a release candidate (RC). Once final approval for the rules is complete, the RC versions of the library will be removed from the index, the next branch wil be merged into master, and a new major version of the library will be released<!-- on the [global pypi index](https://pypi.python.org/simple/dqc-us-rules/)-->.
### Requirements for a Pull Request (PR):

  - Branch off master, develop on your independent fork, PR back to master or other appropriate branch on the root fork.
  - Your code should pass [flake8](https://flake8.readthedocs.org/en/latest/).
  - Unit test coverage is required or an explanation for why the change is already covered or not coverable.
  - Good [Docstrings](https://github.com/Workiva/styleguide/blob/master/python/style.rst) are required.
  - Good [commit messages](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html) are required.
  - The pull request must go through the review process described below.

### Pull Request Review Process:

  - Each pull request must have at least one ```+1` comment from another community member.
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

## License

See [License](https://xbrl.us/dqc-license) for license information.  
See [Patent Notice](https://xbrl.us/dqc-patent) for patent infringement notice.

Copyright 2015 - 2018 XBRL US, Inc. All rights reserved.
