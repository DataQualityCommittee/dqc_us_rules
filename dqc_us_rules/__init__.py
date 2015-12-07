# (c) Copyright 2015, XBRL US Inc, All rights reserved   
# See license.md for license information.  
# See PatentNotice.md for patent infringement notice.
import pkgutil
import sys
import inspect


def run_checks(val):
    """
    The function to run all of the validation checks under the SEC package
    """
    plugin_modules = _plugins_to_run(sys.modules[__name__])
    for plugin in plugin_modules:
        if plugin.__file__ is not None and plugin.__file__.find('__init__.py') == -1 and hasattr(plugin, '__pluginInfo__'):
            func = plugin.__pluginInfo__['Validate.XBRL.Finally']
            func(val)


def _plugins_to_run(mod, include_start=True):
    """
    Accepts a module/package and returns an iterator
    that will yield all the submodules (or subpackages)
    of the module/package.

    Set `include_start=False` if you do not want the
    iterator to yield the initial, passed module.
    """
    if inspect.ismodule(mod):
        if include_start:
            yield(mod)

        path = getattr(mod, '__path__', None)
        prefix = mod.__name__ + "."
        if path is not None:
            for importer, modname, _ in pkgutil.iter_modules(path):
                sub_mod = __import__(prefix + modname, fromlist="dummy")
                for m in _plugins_to_run(sub_mod):
                    yield m


__pluginInfo__ = {
    'name': 'DQC.SEC.ALL',
    'version': '1.0',
    'description': '''All Data Quality Committee SEC Filing Checks''',
    'author': '',
    'license': 'See accompanying license text',
    # Required plugin for logging
    'import': ( 'logging/dqcParameters.py', ),
    #Mount points
    'Validate.XBRL.Finally': run_checks,
}
