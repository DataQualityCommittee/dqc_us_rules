# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
from .util import messages, facts

import json
import os
import re
import time
from collections import defaultdict

from arelle.ModelDtsObject import ModelConcept
from arelle import ModelXbrl, XbrlConst
from arelle.FileSource import openFileSource, openFileStream, saveFile


_CODE_NAME = 'DQC.US.0041'
_RULE_VERSION = '1.0'


ugtDocs = ({"year": 2012,
            "namespace": "http://fasb.org/us-gaap/2012-01-31",
            "docLB": "http://xbrl.fasb.org/us-gaap/2012/elts/us-gaap-doc-2012-01-31.xml",
            "entryXsd": "http://xbrl.fasb.org/us-gaap/2012/entire/us-gaap-entryPoint-std-2012-01-31.xsd",
            },
           {"year": 2013,
            "namespace": "http://fasb.org/us-gaap/2013-01-31",
            "docLB": "http://xbrl.fasb.org/us-gaap/2013/elts/us-gaap-doc-2013-01-31.xml",
            "entryXsd": "http://xbrl.fasb.org/us-gaap/2013/entire/us-gaap-entryPoint-std-2013-01-31.xsd",
            },
           {"year": 2014,
            "namespace": "http://fasb.org/us-gaap/2014-01-31",
            "docLB": "http://xbrl.fasb.org/us-gaap/2014/elts/us-gaap-doc-2014-01-31.xml",
            "entryXsd": "http://xbrl.fasb.org/us-gaap/2014/entire/us-gaap-entryPoint-std-2014-01-31.xsd",
            },
           {"year": 2015,
            "namespace": "http://fasb.org/us-gaap/2015-01-31",
            "docLB": "http://xbrl.fasb.org/us-gaap/2015/us-gaap-2015-01-31.zip/us-gaap-2015-01-31/elts/us-gaap-doc-2015-01-31.xml",
            "entryXsd": "http://xbrl.fasb.org/us-gaap/2015/us-gaap-2015-01-31.zip/us-gaap-2015-01-31/entire/us-gaap-entryPoint-std-2015-01-31.xsd",
            },
           {"year": 2016,
            "namespace": "http://fasb.org/us-gaap/2016-01-31",
            "docLB": "http://xbrl.fasb.org/us-gaap/2016/us-gaap-2016-01-31.zip/us-gaap-2016-01-31/elts/us-gaap-doc-2016-01-31.xml",
            "entryXsd": "http://xbrl.fasb.org/us-gaap/2016/us-gaap-2016-01-31.zip/us-gaap-2016-01-31/entire/us-gaap-entryPoint-std-2016-01-31.xsd",
            }
           )
#END PATCHED CODE


def setup(val):
    val.linroleDefinitionIsDisclosure = re.compile(r"-\s+Disclosure\s+-\s",
                                                   re.IGNORECASE
                                                   )
    val.linkroleDefinitionStatementSheet = (
        re.compile(r"[^-]+-\s+Statement\s+-\s+.*",re.IGNORECASE)
    )  # no restriction to type of statement

    val.ugtNamespace = None
    cntlr = val.modelXbrl.modelManager.cntlr
    # load deprecated concepts for filed year of us-gaap
    for ugt in ugtDocs:
        ugtNamespace = ugt["namespace"]
        if ugtNamespace in val.modelXbrl.namespaceDocs and len(val.modelXbrl.namespaceDocs[ugtNamespace]) > 0:
            val.ugtNamespace = ugtNamespace
            usgaapDoc = val.modelXbrl.namespaceDocs[ugtNamespace][0]
            ugt_default_dimensions_json_file = (
                usgaapDoc.filepathdir + os.sep + "ugt-default-dimensions.json"
            )

            file = None
            try:
                file = openFileStream(
                    cntlr,
                    ugt_default_dimensions_json_file,
                    'rt',
                    encoding='utf-8'
                )

                val.usgaapDefaultDimensions = json.load(file)
                file.close()
            except Exception:
                if file:
                    file.close()
                val.modelXbrl.modelManager.addToLog(_(
                    "loading us-gaap {0} calculations and default dimensions "
                    "into cache"
                ).format(ugt["year"]))

                startedAt = time.time()
                ugtEntryXsd = ugt["entryXsd"]
                val.usgaapDefaultDimensions = {}
                # load without SEC/EFM validation
                # (doc file would not be acceptable)
                prior_validate_disclosure_system = (
                    val.modelXbrl.modelManager.validateDisclosureSystem
                )
                val.modelXbrl.modelManager.validateDisclosureSystem = False
                calculationsInstance = ModelXbrl.load(
                    val.modelXbrl.modelManager,
                      # "http://xbrl.fasb.org/us-gaap/2012/entire/us-gaap-entryPoint-std-2012-01-31.xsd",
                      # load from zip (especially after caching) is incredibly faster
                    openFileSource(ugtEntryXsd, cntlr),
                     _("built us-gaap calculations cache"))
                val.modelXbrl.modelManager.validateDisclosureSystem = prior_validate_disclosure_system
                if calculationsInstance is None:
                    val.modelXbrl.error("arelle:notLoaded",
                        _("US-GAAP calculations not loaded: %(file)s"),
                        modelXbrl=val, file=os.path.basename(ugtEntryXsd))
                else:
                    # load calculations
                    for ELR in calculationsInstance.relationshipSet(XbrlConst.summationItem).linkRoleUris:
                        elrRelSet = calculationsInstance.relationshipSet(XbrlConst.summationItem, ELR)
                        definition = ""
                        for roleType in calculationsInstance.roleTypes.get(ELR,()):
                            definition = roleType.definition
                            break
                        isStatementSheet = bool(val.linkroleDefinitionStatementSheet.match(definition))
                        elrUgtCalcs = {"#roots": [c.name for c in elrRelSet.rootConcepts],
                                       "#definition": definition,
                                       "#isStatementSheet": isStatementSheet}
                        for relFrom, rels in elrRelSet.fromModelObjects().items():
                            elrUgtCalcs[relFrom.name] = [rel.toModelObject.name for rel in rels]
                        val.usgaapCalculations[ELR] = elrUgtCalcs
                    jsonStr = _STR_UNICODE(json.dumps(val.usgaapCalculations, ensure_ascii=False, indent=0)) # might not be unicode in 2.7
                    saveFile(cntlr, ugtCalcsJsonFile, jsonStr)  # 2.7 gets unicode this way
                    # load default dimensions
                    for defaultDimRel in calculationsInstance.relationshipSet(XbrlConst.dimensionDefault).modelRelationships:
                        if isinstance(defaultDimRel.fromModelObject, ModelConcept) and isinstance(defaultDimRel.toModelObject, ModelConcept):
                            val.usgaapDefaultDimensions[defaultDimRel.fromModelObject.name] = defaultDimRel.toModelObject.name
                    jsonStr = _STR_UNICODE(json.dumps(val.usgaapDefaultDimensions, ensure_ascii=False, indent=0)) # might not be unicode in 2.7
                    saveFile(cntlr, ugtDefaultDimensionsJsonFile, jsonStr)  # 2.7 gets unicode this way
                    calculationsInstance.close()
                    del calculationsInstance # dereference closed modelXbrl
                val.modelXbrl.profileStat(_("build us-gaap calculations and default dimensions cache"), time.time() - startedAt)
            break
    val.deprecatedFactConcepts = defaultdict(list)
    val.deprecatedDimensions = defaultdict(list)
    val.deprecatedMembers = defaultdict(list)


def fire_dqc_us_0041_errors(val):
    """
    Fires all the dqc_us_0041 errors returned by _catch_dqc_us_0041_errors

    :param val: ModelXbrl to check if it contains errors
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: No explicit return, but it fires all the dqc_us_0041 errors
    :rtype: None
    """
    for error_info in _catch_dqc_us_0041_errors(val.modelXbrl.facts):
        axis_name, axis_default_name, def_name = error_info
        val.modelXbrl.error(
            '{}.16'.format(_CODE_NAME),
            messages.get_message(_CODE_NAME),
            modelObject=[axis_name, axis_default_name, def_name],
            axis_name_label="axis_name_value",
            axis_default_name="axis_default_name",
            def_name="def_name",
            ruleVersion=_RULE_VERSION
        )


def _catch_dqc_us_0041_errors(facts_to_check):
    """
    Returns a tuple containing the parts of the dqc_us_0041 error to be
    displayed

    :return: all dqc_us_0041 errors
    """
    taxonomy_axis_default = _load_cache()

    for fact in facts_to_check:
        for axis_qnames in facts.axis_qnames(fact):
            if axis_qnames not in taxonomy_axis_default:
                yield (fact, fact, fact)


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
