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

### Requirements

* Python 3.x (3.2 or greater is preferred)
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

### Requirements for a Pull Request(PR):

  - Branch off master, develop on your independent fork, PR back to master or other appropriate branch on the root fork.
  - Your code should pass [flake8](https://flake8.readthedocs.org/en/latest/).
  - Unit test coverage is required or an explanation for why the change is already covered or not coverable.
  - Good [Docstrings](https://github.com/Workiva/styleguide/blob/master/PYTHON.rst#docstrings) are required.
  - Good [commit messages](http://tbaggery.com/2008/04/19/a-note-about-git-commit-messages.html) are required.
  - The pull request must have at least one `+1` from another community member.
  - There must be no unaddressed comments.
  - PR text must be in the specified format:
    ```
    #### Changes:

    - Change_one with reasoning
    - Change_two with reasoning

    Please review: @hefischer  @andrewperkins-wf
    ```

## License

See [License](License.md) for license information.  
See [Patent Notice](PatentNotice.md) for patent infringement notice.

Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
