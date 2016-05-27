# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
from collections import OrderedDict
from datetime import date
from decimal import Decimal
import math
import unittest
from unittest.mock import Mock

from dqc_us_rules.util import facts as fact_lib


class TestFilterDuplicateFacts(unittest.TestCase):

    def test_filter_duplicate_facts_None_contextID(self):
        """
        Tests to see if duplicate facts with a contextID equal to None are
        filtered
        """
        facts = [
            # Should be included because no duplicates
            Mock(
                contextID='context1', unitID='unit1',
                isNil=False, xValid=True
            ),
            # Should skip because None contextID
            Mock(
                contextID=None, unitID='unit1',
                isNil=False, xValid=True
            ),
            Mock(
                contextID=None, unitID=None,
                isNil=False, xValid=True
            ),
            # Should skip because empty contextID
            Mock(
                contextID=None, unitID='unit1',
                isNil=False, xValid=True
            ),
            Mock(
                contextID=None, unitID=None,
                isNil=False, xValid=True
            ),
        ]
        results = fact_lib.filter_duplicate_facts(facts)
        self.assertEqual(1, len(results))
        self.assertEqual('context1', results[0].contextID)
        self.assertEqual('unit1', results[0].unitID)

    def test_filter_duplicate_facts_duplicate_contextID_unitID(self):
        """
        Tests to see if duplicate facts with the same contextID are filtered
        """
        facts = [
            # Should be included because no duplicates
            Mock(
                contextID='context1', unitID='unit1',
                isNil=False, xValid=True
            ),
            # Should skip because duplicate
            Mock(
                contextID='context2', unitID='unit1',
                isNil=False, xValid=True
            ),
            Mock(
                contextID='context2', unitID='unit1',
                isNil=False, xValid=True
            ),
            # Should include because new unit
            Mock(
                contextID='context1', unitID='unit2',
                isNil=False, xValid=True
            ),
            Mock(
                contextID='context2', unitID='unit2',
                isNil=False, xValid=True
            ),
            # Should not include because dupes
            Mock(
                contextID='context3', unitID=None,
                isNil=False, xValid=True
            ),
            Mock(
                contextID='context3', unitID=None,
                isNil=False, xValid=True
            ),
            # Should include because none units
            Mock(
                contextID='context1', unitID=None,
                isNil=False, xValid=True
            ),
            Mock(
                contextID='context2', unitID=None,
                isNil=False, xValid=True
            ),
        ]
        results = fact_lib.filter_duplicate_facts(facts)
        self.assertEqual(5, len(results))
        self.assertIn(facts[0], results)
        self.assertIn(facts[3], results)
        self.assertIn(facts[4], results)
        self.assertIn(facts[7], results)
        self.assertIn(facts[8], results)

    def test_ignore_units(self):
        """
        Test to see if ignore units works when filtering duplicate facts
        """
        facts = [
            Mock(
                contextID='context1', unitID='unit1',
                isNil=False, xValid=True
            ),
            Mock(
                contextID='context1', unitID='unit2',
                isNil=False, xValid=True
            ),
            Mock(
                contextID='context2', unitID='unit1',
                isNil=False, xValid=True
            )
        ]
        results = fact_lib.filter_duplicate_facts(facts, ignore_units=True)
        self.assertEqual(1, len(results))
        self.assertEqual('context2', results[0].contextID)
        self.assertEqual('unit1', results[0].unitID)

    def test_isNil_filtering(self):
        """
        Test to see if isNil filtering correctly works
        """
        facts = [
            Mock(
                contextID='context1', unitID='unit1',
                isNil=True, xValid=True
            ),
            Mock(
                contextID='context2', unitID='unit1',
                isNil=False, xValid=True
            )
        ]
        results = fact_lib.filter_duplicate_facts(facts, ignore_units=False)
        self.assertEqual(1, len(results))
        self.assertEqual('context2', results[0].contextID)
        self.assertEqual('unit1', results[0].unitID)

    def test_xValid_filtering(self):
        """
        Tests to see if xValid filtering works correctly
        """
        facts = [
            Mock(
                contextID='context1', unitID='unit1',
                isNil=False, xValid=False
            ),
            Mock(
                contextID='context2', unitID='unit1',
                isNil=False, xValid=True
            )
        ]
        results = fact_lib.filter_duplicate_facts(facts, ignore_units=False)
        self.assertEqual(1, len(results))
        self.assertEqual('context2', results[0].contextID)
        self.assertEqual('unit1', results[0].unitID)


class TestPrepareFactsForCalculation(unittest.TestCase):

    def test_prepare_facts_for_calculation_happy_path(self):
        """
        Tests to see prepare_facts_for_calculation works correctly when there
        is an easy path
        """
        fact_dict = {
            'concept1': [
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                )
            ],
            'concept2': [
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                )
            ],
        }
        prepared = fact_lib.prepare_facts_for_calculation(fact_dict)
        self.assertEqual(2, len(prepared))
        for fs in prepared:
            self.assertEqual(2, len(fs))
            self.assertEqual(
                fs['concept1'].contextID, fs['concept2'].contextID
            )
            self.assertEqual(fs['concept1'].unitID, fs['concept2'].unitID)

    def test_prepare_facts_for_calculation_mixed_bag(self):
        """
        Tests to see if prepare_facts_for_calculation works when the path is
        not easy
        """
        fact_dict = {
            'concept1': [
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                )
            ],
            'concept2': [
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                )
            ],
            'concept3': [
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context2', unitID='unit2',
                    isNil=False, xValid=True
                ),
                Mock(contextID=None, isNil=False, xValid=True)
            ],
        }
        prepared = fact_lib.prepare_facts_for_calculation(fact_dict)
        self.assertEqual(1, len(prepared))
        for fs in prepared:
            self.assertEqual(3, len(fs))
            self.assertEqual(
                fs['concept1'].contextID, fs['concept2'].contextID
            )
            self.assertEqual(
                fs['concept1'].contextID, fs['concept3'].contextID
            )
            self.assertEqual(fs['concept1'].unitID, fs['concept2'].unitID)
            self.assertEqual(fs['concept1'].unitID, fs['concept3'].unitID)

    def test_ignore_units_clean(self):
        """
        Tests prepare_facts_for_calculation when ignore units is on but nothing
        needs to be ignored
        """
        fact_dict = {
            'concept1': [
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                )
            ],
            'concept2': [
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                )
            ],
            'concept3': [
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context2', unitID='unit2',
                    isNil=False, xValid=True
                ),
                Mock(contextID=None)
            ],
        }
        prepared = fact_lib.prepare_facts_for_calculation(
            fact_dict, unit_ignored_dict={'concept3': True}
        )
        self.assertEqual(2, len(prepared))

    def test_ignore_units(self):
        """
        Tests prepare_facts_for_calculation when ignore units is on
        """
        fact_dict = {
            'concept1': [
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                )
            ],
            'concept2': [
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                )
            ],
            'concept3': [
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                ),
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                ),
                Mock(contextID=None, isNil=False, xValid=True)
            ]
        }
        prepared = fact_lib.prepare_facts_for_calculation(
            fact_dict, unit_ignored_dict={'concept3': True}
        )
        self.assertEqual(0, len(prepared))

    def test_ignore_units_single_item(self):
        """
        Tests prepare_facts_for_calculation when the last item needs to be
        ignored
        """
        fact_dict = {
            'concept1': [
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                )
            ],
            'concept2': [
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                )
            ],
            'concept3': [
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                )
            ],
        }
        prepared = fact_lib.prepare_facts_for_calculation(
            fact_dict, unit_ignored_dict={'concept3': True}
        )
        self.assertEqual(1, len(prepared))

    def test_first_ignored_unit(self):
        """
        Tests prepare_for_calculation when the first item needs to be ignored
        """
        pair1 = (
            'concept1',
            [
                Mock(
                    contextID='context1', unitID='unit1',
                    isNil=False, xValid=True
                )
            ]
        )
        pair2 = (
            'concept2',
            [
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                )
            ]
        )
        pair3 = (
            'concept3',
            [
                Mock(
                    contextID='context1', unitID='unit2',
                    isNil=False, xValid=True
                )
            ]
        )

        fact_dict_ordered = OrderedDict([pair1, pair2, pair3])

        keys = list(fact_dict_ordered.keys())
        self.assertEqual('concept1', keys[0])

        prepared = fact_lib.prepare_facts_for_calculation(
            fact_dict_ordered, unit_ignored_dict={'concept1': True}
        )
        self.assertEqual(1, len(prepared))


class TestDei(unittest.TestCase):
    def setUp(self):
        """
        sets up the values needed for the unit tests
        """
        mock_type = Mock()
        mock_type.name = 'textBlockItemType'
        mock_qname = Mock(
            return_value=(
                '{http://xbrl.sec.gov/dei/2014-01-31}DocumentPeriodEndDate'
            ),
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            localName='DocumentPeriodEndDate'
        )
        mock_concept = Mock(
            qname=mock_qname, type=mock_type
        )
        mock_nameconcepts = {'DocumentPeriodEndDate': [mock_concept]}
        mock_segdimval = {}
        mock_context = Mock(
            endDatetime=date(2015, 1, 1),
            segDimValues=mock_segdimval
        )
        mock_fact = Mock(
            context=mock_context,
            concept=mock_concept,
            xValue=date(2015, 1, 1)
        )
        mock_factsbyqname = {mock_concept.qname: [mock_fact]}
        self.mock_disclosure = Mock(
            standardTaxonomiesDict={'http://xbrl.sec.gov/dei/2014-01-31': None}
        )
        self.mock_model = Mock(
            factsByQname=mock_factsbyqname,
            facts=[mock_fact],
            nameConcepts=mock_nameconcepts
        )

    def test_lookup_dei(self):
        """
        Tests the lookup_dei_facts
        """
        facts = fact_lib.lookup_dei_facts(
            'DocumentPeriodEndDate', self.mock_model
        )
        self.assertEqual(len(facts), 1)
        facts = fact_lib.lookup_dei_facts('SpamFact', self.mock_model)
        self.assertEqual(len(facts), 0)

    def test_get_facts_with_type(self):
        """
        Tests get_facts_with_type
        """
        facts = fact_lib.get_facts_with_type(
            ['textBlockItemType'], self.mock_model
        )
        self.assertEqual(len(facts), 1)
        facts = fact_lib.get_facts_with_type(['eggItemType'], self.mock_model)
        self.assertEqual(len(facts), 0)

    def test_get_facts_dei(self):
        """
        Tests get_facts_dei
        """
        check_list = [
            'AmendmentDescription', 'AmendmentFlag',
            'CurrentFiscalYearEndDate', 'DocumentPeriodEndDate',
            'DocumentFiscalYearFocus', 'DocumentFiscalPeriodFocus',
            'DocumentType', 'EntityRegistrantName',
            'EntityCentralIndexKey', 'EntityFilerCategory'
        ]
        facts = fact_lib.get_facts_dei(check_list, self.mock_model)
        self.assertEqual(len(facts), 1)


class TestGaap(unittest.TestCase):
    def setUp(self):
        """
        Sets up values for the unit tests
        """
        mock_type = Mock()
        mock_type.name = 'textBlockItemType'
        mock_qname = Mock(
            return_value=(
                '{http://fasb.org/us-gaap/2015-01-31}DocumentPeriodEndDate'
            ),
            namespaceURI='http://fasb.org/us-gaap/2015-01-31',
            localName='DocumentPeriodEndDate')
        mock_concept = Mock(qname=mock_qname,
                            type=mock_type)
        mock_nameconcepts = {'DocumentPeriodEndDate': [mock_concept]}
        mock_segdimval = {}
        mock_context = Mock(
            endDatetime=date(2015, 1, 1),
            segDimValues=mock_segdimval
        )
        mock_fact = Mock(
            context=mock_context,
            concept=mock_concept,
            xValue=date(2015, 1, 1)
        )
        mock_factsbyqname = {mock_concept.qname: [mock_fact]}
        self.mock_disclosure = Mock(
            standardTaxonomiesDict={'http://fasb.org/us-gaap/2015-01-31': None}
        )
        self.mock_model = Mock(
            factsByQname=mock_factsbyqname,
            facts=[mock_fact],
            nameConcepts=mock_nameconcepts
        )

    def test_lookup_gaap(self):
        """
        Tests lookup_gaap_facts
        """
        facts = fact_lib.lookup_gaap_facts(
            'DocumentPeriodEndDate', self.mock_model
        )
        self.assertEqual(len(facts), 1)
        facts = fact_lib.lookup_dei_facts('SpamFact', self.mock_model)
        self.assertEqual(len(facts), 0)


class TestScaleValues(unittest.TestCase):

    def test_scale_values_all_inf(self):
        """
        Tests scaling all facts by infinity
        """
        facts = [
            Mock(
                decimals='INF', value='3210.9876',
                xValue=3210.9876, precision=None
            ),
            Mock(
                decimals='INF', value='20',
                xValue=20, precision=None
            )
        ]
        results = fact_lib.scale_values(facts)
        expected_results = [3210.9876, 20.00]
        self.assertEqual(expected_results, results)

    def test_scale_values_some_inf(self):
        """
        Tests scaling some facts by infinity
        """
        facts = [
            Mock(
                decimals='INF', value='3210.9876',
                xValue=3210.9876, precision=None
            ),
            Mock(
                decimals='2', value='20.00',
                xValue=20.00, precision=None
            )
        ]
        results = fact_lib.scale_values(facts)
        expected_results = [Decimal('3210.99'), Decimal('20.00')]
        self.assertEqual(expected_results, results)

    def test_scale_values_mix(self):
        """
        Tests scaling some facts by infinity that are not in order
        """
        facts = [
            Mock(
                decimals='INF', value='3210.9876',
                xValue=3210.9876, precision=None
            ),
            Mock(
                decimals='2', value='450.00',
                xValue=450.00, precision=None
            ),
            Mock(
                decimals='0', value='50',
                xValue=50, precision=None
            ),
            Mock(
                decimals='-2', value='200',
                xValue=200, precision=None
            )
        ]
        results = fact_lib.scale_values(facts)
        expected_results = [
            Decimal('3200'),
            Decimal('400'),
            Decimal('0'),
            Decimal('200')
        ]
        self.assertEqual(expected_results, results)

    def test_scale_values_all_same(self):
        """
        Tests scaling all values by the same value
        """
        facts = [
            Mock(
                decimals='2', value='3210.99',
                xValue=3210.99, precision=None
            ),
            Mock(
                decimals='2', value='20.00',
                xValue=20.00, precision=None
            ),
            Mock(
                decimals='2', value='8920.00',
                xValue=8920.00, precision=None
            )
        ]
        results = fact_lib.scale_values(facts)
        expected_results = [3210.99, 20.00, 8920.00]
        self.assertEqual(expected_results, results)

    def test_scale_values_all_missing_decimals(self):
        """
        Tests scaling without any scale values
        """
        facts = [
            Mock(
                decimals=None, value='3210.99',
                xValue=3210.99, precision=None
            ),
            Mock(
                decimals=None, value='20.00',
                xValue=20.00, precision=None
            )
        ]
        results = fact_lib.scale_values(facts)
        expected_results = [3210.99, 20.00]
        self.assertEqual(expected_results, results)

    def test_scale_values_some_missing_decimals(self):
        """
        Tests scaling with one of the scale values missing
        """
        facts = [
            Mock(
                decimals=None, value='3210.992',
                xValue=3210.992, precision=None
            ),
            Mock(
                decimals=2, value='20.00',
                xValue=20.00, precision=None
            )
        ]
        results = fact_lib.scale_values(facts)
        expected_results = [Decimal('3210.99'), Decimal('20.00')]
        self.assertEqual(expected_results, results)

    def test_scale_values_invalid_values(self):
        """
        Test scaling with values that can't be scaled
        """
        facts = [
            Mock(
                decimals='INF', value='3210.9876',
                xValue=3210.9876, precision=None
            ),
            Mock(
                decimals='2', value='41.50',
                xValue=40.00, precision=None
            ),
            Mock(
                decimals='-1', value='Fifty units',
                xValue=None, precision=None
            )
        ]
        results = fact_lib.scale_values(facts)
        self.assertTrue(math.isnan(results[2]))
        expected_results = [Decimal('3.21E+3'), Decimal('4E+1')]
        self.assertEqual(expected_results, results[0:2])

    def test_scale_values_negatives(self):
        """
        Tests scaling by negative numbers
        """
        facts = [
            Mock(
                decimals='-1', value='670',
                xValue=670, precision=None
            ),
            Mock(
                decimals='-2', value='6500',
                xValue=6500, precision=None
            ),
            Mock(
                decimals='-3', value='23000',
                xValue=23000, precision=None
            )
        ]
        results = fact_lib.scale_values(facts)
        expected_results = [
            Decimal('1E+3'),
            Decimal('6E+3'),
            Decimal('2.3E+4')
        ]
        self.assertEqual(expected_results, results)

    def test_scale_values_positives(self):
        """
        Tests scaling with possitive numbers
        """
        facts = [
            Mock(decimals='1', value='6.7', xValue=6.7, precision=None),
            Mock(decimals='2', value='1.15', xValue=1.15, precision=None),
            Mock(decimals='2', value='1.25', xValue=1.25, precision=None),
            Mock(decimals='3', value='2.449', xValue=2.449, precision=None)
        ]
        results = fact_lib.scale_values(facts)
        expected_results = [
            Decimal('6.7'),
            Decimal('1.2'),
            Decimal('1.2'),
            Decimal('2.4')
        ]
        self.assertEqual(expected_results, results)


class TestAxisQnames(unittest.TestCase):

    def test_axis_qnames_no_axis(self):
        """
        Tests axis_qnames with no axis
        """
        dim = Mock(dimensionQname='us-gaap:CashCheckAxis')
        seg_dim_values = {'cashcheckaxis': dim}
        context = Mock(segDimValues=seg_dim_values)
        fact = Mock(context=context)
        expected = ['us-gaap:CashCheckAxis']
        self.assertEqual(expected, fact_lib.axis_qnames(fact))

    def test_axis_qnames(self):
        """
        Tests axis_qnames with valid axis
        """
        context = Mock(segDimValues={})
        fact = Mock(context=context)
        expected = []
        self.assertEqual(expected, fact_lib.axis_qnames(fact))


class TestMemberQnames(unittest.TestCase):

    def test_member_qnames(self):
        """
        Tests member_qnames with valid member_qnames
        """
        member = Mock(qname='CashCheckAxis')
        dim = Mock(member=member, isExplicit=True)
        segDimValues = {'cashcheckaxis': dim}
        context = Mock(segDimValues=segDimValues)
        fact = Mock(context=context)
        expected = ['CashCheckAxis']
        self.assertEqual(expected, fact_lib.member_qnames(fact))


class TestFactsAreValid(unittest.TestCase):
    def test_fact_components_valid_on_valid_fact(self):
        """
        Tests to make sure that a valid fact still works
        """
        fact = Mock(
            decimals='-4', value='869098', xvalue=869098, precision=None
        )
        self.assertTrue(fact_lib._fact_components_valid(fact))

    def test_fact_components_valid_on_none_type_fact(self):
        """
        Tests to make sure that a None type fact is not valid
        """
        fact = None
        self.assertFalse(fact_lib._fact_components_valid(fact))

    def test_fact_components_valid_on_none_type_context(self):
        """
        Tests to make sure that a Fact with a None type context is not valid
        """
        fact = Mock(decimals='-1', value='670', xValue=670, precision=None)
        fact.context = None
        self.assertFalse(fact_lib._fact_components_valid(fact))

    def test_fact_components_valid_on_none_type_segDimValue(self):
        """
        Tests to make sure that a Fact.context with a None type segDimValue is
        not valid
        """
        fact = Mock(decimals='-2', value='6500', xValue=6500, precision=None)
        fact.context.segDimValues = None
        self.assertFalse(fact_lib._fact_components_valid(fact))


class TestAllFactsUnder(unittest.TestCase):
    def test_all_facts_under(self):
        "Tests that all facts a certain axis/member are returned."
        mock_qname = Mock(localName="foo")
        mock_qname2 = Mock(localName="bar")
        mock_member = Mock(qname=mock_qname)
        mock_dimension = Mock(qname=mock_qname2)
        mock_dim = Mock(
            member=mock_member,
            dimension=mock_dimension,
            isExplicit=True
        )
        segDimValues = {'1': mock_dim}
        mock_context = Mock(segDimValues=segDimValues)
        mock_fact = Mock(context=mock_context)
        mock_modelxbrl = Mock(facts=[mock_fact])
        self.assertEqual(
            fact_lib.axis_member_fact('bar', 'foo', mock_modelxbrl),
            [mock_fact]
        )

        mock_qname3 = Mock(localName="NOPE")
        mock_member2 = Mock(qname=mock_qname3)
        mock_dim2 = Mock(
            member=mock_member2,
            dimension=mock_dimension,
            isExplicit=True
        )
        segDimValues = {'1': mock_dim2, '2': mock_dim2}
        mock_context = Mock(segDimValues=segDimValues)
        mock_fact = Mock(context=mock_context)
        mock_modelxbrl = Mock(facts=[mock_fact])
        self.assertEqual(
            fact_lib.axis_member_fact('bar', 'foo', mock_modelxbrl),
            []
        )
