# (c) Copyright 2015, XBRL US Inc, All rights reserved   
# See license.md for license information.  
# See PatentNotice.md for patent infringement notice.
import re
from .util import facts, messages

from arelle.XmlUtil import dateunionValue

LEGALENTITYAXIS_DEFAULT = ''
_dei_pattern = re.compile(r'^http://xbrl\.((sec\.gov)|(us))/dei/\d{4}-\d{2}-\d{2}')
_CODE_NAME = 'DQC.US.0005'
_RULE_VERSION = '1.0'


def _get_end_of_period(val):
    """
    Gets the end of period date (dei:DocumentPeriodEndDate).  Returns the fact value or the context end date on the fact, whichever is later,
    in a tuple with the fact itself and a string representation of the date. The tuple is in a dict keyed off of any LegalEntityAxis members.
    The end of period string is adjusted for viewing to represent the day as expected.  In other words, dates that end in 24:00 will be put at 00:00 of the expected day.

    @return A dictionary of tuples containing the fact, found date and a string representation of that date, keyed off of the LegalEntityAxis members in the format {lea_member: (fact, found_date, date_str)}
    """
    results = {}
    end_of_period_concepts = [c for c in val.modelXbrl.nameConcepts['DocumentPeriodEndDate'] if c.qname.namespaceURI in val.disclosureSystem.standardTaxonomiesDict]
    if len(end_of_period_concepts) == 1:
        end_of_period_dict = facts.LegalEntityAxis_facts_by_member(val.modelXbrl.factsByQname[end_of_period_concepts[0].qname])
        for lea_member, end_of_period_facts in end_of_period_dict.items():
            for fact in end_of_period_facts:
                eop_date = fact.xValue
                # Get maximum of fact value and fact's context end date
                if fact.context is not None:
                    eop_context_end = fact.context.endDatetime
                    date_str = dateunionValue(eop_context_end, subtractOneDay=True)
                    if eop_context_end is not None and (eop_date is None or eop_context_end > eop_date):
                        eop_date = eop_context_end
                        # end dates have a time of 24:00 so adjust them back 1 day
                        date_str = dateunionValue(eop_date, subtractOneDay=True)
                    if lea_member in results:
                        if results[lea_member][1] < eop_date:
                            results[lea_member] = (fact, eop_date, date_str)
                    else:
                        results[lea_member] = (fact, eop_date, date_str)
    return results


def validate_facts(val):
    eop_results = _get_end_of_period(val)
    fact_dict = facts.LegalEntityAxis_facts_by_member(filter(lambda f: f.context is not None, val.modelXbrl.facts))
    for lea_member, fact_list in fact_dict.items():
        lookup = lea_member if lea_member in eop_results else facts.LEGALENTITYAXIS_DEFAULT
        if lookup in eop_results:
            for fact in fact_list:
                fact_date = fact.context.endDatetime  # endDateTime will be the instant date time if this is an instant period
                if fact_date is not None:
                    # Check for the case where a fact is less than the expected eop dates
                    comparison_date = eop_results[lookup][1]
                    if fact_date <= comparison_date:
                        if fact.localName == 'EntityCommonStockSharesOutstanding':
                            # if a fact whose qname is EntityCommonStockSharesOutstanding has an end date prior to eop then fire an error
                            if fact_date < comparison_date:  # Only fire if it is actually less than the comparison date
                                val.modelXbrl.error('{base_code}.17'.format(base_code=_CODE_NAME), messages.get_message(_CODE_NAME, "17"),
                                                    modelObject=[fact] + list(eop_results[lookup]),
                                                    ruleVersion=_RULE_VERSION)
                        elif facts.axis_exists(val, fact, 'SubsequentEventTypeAxis'):
                            val.modelXbrl.error('{base_code}.48'.format(base_code=_CODE_NAME), messages.get_message(_CODE_NAME, "48"),
                                                modelObject=[fact] + list(eop_results[lookup]),
                                                ruleVersion=_RULE_VERSION)
                        elif facts.axis_member_exists(val, fact, 'StatementScenarioAxis', 'ScenarioForecastMember'):
                            val.modelXbrl.error('{base_code}.49'.format(base_code=_CODE_NAME), messages.get_message(_CODE_NAME, "49"),
                                                modelObject=[fact] + list(eop_results[lookup]),
                                                ruleVersion=_RULE_VERSION)

__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': '''A subsequent event test ''',
    #Mount points
    'Validate.XBRL.Finally': validate_facts,
}
