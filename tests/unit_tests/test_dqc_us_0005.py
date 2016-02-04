# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.   
# See license.md for license information.  
# See PatentNotice.md for patent infringement notice.
import unittest
from src import dqc_us_0005
from mock import Mock, patch
from datetime import date
import src.util.facts


class TestContextChecks(unittest.TestCase):
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

    def test_dei_regex(self):
        should_pass_list = ['http://xbrl.sec.gov/dei/2014-01-31',
                            'http://xbrl.sec.gov/dei/2013-01-31',
                            'http://xbrl.sec.gov/dei/2012-01-31',
                            'http://xbrl.sec.gov/dei/2011-01-31',
                            'http://xbrl.us/dei/2009-01-31']
        should_fail_list = ['not a url',
                            'http://www.google.com/dei/2014-01-31',
                            'https://xbrl.sec.gov/dei/2014-01-31',
                            'http://www.xbrl.com/',
                            'http://xbrl.sec.gov/notdei/2014-01-31']
        for ns in should_pass_list:
            self.assertTrue(dqc_us_0005._dei_pattern.match(ns))
        for ns in should_fail_list:
            self.assertFalse(dqc_us_0005._dei_pattern.match(ns))

    @patch('src.dqc_us_0005.dateunionValue', return_value='2015-01-01')
    def test_get_end_of_period_no_concept(self, mock_func):
        mock_val = Mock(modelXbrl=self.mock_model, disclosureSystem=self.mock_disclosure)
        eop_dict = dqc_us_0005._get_end_of_period(mock_val)
        found_fact, found_date, date_str = eop_dict['']
        self.assertIsNotNone(found_fact.xValue, 'Should have a found_fact, instead had "{}"'.format(found_fact))
        self.assertIsNotNone(found_date, 'Should have a found_date, instead had "{}"'.format(found_date))
        self.assertEqual('2015-01-01', date_str, 'Should have a string with the date string when we have no concept, instead had "{}"'.format(date_str))

    def test_axis_exists_multi_axis(self):
        mock_val = Mock(disclosureSystem=Mock(standardTaxonomiesDict={'namespace': None}))
        dimension_names = ['ALocalName', 'AnotherAxis', 'YetAnotherAxis']
        dimensions = []
        for n in dimension_names:
            dimensions.append(Mock(isExplicit=True, dimensionQname=Mock(localName=n, namespaceURI='namespace')))
        mock_fact = Mock(context=Mock(qnameDims=Mock(values=Mock(return_value=dimensions))))
        for n in dimension_names:
            self.assertTrue(src.util.facts.axis_exists(mock_val, mock_fact, n))
        self.assertFalse(src.util.facts.axis_exists(mock_val, mock_fact, 'not a used axis'))


class TestDeiChecks(unittest.TestCase):

    def test_dei_regex(self):
        should_pass_list = ['http://xbrl.sec.gov/dei/2014-01-31',
                            'http://xbrl.sec.gov/dei/2013-01-31',
                            'http://xbrl.sec.gov/dei/2012-01-31',
                            'http://xbrl.sec.gov/dei/2011-01-31',
                            'http://xbrl.us/dei/2009-01-31']
        should_fail_list = ['not a url',
                            'http://www.google.com/dei/2014-01-31',
                            'https://xbrl.sec.gov/dei/2014-01-31',
                            'http://www.xbrl.com/',
                            'http://xbrl.sec.gov/notdei/2014-01-31']
        for ns in should_pass_list:
            self.assertTrue(dqc_us_0005._dei_pattern.match(ns))
        for ns in should_fail_list:
            self.assertFalse(dqc_us_0005._dei_pattern.match(ns))
