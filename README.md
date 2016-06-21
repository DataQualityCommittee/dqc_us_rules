# XBRL US Data Quality Committee Rules

dqc_us_rules is a plugin for Arelle

## dqc_us_rules contains:

* Final rules that the XBRL US Data Quality Committee approved for public release
* Draft rules that the XBRL US Data Quality Committee approved to expose for public comment
* Reference implementation of the rules, using Arelle as an XBRL processor
* Unit tests for the reference implementation
* Test suite

## Deployment

* Deploy with Arelle
* Specify the sec directory as a plugin with Arelle

## Versioning

The dqc_us_rules library follows a standard semantic versioning system of MAJOR.MINOR.FIX format. Major releases are specified when a new batch of rules have been approved, coded, and accepted by the DQC after a public comment period.

The version specified by each individual rule is tied to the last release version which the rule was altered. For example, a rule being marked as v2.0.0 would have last been functionally modified during the 2.0.0 release of the DQC library.

## Requirements

* Python 3.x (3.4 or greater is preferred)
* Git 1.7+
* C compiler toolchain (for LXML)
* libxml2 (also for LXML)
* Arelle

## Development

It is strongly recommended that one uses a python virtual environment, such as [virtualenv](http://www.virtualenv.org/en/latest/), to do development.  To make development and management of virtual environments easier, we recommend checking out [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/).

The rest of this setup will assume you have installed [virtualenv](http://www.virtualenv.org/en/latest/) and [virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/).

### Creating a virtual environment

To create a virtual environment, change your directory to the root of this project, and execute the following command:

    mkvirtualenv dqc -a $PWD -p <path_to_python3>

This will give you a virtual environment that you can then work within by inputting

    workon dqc

any time you need to work in it.

### Installing dependencies

To install the dependencies for development of only the DQC ruleset, you will use [pip](https://pip.pypa.io/en/latest/installing.html) to install the requirements. Install the development requirements using:

    pip install -r requirements-dev.txt

### Running unit tests

To run the unit tests, simply run the included shell script

    ./run-unit-tests.sh

### Running test suite

See documentation in the test suite

## Rule Index

The rule definition index is [here](docs/README.md).

## Proposed Changes

We actively accept, and encourage, pull requests for code changes. A list of the requirements for a pull request follows, and the request will be reviewed by the technical leads of the project. If the request is accepted it will be merged into the appropriate branch. Some requests may require Committee approval which may take longer to implement. If the request is found to be missing parts or is otherwise incomplete, comments will be noted regarding the missing or incomplete parts.

### Development of Rules that are "Ready for Coding":

When new rules that have been approved for coding are released by the DQC, the rules will be developed on a branch named `next_q#_YY` where the `#` is the quarter, and the `YY` is replaced by the current year. All new coding for the proposed rules will target this branch on the root DataQualityCommittee fork. Periodically, this branch will be tagged and released on the global pypi index as a release candidate (RC). Once final approval for the rules is complete, the RC versions of the library will be removed from the index, the next branch wil be merged into master, and a new major version of the library will be released on the [global pypi index](https://pypi.python.org/simple/dqc-us-rules/).

### Requirements for a Pull Request (PR):

  - Branch off master, develop on your independent fork, PR back to master or other appropriate branch on the root fork.
  - Your code should pass [flake8](https://flake8.readthedocs.org/en/latest/).
  - Unit test coverage is required or an explanation for why the change is already covered or not coverable.
  - Good [Docstrings](https://github.com/Workiva/styleguide/blob/master/PYTHON.rst#docstrings) are required.
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
        - Flake8 on dqc_us_rules:
        ```
        <Paste output of flake8 on the dqc_us_rules directory here.>
        ```
        - Flake8 on tests:
        ```
        <Paste output of flake8 on the tests directory here.>
        ```
        - Nosetest result:
        ```
        <Paste output of nose tests here.>
        ```

        #### Result: <Put result here.>

The result will be any of a few things. For example a +10 for passing, or just a comment like "sent back for rework", or whatever else is needed to be done before another pass at QA.

## License

See [License](License.md) for license information.  
See [Patent Notice](PatentNotice.md) for patent infringement notice.

Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
