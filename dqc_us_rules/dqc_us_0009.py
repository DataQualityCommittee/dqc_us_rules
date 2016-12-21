# (c) Copyright 2015 - 2017, XBRL US Inc. All rights reserved.
# See https://xbrl.us/dqc-license for license information.
# See https://xbrl.us/dqc-patent for patent infringement notice.
from .util import facts, messages
import csv
import os


_CODE_NAME = 'DQC.US.0009'
_RULE_VERSION = '1.0.0'


def fact_gt_other_fact(val, *args, **kwargs):
    """
    Checks that the various fact pairs that are defined in the configuration
    are of an appropriate relative value (lesser or greater than one or the
    other, as per the config).

    :param val: val to to throw error from
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: No explicit return, but throws an error for things returned by
        _compare_facts
    :rtype: None
    """
    for index, lesser, greater in _read_csv():
        for fact_group in _compare_facts(lesser, greater, val):
            lesser_fact = fact_group[lesser]
            greater_fact = fact_group[greater]
            val.modelXbrl.error(
                '{base_code}.{index_id}'.format(
                    base_code=_CODE_NAME,
                    index_id=index
                ),
                messages.get_message(_CODE_NAME, index),
                modelObject=[lesser_fact, greater_fact],
                lesser_label=lesser_fact.concept.label(),
                greater_label=greater_fact.concept.label(),
                ruleVersion=_RULE_VERSION
            )


def _read_csv():
    """
    Reads in information from dqc_us_config.csv and returns
    it in a tuple

    :return: tuple of info read in from dqc_us_config.csv
    :rtype: tuple (str, str, str)
    """
    path = os.path.join(
        os.path.dirname(__file__),
        'resources/DQC_US_0009/dqc_us_9_config.csv'
    )
    with open(path, 'rt') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            yield row[0], row[1], row[2]


def _compare_facts(lesser, greater, val):
    """
    Compares the facts that are passed in based on the comparison data.
    Returns a list of facts that don't match up, if any.

    :param lesser: A dictionary with a 'lesser' us-gaap concept name
    :type lesser: dict
    :param greater: A dictionary 'greater' us-gaap concept name.
    :type greater: dict
    :param val: The validation information which includes a modelXbrl object.
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: A list of the fact pairs
    :rtype: list [tuple]
    """
    fact_dict = {
        lesser: facts.lookup_gaap_facts(lesser, val.modelXbrl),
        greater: facts.lookup_gaap_facts(greater, val.modelXbrl)
    }
    mapped_fact_groups = facts.prepare_facts_for_calculation(fact_dict)
    results = []
    for group in mapped_fact_groups:
        vals = facts.scale_values([group[greater], group[lesser]])
        greater_val = vals[0]
        lesser_val = vals[1]
        if greater_val < lesser_val:
            results.append(group)
    return results


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': (
        'Checks pairs of facts to ensure '
        'that one is greater than the other.'
    ),
    # Mount points
    'Validate.XBRL.Finally': fact_gt_other_fact,
}
