# (c) Copyright 2015, XBRL US Inc, All rights reserved   
# See license.md for license information.  
# See PatentNotice.md for patent infringement notice.
from decimal import Decimal

from .util import facts, messages
from arelle.ValidateXbrlCalcs import inferredDecimals, roundValue

_ASSETS_CONCEPT = 'Assets'
_LIABILITIES_CONCEPT = 'LiabilitiesAndStockholdersEquity'
_CODE_NAME = 'DQC.US.0004'
_RULE_VERSION = '1.0'
_TEN = Decimal(10)

def assets_eq_liability_equity(val):
    """
    Assets equals Liabilities and Stockholders Equity
    """
    for fact_assets, fact_liabilities in _assets_eq_liability_equity(val.modelXbrl):
        val.modelXbrl.error('{}.16'.format(_CODE_NAME), messages.get_message(_CODE_NAME),
                            modelObject=[fact_assets, fact_liabilities], ruleVersion=_RULE_VERSION)


def _assets_eq_liability_equity(modelXbrl):
    assets_concept = modelXbrl.nameConcepts[_ASSETS_CONCEPT][0] if modelXbrl.nameConcepts[_ASSETS_CONCEPT] else None
    liability_equity_concept = modelXbrl.nameConcepts[_LIABILITIES_CONCEPT][0] if modelXbrl.nameConcepts[_LIABILITIES_CONCEPT] else None

    if assets_concept is not None and liability_equity_concept is not None:
        assets_facts = modelXbrl.factsByQname[assets_concept.qname]
        liability_equity_facts = modelXbrl.factsByQname[liability_equity_concept.qname]

        fact_dict = {}
        fact_dict[_ASSETS_CONCEPT] = assets_facts
        fact_dict[_LIABILITIES_CONCEPT] = liability_equity_facts
        fact_groups = facts.prepare_facts_for_calculation(fact_dict)

        for fact_group in fact_groups:
            fact_assets = fact_group[_ASSETS_CONCEPT]
            fact_liabilities = fact_group[_LIABILITIES_CONCEPT]
            if fact_assets.context is not None and fact_assets.context.instantDatetime is not None:
                dec_assets = inferredDecimals(fact_assets)
                dec_liabilities = inferredDecimals(fact_liabilities)
                min_dec = min(dec_assets, dec_liabilities)
                if _values_unequal(fact_assets.xValue, fact_liabilities.xValue, min_dec):
                    yield fact_assets, fact_liabilities


def _values_unequal(val1, val2, dec_scale, margin_scale=2):
    """
    Checks the values for equality based on their scaling.
    Returns False if the values are equal, otherwise True.
    """
    round_val1 = roundValue(val1, decimals=dec_scale)
    round_val2 = roundValue(val2, decimals=dec_scale)
    margin_of_error = Decimal(margin_scale) * (_TEN ** Decimal(-dec_scale))
    return round_val1 < round_val2 - margin_of_error or round_val1 > round_val2 + margin_of_error


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': '''Assets should equal Liabilities and Shareholders Equity''',
    #Mount points
    'Validate.XBRL.Finally': assets_eq_liability_equity,
}
