# (c) Copyright 2015 - 2017, XBRL US Inc. All rights reserved.
# See https://xbrl.us/dqc-license for license information.
# See https://xbrl.us/dqc-patent for patent infringement notice.
import json
import os
from arelle import ModelDtsObject
from arelle import XbrlConst, ModelXbrl
from .util import facts, messages
import itertools
from collections import defaultdict, OrderedDict
from arelle.FileSource import saveFile, openFileSource

_CODE_NAME = 'DQC.US.0001'
_RULE_VERSION = '3.3.1'
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
_EARLIEST_US_GAAP_YEAR = 2014
_CONFIG_JSON_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0001',
    'dqc_0001.json'
    )

_UGT_DOCS = (
    {
        "year": 2014,
        "namespace": "http://fasb.org/us-gaap/2014-01-31",
        "docLB": "http://xbrl.fasb.org/us-gaap/2014/us-gaap-2014-01-31.zip/us-gaap-2014-01-31/elts/us-gaap-doc-2014-01-31.xml",  # noqa
        "entryXsd": "http://xbrl.fasb.org/us-gaap/2014/us-gaap-2014-01-31.zip/us-gaap-2014-01-31/entire/us-gaap-entryPoint-std-2014-01-31.xsd",  # noqa
    }, {
        "year": 2015,
        "namespace": "http://fasb.org/us-gaap/2015-01-31",
        "docLB": "http://xbrl.fasb.org/us-gaap/2015/us-gaap-2015-01-31.zip/us-gaap-2015-01-31/elts/us-gaap-doc-2015-01-31.xml",  # noqa
        "entryXsd": "http://xbrl.fasb.org/us-gaap/2015/us-gaap-2015-01-31.zip/us-gaap-2015-01-31/entire/us-gaap-entryPoint-std-2015-01-31.xsd",  # noqa
    }, {
        "year": 2016,
        "namespace": "http://fasb.org/us-gaap/2016-01-31",
        "docLB": "http://xbrl.fasb.org/us-gaap/2016/us-gaap-2016-01-31.zip/us-gaap-2016-01-31/elts/us-gaap-doc-2016-01-31.xml",  # noqa
        "entryXsd": "http://xbrl.fasb.org/us-gaap/2016/us-gaap-2016-01-31.zip/us-gaap-2016-01-31/entire/us-gaap-entryPoint-std-2016-01-31.xsd",  # noqa
    }, {
        "year": 2017,
        "namespace": "http://fasb.org/us-gaap/2017-01-31",
        "docLB": "http://xbrl.fasb.org/us-gaap/2017/us-gaap-2017-01-31.zip/us-gaap-2017-01-31/elts/us-gaap-doc-2017-01-31.xml",  # noqa
        "entryXsd": "http://xbrl.fasb.org/us-gaap/2017/us-gaap-2017-01-31.zip/us-gaap-2017-01-31/entire/us-gaap-entryPoint-std-2017-01-31.xsd",  # noqa
    }
)


def _tr_mem(val,
            ugt,
            dm_ld_inst,
            parent_model_object,
            rel_name,
            elr,
            ax_mem):
    """
    Walks the taxonomy for a given axis
    :param val: val from which to gather end dates
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param ugt: dict of taxonomies and their entirance points
    :type ugt: dict
    :param dm_ld_inst: loaded ugt instance,
    :type dm_ld_inst: ModelXbrl,
    :param parent_model_object: model object for Axis
    :type parent_model_object:class:'~arelle.ModelDTSObject.ModelConcept'
    :param rel_name: The role for the relationship
    :type rel_name: str
    :param elr: Linkrole
    :type elr: str
    :param ax_mem: set into which to accumulate members
    :type ax_mem: set
    :return: set of members for the axis specified
    :rtype: set
    """
    rels = dm_ld_inst.relationshipSet(rel_name,
                                      elr).fromModelObject(parent_model_object)
    for rel in rels:
        if rel.isUsable:
            ax_mem.add(rel.toModelObject.qname.localName)
            _tr_mem(val, ugt, dm_ld_inst,
                    rel.toModelObject,
                    XbrlConst.domainMember, rel.consecutiveLinkrole, ax_mem)
    return ax_mem


def _create_config(val):
    """
    Creates the configs needed for dqc_us_0001

    :param val: ValidateXbrl needed in order to save the cache
    :type val: :class: '~arelle.ValidateXbrl.ValidateXbrl'
    :return: no explicit return but creates and saves configs in
        dqc_us_rule\resources\DQC_US_0001
    :rtype: None
    """
    val.ugtNamespace = None
    cntlr = val.modelXbrl.modelManager.cntlr
    year = _EARLIEST_US_GAAP_YEAR
    config = _load_config(_DQC_01_AXIS_FILE)
    # Create a list of axes in the base config file

    for ugt in _UGT_DOCS:
        # create taxonomy specific name
        config_json_file = os.path.join(
            os.path.dirname(__file__),
            'resources',
            'DQC_US_0001',
            'dqc_0001_{}.json'.format(str(year))
        )
        # copy the base config file
        working_json_file = config
        ugtEntryXsd = ugt["entryXsd"]
        prior_vds = val.modelXbrl.modelManager.validateDisclosureSystem
        val.modelXbrl.modelManager.validateDisclosureSystem = False
        dimLoadingInstance = ModelXbrl.load(
            val.modelXbrl.modelManager, openFileSource(ugtEntryXsd, cntlr),
            ("built us-gaap member cache")
        )
        val.modelXbrl.modelManager.validateDisclosureSystem = prior_vds

        for axis, info in config.items():
            info['defined_members'] = defaultdict(set)
            axisConcept = dimLoadingInstance.nameConcepts.get(axis, (None,))[0]
            if axisConcept is not None:
                working_json_file[axis]['defined_members'] = sorted(
                    _tr_mem(
                        val,
                        ugt,
                        dimLoadingInstance,
                        axisConcept,
                        XbrlConst.dimensionDomain,
                        None,
                        set()
                    )
                )
        json_str = str(
            json.dumps(
                OrderedDict(sorted(working_json_file.items())),
                ensure_ascii=False, indent=4, sort_keys=True
            )
        )
        saveFile(cntlr, config_json_file, json_str)
        dimLoadingInstance.close()
        del dimLoadingInstance
        year += 1


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
    config_json_file = _determine_namespace(val)
    config = _load_config(config_json_file)
    if not config:
        _create_config(val)
        config = _load_config(config_json_file)
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


def _determine_namespace(val):
    """
    Determines which json file to use based off of the
    namespace of the filing.

    :param val: val from which to determine namespace
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: Name of config file to use
    :rtype: String
    """
    NS_2017 = "http://fasb.org/us-gaap/2017-01-31"
    NS_2016 = "http://fasb.org/us-gaap/2016-01-31"
    NS_2015 = "http://fasb.org/us-gaap/2015-01-31"
    NS_2014 = "http://fasb.org/us-gaap/2014-01-31"
    RESOURCE_DIR = 'resources'
    RULE = 'DQC_US_0001'

    if NS_2017 in val.modelXbrl.namespaceDocs.keys():
        config_json_file = os.path.join(
            os.path.dirname(__file__),
            RESOURCE_DIR,
            RULE,
            'dqc_0001_2017.json'
        )
    elif NS_2016 in val.modelXbrl.namespaceDocs.keys():
        config_json_file = os.path.join(
             os.path.dirname(__file__),
             RESOURCE_DIR,
             RULE,
             'dqc_0001_2016.json'
        )
    elif NS_2015 in val.modelXbrl.namespaceDocs.keys():
        config_json_file = os.path.join(
             os.path.dirname(__file__),
             RESOURCE_DIR,
             RULE,
             'dqc_0001_2015.json'
        )
    elif NS_2014 in val.modelXbrl.namespaceDocs.keys():
        config_json_file = os.path.join(
             os.path.dirname(__file__),
             RESOURCE_DIR,
             RULE,
             'dqc_0001_2014.json'
        )
    else:
        config_json_file = os.path.join(
             os.path.dirname(__file__),
             RESOURCE_DIR,
             RULE,
             'dqc_0001.json'
        )
    return config_json_file


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
        isinstance(concept, ModelDtsObject.ModelConcept) and
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
    try:
        config = open(axis_file)
    except FileNotFoundError:
        return False
    return json.load(config)


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': 'Axis member checks.',
    # Mount points
    'Validate.XBRL.Finally': run_checks,
}
