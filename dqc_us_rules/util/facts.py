# Copyright (c) 2015, Workiva Inc.  All rights reserved
# Copyright (c) 2015, XBRL US Inc.  All rights reserved
from collections import defaultdict
from arelle import ValidateXbrlCalcs

from arelle.ModelValue import QName

DEI_NAMESPACE_LIST = ['http://xbrl.sec.gov/dei/2014-01-31', 'http://xbrl.sec.gov/dei/2013-01-31', 'http://xbrl.sec.gov/dei/2012-01-31', 'http://xbrl.sec.gov/dei/2011-01-31', 'http://xbrl.us/dei/2009-01-31']
GAAP_NAMESPACE_LIST = ['http://fasb.org/us-gaap/2012-01-31', 'http://fasb.org/us-gaap/2013-01-31', 'http://fasb.org/us-gaap/2014-01-31', 'http://fasb.org/us-gaap/2015-01-31']


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
    Accepts a list of facts and returns a list of values from those facts re-scaled by the least precise fact's precision
    Makes no guarantees about data type, known types are integers, floats, and Decimals
    Precision attribute is not allowed in EFM 6.5.17, so this assumes decimals-use only.
    """
    decimals = set([fact.decimals for fact in facts])
    if len(decimals) == 1:  # if all decimals match, then just return xValue (their already scaled value)
        return [fact.xValue for fact in facts]
    #Redo the set getting only numbers
    decimals = set([int(fact.decimals) for fact in facts if fact.decimals != 'INF' and fact.decimals is not None])
    min_decimals_str = str(min(decimals))
    return [ValidateXbrlCalcs.roundFact(DecimalOverriddenFact(fact, min_decimals_str), inferDecimals=True) for fact in facts]


def filter_duplicate_facts(facts, ignore_units=False):
    """
    This utility method should be used to prune duplicate facts from a set of facts.  The facts should
    all be the same concept, and the set returned will be all the unique facts in the set.
    """
    mapped_facts = defaultdict(list)
    for f in facts:
        if f.contextID is not None and not f.isNil and f.xValid:
            mapped_facts[(f.contextID, None if ignore_units else f.unitID)].append(f)
    result = []
    for v in mapped_facts.values():
        if len(v) == 1:
            result.extend(v)
    return result


def prepare_facts_for_calculation(fact_dict, unit_ignored_dict=None):
    """
    Takes a group of facts for calculations and groups them by context and units, and strips out the ones that
    are duplicated or not complete groupings.

    @param fact_dict: The fact dictionary.  Should be {'conceptName':[facts_tagged_as_concept]...}
    @param unit_ignored_dict: The dictionary of concepts to ignore units for duplication checking.  Should be {'conceptName': True...}.
                              Defaults to 'False' for anything not defined, and all units are tested otherwise.
    @return A list of dicts that map a context-unit-matched set of the facts together.
            Should be: [{'conceptName1':fact, 'conceptName2':fact2,...}...]
    """
    unit_ignored = defaultdict(lambda: False)
    if unit_ignored_dict:
        unit_ignored.update(unit_ignored_dict)
    cleaned_fact_map = defaultdict()
    for k, v in fact_dict.items():
        cleaned_fact_map[k] = filter_duplicate_facts(v, ignore_units=unit_ignored[k])
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
    given a fact, check if fact is dimensionalized
    with given axis
    """
    return any(axis_name == dim.dimensionQname.localName
               for dim in fact.context.qnameDims.values()
               if dim.isExplicit and dim.dimensionQname
               and dim.dimensionQname.namespaceURI in val.disclosureSystem.standardTaxonomiesDict)


def member_exists(val, fact, member_name):
    """
    given a fact, check if fact is dimensionalized
    with given axis
    """
    return any(member_name == dim.member.qname.localName
               for dim in fact.context.segDimValues.values()
               if dim.isExplicit and dim.member is not None
               and dim.member.qname.namespaceURI in val.disclosureSystem.standardTaxonomiesDict)


def axis_member_exists(val, fact, axis_name, member_name):
    """
    Given a fact, check if the fact is dimensionalized for a axis/member pairing
    """
    return any(member_name == dim.memberQname.localName and axis_name == dim.dimensionQname.localName
               for dim in fact.context.segDimValues.values()
               if dim.isExplicit and dim.memberQname is not None
               and dim.memberQname.namespaceURI in val.disclosureSystem.standardTaxonomiesDict
               and dim.dimensionQname is not None
               and dim.dimensionQname.namespaceURI in val.disclosureSystem.standardTaxonomiesDict)


def get_facts_with_type(lookup_type_strings, modelXbrl):
    """
    Returns a list of facts from the modelXbrl whose types match the types supplied in the lookup_type_strings list
    """
    list_types = []
    if lookup_type_strings:
        for type in lookup_type_strings:
            list_types.extend(f for f in list(modelXbrl.facts) if f.context is not None
                              and f.concept.type is not None and f.concept.type.name == type)
    return list_types


def lookup_gaap_facts(fact_name, modelXbrl):
    """
    returns the set of us-gaap facts for the
    given fact name.  Note that the facts will not be
    returned if the context or xValue is None.
    """
    def valid_fact(fact):
        return fact.concept.qname.namespaceURI in GAAP_NAMESPACE_LIST and fact.context is not None and fact.xValue is not None
    facts = [f for f in modelXbrl.facts if f.concept.qname.localName == fact_name and valid_fact(f)]
    return facts


def get_facts_dei(lookup_concept_strings, modelXbrl):
    """
    Returns a list of dei facts from the modelXbrl whose name matches the names supplied in the lookup_concept_strings list
    """
    list_dei = []
    if lookup_concept_strings:
        for dei in lookup_concept_strings:
            list_dei.extend(lookup_dei_facts(dei, modelXbrl, False))
    return list_dei


def lookup_dei_facts(fact_name, modelXbrl, validation=True):
    """
    returns the set of dei facts for the
    given fact name
    """
    facts = [f for f in modelXbrl.facts if f.concept.qname.localName == fact_name and f.concept.qname.namespaceURI in DEI_NAMESPACE_LIST]
    if validation:
        facts = [f for f in facts if f.context is not None and f.xValue is not None]
    return facts


LEGALENTITYAXIS_DEFAULT = ''
def LegalEntityAxis_facts_by_member(facts):
    """
    Returns a dictionary of lists of facts, keyed off of the LegalEntityAxis member, or
    defaults to LEGALENTITYAXIS_DEFAULT if the fact has no LEA member.
    """
    results = defaultdict(list)
    for fact in facts:
        legalDim = LEGALENTITYAXIS_DEFAULT
        if _fact_components_valid(fact):
            dims = [dim for dim in fact.context.segDimValues.values() if dim.isExplicit and dim.member is not None]
            for dim in dims:
                if dim.dimension.qname.localName == 'LegalEntityAxis':
                    legalDim = dim.member.qname.localName
                    break
            results[legalDim].append(fact)
    return results


def _fact_components_valid(fact):
    """
    Return true if all of the components in a fact are not none

    :param fact: The fact to check if it is valid
    :type fact: arelle.ModelInstanceObject.ModelFact
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

    :param fact: (ModelFact) An arelle ModelFact instance.
    :returns: ([str, ..., str]) A list of the string representation of each of the fact's member's qnames.
    """
    if axis_filter:
        return [str(dim.member.qname) for dim in fact.context.segDimValues.values() if dim.isExplicit and dim.member is not None
                and dim.dimensionQname is not None and dim.dimensionQname.localName in axis_filter]
    else:
        return [str(dim.member.qname) for dim in fact.context.segDimValues.values() if dim.isExplicit and dim.member is not None]


def axis_qnames(fact):
    """
    @return a list of the @param fact's axes.
    """
    return [str(dim.dimensionQname) for dim in fact.context.segDimValues.values() if dim.dimensionQname is not None]
