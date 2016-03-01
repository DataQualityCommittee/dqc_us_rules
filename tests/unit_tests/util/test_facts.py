# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.   
# See license.md for license information.  
# See PatentNotice.md for patent infringement notice.
import unittest
from mock import Mock
import src.util.facts
from datetime import date
from decimal import Decimal
import math
from collections import OrderedDict


class TestFilterDuplicateFacts(unittest.TestCase):

    def test_filter_duplicate_facts_None_contextID(self):
        facts = [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True),  # Should be included because no duplicates
                 # Should skip because None contextID
                 Mock(contextID=None, unitID='unit1', isNil=False, xValid=True),
                 Mock(contextID=None, unitID=None, isNil=False, xValid=True),
                 # Shoud skip because empty contextID
                 Mock(contextID=None, unitID='unit1', isNil=False, xValid=True),
                 Mock(contextID=None, unitID=None, isNil=False, xValid=True),
                 ]
        results = src.util.facts.filter_duplicate_facts(facts)
        self.assertEqual(1, len(results))
        self.assertEqual('context1', results[0].contextID)
        self.assertEqual('unit1', results[0].unitID)

    def test_filter_duplicate_facts_duplicate_contextID_unitID(self):
        facts = [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True),  # Should be included because no duplicates
                 # Should skip because duplicate
                 Mock(contextID='context2', unitID='unit1', isNil=False, xValid=True),
                 Mock(contextID='context2', unitID='unit1', isNil=False, xValid=True),
                 # Should include because new unit
                 Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True),
                 Mock(contextID='context2', unitID='unit2', isNil=False, xValid=True),
                 #Should not include because dupes
                 Mock(contextID='context3', unitID=None, isNil=False, xValid=True),
                 Mock(contextID='context3', unitID=None, isNil=False, xValid=True),
                 #Should include because none units
                 Mock(contextID='context1', unitID=None, isNil=False, xValid=True),
                 Mock(contextID='context2', unitID=None, isNil=False, xValid=True),
                 ]
        results = src.util.facts.filter_duplicate_facts(facts)
        self.assertEqual(5, len(results))
        self.assertIn(facts[0], results)
        self.assertIn(facts[3], results)
        self.assertIn(facts[4], results)
        self.assertIn(facts[7], results)
        self.assertIn(facts[8], results)

    def test_ignore_units(self):
        facts = [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True),
                 Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True),
                 Mock(contextID='context2', unitID='unit1', isNil=False, xValid=True)]
        results = src.util.facts.filter_duplicate_facts(facts, ignore_units=True)
        self.assertEqual(1, len(results))
        self.assertEqual('context2', results[0].contextID)
        self.assertEqual('unit1', results[0].unitID)

    def test_isNil_filtering(self):
        facts = [Mock(contextID='context1', unitID='unit1', isNil=True, xValid=True),
                 Mock(contextID='context2', unitID='unit1', isNil=False, xValid=True)]
        results = src.util.facts.filter_duplicate_facts(facts, ignore_units=False)
        self.assertEqual(1, len(results))
        self.assertEqual('context2', results[0].contextID)
        self.assertEqual('unit1', results[0].unitID)

    def test_xValid_filtering(self):
        facts = [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=False),
                 Mock(contextID='context2', unitID='unit1', isNil=False, xValid=True)]
        results = src.util.facts.filter_duplicate_facts(facts, ignore_units=False)
        self.assertEqual(1, len(results))
        self.assertEqual('context2', results[0].contextID)
        self.assertEqual('unit1', results[0].unitID)


class TestPrepareFactsForCalculation(unittest.TestCase):

    def test_prepare_facts_for_calculation_happy_path(self):
        fact_dict = {'concept1': [Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True), Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True)],
                     'concept2': [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True), Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True)],
                     }
        prepared = src.util.facts.prepare_facts_for_calculation(fact_dict)
        self.assertEqual(2, len(prepared))
        for fs in prepared:
            self.assertEqual(2, len(fs))
            self.assertEqual(fs['concept1'].contextID, fs['concept2'].contextID)
            self.assertEqual(fs['concept1'].unitID, fs['concept2'].unitID)

    def test_prepare_facts_for_calculation_mixed_bag(self):
        fact_dict = {'concept1': [Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True), Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True)],
                     'concept2': [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True), Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True)],
                     'concept3': [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True), Mock(contextID='context2', unitID='unit2', isNil=False, xValid=True), Mock(contextID=None, isNil=False, xValid=True)],
                     }
        prepared = src.util.facts.prepare_facts_for_calculation(fact_dict)
        self.assertEqual(1, len(prepared))
        for fs in prepared:
            self.assertEqual(3, len(fs))
            self.assertEqual(fs['concept1'].contextID, fs['concept2'].contextID)
            self.assertEqual(fs['concept1'].contextID, fs['concept3'].contextID)
            self.assertEqual(fs['concept1'].unitID, fs['concept2'].unitID)
            self.assertEqual(fs['concept1'].unitID, fs['concept3'].unitID)

    def test_ignore_units_clean(self):
        fact_dict = {'concept1': [Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True), Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True)],
                     'concept2': [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True), Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True)],
                     'concept3': [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True), Mock(contextID='context2', unitID='unit2', isNil=False, xValid=True), Mock(contextID=None)],
                     }
        prepared = src.util.facts.prepare_facts_for_calculation(fact_dict, unit_ignored_dict={'concept3': True})
        self.assertEqual(2, len(prepared))

    def test_ignore_units(self):
        fact_dict = {'concept1': [Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True), Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True)],
                     'concept2': [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True), Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True)],
                     'concept3': [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True), Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True), Mock(contextID=None, isNil=False, xValid=True)],
                     }
        prepared = src.util.facts.prepare_facts_for_calculation(fact_dict, unit_ignored_dict={'concept3': True})
        self.assertEqual(0, len(prepared))

    def test_ignore_units_single_item(self):
        fact_dict = {'concept1': [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True)],
                     'concept2': [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True)],
                     'concept3': [Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True)],
                     }
        prepared = src.util.facts.prepare_facts_for_calculation(fact_dict, unit_ignored_dict={'concept3': True})
        self.assertEqual(1, len(prepared))

    def test_first_ignored_unit(self):
        pair1 = ('concept1', [Mock(contextID='context1', unitID='unit1', isNil=False, xValid=True)])
        pair2 = ('concept2', [Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True)])
        pair3 = ('concept3', [Mock(contextID='context1', unitID='unit2', isNil=False, xValid=True)])

        fact_dict_ordered = OrderedDict([pair1, pair2, pair3])

        keys = list(fact_dict_ordered.keys())
        self.assertEqual('concept1', keys[0])

        prepared = src.util.facts.prepare_facts_for_calculation(fact_dict_ordered, unit_ignored_dict={'concept1': True})
        self.assertEqual(1, len(prepared))


class TestDei(unittest.TestCase):
    def setUp(self):
        mock_type = Mock()
        mock_type.name = 'textBlockItemType'
        mock_qname = Mock(return_value='{http://xbrl.sec.gov/dei/2014-01-31}DocumentPeriodEndDate',
                          namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
                          localName='DocumentPeriodEndDate')
        mock_concept = Mock(qname=mock_qname,
                            type=mock_type)
        mock_nameConcepts = {'DocumentPeriodEndDate': [mock_concept]}
        mock_segDimVal = {}
        mock_context = Mock(endDatetime=date(2015, 1, 1),
                            segDimValues=mock_segDimVal)
        mock_fact = Mock(context=mock_context,
                         concept=mock_concept,
                         xValue=date(2015, 1, 1))
        mock_factsByQname = {mock_concept.qname: [mock_fact]}
        self.mock_disclosure = Mock(standardTaxonomiesDict={'http://xbrl.sec.gov/dei/2014-01-31': None})
        self.mock_model = Mock(factsByQname=mock_factsByQname,
                               facts=[mock_fact],
                               nameConcepts=mock_nameConcepts)

    def test_lookup_dei(self):
        facts = src.util.facts.lookup_dei_facts('DocumentPeriodEndDate', self.mock_model)
        self.assertEqual(len(facts), 1)
        facts = src.util.facts.lookup_dei_facts('SpamFact', self.mock_model)
        self.assertEqual(len(facts), 0)

    def test_get_facts_with_type(self):
        facts = src.util.facts.get_facts_with_type(['textBlockItemType'], self.mock_model)
        self.assertEqual(len(facts), 1)
        facts = src.util.facts.get_facts_with_type(['eggItemType'], self.mock_model)
        self.assertEqual(len(facts), 0)

    def test_get_facts_dei(self):
        check_list = ['AmendmentDescription', 'AmendmentFlag', 'CurrentFiscalYearEndDate', 'DocumentPeriodEndDate',
                      'DocumentFiscalYearFocus', 'DocumentFiscalPeriodFocus', 'DocumentType', 'EntityRegistrantName',
                      'EntityCentralIndexKey', 'EntityFilerCategory']
        facts = src.util.facts.get_facts_dei(check_list, self.mock_model)
        self.assertEqual(len(facts), 1)


class TestGaap(unittest.TestCase):
    def setUp(self):
        mock_type = Mock()
        mock_type.name = 'textBlockItemType'
        mock_qname = Mock(return_value='{http://fasb.org/us-gaap/2015-01-31}DocumentPeriodEndDate',
                          namespaceURI='http://fasb.org/us-gaap/2015-01-31',
                          localName='DocumentPeriodEndDate')
        mock_concept = Mock(qname=mock_qname,
                            type=mock_type)
        mock_nameConcepts = {'DocumentPeriodEndDate': [mock_concept]}
        mock_segDimVal = {}
        mock_context = Mock(endDatetime=date(2015, 1, 1),
                            segDimValues=mock_segDimVal)
        mock_fact = Mock(context=mock_context,
                         concept=mock_concept,
                         xValue=date(2015, 1, 1))
        mock_factsByQname = {mock_concept.qname: [mock_fact]}
        self.mock_disclosure = Mock(standardTaxonomiesDict={'http://fasb.org/us-gaap/2015-01-31': None})
        self.mock_model = Mock(factsByQname=mock_factsByQname,
                               facts=[mock_fact],
                               nameConcepts=mock_nameConcepts)

    def test_lookup_gaap(self):
        facts = src.util.facts.lookup_gaap_facts('DocumentPeriodEndDate', self.mock_model)
        self.assertEqual(len(facts), 1)
        facts = src.util.facts.lookup_dei_facts('SpamFact', self.mock_model)
        self.assertEqual(len(facts), 0)


class TestScaleValues(unittest.TestCase):

    def test_scale_values_all_inf(self):
        facts = [Mock(decimals='INF', value='3210.9876', xValue=3210.9876, precision=None),
                 Mock(decimals='INF', value='20', xValue=20, precision=None)]
        results = src.util.facts.scale_values(facts)
        expected_results = [3210.9876, 20.00]
        self.assertEqual(expected_results, results)

    def test_scale_values_some_inf(self):
        facts = [Mock(decimals='INF', value='3210.9876', xValue=3210.9876, precision=None),
                 Mock(decimals='2', value='20.00', xValue=20.00, precision=None)]
        results = src.util.facts.scale_values(facts)
        expected_results = [Decimal('3210.99'), Decimal('20.00')]
        self.assertEqual(expected_results, results)

    def test_scale_values_mix(self):
        facts = [Mock(decimals='INF', value='3210.9876', xValue=3210.9876, precision=None),
                 Mock(decimals='2', value='450.00', xValue=450.00, precision=None),
                 Mock(decimals='0', value='50', xValue=50, precision=None),
                 Mock(decimals='-2', value='200', xValue=200, precision=None)]
        results = src.util.facts.scale_values(facts)
        expected_results = [Decimal('3200'), Decimal('400'), Decimal('0'), Decimal('200')]
        self.assertEqual(expected_results, results)

    def test_scale_values_all_same(self):
        facts = [Mock(decimals='2', value='3210.99', xValue=3210.99, precision=None),
                 Mock(decimals='2', value='20.00', xValue=20.00, precision=None),
                 Mock(decimals='2', value='8920.00', xValue=8920.00, precision=None)]
        results = src.util.facts.scale_values(facts)
        expected_results = [3210.99, 20.00, 8920.00]
        self.assertEqual(expected_results, results)

    def test_scale_values_all_missing_decimals(self):
        facts = [Mock(decimals=None, value='3210.99', xValue=3210.99, precision=None),
                 Mock(decimals=None, value='20.00', xValue=20.00, precision=None)]
        results = src.util.facts.scale_values(facts)
        expected_results = [3210.99, 20.00]
        self.assertEqual(expected_results, results)

    def test_scale_values_some_missing_decimals(self):
        facts = [Mock(decimals=None, value='3210.992', xValue=3210.992, precision=None),
                 Mock(decimals=2, value='20.00', xValue=20.00, precision=None)]
        results = src.util.facts.scale_values(facts)
        expected_results = [Decimal('3210.99'), Decimal('20.00')]
        self.assertEqual(expected_results, results)

    def test_scale_values_invalid_values(self):
        facts = [Mock(decimals='INF', value='3210.9876', xValue=3210.9876, precision=None),
                 Mock(decimals='2', value='41.50', xValue=40.00, precision=None),
                 Mock(decimals='-1', value='Fifty units', xValue=None, precision=None)]
        results = src.util.facts.scale_values(facts)
        self.assertTrue(math.isnan(results[2]))
        expected_results = [Decimal('3.21E+3'), Decimal('4E+1')]
        self.assertEqual(expected_results, results[0:2])

    def test_scale_values_negatives(self):
        facts = [Mock(decimals='-1', value='670', xValue=670, precision=None),
                 Mock(decimals='-2', value='6500', xValue=6500, precision=None),
                 Mock(decimals='-3', value='23000', xValue=23000, precision=None)]
        results = src.util.facts.scale_values(facts)
        expected_results = [Decimal('1E+3'), Decimal('6E+3'), Decimal('2.3E+4')]
        self.assertEqual(expected_results, results)

    def test_scale_values_positives(self):
        facts = [Mock(decimals='1', value='6.7', xValue=6.7, precision=None),
                 Mock(decimals='2', value='1.15', xValue=1.15, precision=None),
                 Mock(decimals='2', value='1.25', xValue=1.25, precision=None),
                 Mock(decimals='3', value='2.449', xValue=2.449, precision=None)]
        results = src.util.facts.scale_values(facts)
        expected_results = [Decimal('6.7'), Decimal('1.2'), Decimal('1.2'), Decimal('2.4')]
        self.assertEqual(expected_results, results)


class TestAxisQnames(unittest.TestCase):

    def test_axis_qnames_no_axis(self):
        dim = Mock(dimensionQname='us-gaap:CashCheckAxis')
        segDimValues = {'cashcheckaxis': dim}
        context = Mock(segDimValues=segDimValues)
        fact = Mock(context=context)
        expected = ['us-gaap:CashCheckAxis']
        self.assertEqual(expected, src.util.facts.axis_qnames(fact))

    def test_axis_qnames(self):
        context = Mock(segDimValues={})
        fact = Mock(context=context)
        expected = []
        self.assertEqual(expected, src.util.facts.axis_qnames(fact))


class TestMemberQnames(unittest.TestCase):

    def test_member_qnames(self):
        member = Mock(qname='CashCheckAxis')
        dim = Mock(member=member, isExplicit=True)
        segDimValues = {'cashcheckaxis': dim}
        context = Mock(segDimValues=segDimValues)
        fact = Mock(context=context)
        expected = ['CashCheckAxis']
        self.assertEqual(expected, src.util.facts.member_qnames(fact))
