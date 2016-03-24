# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
from .util import messages, facts

_CODE_NAME = 'DQC.US.0041'
_RULE_VERSION = '1.0'


def check_for_errors(val):
    for fact in _error():
        val.modelXbrl.error(
            '{}.16'.format(_CODE_NAME),
            messages.get_message(_CODE_NAME),
            modelObject=[fact],
            ruleVersion=_RULE_VERSION
        )


def _error():
    return None


def _load_cache(cached):
    if not cached:
        _create_cache()
        cached = not cached
        return _load_cache()
    return None


def _create_cache():

    return None


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': 'All axis defaults should be the same as the axis default '
                   'defined in the taxonomy.',
    # Mount points
    'Validate.XBRL.Finally': check_for_errors,
}