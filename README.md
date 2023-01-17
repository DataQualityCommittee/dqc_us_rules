# XBRL US Data Quality Committee Rules

**This Data Quality Committee (DQC) repository contains:**

* Final rules that the XBRL US Data Quality Committee approved for public release
* Draft rules that the XBRL US Data Quality Committee approved to expose for public comment
* Archived files in .zip format for approved and public exposure rules that can be installed and invoked as an Arelle plugin 
* Unit tests for the reference implementation
* Test suite documentation

## About the DQC Arelle plugin (v5 and later)

The DQC rules are run using an Arelle plugin written in an XBRL rule syntax called Xule. Xule is processed in a plugin for the [Arelle Open Source XBRL processor](http://arelle.org/pub) on a local computer or server. The DQC Arelle plugin reads a specified ruleset and the assertions defined in the ruleset are evaluated against an XBRL instance, a taxonomy or an extension taxonomy, creating validation messages.

### [Download the latest Xule release and DQC validation plugin](https://github.com/xbrlus/xule/releases/latest)

  - **Read [Deployment and Usage](usage.md) for details on deployment, configuration and usage of the compiled ruleset.zip files.**

The ruleset is comprised of compiled rule files representing rule submission forms that define the rules in a human-readable syntax. Both the compiled rule files and the human-readable rule submission forms are included in the distribution. 

  - **[The ``docs`` subdirectory README](docs/README.md) includes an index of human-readable Data Quality Committee rule submission forms**. The index lists the most-recent major version in which each rule was released or substantively modified. 

## Repository Change Management (versioning)

The dqc_us_rules reference implementation library (and compiled ruleset.zip files) follows a standard semantic versioning system of MAJOR.MINOR.FIX format. Major releases are specified at the beginning of each public comment period, suffixed with Release Candidate subversions (RC), and become the [latest-approved version (x.0.0)](https://github.com/DataQualityCommittee/dqc_us_rules/releases/) when a new set of rules have been approved, coded, and accepted by the DQC after a public comment period. Each release is inclusive of all prior approved rules, and error messages include this detail [as referenced to the corresponding taxonomy's constant.xule or constant-IFRS.xule](https://github.com/DataQualityCommittee/dqc_us_rules/search?q=constant+%24ruleVersion)).

### Proposed Changes

We actively accept, and encourage, pull requests for code changes. A list of the requirements for a pull request follows, and the request will be reviewed by the technical leads of the project. If the request is accepted it will be merged into the appropriate branch. Some requests may require Committee approval which may take longer to implement. If the request is found to be missing parts or is otherwise incomplete, comments will be noted regarding the missing or incomplete parts.

### Development of Rules that are "Ready for Coding":

When new rules that have been approved for coding are released by the DQC, the rules will be developed on a branch corresponding to the expected release version. All new coding for the proposed rules will target this branch on the root DataQualityCommittee dqc_us_rules repository. Periodically, this branch will be tagged and incremented as a release candidate (RC). Once final approval for the rules is complete, the RC versions of the library will be removed from the index, the next branch wil be merged into master, and a new major version of the library will be released.

### Requirements for a Pull Request (PR):

  - Branch off master, develop on your independent fork, PR back to master or other appropriate branch on the root fork.
  - Your code should pass [flake8](https://flake8.readthedocs.org/en/latest/).
  - Unit test coverage is required or an explanation for why the change is already covered or not coverable.
  - Good [Docstrings](https://github.com/Workiva/styleguide/blob/master/python/style.md) are required.
  - Good [commit messages](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html) are required.
  - External pull requests must go through the review process described below.

### Pull Request Review Process:

  - Each pull request must have at least one `+1` comment from DQC member or XBRL US staff.
  - For code changes, you must have a second `+1` comment from a second  DQC member or XBRL US staff.
  - The request will need to go through the Quality Assurance process defined below and receive a `+10` comment. This can be from another DQC member or XBRL US staff, including one of the reviewers.
  - At this point, the request can be submitted to one of the project maintainers to be merged.

## License and Patent

See [License](https://xbrl.us/dqc-license) for license information.  
See [Patent Notice](https://xbrl.us/dqc-patent) for patent infringement notice.

Copyright 2015 - 2023 XBRL US, Inc. All rights reserved.
