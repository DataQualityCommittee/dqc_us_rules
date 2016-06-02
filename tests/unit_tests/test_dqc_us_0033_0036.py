# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
from datetime import date
import unittest
from unittest import mock

from dqc_us_rules import dqc_us_0033_0036
from collections import defaultdict
from arelle.ModelInstanceObject import ModelDimensionValue, ModelFact
from arelle.ModelValue import QName
from arelle.ModelXbrl import ModelXbrl


DEI_NAMESPACE_LIST = [
    'http://xbrl.sec.gov/dei/2014-01-31',
    'http://xbrl.sec.gov/dei/2013-01-31',
    'http://xbrl.sec.gov/dei/2012-01-31',
    'http://xbrl.sec.gov/dei/2011-01-31',
    'http://xbrl.us/dei/2009-01-31'
]


class TestIsValidEOPFact(unittest.TestCase):

    def test_is_valid_eop_fact(self):
        """
        Tests to make sure that _is_valid_eop_fact catches errors
        """
        fact_valid = mock.Mock()
        fact_valid.xValue = date(year=2015, month=1, day=1)
        fact_not_valid1 = None
        fact_not_valid2 = mock.Mock()
        fact_not_valid2.xValue = None
        self.assertTrue(dqc_us_0033_0036._is_valid_eop_fact(fact_valid))
        self.assertFalse(dqc_us_0033_0036._is_valid_eop_fact(fact_not_valid1))
        self.assertFalse(dqc_us_0033_0036._is_valid_eop_fact(fact_not_valid2))


class TestDocPerEndDateChk(unittest.TestCase):

    def setUp(self):
        """
        Sets up values for following unit tests
        """
        m_qn_bad1 = mock.Mock(
            localName='EntityCommonStockSharesOutstanding',
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31'
        )
        m_qn_bad2 = mock.Mock(
            localName='EntityPublicFloat',
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31'
        )
        m_qn_bad3 = mock.Mock(
            localName='DocumentPeriodEndDate',
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31'
        )
        m_qn_good1 = mock.Mock(
            localName='concept1',
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31'
        )
        m_qn_good2 = mock.Mock(
            localName='concept2',
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31'
        )
        m_qn_good3 = mock.Mock(
            localName='concept3',
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31'
        )
        concept_dur1 = mock.Mock(periodType='duration', qname=m_qn_good1)
        concept_dur2 = mock.Mock(periodType='duration', qname=m_qn_good2)
        concept_dur3 = mock.Mock(periodType='duration', qname=m_qn_good3)
        concept_inst1 = mock.Mock(periodType='instant', qname=m_qn_good1)
        concept_inst2 = mock.Mock(periodType='instant', qname=m_qn_good2)
        concept_inst3 = mock.Mock(periodType='instant', qname=m_qn_good3)
        concept_sharesout = mock.Mock(qname=m_qn_bad1)
        concept_pubfloat = mock.Mock(qname=m_qn_bad2)
        concept_enddate = mock.Mock(qname=m_qn_bad3)
        mock_edt_norm = mock.Mock()
        mock_edt_norm.date.return_value = date(year=2015, month=1, day=1)
        mock_segdimvalues = {}
        mock_context = mock.Mock(
            endDatetime=mock_edt_norm, segDimValues=mock_segdimvalues
        )
        self.fact_good1 = mock.Mock(
            concept=concept_dur1, qname=m_qn_good1,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            context=mock_context
        )
        self.fact_good2 = mock.Mock(
            concept=concept_dur2, qname=m_qn_good2,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            context=mock_context
        )
        self.fact_good3 = mock.Mock(
            concept=concept_dur3, qname=m_qn_good3,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            context=mock_context
        )
        self.fact_bad1 = mock.Mock(
            concept=concept_inst1, qname=m_qn_good1,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            context=mock_context
        )
        self.fact_bad2 = mock.Mock(
            concept=concept_inst2, qname=m_qn_good2,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            context=mock_context
        )
        self.fact_bad3 = mock.Mock(
            concept=concept_inst3, qname=m_qn_good3,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            context=mock_context
        )
        self.fact_shares = mock.Mock(
            concept=concept_sharesout, qname=m_qn_bad1,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            context=mock_context
        )
        self.fact_public = mock.Mock(
            concept=concept_pubfloat, qname=m_qn_bad2,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            context=mock_context
        )
        self.fact_end = mock.Mock(
            concept=concept_enddate, qname=m_qn_bad3,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            context=mock_context
        )

    def test_setup_facts(self):
        """
        Tests _setup_facts against expected dped and dei dicts
        """
        mock_model = mock.Mock(
            facts=[
                self.fact_good1, self.fact_good2, self.fact_good3,
                self.fact_bad1, self.fact_bad2, self.fact_bad3,
                self.fact_shares, self.fact_public, self.fact_end
            ]
        )
        expected_dped = defaultdict(list)
        expected_dped[''].extend([self.fact_end])
        expected_dei = defaultdict(list)
        expected_dei[''].extend([
            self.fact_good1, self.fact_good2, self.fact_good3, self.fact_bad1,
            self.fact_bad2, self.fact_bad3
        ])
        res_dped, res_dei = dqc_us_0033_0036._setup_dei_facts(mock_model)
        self.assertEqual(expected_dped, res_dped)
        self.assertEqual(expected_dei, res_dei)

    @mock.patch(
        'dqc_us_rules.dqc_us_0033_0036.dateunionDate',
        side_effect=lambda x, subtractOneDay: x.date()  # noqa
    )
    def test_a_warn(self, mock_func):
        """
        Tests _doc_period_end_date_check to see of the length is right and that
        it returns the correct values
        """
        mock_segdimvalues = {}
        mock_edt_norm = mock.Mock()
        mock_edt_norm.date.return_value = date(year=2015, month=1, day=1)
        mock_dped_context = mock.Mock(
            endDatetime=mock_edt_norm, segDimValues=mock_segdimvalues
        )

        mock_edt_off = mock.Mock()
        mock_edt_off.date.return_value = date(year=2015, month=2, day=1)
        self.fact_end.context = mock_dped_context
        self.fact_end.xValue = mock_edt_off

        mock_model = mock.Mock(
            facts=[
                self.fact_good1, self.fact_good2, self.fact_good3,
                self.fact_bad1, self.fact_bad2, self.fact_bad3,
                self.fact_shares, self.fact_public, self.fact_end
            ]
        )

        res = dqc_us_0033_0036._doc_period_end_date_check(mock_model)
        self.assertEqual(len(res), 1)
        code, message, eop_date, eop_fact, dped_fact = res[0]
        self.assertEqual(code, 'DQC.US.0036.1')

    @mock.patch(
        'dqc_us_rules.dqc_us_0033_0036.dateunionDate',
        side_effect=lambda x, subtractOneDay: x.date()  # noqa
    )
    def test_an_error(self, mock_func):
        """
        Tests _doc_period_end_date_check when it should return an error
        """
        mock_segdimvalues = {}
        mock_edt_norm = mock.Mock()
        mock_edt_norm.date.return_value = date(year=2015, month=1, day=1)
        mock_edt_off = mock.Mock()
        mock_edt_off.date.return_value = date(year=2015, month=1, day=5)
        mock_off_context = mock.Mock(
            endDatetime=mock_edt_off, segDimValues=mock_segdimvalues
        )
        self.fact_end.xValue = mock_edt_norm
        self.fact_good1.context = mock_off_context

        mock_model = mock.Mock(
            facts=[
                self.fact_good1, self.fact_good2, self.fact_good3,
                self.fact_bad1, self.fact_bad2, self.fact_bad3, self.fact_end
            ]
        )
        res = dqc_us_0033_0036._doc_period_end_date_check(mock_model)
        self.assertEqual(len(res), 1)
        code, message, eop_date, eop_fact, dped_fact = res[0]
        self.assertEqual(code, 'DQC.US.0033.2')

    @mock.patch(
        'dqc_us_rules.dqc_us_0033_0036.dateunionDate',
        side_effect=lambda x, subtractOneDay: x.date()  # noqa
    )
    def test_a_warn_and_error_no_dims(self, mock_func):
        """
        Tests _doc_period_end_date_check when it should return a 36 but not a
        33 since there are no dimensions
        """
        mock_segdimvalues = {}

        mock_edt_norm = mock.Mock()
        mock_edt_norm.date.return_value = date(year=2015, month=1, day=1)

        mock_edt_off = mock.Mock()
        # This will cause 36 to fire
        mock_edt_off.date.return_value = date(year=2015, month=1, day=5)
        mock_off_context = mock.Mock(
            endDatetime=mock_edt_off, segDimValues=mock_segdimvalues
        )

        mock_edt_off2 = mock.Mock()
        # This will cause 33 to fire
        mock_edt_off2.date.return_value = date(year=2015, month=1, day=3)
        mock_off2_context = mock.Mock(
            endDatetime=mock_edt_off2, segDimValues=mock_segdimvalues
        )

        m_qn_bad = mock.Mock(
            localName='DocumentPeriodEndDate',
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31'
        )
        concept_enddate = mock.Mock(qname=m_qn_bad)
        mock_dped_off = mock.Mock(
            context=mock_off_context, xValue=mock_edt_off,
            concept=concept_enddate, qname=m_qn_bad,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31'
        )
        self.fact_end.xValue = mock_edt_off

        self.fact_good1.context = mock_off_context  # fact for 36
        self.fact_good2.context = mock_off2_context  # fact for 33
        mock_model = mock.Mock(
            facts=[
                self.fact_good1, self.fact_good2, self.fact_good3,
                self.fact_bad1, self.fact_bad2, self.fact_bad3,
                self.fact_end, mock_dped_off
            ]
        )

        res = dqc_us_0033_0036._doc_period_end_date_check(mock_model)
        self.assertEqual(len(res), 1)  # Only 36 fires since they have no dims

    @mock.patch(
        'dqc_us_rules.dqc_us_0033_0036.dateunionDate',
        side_effect=lambda x, subtractOneDay: x.date()  # noqa
    )
    def test_both_warn_and_error_dimensions(self, mock_func):
        """
        Tests _doc_period_end_date_check when there are dimensions.  This
        should return a 36 and 33(s)
        """
        # Dimensions for the 36 fact
        mock_mem1_qn = mock.Mock(localName='foo')
        mock_dim1_qn = mock.Mock(localName='LegalEntityAxis')
        mock_dim1_dim = mock.Mock(qname=mock_dim1_qn)
        mock_member1 = mock.Mock(qname=mock_mem1_qn)
        mock_dim1 = mock.Mock(
            isExplicit=True, member=mock_member1, dimension=mock_dim1_dim
        )
        mock_more_dims1 = {mock_dim1_dim: mock_dim1}

        # Dimensions for the 33 fact
        mock_mem2_qn = mock.Mock(localName='bar')
        mock_dim2_qn = mock.Mock(localName='LegalEntityAxis')
        mock_dim2_dim = mock.Mock(qname=mock_dim2_qn)
        mock_member2 = mock.Mock(qname=mock_mem2_qn)
        mock_dim2 = mock.Mock(
            isExplicit=True, member=mock_member2, dimension=mock_dim2_dim
        )
        mock_more_dims2 = {mock_dim2_dim: mock_dim2}

        mock_no_dims = {}

        mock_edt_norm = mock.Mock()
        mock_edt_norm.date.return_value = date(year=2015, month=1, day=1)

        # This will cause 36 to fire
        mock_edt_off = mock.Mock()
        mock_edt_off.date.return_value = date(year=2015, month=1, day=5)
        mock_off_context = mock.Mock(
            endDatetime=mock_edt_off, segDimValues=mock_more_dims1
        )

        # This will cause 33 to fire (LEA axis but different member than the
        # DocumentPeriodEndDate (DQC 36) fact)
        mock_edt_off2 = mock.Mock()
        mock_edt_off2.date.return_value = date(year=2015, month=1, day=8)
        mock_off2_context = mock.Mock(
            endDatetime=mock_edt_off2, segDimValues=mock_more_dims2
        )

        # This will cause 33 to fire (no dimensions but date is greater than
        # three days from the DocumentPeriodEndDate
        mock_edt_off3 = mock.Mock()
        mock_edt_off3.date.return_value = date(year=2015, month=1, day=9)
        mock_off3_context = mock.Mock(
            endDatetime=mock_edt_off3, segDimValues=mock_no_dims
        )

        # This will not cause 33 to fire (same LEA axis and member but the
        # context end date is not greater than three days from the
        # DocumentPeriodEndDate)
        mock_edt_off4 = mock.Mock()
        mock_edt_off4.date.return_value = date(year=2015, month=1, day=4)
        mock_off4_context = mock.Mock(
            endDatetime=mock_edt_off4, segDimValues=mock_more_dims1
        )

        m_qn_bad = mock.Mock(
            localName='DocumentPeriodEndDate',
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
        )
        concept_enddate = mock.Mock(qname=m_qn_bad)
        mock_dped_off = mock.Mock(
            context=mock_off_context, xValue=mock_edt_off,
            concept=concept_enddate, qname=m_qn_bad,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            segDimValues=mock_more_dims1
        )

        # fact for 36
        self.fact_end.xValue = mock_edt_off

        # facts for 33 and both will fire
        self.fact_good1.context = mock_off2_context
        self.fact_good3.context = mock_off3_context

        # fact for 33 but won't fire because the context end date is less than
        # three days from the DPED even though it has the same axis/member that
        # DQC 36 fired on
        self.fact_bad1.context = mock_off4_context

        # fact for 33 but won't fire because it is on the exclude list
        self.fact_shares.context = mock_off2_context

        # Setting the dimensions on the fact_end fact
        self.fact_end.context.segDimValues = mock_more_dims1

        mock_model = mock.Mock(
            facts=[
                self.fact_good1, self.fact_good2, self.fact_good3,
                self.fact_bad1, self.fact_bad2, self.fact_bad3,
                self.fact_shares, self.fact_end, mock_dped_off
            ]
        )

        res = dqc_us_0033_0036._doc_period_end_date_check(mock_model)
        # 36 should fire and both 33's should fire because the LEA/member is
        # different on one and the axis/member are completely different (there
        # aren't any dimensions) on the other
        self.assertEqual(len(res), 3)

    @mock.patch(
        'dqc_us_rules.dqc_us_0033_0036.dateunionDate',
        side_effect=lambda x, subtractOneDay: x.date()  # noqa
    )
    def test_33_no_fire_on_lea_that_fires_36(self, moc_func):
        """
        Tests _doc_period_end_date_check to ensure that facts that should fire
        rule 33 do not if rule 36 fires on a Legal Entity Axis and the rule 33
        facts the member of the Legal Entity Axis
        """
        mock_mem_qn = mock.Mock(localName='foo')
        mock_dim_qn = mock.Mock(localName='LegalEntityAxis')
        mock_dim_dim = mock.Mock(qname=mock_dim_qn)
        mock_member = mock.Mock(qname=mock_mem_qn)
        mock_dim = mock.Mock(
            isExplicit=True, member=mock_member, dimension=mock_dim_dim
        )

        mock_more_dims = {mock_dim_dim: mock_dim}

        mock_edt_norm = mock.Mock()
        mock_edt_norm.date.return_value = date(year=2015, month=1, day=1)

        # This will cause 36 to fire
        mock_edt_off = mock.Mock()
        mock_edt_off.date.return_value = date(year=2015, month=1, day=5)
        mock_off_context = mock.Mock(
            endDatetime=mock_edt_off, segDimValues=mock_more_dims
        )

        # This will cause 33 to fire (except it won't in this test as per the
        # reason noted in the docstring)
        mock_edt_off2 = mock.Mock()
        mock_edt_off2.date.return_value = date(year=2015, month=1, day=6)
        mock_off2_context = mock.Mock(
            endDatetime=mock_edt_off2, segDimValues=mock_more_dims
        )

        # This will cause 33 to fire (except it won't in this test as per the
        # reason noted in the docstring)
        mock_edt_off3 = mock.Mock()
        mock_edt_off3.date.return_value = date(year=2015, month=1, day=7)
        mock_off3_context = mock.Mock(
            endDatetime=mock_edt_off3, segDimValues=mock_more_dims
        )

        m_qn_bad = mock.Mock(
            localName='DocumentPeriodEndDate',
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
        )
        concept_enddate = mock.Mock(qname=m_qn_bad)
        mock_dped_off = mock.Mock(
            context=mock_off_context, xValue=mock_edt_off,
            concept=concept_enddate, qname=m_qn_bad,
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            segDimValues=mock_more_dims
        )

        # fact for 36
        self.fact_end.xValue = mock_edt_off

        # facts for 33 but neither will fire because 36 fires on fact_end
        self.fact_good1.context = mock_off2_context
        self.fact_good3.context = mock_off3_context

        # Setting the dimensions on the fact_end fact
        self.fact_end.context.segDimValues = mock_more_dims

        # fact for 33 but won't fire because it is on the exclude list
        self.fact_shares.context = mock_off2_context

        mock_model = mock.Mock(
            facts=[
                self.fact_good1, self.fact_good2, self.fact_good3,
                self.fact_bad1, self.fact_bad2, self.fact_bad3,
                self.fact_shares, self.fact_end, mock_dped_off
            ]
        )

        res = dqc_us_0033_0036._doc_period_end_date_check(mock_model)
        # Only 36 fires because 33 shouldn't fire when 36 fires on a LEA axis
        self.assertEqual(len(res), 1)

    def test_check_for_lea_member(self):
        """
        Test to make sure False (so that the check for rule 33 is not hit) is
        returned when the fact has the legal entity member
        """
        not_valid_dped = ['vault', 'bars', 'foo', 'beam', 'floor', 'boo']
        mock_mem1_qn = mock.Mock(spec=QName)
        mock_mem1_qn.localName = 'foo'
        mock_dim1_qn = mock.Mock(spec=QName)
        mock_dim1_qn.localName = 'LegalEntityAxis'
        mock_dim1_dim = mock.Mock(
            spec=ModelDimensionValue, dimensionQname=mock_dim1_qn
        )
        mock_dimension1 = mock.Mock(
            spec=ModelDimensionValue, isExplicit=True,
            memberQname=mock_mem1_qn, dimension=mock_dim1_dim
        )

        mock_mem2_qn = mock.Mock(spec=QName)
        mock_mem2_qn.localName = 'moo'
        mock_dim2_qn = mock.Mock(spec=QName)
        mock_dim2_qn.localName = 'Scenario'
        mock_dim2_dim = mock.Mock(
            spec=ModelDimensionValue, dimensionQname=mock_dim2_qn
        )
        mock_dimension2 = mock.Mock(
            spec=ModelDimensionValue, isExplicit=True,
            memberQname=mock_mem2_qn, dimension=mock_dim2_dim
        )

        mock_more_dims1 = {mock_dim1_dim: mock_dimension1}
        mock_more_dims2 = {mock_dim2_dim: mock_dimension2}
        mock_no_dimensions = {}

        mock_context1 = mock.Mock(
            spec=ModelXbrl, segDimValues=mock_more_dims1
        )
        mock_context2 = mock.Mock(
            spec=ModelXbrl, segDimValues=mock_more_dims2
        )
        mock_context3 = mock.Mock(
            spec=ModelXbrl, segDimValues=mock_no_dimensions
        )

        self.fact_one = mock.Mock(spec=ModelFact, context=mock_context1)
        self.fact_two = mock.Mock(spec=ModelFact, context=mock_context2)
        self.fact_three = mock.Mock(spec=ModelFact, context=mock_context3)

        self.assertFalse(dqc_us_0033_0036.check_for_lea_member(
            self.fact_one, not_valid_dped
        ))
        self.assertTrue(dqc_us_0033_0036.check_for_lea_member(
            self.fact_two, not_valid_dped
        ))
        self.assertTrue(dqc_us_0033_0036.check_for_lea_member(
            self.fact_three, not_valid_dped
        ))


class TestGetDefaultDped(unittest.TestCase):

    def test_no_dped(self):
        """
        Tests to make sure that _get_default_dped on an empty dict returns None
        """
        self.assertIsNone(dqc_us_0033_0036._get_default_dped({}))

    def test_length_one_dped(self):
        """
        Tests to make sure that _get_default_dped on a dict with a None and a
        string returns the string
        """
        self.assertEqual(
            ['test_case'],
            dqc_us_0033_0036._get_default_dped({'': ['test_case']})
        )

    def test_multi_dped(self):
        """
        Tests to make sure that _get_default_dped return the first non Nil
        string in a dict
        """
        self.assertEqual(
            ['test_case'],
            dqc_us_0033_0036._get_default_dped(
                {'': ['test_case'], 'foo': ['another test case']}
            )
        )
