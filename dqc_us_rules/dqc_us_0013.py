# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import os
import collections

from .util import facts, messages, neg_num


_CODE_NAME = 'DQC.US.0013'
_RULE_VERSION = '1.1'
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

_PRECONDITION_ELEMENTS = collections.OrderedDict([
    (
        (
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxes'
            'ExtraordinaryItemsNoncontrollingInterest'
        ), []),
    (
        (
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinority'
            'InterestAndIncomeLossFromEquityMethodInvestments'
        ),
        ['IncomeLossFromEquityMethodInvestments']
    ),
    (
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic',
        [
            'IncomeLossFromEquityMethodInvestments',
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign'
        ]
    ),
    (
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign',
        [
            'IncomeLossFromEquityMethodInvestments',
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic'
        ]
    )
])


def run_negative_values_with_dependence(val):
    """
    Run the list of facts against our negative number checks and add errors for
    the hits in the various lists.

    :param val: The validation object which carries the validation information,
        including the ModelXBRL
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: No direct return, but throws errors for facts matching the
        blacklist
    :rtype: None
    """
    # filter down to numeric facts
    blacklist_dict = neg_num.concept_map_from_csv(_DEFAULT_CONCEPTS_FILE)
    blacklist_facts = filter_negative_number_with_dependence_facts(
        val, blacklist_dict.keys()
    )
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


def filter_negative_number_with_dependence_facts(val, blacklist_concepts):
    """
    Checks the numeric, negative value facts in the provided ModelXBRL instance
    against the rule dictionary and returns those which meet the conditions of
    the blacklist.

    :param val: val whose modelXbrl provides the facts to check
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param blacklist_concepts: An iterable of the blacklist concepts we should
        be testing against.
    :type blacklist_concepts: list [str]
    :return: Return list of the facts falling into the blacklist.
    :rtype: list [:class:'~arelle.ModelInstanceObject.ModelFact']
    """
    blacklist_exclusion_rules = neg_num.get_rules_from_csv(
        _DEFAULT_EXCLUSIONS_FILE
    )
    bad_blacklist = []
    # Checks if the precondition concept exists and only proceeds with check
    # if true
    if dqc_13_precondition_check(val):
        numeric_facts = facts.grab_numeric_facts(list(val.modelXbrl.facts))
        # other filters before running negative numbers check
        # numeric_facts has already checked if fact.value can be made into
        # a number
        facts_to_check = [
            fact for fact in numeric_facts
            if fact.xValue < 0 and
            fact.concept.type is not None and
            # facts with numerical values less than 0 and contexts and
            fact.context is not None
        ]

        # identify facts which should be reported as included in the list
        for fact in facts_to_check:
            if neg_num.check_rules(fact, blacklist_exclusion_rules):
                continue  # cannot be black
            if fact.qname.localName in blacklist_concepts:
                bad_blacklist.append(fact)

    return bad_blacklist


def dqc_13_precondition_check(val):
    """
    Checks if the precondition fact(s) exist and grabs their values.  Runs
    through an if/else statement of the precondition check and totals the
    values to ensure they are greater than zero.

    :param val: val whose modelXbrl provides the facts to check
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: True or False depending on the precondition check
    :rtype: bool

    """
    facts_list = list(val.modelXbrl.facts)

    for precondition, pre_checks in _PRECONDITION_ELEMENTS.items():
        check, value = facts.precondition_fact_exists(facts_list, precondition)
        if check:
            for element in pre_checks:
                new_check, new_value = facts.precondition_fact_exists(
                    facts_list, element
                )
                value = value + new_value
        if value > 0:
            return True

    return False


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': (),
    # Mount points
    'Validate.XBRL.Finally': run_negative_values_with_dependence,
}
