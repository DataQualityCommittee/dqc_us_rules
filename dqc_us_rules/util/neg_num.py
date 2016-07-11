import csv
from . import facts


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
            fact_matches = contains_insensitive(
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


def contains_insensitive(fact_part, dict_check):
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
        artifacts = facts.member_qnames(fact)
    if artifact_type == "Axis":
        if '|' in rule_dict['item_check']:
            artifacts = facts.member_qnames(
                fact, axis_filter=rule_dict['item_check'].split('|')[0]
            )
        else:
            artifacts = facts.axis_qnames(fact)

    return artifacts

# =============================Deal with CSV ================================


def concept_map_from_csv(neg_num_file):
    """
    Returns a map of {qname: id} of the concepts to test for the blacklist

    :param neg_num_file: The .csv file containing the list of concepts for
        this rule.
    :type neg_num_file: file
    :return: A map of {qname: id}.
    :rtype: dict
    """
    with open(neg_num_file, 'rt') as f:
        reader = csv.reader(f)
        return {row[1]: row[0] for row in reader}


def get_rules_from_csv(exclusion_file):
    """
    Return a list of rules for blacklist exclusions

    :return: a list representing the data from the negative_numbers.csv file.
    :rtype: list
    """
    blacklist_exclusion_rules = list()
    with open(exclusion_file, 'rt') as f:
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
