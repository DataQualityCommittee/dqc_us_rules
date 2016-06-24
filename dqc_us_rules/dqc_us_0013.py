# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import os
import collections

from .util import facts, messages, neg_num


_CODE_NAME = 'DQC.US.0013'
_RULE_VERSION = '2.0.0'
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

# This is setup as a list of tuples.  The first item is the concept to check
# for existence of, the second is a list of concept(s) to sum and check if
# they are greater than zero.
_PRE_CFG = [
    (
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest',  # noqa
        [
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'  # noqa
        ]
    ),
    (
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments',  # noqa
        [
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesMinorityInterestAndIncomeLossFromEquityMethodInvestments',  # noqa
            'IncomeLossFromEquityMethodInvestments'
        ]
    ),
    (
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic',
        [
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic',
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign',
            'IncomeLossFromEquityMethodInvestments'
        ]
    ),
    (
        'IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign',
        [
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesDomestic',
            'IncomeLossFromContinuingOperationsBeforeIncomeTaxesForeign',
            'IncomeLossFromEquityMethodInvestments'
        ]
    )
]

_PRECONDITION_ELEMENTS = collections.OrderedDict(_PRE_CFG)


def run_negative_values_with_dependence(val, *args, **kwargs):
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
    numeric_facts = facts.grab_numeric_facts(list(val.modelXbrl.facts))
    # Checks if the precondition concept exists and only proceeds with check
    # if true and if the fact context matches the context of the
    # precondition fact
    precondition_met, precondition_contexts = dqc_13_precondition_check(val)
    # precondition_contexts = dqc_13_precondition_check(val)

    # other filters before running negative numbers check
    # numeric_facts has already checked if fact.value can be made into
    # a number
    facts_to_check = [
        fact for fact in numeric_facts
        # facts with numerical values less than 0
        if fact.xValue < 0 and
        fact.concept.type is not None and
        # and the precondition value is greater than zero
        precondition_met and
        # and the fact context matches the context of the precondition fact
        fact.context in precondition_contexts
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
    :return: True or False depending on whether the precondition value is
        greater than zero or not. Additionally, it also returns the list of
        context(s) of the precondition fact(s).
    :rtype: bool, :class:'~arelle.ModelInstanceObject.ModelContext'

    """
    facts_list = list(val.modelXbrl.facts)
    precondition_contexts = []
    value = 0
    for fact in facts_list:
        print('NAME = {}'.format(fact.concept.qname.localName))
        value = 0
        for precondition, pre_checks in _PRECONDITION_ELEMENTS.items():
            if fact.concept.qname.localName == precondition:
                precondition_contexts.append(fact.context)
                value = value + fact.xValue
                print('FIRST TOTAL = {}'.format(value))
            for element in pre_checks:
                if fact.concept.qname.localName == element:
                    precondition_contexts.append(fact.context)
                    value = value + fact.xValue
    print('FINAL TOTAL = {}'.format(value))
    if value > 0:
        return True, precondition_contexts
    else:
        return False, precondition_contexts


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': (),
    # Mount points
    'Validate.XBRL.Finally': run_negative_values_with_dependence,
}
