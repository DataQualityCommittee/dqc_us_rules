# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
from .util import messages, facts

import json
import os
import re
import time

from arelle.ModelDtsObject import ModelConcept
from arelle import XbrlConst, ModelXbrl
from arelle.FileSource import openFileStream, saveFile, openFileSource


_CODE_NAME = 'DQC.US.0041'
_RULE_VERSION = '1.0'


ugtDocs = (
    {"year": 2012,
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


def _setup_cache(val):
    val.linroleDefinitionIsDisclosure = (
        re.compile(r"-\s+Disclosure\s+-\s", re.IGNORECASE)
    )

    val.linkroleDefinitionStatementSheet = (
        re.compile(r"[^-]+-\s+Statement\s+-\s+.*", re.IGNORECASE)
    )  # no restriction to type of statement

    val.ugtNamespace = None
    cntlr = val.modelXbrl.modelManager.cntlr

    for ugt in ugtDocs:
        ugt_namespace = ugt["namespace"]

        if ((ugt_namespace in val.modelXbrl.namespaceDocs and
             len(val.modelXbrl.namespaceDocs[ugt_namespace]) > 0
             )):

            usgaapDoc = os.path.join(
                os.path.dirname(__file__),
                'resources',
                'DQC_US_0041'
            )

            ugtCalcsJsonFile = usgaapDoc + os.sep + "ugt-calculations.json"
            ugtDefaultDimensionsJsonFile = usgaapDoc + os.sep + "ugt-default-dimensions.json"
            file = None
            try:
                file = openFileStream(cntlr, ugtCalcsJsonFile, 'rt', encoding='utf-8')
                val.usgaapCalculations = json.load(file)
                file.close()
                file = openFileStream(cntlr, ugtDefaultDimensionsJsonFile, 'rt', encoding='utf-8')
                val.usgaapDefaultDimensions = json.load(file)
                file.close()
            except Exception:
                if file:
                    file.close()
                val.modelXbrl.modelManager.addToLog(_("loading us-gaap {0} calculations and default dimensions into cache").format(ugt["year"]))
                startedAt = time.time()
                ugtEntryXsd = ugt["entryXsd"]
                val.usgaapCalculations = {}
                val.usgaapDefaultDimensions = {}
                priorValidateDisclosureSystem = val.modelXbrl.modelManager.validateDisclosureSystem
                val.modelXbrl.modelManager.validateDisclosureSystem = False
                calculationsInstance = ModelXbrl.load(val.modelXbrl.modelManager,
                      openFileSource(ugtEntryXsd, cntlr),
                      _("built us-gaap calculations cache"))
                val.modelXbrl.modelManager.validateDisclosureSystem = priorValidateDisclosureSystem
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
                    jsonStr = str(json.dumps(val.usgaapCalculations, ensure_ascii=False, indent=0)) # might not be unicode in 2.7
                    saveFile(cntlr, ugtCalcsJsonFile, jsonStr)  # 2.7 gets unicode this way
                    # load default dimensions
                    for defaultDimRel in calculationsInstance.relationshipSet(XbrlConst.dimensionDefault).modelRelationships:
                        if isinstance(defaultDimRel.fromModelObject, ModelConcept) and isinstance(defaultDimRel.toModelObject, ModelConcept):
                            val.usgaapDefaultDimensions[defaultDimRel.fromModelObject.name] = defaultDimRel.toModelObject.name
                    jsonStr = str(json.dumps(val.usgaapDefaultDimensions, ensure_ascii=False, indent=0)) # might not be unicode in 2.7
                    saveFile(cntlr, ugtDefaultDimensionsJsonFile, jsonStr)  # 2.7 gets unicode this way
                    calculationsInstance.close()
                    del calculationsInstance # dereference closed modelXbrl
                val.modelXbrl.profileStat(_("build default dimensions cache"), time.time() - startedAt)
                return


def fire_dqc_us_0041_errors(val):
    """
    Fires all the dqc_us_0041 errors returned by _catch_dqc_us_0041_errors

    :param val: ModelXbrl to check if it contains errors
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: No explicit return, but it fires all the dqc_us_0041 errors
    :rtype: None
    """
    for error_info in _catch_dqc_us_0041_errors(val):
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


def _catch_dqc_us_0041_errors(val):
    """
    Returns a tuple containing the parts of the dqc_us_0041 error to be
    displayed

    :return: all dqc_us_0041 errors
    """
    _setup_cache(val)

    for fact in val.modelXbrl.facts:
        for dim in fact.context.qnameDims.values():
            if dim.dimensionQname.localName not in val.usgaapDefaultDimensions.keys():
                yield (fact, val.usgaapDefaultDimensions, fact)

__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': 'All axis defaults should be the same as the axis '
                   'defaults defined in the taxonomy.',
    # Mount points
    'Validate.XBRL.Finally': fire_dqc_us_0041_errors,
}
