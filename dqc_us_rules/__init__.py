# (c) Copyright 2015 - 2017, XBRL US Inc. All rights reserved.
# See https://xbrl.us/dqc-license for license information.
# See https://xbrl.us/dqc-patent for patent infringement notice.
import pkgutil
import sys
import inspect


def run_checks(val, *args, **kwargs):
    """
    The function to run all of the validation checks under the SEC package
    """
    if val.disclosureSystem.validationType != "EFM":
        val.modelXbrl.error(
            "dqc_us_rules.exception:disclosureSystem",
            (
                "A disclosureSystem of type EFM is required."
            ),
            modelXbrl=val.modelXbrl,
        )
    plugin_modules = _plugins_to_run(sys.modules[__name__])
    for plugin in plugin_modules:
        try:
            if ((plugin.__file__ is not None and
                 plugin.__file__.find('__init__.py') == -1 and
                 hasattr(plugin, '__pluginInfo__'))):

                func = plugin.__pluginInfo__['Validate.XBRL.Finally']
                func(val, *args, **kwargs)
        except Exception as err:
            # This is an overly generic error catch, but it will hopefully
            # be able to be pared down in the future.
            val.modelXbrl.error(
                "dqc_us_rules.exception:" + type(err).__name__,
                (
                    "Testcase validation exception: "
                    "%(error)s, testcase: %(testcase)s"
                ),
                modelXbrl=val.modelXbrl,
                testcase=val.modelXbrl.modelDocument.basename,
                error=err,
                exc_info=True
            )


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
    'version': '3.6',
    'description': 'All Data Quality Committee SEC Filing Checks',
    'author': '',
    'license': 'See accompanying license text',
    # Required plugin for logging
    'import': ('logging/dqcParameters.py', ),
    # Mount points
    'Validate.XBRL.Finally': run_checks,
}
