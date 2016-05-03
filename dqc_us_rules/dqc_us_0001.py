# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import json
import os
from arelle.ModelDtsObject import ModelConcept
from .util import facts

_CODE_NAME = 'DQC.US.0001'
_RULE_VERSION = '1.1'
_DQC_01_AXIS_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0001',
    'dqc_0001.json'
)
_PARENT_CHILD_ARCROLE = "http://www.xbrl.org/2003/arcrole/parent-child"

def run_checks(val):
    """

    :return:
    """
    config = _load_config(_DQC_01_AXIS_FILE)
    for axis_key, axis_config in config.items():
        axis_filter = lambda model_object: _is_concept(model_object) and model_object.qname.localName == axis_key
        for role in val.modelXbrl.roleTypes:
            relset = val.modelXbrl.relationshipSet(_PARENT_CHILD_ARCROLE, linkrole=role)
            for axis in filter(axis_filter, relset.fromModelObjects()):
                _run_axis_checks(axis, axis_config, relset, val)

def _run_axis_checks(axis, axis_config, relset, val):
    _run_member_checks(axis, axis_config, relset, val)
    _run_extension_checks(axis, axis_config, relset, val)

def _run_member_checks(axis, axis_config, relset, val):
    additional_axes = axis_config['additional_axes']
    excluded_axes = axis_config['excluded_axes']
    allowed_children = axis_config['defined_members'] + axis_config['additional_members']
    disallowed_children = list(member_list for member_list in excluded_axes.values())
    allowed_children.append(member_list for member_list in additional_axes.values())
    if len(disallowed_children) > 0:
        #can only specify disallowed axes or allowed axes.  Not both.  If disallowed is populated, use that.
        for child in _all_members_under(axis, relset):
            print('checking child for disallowed')
            is_extension = child.qname.namespaceURI not in val.disclosureSystem.standardTaxonomiesDict
            if not is_extension and child.qname.localName in disallowed_children:
                fact = facts.axis_member_fact(axis.qname.localName, child.qname.localName, val.modelXbrl)
                if fact is not None:
                    print('AXIS CHECKS EXCLUSION- HAS FACT')
                    print(axis.qname.localName)
                    print(child.qname.localName)
                    print(fact)
                else:
                    print('AXIS CHECKS EXCLUSION- NO FACT')
                    print(axis.qname.localName)
                    print(child.qname.localName)
    else:
        for child in _all_members_under(axis, relset):
            is_extension = child.qname.namespaceURI not in val.disclosureSystem.standardTaxonomiesDict
            if not is_extension and child.qname.localName not in allowed_children:
                fact = facts.axis_member_fact(axis.qname.localName, child.qname.localName, val.modelXbrl)
                if fact is not None:
                    print('AXIS CHECK INCLUSION - FACT')
                    print(axis.qname.localName)
                    print(child.qname.localName)
                    print(fact)
                else:
                    print('AXIS CHECK INCLUSION - NO FACT')
                    print(axis.qname.localName)
                    print(child.qname.localName)

def _run_extension_checks(axis, axis_config, relset, val):
    allow_all = len(axis_config['extensions']) > 0 and axis_config['extensions'][0] == '*'
    if not allow_all:
        allowed_extensions = axis_config['extensions']
        for child in _all_members_under(axis, relset):
            if child.qname.namespaceURI not in val.disclosureSystem.standardTaxonomiesDict:
                if child.qname.localName not in allowed_extensions:
                    fact = facts.axis_member_fact(axis.qname.localName, child.qname.localName, val.modelXbrl)
                    if fact is not None:
                        print('EXTENSION CHECK - HAS FACT')
                        print(axis.qname.localName)
                        print(child.qname.localName)
                        print(fact)
                    else:
                        print('EXTENSION CHECK - NO FACT')
                        print(axis.qname.localName)
                        print(child.qname.localName)

def _is_concept(concept):
    """
        This utility method should be used instead of None checks on
        arc.fromModelObject or arc.toModelObject.
    """
    return concept is not None and isinstance(concept, ModelConcept) and concept.qname is not None

def _all_members_under(axis, relset):
    """
    Returns a dictionary of concepts seen under the provided concept, in the given relset and filtered by the optional filter.

    Dictionary values are locators for the concepts: the `toLocator` from the arc where that concept was discovered.
    """
    concepts = dict()
    arcs_to_check = []
    seen_arcs = set()
    for arc in relset.fromModelObject(axis):
        seen_arcs.add(arc)
        arcs_to_check.append(arc)
    while(arcs_to_check):
        cur_arc = arcs_to_check.pop()
        to_object = cur_arc.toModelObject
        if _is_concept(to_object) and not _is_domain(to_object):
            concepts[to_object] = cur_arc.toLocator
        for arc in relset.fromModelObject(to_object):
            if arc not in seen_arcs:
                seen_arcs.add(arc)
                arcs_to_check.append(arc)
    return concepts

def _is_domain(concept):
    return '[Domain]' in concept.label()

def _load_config(axis_file):
    """
    Returns a map of {qname: id} of the concepts to test for the blacklist

    :return: A map of {qname: id}.
    :rtype +    """

    with open(axis_file) as config:
        return json.load(config)

__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': 'Assets should equal Liabilities and Shareholders Equity',
    # Mount points
    'Validate.XBRL.Finally': run_checks,
}
