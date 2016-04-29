# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import os
from .util import messages, neg_num
from .util import facts as facts_util

_CODE_NAME = 'DQC.US.0015'
_RULE_VERSION = '1.0'
_DEFAULT_CONCEPTS_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0015',
    'dqc_15_concepts.csv'
)
_DEFAULT_EXCLUSIONS_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0015',
    'dqc_15_exclusion_rules.csv'
)


def run_negative_numbers(val):
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
    blacklist_dict = neg_num.concept_map_from_csv(_DEFAULT_CONCEPTS_FILE)
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


def filter_negative_number_facts(val, blacklist_concepts):
    """
    Check the numeric negative value facts in the provided ModelXBRL instance
    against the rule dictionary, and return those which meet the conditions of
    the black list and aren't excluded.

    :param val: val whose modelXbrl provides the facts to check
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param blacklist_concepts: An iterable of the blacklist concepts we should
        be testing against.
    :type blacklist_concepts: list [str]
    :return: Return list of the facts falling into the blacklist.
    :rtype: list [:class:'~arelle.ModelInstanceObject.ModelFact']
    """
    blacklist_exclusion_rules = neg_num.get_rules_from_csv(_DEFAULT_EXCLUSIONS_FILE)
    bad_blacklist = []

    numeric_facts = facts_util.grab_numeric_facts(list(val.modelXbrl.facts))
    # other filters before running negative numbers check
    # numeric_facts has already checked if fact.value can be made into a number
    facts_to_check = [
        f for f in numeric_facts if float(f.value) < 0 and
        f.concept.type is not None and
        # facts with numerical values less than 0 and contexts and
        f.context is not None and
        # check xsd type of the concept
        f.isNumeric
    ]

    # identify facts which should be reported as included in the list
    for fact in facts_to_check:
        if neg_num.check_rules(fact, blacklist_exclusion_rules):
            continue  # cannot be black
        if ((fact.qname.localName in blacklist_concepts and
             fact.qname.namespaceURI in
             val.disclosureSystem.standardTaxonomiesDict)):
            bad_blacklist.append(fact)

    return bad_blacklist


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': (
        'Checks all of the specified types and concepts for their '
        'date ranges to verify the ranges are within expected '
        'parameters for the fiscal periods'
    ),
    # Mount points
    'Validate.XBRL.Finally': run_negative_numbers,
}
