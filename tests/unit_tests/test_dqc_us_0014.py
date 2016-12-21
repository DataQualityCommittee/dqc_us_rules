# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import unittest
from unittest import mock
from dqc_us_rules import util as util

import dqc_us_rules.dqc_us_0014 as dqc_us_0014


class TestDQC0014(unittest.TestCase):
    def setUp(self):
        """
        Sets up values for unit tests
        """
        m_qn_fire1 = mock.Mock(
            localName='DerivativeLiabilities',
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31'
        )
        m_qn_fire2 = mock.Mock(
            localName='Goodwill',
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31'
        )
        m_qn_fire3 = mock.Mock(
            localName='CashDividendsPaidToParentCompany',
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31'
        )
        m_qn_no_fire1 = mock.Mock(
            localName='concept1',
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31'
        )
        m_qn_no_fire2 = mock.Mock(
            localName='concept2',
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31'
        )
        mock_type = mock.Mock()
        mock_type.name = 'monetaryItemType'
        mock_concept1 = mock.Mock(qname=m_qn_fire1, type=mock_type)
        mock_concept2 = mock.Mock(qname=m_qn_fire2, type=mock_type)
        mock_concept3 = mock.Mock(qname=m_qn_fire3, type=mock_type)
        mock_concept4 = mock.Mock(qname=m_qn_no_fire1, type=mock_type)
        mock_concept5 = mock.Mock(qname=m_qn_fire2, type='textBlockItemType')
        mock_concept6 = mock.Mock(qname=m_qn_no_fire2, type='booleanItemType')
        mock_mem1_qn = mock.Mock(localName='InterestRateContractMember')
        mock_dim1_qn = mock.Mock(localName='DerivativeInstrumentRiskAxis')
        mock_mem2_qn = mock.Mock(
            localName='IndefiniteLivedIntangibleAssetsByMajorClassAxis'
        )
        mock_dim2_qn = mock.Mock(localName='OtherIntangibleAssetsMember')
        mock_mem3_qn = mock.Mock(localName='DividendsAxis')
        mock_dim3_qn = mock.Mock(localName='DividendPaidMember')
        mock_dim1_dim = mock.Mock(qname=mock_dim1_qn)
        mock_member1 = mock.Mock(qname=mock_mem1_qn)
        mock_dim2_dim = mock.Mock(qname=mock_dim2_qn)
        mock_member2 = mock.Mock(qname=mock_mem2_qn)
        mock_dim3_dim = mock.Mock(qname=mock_dim3_qn)
        mock_member3 = mock.Mock(qname=mock_mem3_qn)
        mock_dim1 = mock.Mock(
            isExplicit=True, member=mock_member1, dimension=mock_dim1_dim
        )
        mock_dim2 = mock.Mock(
            isExplicit=True, member=mock_member2, dimension=mock_dim2_dim
        )
        mock_dim3 = mock.Mock(
            isExplicit=True, member=mock_member3, dimension=mock_dim3_dim
        )
        mock_dimensions1 = [mock_dim1]
        mock_dimensions2 = [mock_dim2]
        mock_dimensions3 = [mock_dim3]
        mock_no_dimensions = []
        mock_context1 = mock.Mock(segDimValues=mock_dimensions1)
        mock_context2 = mock.Mock(segDimValues=mock_dimensions2)
        mock_context3 = mock.Mock(segDimValues=mock_dimensions3)
        mock_context4 = mock.Mock(segDimValues=mock_no_dimensions)

        # Fact is numeric, has NEGATIVE value, concept in blacklist,
        # and HAS dimensions = No Fire neg num check
        self.fact_one = mock.Mock(
            concept=mock_concept1, qname=m_qn_fire1, xValue=-7,
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_context1, isNumeric=True
        )
        # Fact is numeric, has NEGATIVE value, concept in blacklist,
        # but HAS NO dimensions = Fire neg num check
        self.fact_two = mock.Mock(
            concept=mock_concept2, qname=m_qn_fire2, xValue=-77,
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_context4, isNumeric=True
        )
        # Fact is numeric, has POSITIVE value, concept in blacklist,
        # and HAS NO dimensions = No Fire neg num check
        self.fact_three = mock.Mock(
            concept=mock_concept3, qname=m_qn_fire3, xValue=7,
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_context4, isNumeric=True
        )
        # Fact is numeric, has POSITIVE value, concept NOT IN blacklist,
        # and HAS NO dimensions = No Fire neg num check
        self.fact_four = mock.Mock(
            concept=mock_concept4, qname=m_qn_no_fire1, xValue=77,
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_context4, isNumeric=True
        )
        # Fact is numeric, has POSITIVE value, concept in blacklist,
        # and HAS dimensions = No Fire neg num check
        self.fact_five = mock.Mock(
            concept=mock_concept2, qname=m_qn_fire2, xValue=777,
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_context2, isNumeric=True
        )
        # Fact is NOT numeric (TextItem), has NEGATIVE value,
        # concept in blacklist, and HAS NO dimensions = No Fire
        # neg num check
        # Will fail the numeric facts test
        self.fact_six = mock.Mock(
            concept=mock_concept5, qname=m_qn_fire2,
            xValue='This is some text!',
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_context4, isNumeric=False
        )
        # Fact is NOT numeric (Boolean), has NEGATIVE value,
        # concept NOT IN blacklist, and HAS NO dimensions = No Fire
        # neg num check
        # Will fail the numeric facts test
        self.fact_seven = mock.Mock(
            concept=mock_concept6, qname=m_qn_no_fire2, xValue='true',
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_concept4, isNumeric=False
        )
        # Fact is numeric, has NEGATIVE value, concept in blacklist,
        # and HAS NO dimensions = Fire neg num check
        self.fact_eight = mock.Mock(
            concept=mock_concept3, qname=m_qn_fire3, xValue=-777,
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_context4, isNumeric=True
        )
        # Fact is numeric, has NEGATIVE value, concept in blacklist,
        # and HAS NO dimensions = No Fire neg num check
        self.fact_nine = mock.Mock(
            concept=mock_concept3, qname=m_qn_fire3, xValue=-77.7,
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_context3, isNumeric=True
        )
        #  Will fail the numeric facts test
        self.fact_ten = mock.Mock(
            concept=mock_concept3, qname=m_qn_fire3, xValue='false',
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_context3, isNumeric=False
        )
        # Will fail the numeric facts test
        self.fact_eleven = mock.Mock(
            concept=mock_concept2, qname=m_qn_fire2, xValue=7777,
            namespaceURI='http://xbrl.sec.gov/us-gaap/2014-01-31',
            context=mock_context2, isNumeric=False
        )

    def test_negative_number_no_dimensions(self):
        mock_model1 = mock.Mock(
            modelXbrl=mock.Mock(
                facts=[
                    self.fact_one, self.fact_two, self.fact_three,
                    self.fact_four, self.fact_five, self.fact_six,
                    self.fact_seven, self.fact_eight, self.fact_nine,
                    self.fact_ten, self.fact_eleven
                ]
            )
        )

        blacklist_dict = util.neg_num.concept_map_from_csv(
            dqc_us_0014._DEFAULT_CONCEPTS_FILE
        )
        results1 = dqc_us_0014.filter_negative_number_no_dimensions_facts(
            mock_model1, blacklist_dict.keys()
        )
        self.assertEqual(2, len(results1))

    def test_grab_numeric_facts(self):
        fact_list = [
            self.fact_one, self.fact_two, self.fact_three,
            self.fact_four, self.fact_five, self.fact_six,
            self.fact_seven, self.fact_eight, self.fact_nine,
            self.fact_ten, self.fact_eleven
        ]

        numeric_facts = util.facts.grab_numeric_facts(fact_list)
        print('numeric_facts = ')
        print(fact.qname.localName for fact in numeric_facts)
        self.assertEqual(7, len(numeric_facts))
