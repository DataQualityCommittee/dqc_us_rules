# (c) Copyright 2016 - 2017, XBRL US Inc. All rights reserved.
# See https://xbrl.us/dqc-license for license information.
# See https://xbrl.us/dqc-patent for patent infringement notice.
import json
import os

from .util import messages

from arelle import XbrlConst, ModelXbrl
from arelle.ModelDtsObject import ModelConcept
from arelle.FileSource import openFileStream, openFileSource, saveFile


_CODE_NAME = 'DQC.US.0018'
_RULE_VERSION = '3.4.0'
_EARLIEST_US_GAAP_YEAR = 2014

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
    {
        "year": 2017,
        "namespace": "http://fasb.org/us-gaap/2017-01-31",
        # use change notices reference parts instead of doc LB
        "docLB": "http://xbrl.fasb.org/us-gaap/2017/us-gaap-2017-01-31.zip/us-gaap-2017-01-31/elts/us-gaap-cn-ref-2017-01-31.xml",  # noqa
        "entryXsd": "http://xbrl.fasb.org/us-gaap/2017/us-gaap-2017-01-31.zip/us-gaap-2017-01-31/entire/us-gaap-entryPoint-std-2017-01-31.xsd",  # noqa
    },
)


def _load_cache(val):
    """
    Loads the needed deprecated concepts cache into memory

    :param val: ValidateXbrl to load the concepts into
    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl'
    :return: Return True if cache exists, False otherwise.
    :rtype: bool
    """
    cntlr = val.modelXbrl.modelManager.cntlr
    year = _EARLIEST_US_GAAP_YEAR

    for ugt in ugtDocs:
        ugt_namespace = ugt["namespace"]
        if ((ugt_namespace in val.modelXbrl.namespaceDocs and
             len(val.modelXbrl.namespaceDocs[ugt_namespace]) > 0)):
            val.ugtNamespace = ugt_namespace
            deprecations_json_file = os.path.join(
                os.path.dirname(__file__),
                'resources',
                'DQC_US_0018',
                '{}_deprecated-concepts.json'.format(str(year))
            )
            file = None

            try:
                file = openFileStream(
                    cntlr,
                    deprecations_json_file,
                    'rt',
                    encoding='utf-8'
                )

                val.usgaapDeprecations = json.load(file)
                file.close()

            except FileNotFoundError:  # noqa
                if file:
                    file.close()
                # year should be cached. It is not, so return False
                return False
            # year should be cached, and is. Return True
            return True
        year += 1
    # checked all years. No cache found.
    return False


def _create_cache(val):
    """
    Creates the caches needed for dqc_us_0018

    :param val: ValidateXbrl needed in order to save the cache
    :type val: :class: '~arelle.ValidateXbrl.ValidateXbrl'
    :return: no explicit return but creates and saves a cache in
        dqc_us_rule\resources\DQC_US_0018
    :rtype: None
    """
    val.ugtNamespace = None
    cntlr = val.modelXbrl.modelManager.cntlr
    year = _EARLIEST_US_GAAP_YEAR

    for ugt in ugtDocs:
        deprecations_json_file = os.path.join(
            os.path.dirname(__file__),
            'resources',
            'DQC_US_0018',
            '{}_deprecated-concepts.json'.format(str(year))
        )

        if not os.path.isfile(deprecations_json_file):
            ugt_doc_lb = ugt["docLB"]
            val.usgaapDeprecations = {}
            disclosure_system = (
                val.modelXbrl.modelManager.validateDisclosureSystem
            )

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

            if deprecations_instance is not None:
                dep_label = 'http://www.xbrl.org/2009/role/deprecatedLabel'
                dep_date_label = (
                    'http://www.xbrl.org/2009/role/deprecatedDateLabel'
                )
                concept_label = XbrlConst.conceptLabel
                relationship_set = (
                    deprecations_instance.relationshipSet(concept_label)
                )
                model_relationships = relationship_set.modelRelationships

                for labelRel in model_relationships:
                    model_documentation = labelRel.toModelObject
                    concept = labelRel.fromModelObject.name

                    if model_documentation.role == dep_label:
                        val.usgaapDeprecations[concept] = (
                            val.usgaapDeprecations.get(concept, ('', ''))[0],
                            model_documentation.text
                        )
                    elif model_documentation.role == dep_date_label:
                        val.usgaapDeprecations[concept] = (
                            model_documentation.text,
                            val.usgaapDeprecations.get(concept, ('', ''))[1]
                        )
                dep_ref = 'http://fasb.org/us-gaap/role/changeNote/changeNote'
                concept_reference = XbrlConst.conceptReference
                relationship_set = (
                    deprecations_instance.relationshipSet(concept_reference)
                )
                model_relationships = relationship_set.modelRelationships

                for refRel in model_relationships:
                    model_resource = refRel.toModelObject
                    if model_resource.role == dep_ref:
                        concept = refRel.fromModelObject.name
                        for refPart in model_resource.iterchildren():
                            if refPart.localName == "DeprecatedLabel":
                                val.usgaapDeprecations[concept] = (
                                    val.usgaapDeprecations.get(
                                        concept,
                                        ('', ''))[0],
                                    refPart.text
                                )
                            elif refPart.localName == "DeprecatedDate":
                                val.usgaapDeprecations[concept] = (
                                    refPart.text,
                                    val.usgaapDeprecations.get(
                                        concept,
                                        ('', ''))[1]
                                )
                json_str = str(
                    json.dumps(
                        val.usgaapDeprecations,
                        ensure_ascii=False, indent=0, sort_keys=True
                    )
                )  # might not be unicode in 2.7
                saveFile(cntlr, deprecations_json_file, json_str)
                deprecations_instance.close()
                del deprecations_instance  # dereference closed modelXbrl
        year += 1


def deprecated_concept_errors(val, *args, **kwargs):
    """
    Makes error messages for all deprecation errors

    :param val: ValidateXbrl to check for error
    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl'
    :return: No explicit return, though error messages are created
    :rtype: None
    """
    cache_exists = _load_cache(val)
    if not cache_exists:
        _create_cache(val)

    deprecated_concepts = {}
    _catch_deprecated_fact_errors(val, deprecated_concepts)
    _catch_linkbase_deprecated_errors(val, deprecated_concepts)

    for key in deprecated_concepts.keys():
        val.modelXbrl.error(
            '{}.34'.format(_CODE_NAME),
            messages.get_message(_CODE_NAME),
            concept=key,
            modelObject=deprecated_concepts[key],
            ruleVersion=_RULE_VERSION
        )


def _deprecated_concept(val, concept):
    """
    Returns true if the fact uses a deprecated concept

    :param val: ValidateXbrl to check for deprecated items
    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl'
    :param concept: Concept to check
    :type concept: :class:'~arelle.ModelFact.Concept'
    :return: Returns true if the fact uses a deprecated concept
    :rtype: bool
    """
    if not isinstance(concept, ModelConcept):
        return False
    elif ((hasattr(val, 'usgaapDeprecations') and
           concept.name in val.usgaapDeprecations)):
        return True
    return False


def _deprecated_dimension(val, dim_concept):
    """
    Returns true if the fact uses a deprecated dimension

    :param val: ValidateXbrl to check for deprecated dimensions
    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl'
    :param dim_concept: Concept to check
    :type dim_concept: :class:'~arelle.ModelDtsObject.ModelConcept'
    :return: Returns true if the fact uses a deprecated dimension
    :rtype: bool
    """
    if not isinstance(dim_concept, ModelConcept):
        return False
    elif ((hasattr(val, 'usgaapDeprecations') and
           dim_concept.name in val.usgaapDeprecations)):
        return True
    return False


def _deprecated_member(val, model_dim):
    """
    Returns true if the fact uses a deprecated member

    :param val: ValidateXbrl to check for deprecated dimensions
    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl'
    :param modelDim: Concept to check
    :type modelDim: :class:'~arelle.ModelInstanceObject.ModelDimensionValue'
    :return: Returns true if the fact uses a deprecated dimension
    :rtype: bool
    """
    if model_dim.isExplicit:
        member = model_dim.member
        if member is not None and hasattr(val, 'usgaapDeprecations'):
            if member.name in val.usgaapDeprecations:
                return True
    return False


def _fact_checkable(fact):
    """
    Returns true if fact can be checked

    :param fact: Fact to check concept and context for None
    :type fact: :class:'~arelle.ModelDtsObject.ModelFact'
    :return: Returns true if the fact can be checked
    :rtype: bool
    """
    return (
        fact.concept is not None and
        fact.context is not None
    )


def _catch_linkbase_deprecated_errors(val, deprecated_concepts):
    """
    Check for unused concept relationships of standard taxonomy elements
    and catches abstract deprecated concepts in linkbases

    :param val: :class: '~arelle.ValdiateXbrl.ValidateXbrl'
    :return: No Return
    :rtype: None
    """
    relationships = val.modelXbrl.relationshipSet(XbrlConst.parentChild)
    for rel in relationships.modelRelationships:
        for concept in (rel.fromModelObject, rel.toModelObject):
            if _deprecated_concept(val, concept):
                if not deprecated_concepts.get(concept.name):
                    deprecated_concepts[concept.name] = []
                deprecated_concepts[concept.name].append(
                    rel.locatorOf(concept)
                )


def _fact_uses_deprecated_item(val, fact):
    """
    Checks to see if a fact uses a deprecated item

    :param val: ValidateXbrl to check for deprecated items
    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl'
    :param fact: Fact to check
    :type fact: :class:'~arelle.ModelInstanceObject.ModelFact'
    :return: Returns true if fact uses deprecated item,
        as well as the item's name.
    :rtype: tuple(bool, str)
    """

    if _fact_checkable(fact):
        if _deprecated_concept(val, fact.concept):
            return True, fact.concept.name

        if fact.isItem:
            for dimConcept, modelDim in fact.context.segDimValues.items():
                if _deprecated_concept(val, dimConcept):
                    return True, dimConcept.name
                elif _deprecated_dimension(val, modelDim.dimension):
                    return True, modelDim.dimension.name
    return False, None


def _catch_deprecated_fact_errors(val, deprecated_concepts):
    """
    Checks to see if facts are using deprecated items
    :param val: ValidateXbrl to check for deprecated item

    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl'
    :return: No Return
    :rype: None
    """
    for fact in val.modelXbrl.facts:
        fire, item = _fact_uses_deprecated_item(val, fact)
        if fire:
            if not deprecated_concepts.get(item):
                deprecated_concepts[item] = []
            deprecated_concepts[item].append(fact)


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': (
        'Checks all of the specified types and concepts for their '
        'date ranges to verify the ranges are within expected '
        'parameters for the fiscal periods'
    ),
    # Mount points
    'Validate.XBRL.Finally': deprecated_concept_errors
}
