# (c) Copyright 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
from .util import messages

import json
import os
import re
import time

from arelle.ModelDtsObject import ModelConcept
from arelle import XbrlConst, ModelXbrl
from arelle.FileSource import openFileStream, saveFile, openFileSource


_CODE_NAME = 'DQC.US.0041'
_RULE_VERSION = '2.0.0'

_EARLIEST_GAAP_YEAR = 2014

ugtDocs = (
    {
        "year": 2014,
        "namespace": "http://fasb.org/us-gaap/2014-01-31",
        "docLB": "http://xbrl.fasb.org/us-gaap/2014/elts/us-gaap-doc-2014-01-31.xml",  # noqa
        "entryXsd": "http://xbrl.fasb.org/us-gaap/2014/entire/us-gaap-entryPoint-std-2014-01-31.xsd",  # noqa
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
     }
)


def _make_cache(val, ugt, cntlr, ugt_default_dimensions_json_file):
    """
    Creates a new caches for the Taxonomy default dimensions

    :param val: ValidateXbrl to be validated
    :type val: :class: '~arelle.ValidateXbrl.ValidateXbrl'
    :param ugt: Taxonomy to check
    :type ugt: str
    :param ugt_default_dimensions_json_file: location to save json default
        dimensions
    :type ugt_default_dimensions_json_file: str
    :return: no explicit return, but saves caches for dqc_us_0041
    :rtype: None
    """
    started_at = time.time()
    ugt_entry_xsd = ugt["entryXsd"]
    val.usgaapDefaultDimensions = {}
    prior_validate_disclosure_system = (
        val.modelXbrl.modelManager.validateDisclosureSystem
    )
    val.modelXbrl.modelManager.validateDisclosureSystem = False
    ugt_entry_xsd_instance = (
        ModelXbrl.load(
            val.modelXbrl.modelManager,
            openFileSource(ugt_entry_xsd, cntlr),
            _("opened us-gaap entry xsd")  # noqa
        )
    )
    val.modelXbrl.modelManager.validateDisclosureSystem = (
        prior_validate_disclosure_system
    )

    if ugt_entry_xsd_instance is None:
        val.modelXbrl.error(
            "arelle:notLoaded",
            _("US-GAAP entry xsd not loaded: %(file)s"),  # noqa
            modelXbrl=val,
            file=os.path.basename(ugt_entry_xsd)
        )

    else:
        model_relationships = (
            ugt_entry_xsd_instance.relationshipSet(
                XbrlConst.dimensionDefault
            ).modelRelationships
        )
        for default_dim_rel in model_relationships:
            if _default_dim_rel_is_instance(default_dim_rel):
                from_name = default_dim_rel.fromModelObject.name
                to_name = default_dim_rel.toModelObject.name
                val.usgaapDefaultDimensions[from_name] = to_name
        json_str = str(
            json.dumps(
                val.usgaapDefaultDimensions,
                ensure_ascii=False,
                indent=0
            )
        )  # might not be unicode in 2.7
        # 2.7 gets unicode this way
        saveFile(cntlr, ugt_default_dimensions_json_file, json_str)
        ugt_entry_xsd_instance.close()
        del ugt_entry_xsd_instance  # dereference closed modelXbrl
    val.modelXbrl.profileStat(
        _("build default dimensions cache"),  # noqa
        time.time() - started_at
    )


def _setup_cache(val):
    """
    Builds the cache needed for dqc_us_0041. Should only have to build it the
    first time

    :param val: ValidateXbrl to check if it contains errors
    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl'
    :return: No explicit return, but loads the default dimensions of taxonomies
        into memory
    :rtype: None
    """
    val.linroleDefinitionIsDisclosure = (
        re.compile(r"-\s+Disclosure\s+-\s", re.IGNORECASE)
    )

    val.linkroleDefinitionStatementSheet = (
        re.compile(r"[^-]+-\s+Statement\s+-\s+.*", re.IGNORECASE)
    )  # no restriction to type of statement

    val.ugtNamespace = None
    cntlr = val.modelXbrl.modelManager.cntlr

    year = _EARLIEST_GAAP_YEAR
    for ugt in ugtDocs:
        ugt_default_dimensions_json_file = os.path.join(
            os.path.dirname(__file__),
            'resources',
            'DQC_US_0041',
            '{}_ugt-default-dimensions.json'.format(str(year))
        )

        _make_cache(val, ugt, cntlr, ugt_default_dimensions_json_file)

        year += 1


def _is_in_namespace(val, ugt_namespace):
    """
    Returns true if the ugt_namespace is the same as the current vals namespace

    :param val: ValidateXbrl that is being validated
    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl
    :param ugt_namespace: Namespace of taxonomy for current year
    :type ugt_namespace: str
    :return: True if ugt_namespace is in the val.modelXbrl's namespace docs
    :rtype: bool
    """
    return (
        ugt_namespace in val.modelXbrl.namespaceDocs and
        len(val.modelXbrl.namespaceDocs[ugt_namespace]) > 0
    )


def _default_dim_rel_is_instance(default_dim_rel):
    """
    Checks to makes sure that the fromModelObject and the toModelObject's of a
    defaultDimensionRelationship are both ModelConcept's

    :param default_dim_rel: The default dimension relationship to check
    :type default_dim_rel: :class:'~arelle.ModelXbrl.ModelRelationship'
    :return: True if the default_dim_rel.fromModelObject is a ModelConcept and
        the default_dim_rel.toModelObject is a ModelConcept
    :rtype: bool
    """
    return(
        isinstance(default_dim_rel.fromModelObject, ModelConcept) and
        isinstance(default_dim_rel.toModelObject, ModelConcept)
    )


def _load_cache(val):
    """
    Loads the cached taxonomy default demensions. If the file isn't cached yet
    it will create a new cache

    :param val: ValidateXbrl to be validated
    :type val: :class: '~arelle.ValidateXbrl.ValidateXbrl'
    :return: no explicit return, but loads caches for dqc_us_0041
    :rtype: None
    """
    val.linroleDefinitionIsDisclosure = (
        re.compile(r"-\s+Disclosure\s+-\s", re.IGNORECASE)
    )

    val.linkroleDefinitionStatementSheet = (
        re.compile(r"[^-]+-\s+Statement\s+-\s+.*", re.IGNORECASE)
    )  # no restriction to type of statement

    val.ugtNamespace = None
    cntlr = val.modelXbrl.modelManager.cntlr

    year = _EARLIEST_GAAP_YEAR

    for ugt in ugtDocs:
        ugt_namespace = ugt["namespace"]
        if _is_in_namespace(val, ugt_namespace):
            ugt_default_dimensions_json_file = os.path.join(
                os.path.dirname(__file__),
                'resources',
                'DQC_US_0041',
                '{}_ugt-default-dimensions.json'.format(str(year))
            )

            file = None

            try:
                file = openFileStream(
                    cntlr, ugt_default_dimensions_json_file,
                    'rt', encoding='utf-8'
                )

                val.usgaapDefaultDimensions = json.load(file)
                file.close()

            except FileNotFoundError:  # noqa
                if file:
                    file.close()
        year += 1


def fire_dqc_us_0041_errors(val, *args, **kwargs):
    """
    Fires all the dqc_us_0041 errors returned by _catch_dqc_us_0041_errors

    :param val: ValidateXbrl to check if it contains errors
    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl'
    :return: No explicit return, but it fires all the dqc_us_0041 errors
    :rtype: None
    """
    _load_cache(val)

    for error_info in _catch_dqc_us_0041_errors(val):
        axis_name, axis_default_name, def_name = error_info
        val.modelXbrl.error(
            '{}.73'.format(_CODE_NAME),
            messages.get_message(_CODE_NAME),
            axis_name=axis_name,
            axis_default_name=axis_default_name,
            def_name=def_name,
            ruleVersion=_RULE_VERSION
        )


def _check_relationship_exists(rel):
    """
    Makes sure that the relationship won't throw None type errors

    :param rel: relationship to check
    :type rel: :class:'~arelle.ModelXbrl.ModelRelationship'
    :return: Returns true if both the toModelObject and the fromModelObject
        are both instances of ModelConcepts
    :rtype: bool
    """
    return (
        isinstance(rel.toModelObject, ModelConcept) and
        isinstance(rel.fromModelObject, ModelConcept)
    )


def _default_dimension_mismatch(relation, validation):
    """
    Returns true if the default dimension is not included in the usgaap default
    dimensions

    :param relation: dimension to test if it is a usgaap default dimension.
    :type relation: :class:`~arelle.ModelDtsObject.ModelRelationship`
    :param validation: The validation object used to look up the default name.
    :type validation: :class:`~arelle.ValidationObject.ValidateXbrl`
    :return: True if the default dimensions is not included in the usgaap
        default dimensions.
    :rtype: bool
    """
    if ((not hasattr(validation, "usgaapDefaultDimensions") or
         not isinstance(validation.usgaapDefaultDimensions, dict))):
        return False
    has_a_default_name = (
        validation.usgaapDefaultDimensions.get(relation.fromModelObject.name)
        is not None
    )
    is_the_default_name = (
        relation.toModelObject.name !=
        validation.usgaapDefaultDimensions.get(relation.fromModelObject.name)
    )
    if has_a_default_name and is_the_default_name:
        return True
    return False


def _catch_dqc_us_0041_errors(val):
    """
    Returns a tuple containing the parts of the dqc_us_0041 error to be
    displayed

    :param val: ValidateXbrl to check if it contains errors
    :type val: :class:'~arelle.ValidateXbrl.ValidateXbrl'
    :return: all dqc_us_0041 errors
    :rtype: tuple
    """
    _load_cache(val)
    rel_set = val.modelXbrl.relationshipSet(
        XbrlConst.dimensionDefault
    ).modelRelationships
    for relation in rel_set:
        if _check_relationship_exists(relation):
            if _default_dimension_mismatch(relation, val):
                yield (
                    relation.fromModelObject.name,
                    val.usgaapDefaultDimensions.get(
                        relation.fromModelObject.name
                    ),
                    relation.toModelObject.name
                )

__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': (
        'All axis defaults should be the same as the axis '
        'defaults defined in the taxonomy.'
    ),
    # Mount points
    'Validate.XBRL.Finally': fire_dqc_us_0041_errors,
}
