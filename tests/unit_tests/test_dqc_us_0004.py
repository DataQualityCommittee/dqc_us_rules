# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import unittest
from datetime import datetime
from dqc_us_rules import dqc_us_0004
from unittest.mock import Mock, patch
import arelle.ModelXbrl


class TestAssetsEqLiabilityEquity(unittest.TestCase):

    @patch('dqc_us_rules.dqc_us_0004.inferredDecimals', return_value=0)
    def test_bv_errors(self, patched_decimals):
        """
        Tests to see if errors right numher of errors are thrown
        """
        asset_concept = Mock()
        asset_concept.qname = dqc_us_0004._ASSETS_CONCEPT
        liabilities_concept = Mock()
        liabilities_concept.qname = dqc_us_0004._LIABILITIES_CONCEPT

        mock_context = Mock(instantDatetime=datetime(2013, 12, 22, 11, 30, 59))

        asset_fact = Mock(
            contextID='valid', context=mock_context, unitID='unit1',
            isNil=False, xValid=True, xValue=1
        )
        liabilities_fact = Mock(
            contextID='valid', context=mock_context, unitID='unit1',
            isNil=False, xValid=True, xValue=100
        )

        mock_name_concepts_dict = {
            dqc_us_0004._ASSETS_CONCEPT: [asset_concept],
            dqc_us_0004._LIABILITIES_CONCEPT: [liabilities_concept]
        }

        mock_facts_by_qname = {
            asset_concept.qname: [asset_fact],
            liabilities_concept.qname: [liabilities_fact]
        }

        model_xbrl = Mock(spec=arelle.ModelXbrl.ModelXbrl)
        model_xbrl.nameConcepts = mock_name_concepts_dict
        model_xbrl.factsByQname = mock_facts_by_qname

        error_count = 0
        for fact in dqc_us_0004._assets_eq_liability_equity(model_xbrl):
            asset, liability = fact
            error_count += 1
            self.assertEqual(asset, asset_fact)
            self.assertEqual(liability, liabilities_fact)

        self.assertEqual(error_count, 1)

        mock_name_concepts_dict_no_liability = {
            dqc_us_0004._ASSETS_CONCEPT: [asset_concept],
            dqc_us_0004._LIABILITIES_CONCEPT: []
        }
        model_xbrl.nameConcepts = mock_name_concepts_dict_no_liability

        error_count = 0
        for _ in dqc_us_0004._assets_eq_liability_equity(model_xbrl):
            error_count += 1
        self.assertEqual(error_count, 0)

    def test_bv_no_errors_duration(self):
        """
        Tests to see if no errors are thrown without a duration on fact
        """
        asset_concept = Mock()
        asset_concept.qname = dqc_us_0004._ASSETS_CONCEPT
        liabilities_concept = Mock()
        liabilities_concept.qname = dqc_us_0004._LIABILITIES_CONCEPT

        mock_context = Mock(instantDatetime=None)

        asset_fact = Mock(
            contextID='valid', context=mock_context, unitID='unit1',
            isNil=False, xValid=True, xValue=1
        )
        liabilities_fact = Mock(
            contextID='valid', context=mock_context, unitID='unit1',
            isNil=False, xValid=True, xValue=2
        )

        mock_name_concepts_dict = {
            dqc_us_0004._ASSETS_CONCEPT: [asset_concept],
            dqc_us_0004._LIABILITIES_CONCEPT: [liabilities_concept]
        }

        mock_facts_by_qname = {
            asset_concept.qname: [asset_fact],
            liabilities_concept.qname: [liabilities_fact]
        }

        model_xbrl = Mock(spec=arelle.ModelXbrl.ModelXbrl)
        model_xbrl.nameConcepts = mock_name_concepts_dict
        model_xbrl.factsByQname = mock_facts_by_qname

        error_count = 0
        for _ in dqc_us_0004._assets_eq_liability_equity(model_xbrl):
            error_count += 1
        self.assertEqual(error_count, 0)

    def test_bv_None_context(self):
        """
        Tests to see if no errors are throws by a none context
        """
        asset_concept = Mock()
        asset_concept.qname = dqc_us_0004._ASSETS_CONCEPT
        liabilities_concept = Mock()
        liabilities_concept.qname = dqc_us_0004._LIABILITIES_CONCEPT

        asset_fact = Mock(
            contextID='valid', context=None, unitID='unit1',
            isNil=False, xValid=True, xValue=1
        )
        liabilities_fact = Mock(
            contextID='valid', context=None, unitID='unit1',
            isNil=False, xValid=True, xValue=2
        )

        mock_name_concepts_dict = {
            dqc_us_0004._ASSETS_CONCEPT: [asset_concept],
            dqc_us_0004._LIABILITIES_CONCEPT: [liabilities_concept]
        }

        mock_facts_by_qname = {
            asset_concept.qname: [asset_fact],
            liabilities_concept.qname: [liabilities_fact]
        }

        model_xbrl = Mock(spec=arelle.ModelXbrl.ModelXbrl)
        model_xbrl.nameConcepts = mock_name_concepts_dict
        model_xbrl.factsByQname = mock_facts_by_qname

        error_count = 0
        for _ in dqc_us_0004._assets_eq_liability_equity(model_xbrl):
            error_count += 1
        self.assertEqual(error_count, 0)

    def test_values_unequal_equal_values(self):
        """
        Tests values_unequal with equal values
        """
        self.assertFalse(dqc_us_0004._values_unequal(100, 100, -1))
        self.assertFalse(dqc_us_0004._values_unequal(130, 100, -2))

    def test_values_unequal_unequal_but_still_equal_values(self):
        """
        Tests values_unequal with values that are calculated to be equal
        """
        self.assertFalse(dqc_us_0004._values_unequal(120, 100, -1))
        self.assertFalse(dqc_us_0004._values_unequal(200, 100, -2))

    def test_values_unequal_very_unequal_values(self):
        """
        Test values_unequal with unequal values
        """
        self.assertTrue(dqc_us_0004._values_unequal(220, 100, -1))
        self.assertTrue(dqc_us_0004._values_unequal(600, 100, -2))

    def test_values_scale_nan(self):
        """
        Make sure that the scale value is not valid if it is Not a Number
        """
        self.assertFalse(dqc_us_0004._min_dec_valid(float('nan')))
        self.assertTrue(dqc_us_0004._min_dec_valid(float(2)))

    def test_values_scale_infinity(self):
        """
        Make sure that the scale value is valid if it is infinity
        """
        self.assertTrue(dqc_us_0004._min_dec_valid(float('inf')))

    def test_values_scale_negative_infinity(self):
        """
        Make sure that the scale value is valid if it is negative infinity
        """
        self.assertTrue(dqc_us_0004._min_dec_valid(float('-inf')))

    def test_values_scale_none(self):
        """
        Make sure that the scale value is not valid if is not None
        """
        self.assertFalse(dqc_us_0004._min_dec_valid(None))

    def test_values_scale_is_zero(self):
        """
        Make sure that the scale value is valid when it is zero
        """
        self.assertTrue(dqc_us_0004._min_dec_valid(0))
