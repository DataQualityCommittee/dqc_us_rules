# Copyright (c) 2015-2016, Workiva Inc.  All rights reserved.
# Copyright (c) 2015-2016, XBRL US Inc.  All rights reserved.
from collections import defaultdict
from arelle import ValidateXbrlCalcs


DEI_NAMESPACE_LIST = [
    'http://xbrl.sec.gov/dei/2014-01-31', 'http://xbrl.sec.gov/dei/2013-01-31',
    'http://xbrl.sec.gov/dei/2012-01-31', 'http://xbrl.sec.gov/dei/2011-01-31',
    'http://xbrl.us/dei/2009-01-31'
]

GAAP_NAMESPACE_LIST = [
    'http://fasb.org/us-gaap/2012-01-31', 'http://fasb.org/us-gaap/2013-01-31',
    'http://fasb.org/us-gaap/2014-01-31', 'http://fasb.org/us-gaap/2015-01-31'
]


class DecimalOverriddenFact(object):
    def __init__(self, fact, decimals_override):
        self.fact = fact
        self.decimals_override = decimals_override

    def get_decimals_override(self):
        return self.decimals_override

    def __getattr__(self, name):
        if name == 'decimals':
            return self.get_decimals_override()
        return getattr(self.fact, name)


def scale_values(facts):
    """
    Accepts a list of facts and returns a list of values from those facts
    re-scaled by the least precise fact's precision Makes no guarantees about
    data type, known types are integers, floats, and Decimals Precision
    attribute is not allowed in EFM 6.5.17, so this assumes decimals-use only.

    :param facts: list of facts to scale
    :type facts: list [:class:'~arelle.ModelInstanceObject.ModelFact']
    :return: list of values rescaled by least precise fact's precision
    :rtype: list [:class:'~decimals.Decimal']
    """
    decimals = set([fact.decimals for fact in facts])
    if len(decimals) == 1:
        # if all decimals match, then just return xValue
        # (their already scaled value)
        return [fact.xValue for fact in facts]
    # Redo the set getting only numbers
    decimals = {
        int(fact.decimals)
        for fact in facts
        if fact.decimals != 'INF' and
        fact.decimals is not None
    }
    min_decimals_str = str(min(decimals))
    return [
        ValidateXbrlCalcs.roundFact(
            DecimalOverriddenFact(fact, min_decimals_str),
            inferDecimals=True
        ) for fact in facts
    ]


def filter_duplicate_facts(facts, ignore_units=False):
    """
    This utility method should be used to prune duplicate facts from a set of
    facts.  The facts should all be the same concept, and the set returned will
    be all the unique facts in the set.

    :param facts: list of facts to find unique facts from
    :type facts: list ['~arelle.ModelInstanceObject.ModelFact']
    :param ignore_units: specifies whether units make fact unique or not
    :type ignore_units: bool
    :return: all unique facts in facts
    :rtype: list [:class:'~arelle.ModelInstanceObject.ModelFact']
    """
    mapped_facts = defaultdict(list)
    for f in facts:
        if f.contextID is not None and not f.isNil and f.xValid:
            mapped_facts[
                f.contextID, None if ignore_units else f.unitID
            ].append(f)
    result = []
    for v in mapped_facts.values():
        if len(v) == 1:
            result.extend(v)
    return result


def prepare_facts_for_calculation(fact_dict, unit_ignored_dict=None):
    """
    Takes a group of facts for calculations and groups them by context and
    units, and strips out the ones that
    are duplicated or not complete groupings.

    :param fact_dict: The fact dictionary.
        Should be {'conceptName':[facts_tagged_as_concept]...}
    :type fact_dict: dict
    :param unit_ignored_dict: The dictionary of concepts to ignore units for
        duplication checking. Should be {'conceptName': True...}. Defaults to
        'False' for anything not defined, and all units are tested otherwise.
    :type unit_ignored_dict: dict
    :return: A list of dicts that map a context-unit-matched set of the
        facts together.
        Should be: [{'conceptName1':fact, 'conceptName2':fact2,...}...]
    :rtype: list [dict]
    """
    unit_ignored = defaultdict(lambda: False)
    if unit_ignored_dict:
        unit_ignored.update(unit_ignored_dict)
    cleaned_fact_map = defaultdict()
    for k, v in fact_dict.items():
        cleaned_fact_map[k] = filter_duplicate_facts(
            v, ignore_units=unit_ignored[k]
        )
    result_map = defaultdict(dict)
    for k, v in cleaned_fact_map.items():
        if not unit_ignored[k]:
            for f in v:
                result_map[(f.contextID, f.unitID)][k] = f
    for k, v in cleaned_fact_map.items():
        if unit_ignored[k]:
            for f in v:
                for result_key, rm in result_map.items():
                    if result_key[0] == f.contextID:
                        rm[k] = f
    expected_len = len(fact_dict)
    return [m for m in result_map.values() if len(m) == expected_len]


def axis_exists(val, fact, axis_name):
    """
    Given a fact, check if fact is dimensionalized
    with given axis

    :param val: val with standard taxonomies dict to check
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param fact: fact to check
    :type fact: :class:'~arelle.ModelInstanceObject.ModelFact'
    :param axis_name: name of the axis to check
    :type axis_name: str
    :return: True if fact is demensionalized
    :rtype: bool
    """
    standard_taxonomies_dict = val.disclosureSystem.standardTaxonomiesDict

    return any(
        axis_name == dim.dimensionQname.localName
        for dim in fact.context.qnameDims.values()
        if dim.isExplicit and dim.dimensionQname and
        dim.dimensionQname.namespaceURI in standard_taxonomies_dict
    )


def member_exists(val, fact, member_name):
    """
    Given a fact, check if fact is dimensionalized with given axis

    :param val: val to check against
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param fact: fact to check against
    :type fact: :class:'~arelle.InstanceModelObject.ModelFact'
    :param member_name: member name to check against
    :type member_name: str
    :return: True if fact is demensionalized with gived axis
    :rtype: bool
    """

    standard_taxonomies_dict = val.disclosureSystem.standardTaxonomiesDict

    return any(
        member_name == dim.member.qname.localName
        for dim in fact.context.segDimValues.values()
        if dim.isExplicit and dim.member is not None and
        dim.member.qname.namespaceURI in standard_taxonomies_dict
    )


def axis_member_exists(val, fact, axis_name, member_name):
    """
    Given a fact, check if the fact is dimensionalized for a axis/member
    pairing

    :param val: val to check standard taxonomies dict on
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param fact: fact to check segDimValues of
    :type fact: :class:'~arelle.InstanceModelObject.ModelFact'
    :param axis_name: axis name to check against local name
    :type axis_name: str
    :param member_name: member_name to check against local name
    :type member_name: str
    :return: returns true if fact is dimensionalized
    :rtype: bool
    """
    standard_taxonomies_dict = val.disclosureSystem.standardTaxonomiesDict

    return any(
        member_name == dim.memberQname.localName and
        axis_name == dim.dimensionQname.localName
        for dim in fact.context.segDimValues.values()
        if dim.isExplicit and dim.memberQname is not None and
        dim.memberQname.namespaceURI in standard_taxonomies_dict and
        dim.dimensionQname is not None and
        dim.dimensionQname.namespaceURI in standard_taxonomies_dict
    )


def get_facts_with_type(lookup_type_strings, model_xbrl):
    """
    Returns a list of facts from the modelXbrl whose types match the types
    supplied in the lookup_type_strings list

    :param lookup_type_strings: string specifying what to lookup
    :type lookup_type_strings: str
    :param model_xbrl: modelXbrl to return facts from
    :type model_xbrl: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: list of facts from the specified modelXbrl
    :rtype: list [:class:'~arelle.ModelInstanceObject.ModelFact"]
    """
    list_types = []
    if lookup_type_strings:
        for type in lookup_type_strings:
            list_types.extend(
                f for f in list(model_xbrl.facts)
                if f.context is not None and
                f.concept.type is not None and f.concept.type.name == type
            )
    return list_types


def lookup_gaap_facts(fact_name, model_xbrl):
    """
    Returns the set of us-gaap facts for the
    given fact name.  Note that the facts will not be
    returned if the context or xValue is None.

    :param fact_name: name of the fact to lookup
    :type fact_name: str
    :param model_xbrl: modelXbrl to return facts from
    :type model_xbrl: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: list of us-gaap facts
    :rtype: list [:class:'~arelle.InstanceModelObject.ModelFact']
    """
    def valid_fact(fact):
        return (
            fact.concept.qname.namespaceURI in GAAP_NAMESPACE_LIST and
            fact.context is not None and fact.xValue is not None
        )
    facts = [
        f for f in model_xbrl.facts
        if f.concept.qname.localName == fact_name and valid_fact(f)
    ]
    return facts


def get_facts_dei(lookup_concept_strings, model_xbrl):
    """
    Returns a list of dei facts from the modelXbrl whose name matches the names
    supplied in the lookup_concept_strings list

    :param lookup_concept_strings: strings to look up using a loop
    :type lookup_concept_strings: list [str]
    :param model_xbrl: modelXbrl to get facts from
    :type model_xbrl: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: list of dei facts from specified model_xbrl
    :rtype: list [:class:'~arelle.InstanceModelObject.ModelFact']
    """
    list_dei = []
    if lookup_concept_strings:
        for dei in lookup_concept_strings:
            list_dei.extend(lookup_dei_facts(dei, model_xbrl, False))
    return list_dei


def lookup_dei_facts(fact_name, model_xbrl, validation=True):
    """
    Returns the set of dei facts for the
    given fact name

    :param fact_name: name of the fact
    :type fact_name: str
    :param model_xbrl: ModelXbrl to get the facts from
    :type model_xbrl: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param validation: should check for valid facts
    :type validation: bool
    :return: Set of dei facts for a given fact name
    :rtype: list [:class:'~arelle.InstanceModelObject.ModelFact']
    """
    facts = [
        f for f in model_xbrl.facts
        if f.concept.qname.localName == fact_name and
        f.concept.qname.namespaceURI in DEI_NAMESPACE_LIST
    ]
    if validation:
        facts = [
            f for f in facts
            if f.context is not None and f.xValue is not None
        ]
    return facts


LEGALENTITYAXIS_DEFAULT = ''


def legal_entity_axis_facts_by_member(facts):
    """
    Returns a dictionary of lists of facts, keyed off of the LegalEntityAxis
    member, or defaults to LEGALENTITYAXIS_DEFAULT if the fact has no LEA
    member.

    :param facts: List of facts to key off by the LegalEntityAxis
    :type facts: list [:class:'arelle.InstanceModelObject.ModelFact']
    :return: Dictionary of a list of facts keyed off of the LegalEntityAxis
    :rtype: dict
    """
    results = defaultdict(list)
    for fact in facts:
        legalDim = LEGALENTITYAXIS_DEFAULT
        if _fact_components_valid(fact):
            dims = [
                dim for dim in fact.context.segDimValues.values()
                if dim.isExplicit and dim.member is not None
            ]
            for dim in dims:
                if dim.dimension.qname.localName == 'LegalEntityAxis':
                    legalDim = dim.member.qname.localName
                    break
            results[legalDim].append(fact)
    return results


def axis_member_fact(axis_name, member_name, model_xbrl):
    """
    Return the fact present, if any, under the axis/member combination.

    :param axis_name: The axis name to check
    :type axis_name: str
    :param member_name: The member name to check
    :type member_name: str
    :return: The fact found or None
    :rtype: :class:'~arelle.InstanceModelObject.ModelFact' or None
    """
    fact_list = []
    for fact in model_xbrl.facts:
        if _fact_components_valid(fact):
            dims = [
                dim for dim in fact.context.segDimValues.values()
                if (
                    dim.isExplicit and
                    dim.member is not None and
                    dim.member.qname.localName == member_name
                )
            ]
            for dim in dims:
                if dim.dimension.qname.localName == axis_name:
                    fact_list.append(fact)
    return fact_list


def _fact_components_valid(fact):
    """
    Return true if all of the components in a fact are not none

    :param fact: The fact to check if it is valid
    :type fact: :class:'~arelle.InstanceModelObject.ModelFact'
    :return: True if none of the components of the fact are not None
    :rtype: bool
    """
    if fact is None:
        return False
    elif fact.context is None:
        return False
    elif fact.context.segDimValues is None:
        return False
    elif fact.context.segDimValues.values() is None:
        return False
    return True


def member_qnames(fact, axis_filter=None):
    """
    Return a list of a fact's member(s)

    :param fact: An arelle ModelFact instance.
    :type fact: :class:'~arelle.InstanceModelObject.ModelFact'
    :param axis_filter: The axis to filter for
    :type axis_filter: bool
    :return: ([str, ..., str]) A list of the string representation of each of
        the fact's member's qnames.
    :rtype: list [str]
    """
    if axis_filter:
        return [
            str(dim.member.qname) for dim in fact.context.segDimValues.values()
            if dim.isExplicit and dim.member is not None and dim.dimensionQname
            is not None and dim.dimensionQname.localName in axis_filter
        ]
    else:
        return [
            str(dim.member.qname) for dim in fact.context.segDimValues.values()
            if dim.isExplicit and dim.member is not None
        ]


def axis_qnames(fact):
    """
    Returns a list the dim.dimensionQnames withing the fact as strings

    :param fact: An arelle ModelFact instance.
    :type fact: :class:'~arelle.InstanceModelObject.ModelFact'
    :return: a list of the fact's axes.
    :rtype: list [str]
    """
    return [
        str(dim.dimensionQname) for dim in fact.context.segDimValues.values()
        if dim.dimensionQname is not None
    ]


def grab_numeric_facts(facts_list):
    """
    Given a list of facts, return those facts whose values are numeric

    :param facts_list: list of fact to return numeric values for
    :type facts_list: list [:class:'~arelle.ModelInstanceObject.ModelFact']
    :return: return list of facts with numeric values
    :rtype: list [:class:'~arelle.ModelInstanceObject.ModelFact']
    """
    numeric_facts = []
    for fact in facts_list:
        if not fact.isNumeric:
            continue
        elif fact.xValue is not None:
            numeric_facts.append(fact)
    return numeric_facts
