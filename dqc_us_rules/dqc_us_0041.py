# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
from .util import messages

_CODE_NAME = 'DQC.US.0041'
_RULE_VERSION = '1.0'


def fire_dqc_us_0041_errors(val):
    """
    Fires all the dqc_us_0041 errors returned by _catch_dqc_us_0041_errors

    :param val: ModelXbrl to check if it contains errors
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: No explicit return, but it fires all the dqc_us_0041 errors
    :rtype: None
    """
    for fact in _catch_dqc_us_0041_errors(val.modelXbrl.facts):
        val.modelXbrl.error(
            '{}.16'.format(_CODE_NAME),
            messages.get_message(_CODE_NAME),
            modelObject=[fact],
            ruleVersion=_RULE_VERSION
        )


def _catch_dqc_us_0041_errors(facts_to_check):
    """
    Returns a tuple containing the parts of the dqc_us_0041 error to be
    displayed

    :return: all dqc_us_0041 errors
    """
    taxonomy_default_axis

    for fact in facts_to_check:
        if fact.axis_member != taxonomyAxis:
            yield None


def _is_cache_created():
    """
    Returns true if a cached has been created, otherwise it returns false if
    a cache has not been created

    :return: True is a cache has been created
    :rtype: bool
    """
    return False


def _load_cache():
    """
    Loads the cache if it exists. If the cache doesn't exist then it creates
    a cache and then loads the cache after it is created.

    :return: The loaded cache
    """
    if not _is_cache_created():
        _create_cache()
        return _load_cache()
    return None


def _create_cache():
    """
    Creates a cache in order to save valuable run time

    :return: No explicit return, but this function creates a new cache
    :rtype: None
    """
    return None


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': 'All axis defaults should be the same as the axis '
                   'defaults defined in the taxonomy.',
    # Mount points
    'Validate.XBRL.Finally': fire_dqc_us_0041_errors,
}