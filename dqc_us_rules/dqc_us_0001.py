# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import json
import os
from arelle.ModelDtsObject import ModelConcept
from .util import facts, messages
import itertools
from collections import defaultdict

_CODE_NAME = 'DQC.US.0001'
_RULE_VERSION = '2.0.0'
_DQC_01_AXIS_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0001',
    'dqc_0001.json'
)
_PARENT_CHILD_ARCROLE = 'http://www.xbrl.org/2003/arcrole/parent-child'
_ADDITIONAL_AXES_KEY = 'additional_axes'
_EXCLUDED_AXES_KEY = 'excluded_axes'
_DEFINED_MEMBERS_KEY = 'defined_members'
_ADDITIONAL_MEMBERS_KEY = 'additional_members'
_EXTENSIONS_KEY = 'extensions'
_RULE_INDEX_KEY = 'rule_index'
_UGT_FACT_KEY = 'ugt_fact'
_NO_FACT_KEY = 'no_fact'
_EXT_FACT_KEY = 'ext_fact'


def run_checks(val, *args, **kwargs):
    """
    Entrypoint for the rule.  Load the config, search for instances of
    each axis of interest, and call validations on them.

    :param val: val from which to gather end dates
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: No direct return
    :rtype: None
    """
    checked_axes = defaultdict(list)
    config = _load_config(_DQC_01_AXIS_FILE)
    for axis_key, axis_config in config.items():
        for role in val.modelXbrl.roleTypes:
            relset = val.modelXbrl.relationshipSet(
                _PARENT_CHILD_ARCROLE, linkrole=role
            )

            def filter_func(model_object):
                return (
                    _is_concept(model_object) and
                    model_object.qname.localName == axis_key
                )

            for axis in filter(filter_func, relset.fromModelObjects()):
                _run_axis_checks(
                    axis,
                    axis_key,
                    axis_config,
                    relset,
                    val,
                    role,
                    checked_axes
                )


def _run_axis_checks(axis, axis_key, axis_config, relset, val, role,
                     checked_axes):
    """
    Run the axis checks for a given axis, config dict,
    and set of children.

    :param axis: The axis to check
    :type axis: :class:'~arelle.ModelDTSObject.ModelConcept'
    :param axis_key: The axis name to check
    :type axis_key: str
    :param axis_config: The axis-specific config.
    :type axis_config: dict
    :param relset: The relationshipSet for the axis.
    :type relset: set
    :param val: val from which to gather end dates
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param role: The role for the relationship
    :type role: str
    :param checked_axes: Dictionary of already-fired axis_key: axis/member.
    :type checked_axes: dict
    :return: No direct return
    :rtype: None
    """
    _run_member_checks(
        axis,
        axis_key,
        axis_config,
        relset,
        val,
        role,
        checked_axes
    )
    _run_extension_checks(
        axis,
        axis_key,
        axis_config,
        relset,
        val,
        role,
        checked_axes
    )


def _run_member_checks(axis, axis_key, axis_config, relset, val, role,
                       checked_axes):
    """
    Run the checks on included and excluded members and companion axes.
    Extensions are not checked.  Error as appropriate.

    :param axis: The axis to check
    :type axis: :class:'~arelle.ModelDTSObject.ModelConcept'
    :param axis_key: The axis name to check
    :type axis_key: str
    :param axis_config: The axis-specific config.
    :type axis_config: dict
    :param relset: The relationshipSet for the axis.
    :type relset: set
    :param val: val from which to gather end dates
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param role: The role for the relationship
    :type role: str
    :param checked_axes: Dictionary of already-fired axis_key: axis/member.
    :type checked_axes: dict
    :return: No direct return
    :rtype: None
    """
    additional_axes = axis_config.get(_ADDITIONAL_AXES_KEY, {})
    excluded_axes = axis_config.get(_EXCLUDED_AXES_KEY, {})
    allowed_children = (
        axis_config.get(_DEFINED_MEMBERS_KEY, []) +
        axis_config.get(_ADDITIONAL_MEMBERS_KEY, [])
    )
    disallowed_children = []
    disallowed_children.extend(
        itertools.chain.from_iterable(
            member_list for member_list in excluded_axes.values()
        )
    )
    allowed_children.extend(
        itertools.chain.from_iterable(
            member_list for member_list in additional_axes.values()
        )
    )
    if len(disallowed_children) > 0:
        # Blacklisted axes check - Can only check blacklist (excluded)
        # or whitelist (included) axes.
        # Default to blacklist if both are present.
        for child in _all_members_under(axis, relset):
            if ((not _is_extension(child, val) and
                    child.qname.localName in disallowed_children)):
                axis_mem_pair = (axis.qname, child.qname)
                if axis_mem_pair in checked_axes[axis_key]:
                    continue
                fact_list = facts.axis_member_fact(
                    axis.qname.localName,
                    child.qname.localName,
                    val.modelXbrl
                )

                for fact in fact_list:  # remove grouped messages
                    val.modelXbrl.error(
                        '{base_key}.{extension_key}'.format(
                            base_key=_CODE_NAME,
                            extension_key=axis_config[_RULE_INDEX_KEY]
                        ),
                        messages.get_message(_CODE_NAME, _UGT_FACT_KEY),
                        axis=axis.label(),
                        member=child.label(),
                        modelObject=fact,
                        ruleVersion=_RULE_VERSION
                    )
                checked_axes[axis_key].append(axis_mem_pair)
                if len(fact_list) == 0:
                    val.modelXbrl.error(
                        '{base_key}.{extension_key}'.format(
                            base_key=_CODE_NAME,
                            extension_key=axis_config[_RULE_INDEX_KEY]
                        ),
                        messages.get_message(_CODE_NAME, _NO_FACT_KEY),
                        axis=axis.label(),
                        member=child.label(),
                        group=role,
                        ruleVersion=_RULE_VERSION
                    )
    else:
        # Whitelisted axes are specified.
        for child in _all_members_under(axis, relset):
            if ((not _is_extension(child, val) and
                 child.qname.localName not in allowed_children)):
                axis_mem_pair = (axis.qname, child.qname)
                if axis_mem_pair in checked_axes[axis_key]:
                    continue
                fact_list = facts.axis_member_fact(
                    axis.qname.localName,
                    child.qname.localName,
                    val.modelXbrl
                )
                for fact in fact_list:  # remove for grouped messages
                    val.modelXbrl.error(
                        '{base_key}.{extension_key}'.format(
                            base_key=_CODE_NAME,
                            extension_key=axis_config[_RULE_INDEX_KEY]
                        ),
                        messages.get_message(_CODE_NAME, _UGT_FACT_KEY),
                        axis=axis.label(),
                        member=child.label(),
                        modelObject=fact,
                        ruleVersion=_RULE_VERSION,

                    )
                checked_axes[axis_key].append(axis_mem_pair)
                if len(fact_list) == 0:
                    val.modelXbrl.error(
                        '{base_key}.{extension_key}'.format(
                            base_key=_CODE_NAME,
                            extension_key=axis_config[_RULE_INDEX_KEY]
                        ),
                        messages.get_message(_CODE_NAME, _NO_FACT_KEY),
                        axis=axis.label(),
                        member=child.label(),
                        group=role,
                        ruleVersion=_RULE_VERSION
                    )


def _run_extension_checks(axis, axis_key, axis_config, relset, val, role,
                          checked_axes):
    """
    Check extension members under the given axis.

    :param axis: The axis to check
    :type axis: :class:'~arelle.ModelDTSObject.ModelConcept'
    :param axis_key: The axis name to check
    :type axis_key: str
    :param axis_config: The axis-specific config.
    :type axis_config: dict
    :param relset: The relationshipSet for the axis.
    :type relset: set
    :param val: val from which to gather end dates
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param role: The role for the relationship
    :type role: str
    :param checked_axes: Dictionary of already-fired axis_key: axis/member.
    :type checked_axes: dict
    :return: No direct return
    :rtype: None
    """
    allow_all = (
        len(axis_config[_EXTENSIONS_KEY]) > 0 and
        axis_config[_EXTENSIONS_KEY][0] == '*'
    )
    if not allow_all:
        allowed_extensions = axis_config[_EXTENSIONS_KEY]
        for child in _all_members_under(axis, relset):
            if _is_extension(child, val):
                if child.qname.localName not in allowed_extensions:
                    axis_mem_pair = (axis.qname, child.qname)
                    if axis_mem_pair in checked_axes[axis_key]:
                        continue
                    fact_list = facts.axis_member_fact(
                        axis.qname.localName,
                        child.qname.localName,
                        val.modelXbrl
                    )
                    for fact in fact_list:  # remove for grouped messages
                        val.modelXbrl.error(
                            '{base_key}.{extension_key}'.format(
                                base_key=_CODE_NAME,
                                extension_key=axis_config[_RULE_INDEX_KEY]
                            ),
                            messages.get_message(
                                _CODE_NAME, _EXT_FACT_KEY
                            ),
                            axis=axis.label(),
                            member=child.label(),
                            modelObject=fact,
                            ruleVersion=_RULE_VERSION,
                        )
                    checked_axes[axis_key].append(axis_mem_pair)
                    if len(fact_list) == 0:
                        val.modelXbrl.error(
                            '{base_key}.{extension_key}'.format(
                                base_key=_CODE_NAME,
                                extension_key=axis_config[_RULE_INDEX_KEY]
                            ),
                            messages.get_message(_CODE_NAME, _NO_FACT_KEY),
                            axis=axis.label(),
                            member=child.label(),
                            group=role,
                            ruleVersion=_RULE_VERSION
                        )


def _is_extension(concept, val):
    """
    Return True if concept is an extension.

    :param concept: The concept to check
    :type concept: :class:'~arelle.ModelDTSObject.ModelConcept'
    :param val: val from which to gather end dates
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: True if concept is an extension, else False
    :rtype: bool
    """
    return (
        concept.qname.namespaceURI not in
        val.disclosureSystem.standardTaxonomiesDict
    )


def _is_concept(concept):
    """
    This utility method should be used instead of None checks on
    arc.fromModelObject or arc.toModelObject.

    :param concept: The concept to check
    :type concept: :class:'~arelle.ModelDTSObject.ModelConcept'
    :return: True if it's a valid concept.  False if not.
    :rtype: bool
    """
    return (
        isinstance(concept, ModelConcept) and
        concept.qname
    )


def _all_members_under(axis, relset):
    """
    Returns a dictionary of concepts seen under the provided concept,
    in the given relset.

    Dictionary values are locators for the concepts: the `toLocator`
    from the arc where that concept was discovered.

    :param axis: The axis to check.
    :type axis: :class:'~arelle.ModelDTSObject.ModelConcept'
    :param relset: The relationshipSet.
    :type relset: set
    :return: a list of members under the axis.
    :rtype: [:class:'~arelle.ModelDTSObject.ModelConcept']
    """
    concepts = []
    arcs_to_check = []
    seen_arcs = set()
    for arc in relset.fromModelObject(axis):
        seen_arcs.add(arc)
        arcs_to_check.append(arc)
    while(arcs_to_check):
        cur_arc = arcs_to_check.pop()
        to_object = cur_arc.toModelObject
        if _is_concept(to_object) and not _is_domain(to_object):
            concepts.append(to_object)
        for arc in relset.fromModelObject(to_object):
            if arc not in seen_arcs:
                seen_arcs.add(arc)
                arcs_to_check.append(arc)
    return concepts


def _is_domain(concept):
    """
    Return True if the concept is a domain, else False

    :param concept: The concept to check.
    :type concept: :class:'~arelle.ModelDTSObject.ModelConcept'
    :return: True if the concept is a domain, else False.
    :rtype: bool
    """
    return (
        '[Domain]' in concept.label() or
        concept.qname.localName.endswith('Domain')
    )


def _load_config(axis_file):
    """
    Returns a map of axis/configs to test.

    :param axis_file: the file to open.
    :type axis_file: file
    :return: A map of the config file.
    :rtype: dict
    """

    with open(axis_file) as config:
        return json.load(config)

__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': 'Axis member checks.',
    # Mount points
    'Validate.XBRL.Finally': run_checks,
}
