# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import os
import csv
from .util import messages, neg_num
from .util import facts as facts_util
from arelle.XmlValidate import VALID

_CODE_NAME = 'DQC.US.0015'
_RULE_VERSION = '2.0.0'
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


def run_negative_numbers(val, *args, **kwargs):
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
    blacklist_exclusion_rules = neg_num.get_rules_from_csv(
        _DEFAULT_EXCLUSIONS_FILE
    )
    bad_blacklist = []

    numeric_facts = facts_util.grab_numeric_facts(list(val.modelXbrl.facts))
    # other filters before running negative numbers check
    # numeric_facts has already checked if fact.value can be made into a number
    facts_to_check = [
        f for f in numeric_facts if f.xValid >= VALID and f.xValue < 0 and
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


def check_rules(fact, rule_dicts):
    for rule_dict in rule_dicts:
        if check_rule(fact, rule_dict):
            return True
    return False


def check_rule(fact, rule_dict):
    """
    Check if the input fact meets the conditions of the passed in rule_dict.

    :param fact: An arelle ModelFact instance.
    :type fact: :class:'~arelle.ModelInstanceObject.ModelFact'
    :param rule_dict: A rule from the rule dict.
        E.g. a return value of `_parse_row`.
    :type rule_dict: dict
    :return: True if the fact matched the rule else False.
    :type: bool
    """
    fact_matches = False
    artifacts = get_artifact_lists(fact, rule_dict)
    for fact_artifact in artifacts:
        if rule_dict['relation'] == 'Contains':
            fact_matches = contains(fact_artifact, rule_dict['item_check'])
        elif rule_dict['relation'] == 'Contains_insensitive':
            fact_matches = contains_ignore_case(
                fact_artifact, rule_dict['item_check']
            )
        elif rule_dict['relation'] == 'Equals':
            fact_matches = equals(fact_artifact, rule_dict['item_check'])
        elif rule_dict['relation'] == 'Has_member':
            fact_matches = equals(
                fact_artifact, rule_dict['item_check'].split('|')[1]
            )
        if fact_matches:
            # if fact matches rule condition escape loop,
            # otherwise continue checking
            break

    if rule_dict['negation'] == 'Not':
        fact_matches = not fact_matches

    if rule_dict['additional_conditions'] is None:
        return fact_matches
    else:
        return (
            fact_matches and
            check_rule(fact, rule_dict['additional_conditions'])
        )

# =====================Relationship checks=============================


def contains(fact_part, dict_check):
    """
    Check if the fact_part contains the dict_check item.

    :param fact_part: An arelle model object value pulled off of the current
        ModelFact being tested.
    :type fact_part: :class:'~arelle.InstanceModelObject.ModelFact'
    :param dict_check: Value from the current rule dict to be compared against.
    :type dict_check: dict
    :return: True if the dict_check is contained in fact_part else False.
    :rtype: bool
    """
    return dict_check in str(fact_part)


def contains_ignore_case(fact_part, dict_check):
    """
    Check if the fact_part contains the dict_check item, ignoring case.

    :param fact_part: An arelle model object value pulled off of the current
        ModelFact being tested.
    :type fact_part: :class:'~arelle.InstanceModelObject.ModelFact'
    :param dict_check: Value from the current rule dict to be compared against.
    :type dict_check: dict
    :return: True if the dict_check is contained in fact_part else False.
    :rtype: bool
    """
    return dict_check.lower() in str(fact_part).lower()


def equals(fact_part, dict_check):
    """
    Check if the fact_part equals the dict_check item.

    :param fact_part: A string or number representing some aspect of a fact.
    :type fact_part: str or int
    :param dict_check: Value from the current rule dict to be compared against.
    :type dict_check: str
    :returns: True if dict_check == fact_part or
        if they are numbers and are equal, else False
    :rtype: bool
    """
    if dict_check == str(fact_part):
        return True
    try:
        coerced_dict_value = float(dict_check)
        return coerced_dict_value == fact_part
    except ValueError:
        return False


# =============================Find Artifacts ==============================


def get_artifact_lists(fact, rule_dict):
    """
    Given a ModelFact instance and an "artifact_type" key derived from the
    negative_numbers.csv file, lookup the corresponding field or object off of
    the given ModelFact and return its value.

    :param fact: An arelle ModelFact instance.
    :type fact: :class:'~arelle.InstanceModelFact'
    :param rule_dict: A dictionary with the rule information
    :type rule_dict: dict
    :return: An iterable of the arelle model object values pulled of the
        ModelFact corresponding to the passed in artifact_type.
    :rtype: iterable
    """
    artifacts = []
    artifact_type = rule_dict['artifact']

    if artifact_type == "Member":
        artifacts = facts_util.member_qnames(fact)
    if artifact_type == "Axis":
        if '|' in rule_dict['item_check']:
            artifacts = facts_util.member_qnames(
                fact, axis_filter=rule_dict['item_check'].split('|')[0]
            )
        else:
            artifacts = facts_util.axis_qnames(fact)

    return artifacts

# =============================Deal with CSV ================================


def get_rules_from_csv():
    """
    Return a list of rules for blacklist exclusions

    :return: a list representing the data from the negative_numbers.csv file.
    :rtype: list
    """
    blacklist_exclusion_rules = list()
    with open(_DEFAULT_EXCLUSIONS_FILE, 'rt') as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            rule = _parse_row(row[1:])
            if row[0] == 'BLE':
                blacklist_exclusion_rules.append(rule)
        return blacklist_exclusion_rules


def _parse_row(row):
    """
    Recursively move through a CSV row (ignoring the list inclusion values),
    slicing off the four relevant indexes each time.

    :param row: ([str, ..., str]) A list of strings, representing a row from
    the negative_numbers.csv file, with the first value removed
    :type row: list [str]
    :return: A dictionary representing the data from the CSV row.
    :rtype: dict
    """
    return {
        'artifact': row[0],
        'negation': row[1],
        'relation': row[2],
        'item_check': row[3],
        'additional_conditions': _parse_row(row[4:]) if len(row) > 4 else None
    }


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
