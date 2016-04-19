# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import json
import re
import time

from collections import defaultdict

from arelle.FileSource import openFileStream

_CODE_NAME = 'DQC.US.0018'
_RULE_VERSION = '1.1'

ugtDocs = (
           {"year": 2014,
            "namespace": "http://fasb.org/us-gaap/2014-01-31",
            "docLB": "http://xbrl.fasb.org/us-gaap/2014/us-gaap-2014-01-31.zip/us-gaap-2014-01-31/elts/us-gaap-doc-2014-01-31.xml",
            "entryXsd": "http://xbrl.fasb.org/us-gaap/2014/us-gaap-2014-01-31.zip/us-gaap-2014-01-31/entire/us-gaap-entryPoint-std-2014-01-31.xsd",
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
            },
           )


def setup(val):
    if not val.validateLoggingSemantic:  # all checks herein are SEMANTIC
        return

    val.linroleDefinitionIsDisclosure = re.compile(r"-\s+Disclosure\s+-\s",
                                                   re.IGNORECASE)
    val.linkroleDefinitionStatementSheet = re.compile(r"[^-]+-\s+Statement\s+-\s+.*", # no restriction to type of statement
                                                      re.IGNORECASE)
    val.ugtNamespace = None
    cntlr = val.modelXbrl.modelManager.cntlr
    # load deprecated concepts for filed year of us-gaap
    for ugt in ugtDocs:
        ugtNamespace = ugt["namespace"]
        if ugtNamespace in val.modelXbrl.namespaceDocs and len(val.modelXbrl.namespaceDocs[ugtNamespace]) > 0:
            val.ugtNamespace = ugtNamespace
            usgaapDoc = val.modelXbrl.namespaceDocs[ugtNamespace][0]
            deprecationsJsonFile = usgaapDoc.filepathdir + os.sep + "deprecated-concepts.json"
            file = None
            try:
                file = openFileStream(cntlr, deprecationsJsonFile, 'rt', encoding='utf-8')
                val.usgaapDeprecations = json.load(file)
                file.close()
            except Exception:
                if file:
                    file.close()
                val.modelXbrl.modelManager.addToLog(_("loading us-gaap {0} deprecated concepts into cache").format(ugt["year"]))
                startedAt = time.time()
                ugtDocLB = ugt["docLB"]
                val.usgaapDeprecations = {}
                # load without SEC/EFM validation (doc file would not be acceptable)
                priorValidateDisclosureSystem = val.modelXbrl.modelManager.validateDisclosureSystem
                val.modelXbrl.modelManager.validateDisclosureSystem = False
                deprecationsInstance = ModelXbrl.load(val.modelXbrl.modelManager,
                      # "http://xbrl.fasb.org/us-gaap/2012/elts/us-gaap-doc-2012-01-31.xml",
                      # load from zip (especially after caching) is incredibly faster
                      openFileSource(ugtDocLB, cntlr),
                      _("built deprecations table in cache"))
                val.modelXbrl.modelManager.validateDisclosureSystem = priorValidateDisclosureSystem
                if deprecationsInstance is None:
                    val.modelXbrl.error("arelle:notLoaded",
                        _("US-GAAP documentation not loaded: %(file)s"),
                        modelXbrl=val, file=os.path.basename(ugtDocLB))
                else:
                    # load deprecations
                    for labelRel in deprecationsInstance.relationshipSet(XbrlConst.conceptLabel).modelRelationships:
                        modelDocumentation = labelRel.toModelObject
                        conceptName = labelRel.fromModelObject.name
                        if modelDocumentation.role == 'http://www.xbrl.org/2009/role/deprecatedLabel':
                            val.usgaapDeprecations[conceptName] = (val.usgaapDeprecations.get(conceptName, ('',''))[0], modelDocumentation.text)
                        elif modelDocumentation.role == 'http://www.xbrl.org/2009/role/deprecatedDateLabel':
                            val.usgaapDeprecations[conceptName] = (modelDocumentation.text, val.usgaapDeprecations.get(conceptName, ('',''))[1])
                    json_str = str(json.dumps(val.usgaapDeprecations, ensure_ascii=False, indent=0)) # might not be unicode in 2.7
                    saveFile(cntlr, deprecationsJsonFile, json_str)  # 2.7 gets unicode this way
                    deprecationsInstance.close()
                    del deprecationsInstance # dereference closed modelXbrl
                val.modelXbrl.profileStat(_("build us-gaap deprecated concepts cache"), time.time() - startedAt)
            break
    val.deprecatedFactConcepts = defaultdict(list)
    val.deprecatedDimensions = defaultdict(list)
    val.deprecatedMembers = defaultdict(list)


def deprecated_facts_errors():
    for errors in _catch_deprecated_errors():
        print("")


def _catch_deprecated_errors():
    yield "sage"

__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': (
        'Checks all of the specified types and concepts for their '
        'date ranges to verify the ranges are within expected '
        'parameters for the fiscal periods'
    ),
    # Mount points
    'Validate.XBRL.Finally': deprecated_facts_errors
}