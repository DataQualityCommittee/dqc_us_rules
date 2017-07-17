# (c) Copyright 2015 - 2017, XBRL US Inc. All rights reserved.
# See https://xbrl.us/dqc-license for license information.
# See https://xbrl.us/dqc-patent for patent infringement notice.
import json
import os
from arelle import XbrlConst, ModelXbrl
from .util import messages
# needs to be relative because of the way it is
# brought onto the classpath by Arelle
from collections import defaultdict, OrderedDict
from arelle.FileSource import saveFile, openFileSource

_CODE_NAME = 'DQC.US.0008'
_RULE_VERSION = '4.0.0'
_RULE_INDEX_KEY = '6819'
_NO_FACT_KEY = 'no_fact'
_EARLIEST_US_GAAP_YEAR = 2014
_CONFIG_JSON_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0008',
    'dqc_0008.json'
)
_EMPTY_LIST = []
ugtDocs = (
    {
        'year': 2014,
        'namespace': 'http://fasb.org/us-gaap/2014-01-31',
        'docLB': 'http://xbrl.fasb.org/us-gaap/2014/us-gaap-2014-01-31.zip/us-gaap-2014-01-31/elts/us-gaap-doc-2014-01-31.xml',  # noqa
        'entryXsd': 'http://xbrl.fasb.org/us-gaap/2014/us-gaap-2014-01-31.zip/us-gaap-2014-01-31/entire/us-gaap-entryPoint-std-2014-01-31.xsd',  # noqa
    },
    {
        'year': 2015,
        'namespace': 'http://fasb.org/us-gaap/2015-01-31',
        'docLB': 'http://xbrl.fasb.org/us-gaap/2015/us-gaap-2015-01-31.zip/us-gaap-2015-01-31/elts/us-gaap-doc-2015-01-31.xml',  # noqa
        'entryXsd': 'http://xbrl.fasb.org/us-gaap/2015/us-gaap-2015-01-31.zip/us-gaap-2015-01-31/entire/us-gaap-entryPoint-std-2015-01-31.xsd',  # noqa
    },
    {
        'year': 2016,
        'namespace': 'http://fasb.org/us-gaap/2016-01-31',
        'docLB': 'http://xbrl.fasb.org/us-gaap/2016/us-gaap-2016-01-31.zip/us-gaap-2016-01-31/elts/us-gaap-doc-2016-01-31.xml',  # noqa
        'entryXsd': 'http://xbrl.fasb.org/us-gaap/2016/us-gaap-2016-01-31.zip/us-gaap-2016-01-31/entire/us-gaap-entryPoint-std-2016-01-31.xsd',  # noqa
    },
    {
        'year': 2017,
        'namespace': 'http://fasb.org/us-gaap/2017-01-31',
        'docLB': 'http://xbrl.fasb.org/us-gaap/2017/us-gaap-2017-01-31.zip/us-gaap-2017-01-31/elts/us-gaap-doc-2017-01-31.xml',  # noqa
        'entryXsd': 'http://xbrl.fasb.org/us-gaap/2017/us-gaap-2017-01-31.zip/us-gaap-2017-01-31/entire/us-gaap-entryPoint-std-2017-01-31.xsd',  # noqa
    }
)


def _tr_calc(val, calc_ld_inst, rel_name, cal_ch):
    """
    Walks the taxonomy for a given calc

    :param val: val from which to gather end dates
    :type val: :class:`arelle.ModelXbrl.ModelXbrl`
    :param calc_ld_inst: ugt instance
    :type calc_ld_inst: :class:`arelle.ModelXbrl.ModelXbrl`
    :param rel_name: The role for the relationship
    :type rel_name: str
    :param calc_children: calcChildren
    :type calc_children: dict
    :return: no explicit return but appends relationship to calcChildren
    """

    for rel in calc_ld_inst.relationshipSet(rel_name).modelRelationships:
        cal_ch[rel.fromModelObject.qname.localName].add(
            rel.toModelObject.qname.localName
        )


def _create_config(val):
    """
    Creates the configs needed for dqc_us_0008

    :param val: ValidateXbrl needed in order to save the cache
    :type val: :class: 'arelle.ValidateXbrl.ValidateXbrl'
    :return: no explicit return but creates and saves configs in
        dqc_us_rule\resources\DQC_US_0008
    :rtype: None
    """
    val.ugtNamespace = None
    cntlr = val.modelXbrl.modelManager.cntlr
    year = _EARLIEST_US_GAAP_YEAR
    # Create a list of axes in the base config file
    calc_children = defaultdict(set)
    # receives list of members of above axes
    for ugt in ugtDocs:
        # create taxonomy specific name
        config_json_file = os.path.join(
            os.path.dirname(__file__),
            'resources',
            'DQC_US_0008',
            'dqc_0008_{}.json'.format(str(year))
        )
        # copy the base config file
        ugtEntryXsd = ugt['entryXsd']
        prior_vds = val.modelXbrl.modelManager.validateDisclosureSystem
        val.modelXbrl.modelManager.validateDisclosureSystem = False
        calc_loading_instance = ModelXbrl.load(
            val.modelXbrl.modelManager, openFileSource(ugtEntryXsd, cntlr),
            ('built us-gaap calcs cache')
        )
        val.modelXbrl.modelManager.validateDisclosureSystem = prior_vds
        _tr_calc(
            val, calc_loading_instance,
            XbrlConst.summationItem, calc_children
        )
        # lexicographically order for readability and QA checking
        json_str = _reorder_dictionary(calc_children)
        saveFile(cntlr, config_json_file, json_str)
        calc_loading_instance.close()
        del calc_loading_instance
        year += 1


def _reorder_dictionary(calc_children):
    """
    Reorders dictionary for readability.

    :param calc_children: dictionary of calc_children
    :type calc_children: dict
    :return: ordered dictionary of calc_children
    :rtype: dict
    """
    calc_children_ordered = OrderedDict()
    for key, value in sorted(calc_children.items(), key=lambda i: i[0]):
        calc_children_ordered[key] = sorted(value)
    json_str = str(
        json.dumps(calc_children_ordered, ensure_ascii=False, indent=4)
    )
    return json_str


def _find_errors(val):
    """
    Entrypoint for the rule. Load the config, search for instances of
    reversed calculation relationships.

    :param val: val from which to gather end dates
    :type val: :class:`arelle.ModelXbrl.ModelXbrl`
    :return: list of model relationshipsets
    :rtype: :class:`arelle.ModelXbrl.ModelRelationshipSet`
    """
    config_json_file = _determine_namespace(val)
    if not config_json_file:
        return
    calc_children = _load_config(config_json_file)
    error_list = []
    if not calc_children:
        _create_config(val)
        calc_children = _load_config(config_json_file)
        if not calc_children:
            return  # nothing can be checked
    # convert children lists into sets for faster "in" function processing
    calc_children = dict(
        (key, set(value))
        for key, value in calc_children.items()
    )
    calc_rels = val.modelXbrl.relationshipSet(
        XbrlConst.summationItem
    ).modelRelationships
    for rel in calc_rels:
        calc_child_rels = calc_children.get(
            rel.toModelObject.qname.localName,
            _EMPTY_LIST
        )
        if rel.fromModelObject.qname.localName in calc_child_rels:
            # ugt has reversed relationship
            error_list.append(rel)
    return error_list


def _run_checks(val):
    """
    Entrypoint for the rule.  Load the config, search for instances of
    reversed calculation relationships.

    :param val: val from which to gather end dates
    :type val: :class:`~arelle.ModelXbrl.ModelXbrl`
    :return: No direct return.  Instead it calls messages with any errors.
    :rtype: None
    """
    errors = _find_errors(val)
    if not errors:
        return
    for error in errors:
        val.modelXbrl.error(
            '{base_key}.{extension_key}'.format(
                base_key=_CODE_NAME,
                extension_key=_RULE_INDEX_KEY
            ),
            messages.get_message(_CODE_NAME, _NO_FACT_KEY),
            extCalcSourceName=error.fromModelObject.label(),
            extCalcTargetName=error.toModelObject.label(),
            ruleVersion=_RULE_VERSION
        )


def _determine_namespace(val):
    """
    Determines which json file to use based off of the
    namespace of the filing.

    :param val: val from which to determine namespace
    :type val: :class:`~arelle.ModelXbrl.ModelXbrl`
    :return: Name of config file to use
    :rtype: String
    """
    NS_2017 = 'http://fasb.org/us-gaap/2017-01-31'
    NS_2016 = 'http://fasb.org/us-gaap/2016-01-31'
    NS_2015 = 'http://fasb.org/us-gaap/2015-01-31'
    NS_2014 = 'http://fasb.org/us-gaap/2014-01-31'
    RESOURCE_DIR = 'resources'
    RULE = 'DQC_US_0008'
    config_json_file = None

    if NS_2017 in val.modelXbrl.namespaceDocs.keys():
        config_json_file = os.path.join(
             os.path.dirname(__file__),
             RESOURCE_DIR,
             RULE,
             'dqc_0008_2017.json'
        )
    elif NS_2016 in val.modelXbrl.namespaceDocs.keys():
        config_json_file = os.path.join(
             os.path.dirname(__file__),
             RESOURCE_DIR,
             RULE,
             'dqc_0008_2016.json'
        )
    elif NS_2015 in val.modelXbrl.namespaceDocs.keys():
        config_json_file = os.path.join(
             os.path.dirname(__file__),
             RESOURCE_DIR,
             RULE,
             'dqc_0008_2015.json'
        )
    elif NS_2014 in val.modelXbrl.namespaceDocs.keys():
        config_json_file = os.path.join(
             os.path.dirname(__file__),
             RESOURCE_DIR,
             RULE,
             'dqc_0008_2014.json'
        )
    return config_json_file


def _load_config(calcs_file):
    """
    Returns a map of axis/configs to test.

    :param axis_file: the file to open.
    :type axis_file: file
    :return: A map of the config file.
    :rtype: dict
    """
    try:
        config = open(calcs_file)
    except FileNotFoundError:
        return False
    return json.load(config)


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': 'Calcs reversed checks.',
    # Mount points
    'Validate.XBRL.Finally': _run_checks,
}
