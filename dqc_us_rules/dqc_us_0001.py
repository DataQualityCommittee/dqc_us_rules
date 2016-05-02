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
                _run_axis_checks(axis, axis_config, relset, val.modelXbrl)

def _run_axis_checks(axis, axis_config, relset, modelXbrl):
    _run_member_checks(axis, axis_config, relset, modelXbrl)
    _run_included_excluded_axis_checks(axis, axis_config, relset, modelXbrl)
    _run_extension_checks(axis, axis_config, relset, modelXbrl)

def _run_member_checks(axis, axis_config, relset, modelXbrl):
    allowed_members = axis_config['defined_members'] + axis_config['additional_members']
    for rel in relset.fromModelObject(axis):
        child = rel.toModelObject
        if _is_concept(child) and child.qname.localName not in allowed_members:
            #fire
            if facts.axis_member_has_fact(axis.qname.localName, child.qname.localName, modelXbrl):
                #fire has fact
                pass
            else:
                #fire no fact
                pass


def _run_included_excluded_axis_checks(axis, axis_config, relset, modelXbrl):
    additional_axes = axis_config['additional_axes']
    excluded_axes = axis_config['excluded_axes']
    allowed_members = []
    disallowed_members = []
    allowed_members.append(member_list for member_list in additional_axes.values())
    disallowed_members.append(member_list for member_list in excluded_axes.values())
    if len(disallowed_members) > 0:
        #can only specify disallowed axes or allowed axes.  Not both.  If disallowed is populated, use that.
        for rel in relset.fromModelObject(axis):
            child = rel.toModelObject
            if _is_concept(child) and child.qname.localName in disallowed_members:
                if facts.axis_member_has_fact(axis.qname.localName, child.qname.localName, modelXbrl):
                    #fire has fact
                    pass
                else:
                    #fire no fact
                    pass
    else:
        for rel in relset.fromModelObject(axis):
            child = rel.toModelObject
            if _is_concept(child) and child.qname.localName not in allowed_members:
                if facts.axis_member_has_fact(axis.qname.localName, child.qname.localName, modelXbrl):
                    #fire has fact
                    pass
                else:
                    #fire no fact
                    pass

def _run_extension_checks(axis, axis_config, relset, modelXbrl):
    allow_all = len(axis_config['extensions']) > 0 and axis_config['extensions'][0] == '*'
    if not allow_all:
        allowed_extensions = axis_config['extensions']
        for rel in relset.fromModelObject(axis):
            child = rel.toModelObject
            if _is_concept(child) and child.qname.localName not in allowed_extensions:
                if facts.axis_member_has_fact(axis.qname.localName, child.qname.localName, modelXbrl):
                    #fire has fact
                    pass
                else:
                    #fire no fact
                    pass

def _is_concept(concept):
    """
        This utility method should be used instead of None checks on
        arc.fromModelObject or arc.toModelObject.
    """
    return concept is not None and isinstance(concept, ModelConcept) and concept.qname is not None

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
