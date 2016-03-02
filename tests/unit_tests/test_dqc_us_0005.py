# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.   
# See license.md for license information.  
# See PatentNotice.md for patent infringement notice.
from datetime import date
import unittest
from unittest import mock

from dqc_us_rules import dqc_us_0005
from dqc_us_rules.util import facts


class TestContextChecks(unittest.TestCase):
    def setUp(self):
        mock_type = mock.Mock()
        mock_type.name = 'textBlockItemType'
        mock_qname = mock.Mock(
            return_value=(
                '{http://xbrl.sec.gov/dei/2014-01-31}DocumentPeriodEndDate'
            ),
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            localName='DocumentPeriodEndDate'
        )
        mock_concept = mock.Mock(
            qname=mock_qname, type=mock_type
        )
        mock_nameConcepts = {'DocumentPeriodEndDate': [mock_concept]}
        mock_segDimVal = {}
        mock_context = mock.Mock(
            endDatetime=date(2015, 1, 1),
            segDimValues=mock_segDimVal
        )
        mock_fact = mock.Mock(
            context=mock_context,
            concept=mock_concept,
            xValue=date(2015, 1, 1)
        )
        mock_factsByQname = {mock_concept.qname: [mock_fact]}
        self.mock_disclosure = mock.Mock(
            standardTaxonomiesDict={'http://xbrl.sec.gov/dei/2014-01-31': None}
        )
        self.mock_model = mock.Mock(
            factsByQname=mock_factsByQname,
            facts=[mock_fact],
            nameConcepts=mock_nameConcepts
        )

    def test_dei_regex(self):
        should_pass_list = [
            'http://xbrl.sec.gov/dei/2014-01-31',
            'http://xbrl.sec.gov/dei/2013-01-31',
            'http://xbrl.sec.gov/dei/2012-01-31',
            'http://xbrl.sec.gov/dei/2011-01-31',
            'http://xbrl.us/dei/2009-01-31'
        ]
        should_fail_list = [
            'not a url',
            'http://www.google.com/dei/2014-01-31',
            'https://xbrl.sec.gov/dei/2014-01-31',
            'http://www.xbrl.com/',
            'http://xbrl.sec.gov/notdei/2014-01-31'
        ]
        for ns in should_pass_list:
            self.assertTrue(dqc_us_0005._dei_pattern.match(ns))
        for ns in should_fail_list:
            self.assertFalse(dqc_us_0005._dei_pattern.match(ns))

    @mock.patch(
        'dqc_us_rules.dqc_us_0005.dateunionValue', return_value='2015-01-01'
    )
    def test_get_end_of_period_no_concept(self, mock_func):
        mock_val = mock.Mock(
            modelXbrl=self.mock_model, disclosureSystem=self.mock_disclosure
        )
        eop_dict = dqc_us_0005._get_end_of_period(mock_val)
        found_fact, found_date, date_str = eop_dict['']
        self.assertIsNotNone(
            found_fact.xValue,
            'Should have a found_fact, instead had "{}"'.format(found_fact)
        )
        self.assertIsNotNone(
            found_date,
            'Should have a found_date, instead had "{}"'.format(found_date)
        )
        self.assertEqual(
            '2015-01-01', date_str,
            'Should have a string with the date string when we have no '
            'concept, instead had "{}"'.format(date_str)
        )

    def test_axis_exists_multi_axis(self):
        mock_val = mock.Mock(
            disclosureSystem=mock.Mock(
                standardTaxonomiesDict={'namespace': None}
            )
        )
        dimension_names = ['ALocalName', 'AnotherAxis', 'YetAnotherAxis']
        dimensions = []
        for n in dimension_names:
            dimensions.append(
                mock.Mock(
                    isExplicit=True,
                    dimensionQname=mock.Mock(
                        localName=n, namespaceURI='namespace'
                    )
                )
            )
        mock_fact = mock.Mock(
            context=mock.Mock(
                qnameDims=mock.Mock(values=mock.Mock(return_value=dimensions))
            )
        )
        for n in dimension_names:
            self.assertTrue(facts.axis_exists(mock_val, mock_fact, n))
        self.assertFalse(
            facts.axis_exists(mock_val, mock_fact, 'not a used axis')
        )


class TestDeiChecks(unittest.TestCase):

    def test_dei_regex(self):
        should_pass_list = [
            'http://xbrl.sec.gov/dei/2014-01-31',
            'http://xbrl.sec.gov/dei/2013-01-31',
            'http://xbrl.sec.gov/dei/2012-01-31',
            'http://xbrl.sec.gov/dei/2011-01-31',
            'http://xbrl.us/dei/2009-01-31'
        ]
        should_fail_list = [
            'not a url',
            'http://www.google.com/dei/2014-01-31',
            'https://xbrl.sec.gov/dei/2014-01-31',
            'http://www.xbrl.com/',
            'http://xbrl.sec.gov/notdei/2014-01-31'
        ]
        for ns in should_pass_list:
            self.assertTrue(dqc_us_0005._dei_pattern.match(ns))
        for ns in should_fail_list:
            self.assertFalse(dqc_us_0005._dei_pattern.match(ns))
