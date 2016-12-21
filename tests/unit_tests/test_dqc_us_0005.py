# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
from datetime import date
import unittest
from unittest.mock import Mock, patch
from arelle.ModelInstanceObject import ModelFact

from dqc_us_rules import dqc_us_0005
from dqc_us_rules.util import facts, messages


class TestContextChecks(unittest.TestCase):
    def setUp(self):
        """
        Sets up values for unit tests
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
        mock_name_concepts = {'DocumentPeriodEndDate': [mock_concept]}
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
            nameConcepts=mock_name_concepts
        )

    def test_dei_regex(self):
        """
        Tests _dei_pattern against a pass list and a fail list
        """
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

    @patch(
        'dqc_us_rules.dqc_us_0005.dateunionValue', return_value='2015-01-01'
    )
    def test_get_end_of_period_no_concept(self, mock_func):
        """
        Test _get_end_of_period with no concept
        """
        mock_val = Mock(
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
        """
        Test axis_exists on one fact where the axis exists and one fact where
        the axis is doesn't exist
        """
        mock_val = Mock(
            disclosureSystem=Mock(
                standardTaxonomiesDict={'namespace': None}
            )
        )
        dimension_names = ['ALocalName', 'AnotherAxis', 'YetAnotherAxis']
        dimensions = []
        for n in dimension_names:
            dimensions.append(
                Mock(
                    isExplicit=True,
                    dimensionQname=Mock(
                        localName=n, namespaceURI='namespace'
                    )
                )
            )
        mock_fact = Mock(
            context=Mock(
                qnameDims=Mock(values=Mock(return_value=dimensions))
            )
        )
        for n in dimension_names:
            self.assertTrue(facts.axis_exists(mock_val, mock_fact, n))
        self.assertFalse(
            facts.axis_exists(mock_val, mock_fact, 'not a used axis')
        )

    def test_run_checks_EntityCommonStockSharesOutstanding(self):
        """
        Tests DQC_0005.17 - Checks that the date associated with the value for
        the Entity Common Stock, Shares Outstanding fact is on or after the
        reporting period end date.  Rule fires if the date is earlier than the
        reporting period end date.
        """
        msg = messages.get_message('DQC.US.0005', "17")
        mock_context = Mock(endDatetime=1)
        qname_mock = Mock(localName='EntityCommonStockSharesOutstanding')
        fact = Mock(
            spec=ModelFact,
            qname=qname_mock,
            context=mock_context
        )
        lookup = 'foo'
        eop_results = {lookup: [1, 1]}
        mock_error = Mock()
        mock_modelxbrl = Mock(error=mock_error)
        mock_val = Mock(modelXbrl=mock_modelxbrl)
        dqc_us_0005.run_checks(mock_val, fact, eop_results, lookup)
        self.assertFalse(mock_error.called)
        mock_context = Mock(endDatetime=0)
        qname_mock = Mock(localName='EntityCommonStockSharesOutstanding')
        fact = Mock(
            spec=ModelFact,
            qname=qname_mock,
            context=mock_context
        )
        dqc_us_0005.run_checks(mock_val, fact, eop_results, lookup)
        mock_error.assert_called_with(
            'DQC.US.0005.17',
            msg,
            modelObject=[fact] + list(eop_results[lookup]),
            ruleVersion=dqc_us_0005._RULE_VERSION
        )

    @patch('dqc_us_rules.dqc_us_0005.facts.axis_exists')
    def test_run_checks_axis_exists(self, axis_exists):
        """
        Tests DQC_0005.48 - the check is based on the axis
        """
        axis_exists.return_value = True
        msg = messages.get_message('DQC.US.0005', "48")
        mock_context = Mock(endDatetime=1)
        fact = Mock(localName='foo', context=mock_context)
        lookup = 'foo'
        eop_results = {lookup: [1, 1]}
        mock_error = Mock()
        mock_modelxbrl = Mock(error=mock_error)
        mock_val = Mock(modelXbrl=mock_modelxbrl)
        dqc_us_0005.run_checks(mock_val, fact, eop_results, lookup)
        mock_error.assert_called_with(
            'DQC.US.0005.48',
            msg,
            modelObject=[fact] + list(eop_results[lookup]),
            ruleVersion=dqc_us_0005._RULE_VERSION
        )

    @patch('dqc_us_rules.dqc_us_0005.facts.axis_exists')
    @patch('dqc_us_rules.dqc_us_0005.facts.axis_member_exists')
    def test_run_checks_axis_member_exists(self, axis_member_exists,
                                           axis_exists):
        """
        Tests DQC_0005.49 - this check is based on the axis/member
        """
        axis_exists.return_value = False
        axis_member_exists.return_value = True
        msg = messages.get_message('DQC.US.0005', "49")
        mock_context = Mock(endDatetime=1)
        fact = Mock(localName='foo', context=mock_context)
        lookup = 'foo'
        eop_results = {lookup: [1, 1]}
        mock_error = Mock()
        mock_modelxbrl = Mock(error=mock_error)
        mock_val = Mock(modelXbrl=mock_modelxbrl)
        dqc_us_0005.run_checks(mock_val, fact, eop_results, lookup)
        mock_error.assert_called_with(
            'DQC.US.0005.49',
            msg,
            modelObject=[fact] + list(eop_results[lookup]),
            ruleVersion=dqc_us_0005._RULE_VERSION
        )


class TestDeiChecks(unittest.TestCase):

    def test_dei_regex(self):
        """
        Test _dei_pattern against pass list and fail list
        """
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

    @patch('dqc_us_rules.dqc_us_0005._get_end_of_period', autospec=True)
    def test_report_exclusion(self, get_end_of_period):
        """
        Tests to make sure excluded reports are not validated.
        """
        mock_type = Mock()
        mock_type.name = 'textBlockItemType'
        mock_doc_type_qname = Mock(
            return_value=(
                '{http://xbrl.sec.gov/dei/2014-01-31}DocumentType'
            ),
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            localName='DocumentType'
        )
        mock_doc_type_concept = Mock(
            qname=mock_doc_type_qname, type=mock_type
        )

        mock_name_concepts = {'DocumentType': [mock_doc_type_concept]}
        mock_segdimval = {}
        mock_doc_type_context = Mock(
            endDatetime=date(2015, 1, 1),
            segDimValues=mock_segdimval
        )
        mock_doc_type_fact_1 = Mock(
            context=mock_doc_type_context,
            concept=mock_doc_type_concept,
            xValue=None
        )
        mock_doc_type_fact_2 = Mock(
            context=mock_doc_type_context,
            concept=mock_doc_type_concept,
            xValue=0
        )
        mock_doc_type_fact_3 = Mock(
            context=mock_doc_type_context,
            concept=mock_doc_type_concept,
            xValue=""
        )
        mock_doc_type_fact_4 = Mock(
            context=mock_doc_type_context,
            concept=mock_doc_type_concept,
            xValue="S-11 Ammended"
        )
        mock_factsbyqname = {
            mock_doc_type_context.qname: [
                mock_doc_type_fact_1,
                mock_doc_type_fact_2,
                mock_doc_type_fact_3,
                mock_doc_type_fact_4
            ]
        }
        self.mock_disclosure = Mock(
            standardTaxonomiesDict={'http://xbrl.sec.gov/dei/2014-01-31': None}
        )
        self.mock_model = Mock(
            factsByQname=mock_factsbyqname,
            facts=[
                mock_doc_type_fact_1,
                mock_doc_type_fact_2,
                mock_doc_type_fact_3,
                mock_doc_type_fact_4
            ],
            nameConcepts=mock_name_concepts
        )
        mock_val = Mock(modelXbrl=self.mock_model)
        dqc_us_0005.validate_facts(mock_val)
        self.assertFalse(get_end_of_period.called)

    @patch('dqc_us_rules.dqc_us_0005._get_end_of_period', autospec=True)
    def test_other_report_exclusion(self, get_end_of_period):
        """
        Tests to make sure excluded reports are not validated.
        """
        mock_type = Mock()
        mock_type.name = 'textBlockItemType'
        mock_doc_type_qname = Mock(
            return_value=(
                '{http://xbrl.sec.gov/dei/2014-01-31}DocumentType'
            ),
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            localName='DocumentType'
        )
        mock_doc_type_concept = Mock(
            qname=mock_doc_type_qname, type=mock_type
        )

        mock_name_concepts = {'DocumentType': [mock_doc_type_concept]}
        mock_segdimval = {}
        mock_doc_type_context = Mock(
            endDatetime=date(2015, 1, 1),
            segDimValues=mock_segdimval
        )
        mock_doc_type_fact = Mock(
            context=mock_doc_type_context,
            concept=mock_doc_type_concept,
            xValue="S-11 Ammended"
        )
        mock_factsbyqname = {mock_doc_type_context.qname: [mock_doc_type_fact]}
        self.mock_disclosure = Mock(
            standardTaxonomiesDict={'http://xbrl.sec.gov/dei/2014-01-31': None}
        )
        self.mock_model = Mock(
            factsByQname=mock_factsbyqname,
            facts=[mock_doc_type_fact],
            nameConcepts=mock_name_concepts
        )
        mock_val = Mock(modelXbrl=self.mock_model)
        dqc_us_0005.validate_facts(mock_val)
        self.assertFalse(get_end_of_period.called)
