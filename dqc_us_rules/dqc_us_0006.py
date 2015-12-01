# (c) Copyright 2015, XBRL US Inc, All rights reserved   
# See license.md for license information.  
# See PatentNotice.md for patent infringement notice.
from collections import defaultdict
from datetime import timedelta
from .util import facts, messages

CHECK_TYPES = ['textBlockItemType']
CHECK_DEI = ['AmendmentDescription', 'AmendmentFlag', 'CurrentFiscalYearEndDate', 'DocumentPeriodEndDate',
             'DocumentFiscalYearFocus', 'DocumentFiscalPeriodFocus', 'DocumentType', 'EntityRegistrantName',
             'EntityCentralIndexKey', 'EntityFilerCategory']
DATE_BOUNDS_DICT = {
    "FY": {"min": 340, "max": 390},
    "Q1": {"min": 65, "max": 115},
    "Q2": {"min": 155, "max": 205},
    "Q3": {"min": 245, "max": 295}
}
_CODE_NAME = 'DQC.US.0006'
_RULE_VERSION = '1.0'


def validate_dates_within_periods(val):
    """
    Check Date Ranges are within expected values
    for the fiscal focus period
    """
    doc_type = facts.lookup_dei_facts('DocumentType', val.modelXbrl)
    if len(doc_type) != 1 or 'T' in doc_type[0].xValue:
        # If it is a transitional document, or there is more than one document type declared, we will not run this check.
        return
    dict_of_facts = _date_range_check(CHECK_TYPES, CHECK_DEI, DATE_BOUNDS_DICT, val.modelXbrl)
    for document_fiscal_period_focus, fact_list in dict_of_facts.items():
        for fact in fact_list:
            val.modelXbrl.error('{}.14'.format(_CODE_NAME), messages.get_message(_CODE_NAME), concept=fact.qname,
                                period=document_fiscal_period_focus.xValue,
                                modelObject=[fact, document_fiscal_period_focus],
                                ruleVersion=_RULE_VERSION)


def _date_range_check(check_types, check_dei, date_bounds_dict, modelXbrl):
    """
    Takes two lists of fact names, a dict of date boundaries and modelXbrl and then compiles a list of all
    facts in the modelXbrl that match the names in the supplied name lists. It then compares the context
    date span to the date boundaries for the corresponding document period focus. Any facts with spans less than
    or larger than the supplied boundaries are returned in a dict based on the document period focus.
    """
    facts_in_error = defaultdict(list)
    list_of_facts = facts.LegalEntityAxis_facts_by_member(facts.get_facts_with_type(check_types, modelXbrl))
    list_of_facts = _dict_list_update(list_of_facts, (facts.LegalEntityAxis_facts_by_member(facts.get_facts_dei(check_dei, modelXbrl))))

    dfpf_list = facts.lookup_dei_facts('DocumentFiscalPeriodFocus', modelXbrl)
    dfpf_dict = facts.LegalEntityAxis_facts_by_member(dfpf_list)
    for lea_member, fact_list in list_of_facts.items():
        lookup = lea_member if lea_member in dfpf_dict else facts.LEGALENTITYAXIS_DEFAULT
        if lookup in dfpf_dict:
            focus_l = set([foc for foc in dfpf_dict[lookup] if foc.xValue in date_bounds_dict])
            if len(focus_l) != 1:
                continue
            focus = focus_l.pop()
            min_span = timedelta(days=date_bounds_dict[focus.xValue].get('min'))
            max_span = timedelta(days=date_bounds_dict[focus.xValue].get('max'))
            for fact in fact_list:
                if fact.context.endDatetime is not None and fact.context.startDatetime is not None:
                    span = fact.context.endDatetime - fact.context.startDatetime
                    if span < min_span or span > max_span:
                        facts_in_error[focus].append(fact)
    return facts_in_error


def _dict_list_update(dict_a, dict_b):
    """
    helper for the LEA dictionaries, extends the lists from dict_a with the lists in dict_b.
    """
    for key, val in dict_b.items():
        dict_a[key].extend(val)
    return dict_a


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': '''Checks all of the specified types and concepts for their date ranges to verify the ranges are within expected paramters for the fiscal periods''',
    #Mount points
    'Validate.XBRL.Finally': validate_dates_within_periods,
}
