# (c) Copyright 2015 - 2017, XBRL US Inc. All rights reserved.
# See https://xbrl.us/dqc-license for license information.
# See https://xbrl.us/dqc-patent for patent infringement notice.
from decimal import Decimal
from math import isnan
from .util import facts, messages
from arelle.ValidateXbrlCalcs import inferredDecimals, roundValue

_ASSETS_CONCEPT = 'Assets'
_LIABILITIES_CONCEPT = 'LiabilitiesAndStockholdersEquity'
_CODE_NAME = 'DQC.US.0004'
_RULE_VERSION = '1.0.0'


def assets_eq_liability_equity(val, *args, **kwargs):
    """
    Assets equals Liabilities and Stockholders Equity

    :param val: val to look at the modelXbrl for
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: No direct return, but throws an error for everything returned by
        _assets_eq_liability_equity
    :rtype: None
    """
    for fact in _assets_eq_liability_equity(val.modelXbrl):
        fact_assets, fact_liabilities = fact
        val.modelXbrl.error(
            '{}.16'.format(_CODE_NAME),
            messages.get_message(_CODE_NAME),
            modelObject=[fact_assets, fact_liabilities],
            ruleVersion=_RULE_VERSION
        )


def _assets_eq_liability_equity(model_xbrl):
    """
    Yields fact assets and fact liabilities as long as it is able to

    :param model_xbrl: modelXbrl to check name concepts of
    :type model_xbrl: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: yields fact assets and fact liabilities that should throw errors
    :rtype: tuple
    """
    assets_concept = (
        model_xbrl.nameConcepts[_ASSETS_CONCEPT][0]
        if model_xbrl.nameConcepts[_ASSETS_CONCEPT] else None
    )

    liability_equity_concept = (
        model_xbrl.nameConcepts[_LIABILITIES_CONCEPT][0]
        if model_xbrl.nameConcepts[_LIABILITIES_CONCEPT]
        else None
    )

    if assets_concept is not None and liability_equity_concept is not None:
        assets_facts = model_xbrl.factsByQname[assets_concept.qname]
        liability_equity_facts = (
            model_xbrl.factsByQname[liability_equity_concept.qname]
        )

        fact_dict = dict()
        fact_dict[_ASSETS_CONCEPT] = assets_facts
        fact_dict[_LIABILITIES_CONCEPT] = liability_equity_facts
        fact_groups = facts.prepare_facts_for_calculation(fact_dict)

        for fact_group in fact_groups:
            fact_assets = fact_group[_ASSETS_CONCEPT]
            fact_liabilities = fact_group[_LIABILITIES_CONCEPT]
            if ((fact_assets.context is not None and
                 fact_assets.context.instantDatetime is not None)):
                dec_assets = inferredDecimals(fact_assets)
                dec_liabilities = inferredDecimals(fact_liabilities)
                min_dec = min(dec_assets, dec_liabilities)
                if _values_unequal(
                    fact_assets.xValue, fact_liabilities.xValue, min_dec
                ):
                    yield fact_assets, fact_liabilities


def _min_dec_valid(min_dec):
    """
    Checks to make sure that min_dec values are valid.
    Returns False if min_dec is a None type or if min_dec is Not a number

    :param min_dec: the minumum of dec_assets and dec_liabilities
    :type min_dec: None or int or NaN
    :return: Is min_dec valid
    :rtype: bool
    """

    return min_dec is not None and not isnan(min_dec)


def _values_unequal(val1, val2, dec_scale, margin_scale=2):
    """
    Checks the values for equality based on their scaling.
    Returns False if the values are equal, otherwise True.

    :param val1: first value to round
    :type val1: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param val2: second value to round
    :type val2: :class:'~arelle.ModelXbrl.ModelXbrl'
    :param dec_scale: precision on rounded value
    :type dec_scale: :class:'~decimal.Decimal'
    :param margin_scale: margin of scale for the margin of error
    :type margin_scale: float
    :return: True if the values are not equal
    :rtype: bool
    """

    if not _min_dec_valid(dec_scale):
        return False

    round_val1 = roundValue(val1, decimals=dec_scale)
    round_val2 = roundValue(val2, decimals=dec_scale)
    margin_of_error = (
        Decimal(margin_scale) * (Decimal(10) ** Decimal(-dec_scale))
    )
    return (
        round_val1 < round_val2 - margin_of_error or
        round_val1 > round_val2 + margin_of_error
    )


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': 'Assets should equal Liabilities and Shareholders Equity',
    # Mount points
    'Validate.XBRL.Finally': assets_eq_liability_equity,
}
