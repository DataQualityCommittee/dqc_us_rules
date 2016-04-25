# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import csv
import os
from .util import facts, messages, neg_num

_CODE_NAME = 'DQC.US.0013'
_RULE_VERSION = '1.0'
_DEFAULT_CONCEPTS_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0013',
    'dqc_13_concepts.csv'
)
# The same exclusion rules used in Rule 15 also apply to this rule
_DEFAULT_EXCLUSIONS_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0015',
    'dqc_15_exclusion_rules.csv'
)


def run_negative_values_with_dependence(val):
    """
    Run the list of facts against our negative number checks and add errors for
    the hits in the various lists.

    :param val: The validation object which carries the validation information,
        including the ModelXBRL
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: Nore direct return, but throws errors for facts matching the
        blacklist
    :rtype: None
    """
    # filter down to numeric facts
    blacklist_dict = neg_num.concept_map_from_csv()
    blacklist_facts = filter_negative_number_facts(val, blacklist_dict.keys())
    for fact in blacklist_facts:
        index_key = blacklist_dict[fact.qname.localName]
        val.modelXbrl.error(
            '{base_key}.{extension_key}'.format(
                base_key=_CODE_NAME, extension_key=index_key
            ),
            messages.get_message(_CODE_NAME, str(index_key)),
            concept=fact.concept.label(), modelObject=fact,
            ruleVersion=_RULE_VERSION
        )


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': (),
    # Mount points
    'Validate.XBRL.Finally': run_negative_values_with_dependence,
}
