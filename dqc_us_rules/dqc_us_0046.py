# (c) Copyright 2015 - 2017, XBRL US Inc. All rights reserved.
# See https://xbrl.us/dqc-license for license information.
# See https://xbrl.us/dqc-patent for patent infringement notice.
import json
import os
from arelle import XbrlConst
from .util import messages

_CODE_NAME = 'DQC.US.0046'
_RULE_VERSION = '5.0.0'
_RULE_INDEX_KEY = '1'
_NO_FACT_KEY = 'no_fact'
_CONFIG_JSON_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0046',
    'dqc_0046.json'
)
_EMPTY_LIST = []


def _find_errors(val):
    """
    Entrypoint for the rule.  Load the config, search for instances of
    reversed calculation relationships.

    :param val: val from which to gather end dates
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: error_list if errors are found and None otherwise
    :rtype: List or None
    """
    error_list = []
    calc_children = _load_config(_CONFIG_JSON_FILE)
    if not calc_children:
        return  # nothing can be checked
    calc_rels = val.modelXbrl.relationshipSet(
        XbrlConst.summationItem).modelRelationships
    for rel in calc_rels:
        calc_child_rels = calc_children.get(
            rel.fromModelObject.qname.localName,
            _EMPTY_LIST
        )
        if not calc_child_rels:
            continue  # For some reason there are no calcs defined.
        if rel.toModelObject.qname.localName in calc_child_rels:
            error_list.append(rel)
            return error_list


def _run_checks(val):
    """
    Entrypoint for the rule.  Load the config, search for instances of
    reversed calculation relationships.

    :param val: val from which to gather end dates
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: No direct return, instead it calls message with any errors
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


def _load_config(calcs_file):
    """
    Returns a map of axis/configs to test.

    :param axis_file: the file to open.
    :type axis_file: file
    :return: A map of the config file.
    :rtype: dict or None
    """
    try:
        config = open(calcs_file)
    except FileNotFoundError:
        return
    return json.load(config)


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': 'Calcs reversed checks.',
    # Mount points
    'Validate.XBRL.Finally': _run_checks,
}
