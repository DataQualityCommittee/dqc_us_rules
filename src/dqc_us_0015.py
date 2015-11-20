# (c) Copyright 2015, XBRL US Inc, All rights reserved   
# See license.md for license information.  
# See PatentNotice.md for patent infringement notice.
import csv
import os
from .util import facts, messages

_CODE_NAME = 'DQC.US.0015'
_RULE_VERSION = '1.0'
_DEFAULT_CONCEPTS_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'DQC_US_0015', 'dqc_15_concepts.csv')
_DEFAULT_EXCLUSIONS_FILE = os.path.join(os.path.dirname(__file__), 'resources', 'DQC_US_0015', 'dqc_15_exclusion_rules.csv')


def run_negative_numbers(val):
    """
    Run the list of facts against our negative number checks and add errors for the hits in the various lists.

    :param val: The validation object which carries the validation information, including the ModelXBRL
    :side effect: Fire errors for facts matching the blacklist.
    """
    # filter down to numeric facts
    blacklist_dict = concept_map_from_csv()
    blacklist_facts = filter_negative_number_facts(val, blacklist_dict.keys())
    for fact in blacklist_facts:
        index_key = blacklist_dict[fact.qname.localName]
        val.modelXbrl.error('{base_key}.{extension_key}'.format(base_key=_CODE_NAME, extension_key=index_key),
                            messages.get_message(_CODE_NAME, str(index_key)), concept=fact.concept.label(), modelObject=fact,
                            ruleVersion=_RULE_VERSION)


def filter_negative_number_facts(val, blacklist_concepts):
    """
    Check the numeric negative value facts in the provided ModelXBRL instance against the rule dictionary,
    and return those which meet the conditions of the black list and aren't excluded.

    :param modelXbrl: (ModelXBRL) The arelle ModelXBRL instance for the document being validated.
    :param blacklist_concepts: An iterable of the blacklist concepts we should be testing against.
    :return: list Return list of the facts falling into the blacklist.
    """
    blacklist_exclusion_rules = get_rules_from_csv()
    bad_blacklist = []

    numeric_facts = grab_numeric_facts(list(val.modelXbrl.facts))
    # other filters before running negative numbers check
    facts_to_check = [f for f in numeric_facts if float(f.value) < 0  # numeric_facts has already checked if fact.value can be made into a number
                      and f.concept.type is not None
                      and f.context is not None  # facts with numerical values less than 0 and contexts
                      and f.isNumeric]  # check xsd type of the concept

    # identify facts which should be reported as included in the list
    for fact in facts_to_check:
        if check_rules(fact, blacklist_exclusion_rules):
            continue  # cannot be black
        if fact.qname.localName in blacklist_concepts and fact.qname.namespaceURI in val.disclosureSystem.standardTaxonomiesDict:
            bad_blacklist.append(fact)

    return bad_blacklist


def grab_numeric_facts(facts_list):
    '''
    Given a list of facts, return
    those facts whose values are
    numeric
    '''
    numeric_facts = []
    for fact in facts_list:
        try:
            float(fact.value)
            numeric_facts.append(fact)
        except ValueError:
            continue
    return numeric_facts


def check_rules(fact, rule_dicts):
    for rule_dict in rule_dicts:
        if check_rule(fact, rule_dict):
            return True
    return False


def check_rule(fact, rule_dict):
    """
    Check if the input fact meets the conditions of the passed in rule_dict.

    :param fact: (ModelFact) An arelle ModelFact instance.
    :param rule_dict: (dictionary) A rule from the rule dict. E.g. a return value of `_parse_row`.
    :returns: (boolean) True if the fact matched the rule else False.
    """
    fact_matches = False
    artifacts = get_artifact_lists(fact, rule_dict)
    for fact_artifact in artifacts:
        if rule_dict['relation'] == 'Contains':
            fact_matches = contains(fact_artifact, rule_dict['item_check'])
        elif rule_dict['relation'] == 'Contains_insensitive':
            fact_matches = contains_insensitive(fact_artifact, rule_dict['item_check'])
        elif rule_dict['relation'] == 'Equals':
            fact_matches = equals(fact_artifact, rule_dict['item_check'])
        elif rule_dict['relation'] == 'Has_member':
            fact_matches = equals(fact_artifact, rule_dict['item_check'].split('|')[1])
        if fact_matches:
            break  # if fact matches rule condition escape loop, otherwise continue checking

    if rule_dict['negation'] == 'Not':
        fact_matches = not fact_matches

    if rule_dict['additional_conditions'] is None:
        return fact_matches
    else:
        return (fact_matches and check_rule(fact, rule_dict['additional_conditions']))

#====================================================Relationship checks =============================================================


def contains(fact_part, dict_check):
    """
    Check if the fact_part contains the dict_check item.

    :param fact_part: (ModelFact) An arelle model object value pulled off of the current ModelFact being tested.
    :param dict_check: (dictionary) The value from the current rule dict to be compared against.
    :returns: (boolean) True if the dict_check is contained in fact_part else False.
    """
    return dict_check in str(fact_part)


def contains_insensitive(fact_part, dict_check):
    """
    Check if the fact_part contains the dict_check item, ignoring case.

    :param fact_part: (ModelFact) An arelle model object value pulled off of the current ModelFact being tested.
    :param dict_check: (dictionary) The value from the current rule dict to be compared against.
    :returns: (boolean) True if the dict_check is contained in fact_part else False. (ignoring case)
    """
    return dict_check.lower() in str(fact_part).lower()


def equals(fact_part, dict_check):
    """
    Check if the fact_part equals the dict_check item.

    :param fact_part: (str/number) A string or number representing some aspect of a fact.
    :param dict_check: (str) The value from the current rule dict to be compared against.
    :returns: (boolean) True if dict_check == fact_part or if they are numbers and are equal, else False
    """
    if dict_check == str(fact_part):
        return True
    try:
        coerced_dict_value = float(dict_check)
        return coerced_dict_value == fact_part
    except:
        return False


#====================================================Find Artifacts =============================================================


def get_artifact_lists(fact, rule_dict):
    """
    Given a ModelFact instance and an "artifact_type" key derived from the negative_numbers.csv file,
    lookup the corresponding field or object off of the given ModelFact and return its value.

    :param fact: (ModelFact) An arelle ModelFact instance.
    :param rule_dict: (dict) A dictionary with the rule information
    :returns: An iterable of the arelle model object values pulled of the ModelFact corresponding to the passed in artifact_type.
    """
    artifacts = []
    artifact_type = rule_dict['artifact']

    if artifact_type == "Member":
        artifacts = facts.member_qnames(fact)
    if artifact_type == "Axis":
        if '|' in rule_dict['item_check']:
            artifacts = facts.member_qnames(fact, axis_filter=rule_dict['item_check'].split('|')[0])
        else:
            artifacts = facts.axis_qnames(fact)

    return artifacts

#====================================================Deal with CSV =============================================================


def concept_map_from_csv():
    """
    Returns a map of {qname: id} of the concepts to test for the blacklist

    :returns: A map of {qname: id}.
    """
    with open(_DEFAULT_CONCEPTS_FILE, 'rt') as f:
        reader = csv.reader(f)
        return {row[1]: row[0] for row in reader}


def get_rules_from_csv():
    """
    Return a list of rules for blacklist exclusions

    :returns: a list representing the data from the negative_numbers.csv file.
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
    Recursively move through a CSV row (ignoring the list inclusion values), slicing off the four relevant indexes each time.

    :param row: ([str, ..., str]) A list of strings, representing a row from the negative_numbers.csv file, with the first value removed
    :returns: (dictionary) A dictionary representing the data from the CSV row.
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
    'description': '''Checks all of the specified types and concepts for their date ranges to verify the ranges are within expected paramters for the fiscal periods''',
    #Mount points
    'Validate.XBRL.Finally': run_negative_numbers,
}
