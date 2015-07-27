# Copyright (c) 2015, Workiva Inc.  All rights reserved
# Copyright (c) 2015, XBRL US Inc.  All rights reserved
import mock
import unittest
import src.dqc_us_0033_0036 as dpedc
from collections import defaultdict
from datetime import date
DEI_NAMESPACE_LIST = ['http://xbrl.sec.gov/dei/2014-01-31', 'http://xbrl.sec.gov/dei/2013-01-31',
                      'http://xbrl.sec.gov/dei/2012-01-31', 'http://xbrl.sec.gov/dei/2011-01-31', 'http://xbrl.us/dei/2009-01-31']


class TestDocPerEndDateChk(unittest.TestCase):

    def setUp(self):
        m_qn_bad1 = mock.Mock(
            localName='EntityCommonStockSharesOutstanding', namespaceURI='http://xbrl.sec.gov/dei/2014-01-31')
        m_qn_bad2 = mock.Mock(
            localName='EntityPublicFloat', namespaceURI='http://xbrl.sec.gov/dei/2014-01-31')
        m_qn_bad3 = mock.Mock(
            localName='DocumentPeriodEndDate', namespaceURI='http://xbrl.sec.gov/dei/2014-01-31')
        m_qn_good1 = mock.Mock(
            localName='concept1', namespaceURI='http://xbrl.sec.gov/dei/2014-01-31')
        m_qn_good2 = mock.Mock(
            localName='concept2', namespaceURI='http://xbrl.sec.gov/dei/2014-01-31')
        m_qn_good3 = mock.Mock(
            localName='concept3', namespaceURI='http://xbrl.sec.gov/dei/2014-01-31')
        concept_dur1 = mock.Mock(periodType='duration', qname=m_qn_good1)
        concept_dur2 = mock.Mock(periodType='duration', qname=m_qn_good2)
        concept_dur3 = mock.Mock(periodType='duration', qname=m_qn_good3)
        concept_inst1 = mock.Mock(periodType='instant', qname=m_qn_good1)
        concept_inst2 = mock.Mock(periodType='instant', qname=m_qn_good2)
        concept_inst3 = mock.Mock(periodType='instant', qname=m_qn_good3)
        concept_SharesOut = mock.Mock(qname=m_qn_bad1)
        concept_PubFloat = mock.Mock(qname=m_qn_bad2)
        concept_EndDate = mock.Mock(qname=m_qn_bad3)
        mock_edt_norm = mock.Mock()
        mock_edt_norm.date.return_value = date(year=2015, month=1, day=1)
        mock_segDimValues = mock.Mock()
        mock_segDimValues.values.return_value = []
        mock_context = mock.Mock(endDatetime=mock_edt_norm, segDimValues=mock_segDimValues)
        self.fact_good1 = mock.Mock(concept=concept_dur1, qname=m_qn_good1,
                                    namespaceURI='http://xbrl.sec.gov/dei/2014-01-31', context=mock_context)
        self.fact_good2 = mock.Mock(concept=concept_dur2, qname=m_qn_good2,
                                    namespaceURI='http://xbrl.sec.gov/dei/2014-01-31', context=mock_context)
        self.fact_good3 = mock.Mock(concept=concept_dur3, qname=m_qn_good3,
                                    namespaceURI='http://xbrl.sec.gov/dei/2014-01-31', context=mock_context)
        self.fact_bad1 = mock.Mock(concept=concept_inst1, qname=m_qn_good1,
                                   namespaceURI='http://xbrl.sec.gov/dei/2014-01-31', context=mock_context)
        self.fact_bad2 = mock.Mock(concept=concept_inst2, qname=m_qn_good2,
                                   namespaceURI='http://xbrl.sec.gov/dei/2014-01-31', context=mock_context)
        self.fact_bad3 = mock.Mock(concept=concept_inst3, qname=m_qn_good3,
                                   namespaceURI='http://xbrl.sec.gov/dei/2014-01-31', context=mock_context)
        self.fact_shares = mock.Mock(concept=concept_SharesOut, qname=m_qn_bad1,
                                     namespaceURI='http://xbrl.sec.gov/dei/2014-01-31', context=mock_context)
        self.fact_public = mock.Mock(concept=concept_PubFloat, qname=m_qn_bad2,
                                     namespaceURI='http://xbrl.sec.gov/dei/2014-01-31', context=mock_context)
        self.fact_end = mock.Mock(concept=concept_EndDate, qname=m_qn_bad3,
                                  namespaceURI='http://xbrl.sec.gov/dei/2014-01-31', context=mock_context)

    def test_setup_facts(self):
        mock_model = mock.Mock(facts=[self.fact_good1, self.fact_good2, self.fact_good3, self.fact_bad1, self.fact_bad2, self.fact_bad3,
                                      self.fact_shares, self.fact_public, self.fact_end])
        expected_dped = defaultdict(list)
        expected_dped[''].extend([self.fact_end])
        expected_dei = defaultdict(list)
        expected_dei[''].extend(
            [self.fact_good1, self.fact_good2, self.fact_good3, self.fact_bad1, self.fact_bad2, self.fact_bad3])

        res_dped, res_dei = dpedc._setup_dei_facts(mock_model)
        self.assertEqual(expected_dped, res_dped)
        self.assertEqual(expected_dei, res_dei)

    @mock.patch('src.dqc_us_0033_0036.dateunionDate', side_effect=lambda x, subtractOneDay: x.date())
    def test_a_warn(self, mock_func):
        mock_segDimValues = mock.Mock()
        mock_segDimValues.values.return_value = []
        mock_edt_norm = mock.Mock()
        mock_edt_norm.date.return_value = date(year=2015, month=1, day=1)
        mock_dped_context = mock.Mock(endDatetime=mock_edt_norm, segDimValues=mock_segDimValues)
        mock_edt_off = mock.Mock()
        mock_edt_off.date.return_value = date(year=2015, month=2, day=1)
        self.fact_end.context = mock_dped_context
        self.fact_end.xValue = mock_edt_off

        mock_model = mock.Mock(facts=[self.fact_good1, self.fact_good2, self.fact_good3, self.fact_bad1, self.fact_bad2, self.fact_bad3,
                                      self.fact_shares, self.fact_public, self.fact_end])

        res = dpedc._doc_period_end_date_check(mock_model)
        self.assertTrue(len(res) == 1)
        code, message, eop_date, eop_fact, dped_fact = res[0]
        self.assertEqual(code, 'DQC.US.0036.1')

    @mock.patch('src.dqc_us_0033_0036.dateunionDate', side_effect=lambda x, subtractOneDay: x.date())
    def test_an_error(self, mock_func):
        mock_segDimValues = mock.Mock()
        mock_segDimValues.values.return_value = []
        mock_edt_norm = mock.Mock()
        mock_edt_norm.date.return_value = date(year=2015, month=1, day=1)
        mock_edt_off = mock.Mock()
        mock_edt_off.date.return_value = date(year=2015, month=2, day=1)
        mock_off_context = mock.Mock(endDatetime=mock_edt_off, segDimValues=mock_segDimValues)
        self.fact_end.xValue = mock_edt_norm
        self.fact_good1.context = mock_off_context

        mock_model = mock.Mock(
            facts=[self.fact_good1, self.fact_good2, self.fact_good3, self.fact_bad1, self.fact_bad2, self.fact_bad3, self.fact_end])
        res = dpedc._doc_period_end_date_check(mock_model)
        self.assertTrue(len(res) == 1)
        code, message, eop_date, eop_fact, dped_fact = res[0]
        self.assertEqual(code, 'DQC.US.0033.2')

    @mock.patch('src.dqc_us_0033_0036.dateunionDate', side_effect=lambda x, subtractOneDay: x.date())
    def test_a_warn_and_error(self, mock_func):
        mock_mem_qn = mock.Mock(localName='foo')
        mock_dim_qn = mock.Mock(localName='LegalEntityAxis')
        mock_dim_dim = mock.Mock(qname=mock_dim_qn)
        mock_member = mock.Mock(qname=mock_mem_qn)
        mock_dim = mock.Mock(isExplicit=True, member=mock_member, dimension=mock_dim_dim)

        mock_more_dims = mock.Mock()
        mock_more_dims.values.return_value = [mock_dim]

        mock_segDimValues = mock.Mock()
        mock_segDimValues.values.return_value = []

        mock_edt_norm = mock.Mock()
        mock_edt_norm.date.return_value = date(year=2015, month=1, day=1)

        mock_edt_off = mock.Mock()
        mock_edt_off.date.return_value = date(year=2015, month=2, day=1)
        mock_off_context = mock.Mock(endDatetime=mock_edt_off, segDimValues=mock_segDimValues)
        mock_off_context_lea = mock.Mock(endDatetime=mock_edt_off, segDimValues=mock_more_dims)

        m_qn_bad = mock.Mock(
            localName='DocumentPeriodEndDate', namespaceURI='http://xbrl.sec.gov/dei/2014-01-31')
        concept_EndDate = mock.Mock(qname=m_qn_bad)
        mock_dped_off = mock.Mock(context=mock_off_context, xValue=mock_edt_off,
                                  concept=concept_EndDate, qname=m_qn_bad, namespaceURI='http://xbrl.sec.gov/dei/2014-01-31')
        self.fact_end.xValue = mock_edt_off

        self.fact_good1.context = mock_off_context
        mock_model = mock.Mock(facts=[self.fact_good1, self.fact_good2, self.fact_good3,
                                      self.fact_bad1, self.fact_bad2, self.fact_bad3, self.fact_end, mock_dped_off])

        res = dpedc._doc_period_end_date_check(mock_model)
        self.assertEqual(len(res), 1)  # Only expect one because test 33 will not happen if 36 fires.


class TestGetDefaultDped(unittest.TestCase):

    def test_no_dped(self):
        self.assertIsNone(dpedc._get_default_dped({}))

    def test_length_one_dped(self):
        self.assertEqual(['test_case'], dpedc._get_default_dped({'': ['test_case']}))

    def test_multi_dped(self):
        self.assertEqual(['test_case'], dpedc._get_default_dped({'': ['test_case'], 'foo': ['another test case']}))
