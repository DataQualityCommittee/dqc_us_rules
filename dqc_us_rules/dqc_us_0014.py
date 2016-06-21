# (c) Copyright 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import os

from .util import messages, neg_num
from .util import facts as facts_util


_CODE_NAME = 'DQC.US.0014'
_RULE_VERSION = '2.0.0'
_DEFAULT_CONCEPTS_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0014',
    'dqc_14_concepts.csv'
)


def run_negative_numbers_no_dimensions(val, *args, **kwargs):
    """
    Run the list of facts against our negative number check for facts with
    no dimensions and add errors for the hits in the various lists.

    :param val: The validation object which carries the validation information,
        including the ModelXBRL
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: No direct return but throws errors for facts matching
        the blacklist.
    :rtype: None
    """
    blacklist_dict = neg_num.concept_map_from_csv(_DEFAULT_CONCEPTS_FILE)
    blacklist_facts = filter_negative_number_no_dimensions_facts(
        val, blacklist_dict.keys()
    )
    for fact in blacklist_facts:
        index_key = blacklist_dict[fact.qname.localName]
        val.modelXbrl.error(
            '{base_key}.{extension_key}'.format(
                base_key=_CODE_NAME, extension_key=index_key
            ),
            messages.get_message(_CODE_NAME, str(index_key)),
            concept=fact.concept.label(),
            modelObject=fact,
            ruleVersion=_RULE_VERSION
        )


def filter_negative_number_no_dimensions_facts(val, blacklist_concepts):
    """
    Checks the numeric negative value dimensionless facts in the provided
    ModelXBRL instance against the rule dictionary and returns those which
    meet the conditions of the blacklist.

    :param val: The validation object which carries the validation information,
        including the ModelXBRL
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param blacklist_concepts: An iterable of the blacklist concepts we should
        be testing against.
    :type blacklist_concepts: list [str]
    :return: Returns a list of facts that fall in the blacklist
    :rtype: list [:class:'~arelle.ModelInstanceObject.ModelFact']
    """
    bad_blacklist = []

    numeric_facts = facts_util.grab_numeric_facts(list(val.modelXbrl.facts))
    # other filters before running negative numbers check
    # numeric_facts has already checked if fact.value can be made into a number
    facts_to_check = [
        fact for fact in numeric_facts
        if fact.xValue < 0 and
        fact.concept is not None and
        fact.concept.type is not None and
        # facts with numerical values less than 0 (negative) and contexts
        fact.context is not None and
        fact.context.segDimValues is not None and
        # check that the fact does not have dimensions
        len(fact.context.segDimValues) == 0
    ]

    # identify facts which should be reported as included in the list
    for fact in facts_to_check:
        if fact.qname.localName in blacklist_concepts:
            bad_blacklist.append(fact)

    return bad_blacklist


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': (
        'Checks that the values for a given list of elements with no '
        'dimensions are negative'
    ),
    # Mount points
    'Validate.XBRL.Finally': run_negative_numbers_no_dimensions,
}
