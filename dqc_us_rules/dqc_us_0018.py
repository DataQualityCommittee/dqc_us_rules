# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import json
import os
import re
import time

from collections import defaultdict

from arelle import XbrlConst, ModelXbrl
from arelle.FileSource import openFileStream, openFileSource, saveFile

_CODE_NAME = 'DQC.US.0018'
_RULE_VERSION = '1.1'

ugtDocs = (
           {
               "year": 2014,
               "namespace": "http://fasb.org/us-gaap/2014-01-31",
               "docLB": "http://xbrl.fasb.org/us-gaap/2014/us-gaap-2014-01-31.zip/us-gaap-2014-01-31/elts/us-gaap-doc-2014-01-31.xml",  # noqa
               "entryXsd": "http://xbrl.fasb.org/us-gaap/2014/us-gaap-2014-01-31.zip/us-gaap-2014-01-31/entire/us-gaap-entryPoint-std-2014-01-31.xsd",  # noqa
            },
           {
               "year": 2015,
               "namespace": "http://fasb.org/us-gaap/2015-01-31",
               "docLB": "http://xbrl.fasb.org/us-gaap/2015/us-gaap-2015-01-31.zip/us-gaap-2015-01-31/elts/us-gaap-doc-2015-01-31.xml",  # noqa
               "entryXsd": "http://xbrl.fasb.org/us-gaap/2015/us-gaap-2015-01-31.zip/us-gaap-2015-01-31/entire/us-gaap-entryPoint-std-2015-01-31.xsd",  # noqa
            },
           {
               "year": 2016,
               "namespace": "http://fasb.org/us-gaap/2016-01-31",
               "docLB": "http://xbrl.fasb.org/us-gaap/2016/us-gaap-2016-01-31.zip/us-gaap-2016-01-31/elts/us-gaap-doc-2016-01-31.xml",  # noqa
               "entryXsd": "http://xbrl.fasb.org/us-gaap/2016/us-gaap-2016-01-31.zip/us-gaap-2016-01-31/entire/us-gaap-entryPoint-std-2016-01-31.xsd",  # noqa
            },
           )


def _load(val):
    val.linroleDefinitionIsDisclosure = re.compile(
        r"-\s+Disclosure\s+-\s", re.IGNORECASE
    )
    val.linkroleDefinitionStatementSheet = re.compile(
        r"[^-]+-\s+Statement\s+-\s+.*", re.IGNORECASE
    )
    val.ugtNamespace = None
    cntlr = val.modelXbrl.modelManager.cntlr
    # load deprecated concepts for filed year of us-gaap
    for ugt in ugtDocs:
        ugt_namespace = ugt["namespace"]
        if ((ugt_namespace in val.modelXbrl.namespaceDocs and
             len(val.modelXbrl.namespaceDocs[ugt_namespace]) > 0)):
            val.ugtNamespace = ugt_namespace
            usgaap_doc = val.modelXbrl.namespaceDocs[ugt_namespace][0]
            deprecations_json_file = os.path.join(
                usgaap_doc.filepathdir,
                os.sep,
                "deprecated-concepts.json"
                )
            file = None
            try:
                file = openFileStream(cntlr,
                                      deprecations_json_file,
                                      'rt',
                                      encoding='utf-8')

                val.usgaapDeprecations = json.load(file)
                file.close()
            except Exception:
                if file:
                    file.close()


def _make(val):
    val.linroleDefinitionIsDisclosure = re.compile(
        r"-\s+Disclosure\s+-\s", re.IGNORECASE
    )
    val.linkroleDefinitionStatementSheet = re.compile(
        r"[^-]+-\s+Statement\s+-\s+.*", re.IGNORECASE
    )
    val.ugtNamespace = None
    cntlr = val.modelXbrl.modelManager.cntlr

    for ugt in ugtDocs:
        deprecations_json_file = os.path.join(
            os.path.dirname(__file__),
            'resources',
            'DQC_US_0018',
            "deprecated-concepts.json"
        )
        
        if not os.path.isfile(deprecations_json_file):
            started_at = time.time()
            ugt_doc_lb = ugt["docLB"]
            val.usgaapDeprecations = {}
            disclosure_system = (
                val.modelXbrl.modelManager.validateDisclosureSystem
            )
            # load without SEC/EFM validation (doc file would not be acceptable)
            prior_validate_disclosure_system = disclosure_system
            val.modelXbrl.modelManager.validateDisclosureSystem = False
            deprecations_instance = ModelXbrl.load(
                val.modelXbrl.modelManager,
                openFileSource(ugt_doc_lb, cntlr),
                _("built deprecations table in cache")  # noqa
            )
            val.modelXbrl.modelManager.validateDisclosureSystem = (
                prior_validate_disclosure_system
            )

            if deprecations_instance is None:
                val.modelXbrl.error("arelle:notLoaded",
                    _("US-GAAP documentation not loaded: %(file)s"),
                    modelXbrl=val, file=os.path.basename(ugt_doc_lb))
            else:
                # load deprecations
                dep_label = 'http://www.xbrl.org/2009/role/deprecatedLabel'
                dep_date_label = (
                    'http://www.xbrl.org/2009/role/deprecatedDateLabel'
                )
                for labelRel in deprecations_instance.relationshipSet(XbrlConst.conceptLabel).modelRelationships:
                    model_documentation = labelRel.toModelObject
                    concept_name = labelRel.fromModelObject.name

                    if model_documentation.role == dep_label:
                        val.usgaapDeprecations[concept_name] = (
                            val.usgaapDeprecations.get(
                                concept_name,
                                ('', ''))[0],
                            model_documentation.text
                        )
                    elif model_documentation.role == dep_date_label:
                        val.usgaapDeprecations[concept_name] = (
                            model_documentation.text,
                            val.usgaapDeprecations.get(
                                concept_name,
                                ('', ''))[1]
                        )
                json_str = str(json.dumps(
                    val.usgaapDeprecations,
                    ensure_ascii=False,
                    indent=0)
                )  # might not be unicode in 2.7
                saveFile(cntlr, deprecations_json_file, json_str)
                deprecations_instance.close()
                del deprecations_instance  # dereference closed modelXbrl
            val.modelXbrl.profileStat(
                _("build us-gaap deprecated concepts cache"),  # noqa
                time.time() - started_at
            )
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