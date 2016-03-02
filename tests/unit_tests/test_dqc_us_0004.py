# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.   
# See license.md for license information.  
# See PatentNotice.md for patent infringement notice.
import unittest
from datetime import datetime, timedelta
from src.dqc_us_0004 import _assets_eq_liability_equity, _ASSETS_CONCEPT, _LIABILITIES_CONCEPT, _values_unequal, _min_dec_valid
from mock import Mock, patch

class TestAssetsEqLiabilityEquity(unittest.TestCase):

    @patch('src.dqc_us_0004.inferredDecimals', return_value=0)
    def test_bv_errors(self, patched_decimals):
        asset_concept = Mock()
        asset_concept.qname = _ASSETS_CONCEPT
        liabilities_concept = Mock()
        liabilities_concept.qname = _LIABILITIES_CONCEPT

        mock_context = Mock(instantDatetime=datetime(2013, 12, 22, 11, 30, 59))

        asset_fact = Mock(contextID='valid', context=mock_context, unitID='unit1', isNil=False, xValid=True, xValue=1)
        liabilities_fact = Mock(contextID='valid', context=mock_context, unitID='unit1', isNil=False, xValid=True, xValue=100)

        mock_name_concepts_dict = {
            _ASSETS_CONCEPT: [asset_concept],
            _LIABILITIES_CONCEPT: [liabilities_concept]
        }

        mock_facts_by_qname = {
            asset_concept.qname: [asset_fact],
            liabilities_concept.qname: [liabilities_fact]
        }

        modelXbrl = Mock()
        modelXbrl.nameConcepts = mock_name_concepts_dict
        modelXbrl.factsByQname = mock_facts_by_qname

        error_count = 0
        for asset, liability in _assets_eq_liability_equity(modelXbrl):
            error_count += 1
            self.assertEqual(asset, asset_fact)
            self.assertEqual(liability, liabilities_fact)

        self.assertEqual(error_count, 1)

        mock_name_concepts_dict_no_liability = {
            _ASSETS_CONCEPT: [asset_concept],
            _LIABILITIES_CONCEPT: []
        }
        modelXbrl.nameConcepts = mock_name_concepts_dict_no_liability

        error_count = 0
        for asset, liability, date in _assets_eq_liability_equity(modelXbrl):
            error_count += 1
        self.assertEqual(error_count, 0)

    def test_bv_no_errors_duration(self):
        asset_concept = Mock()
        asset_concept.qname = _ASSETS_CONCEPT
        liabilities_concept = Mock()
        liabilities_concept.qname = _LIABILITIES_CONCEPT

        mock_context = Mock(instantDatetime=None)

        asset_fact = Mock(contextID='valid', context=mock_context, unitID='unit1', isNil=False, xValid=True, xValue=1)
        liabilities_fact = Mock(contextID='valid', context=mock_context, unitID='unit1', isNil=False, xValid=True, xValue=2)

        mock_name_concepts_dict = {
            _ASSETS_CONCEPT: [asset_concept],
            _LIABILITIES_CONCEPT: [liabilities_concept]
        }

        mock_facts_by_qname = {
            asset_concept.qname: [asset_fact],
            liabilities_concept.qname: [liabilities_fact]
        }

        modelXbrl = Mock()
        modelXbrl.nameConcepts = mock_name_concepts_dict
        modelXbrl.factsByQname = mock_facts_by_qname

        error_count = 0
        for asset, liability, date in _assets_eq_liability_equity(modelXbrl):
            error_count += 1
        self.assertEqual(error_count, 0)

    def test_bv_None_context(self):
        asset_concept = Mock()
        asset_concept.qname = _ASSETS_CONCEPT
        liabilities_concept = Mock()
        liabilities_concept.qname = _LIABILITIES_CONCEPT

        asset_fact = Mock(contextID='valid', context=None, unitID='unit1', isNil=False, xValid=True, xValue=1)
        liabilities_fact = Mock(contextID='valid', context=None, unitID='unit1', isNil=False, xValid=True, xValue=2)

        mock_name_concepts_dict = {
            _ASSETS_CONCEPT: [asset_concept],
            _LIABILITIES_CONCEPT: [liabilities_concept]
        }

        mock_facts_by_qname = {
            asset_concept.qname: [asset_fact],
            liabilities_concept.qname: [liabilities_fact]
        }

        modelXbrl = Mock()
        modelXbrl.nameConcepts = mock_name_concepts_dict
        modelXbrl.factsByQname = mock_facts_by_qname

        error_count = 0
        for asset, liability, date in _assets_eq_liability_equity(modelXbrl):
            error_count += 1
        self.assertEqual(error_count, 0)

    def test_values_unequal_equal_values(self):
        self.assertFalse(_values_unequal(100, 100, -1))
        self.assertFalse(_values_unequal(130, 100, -2))

    def test_values_unequal_unequal_but_still_equal_values(self):
        self.assertFalse(_values_unequal(120, 100, -1))
        self.assertFalse(_values_unequal(200, 100, -2))

    def test_values_unequal_very_unequal_values(self):
        self.assertTrue(_values_unequal(220, 100, -1))
        self.assertTrue(_values_unequal(600, 100, -2))

    def test_values_scale_nan(self):
        """
        Make sure that the scale value is not valid if it is Not a Number
        """
        self.assert_true(_min_dec_valid(float('nan')))
        self.assert_true(_min_dec_valid(float('nan')))

    def test_values_scale_infinity(self):
        """
        Make sure that the scale value is valid if it is infinity
        """
        self.assert_true(_min_dec_valid(float('inf')))
        self.assert_true(_min_dec_valid(float('inf')))

    def test_values_scale_negative_infinity(self):
        """
        Make sure that the scale value is valid if it is negative infinity
        """
        self.assert_true(_min_dec_valid(float('-inf')))
        self.assert_true(_min_dec_valid(float('-inf')))

    def test_values_scale_none(self):
        """
        Make sure that the scale value is not valid if is not None
        """
        self.assert_false(_min_dec_valid(None))
        self.assert_false(_min_dec_valid(None))

    def test_values_scale_is_zero(self):
        """
        Make sure that the scale value is valid when it is zero
        """
        self.assert_true(_min_dec_valid(100, 100, 0))
        self.assert_true(_min_dec_valid(100, 200, 0))