# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
from collections import defaultdict
import unittest
from unittest.mock import Mock

from dqc_us_rules import dqc_us_0006
from dqc_us_rules.util import facts


class TestContextDates(unittest.TestCase):
    def setUp(self):
        """
        Set up values for the unit tests that follow
        """
        mock_type = Mock()
        mock_type.name = 'textBlockItemType'
        mock_qname = Mock(
            return_value=(
                '{http://xbrl.sec.gov/dei/2014-01-31}DocumentFiscalPeriodFocus'
            ),
            namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
            localName='DocumentFiscalPeriodFocus'
        )
        mock_concept = Mock(qname=mock_qname, type=mock_type)
        mock_nameconcepts = {'DocumentFiscalPeriodFocus': [mock_concept]}
        mock_context = Mock()
        mock_fact = Mock(
            context=mock_context,
            concept=mock_concept,
            qname=mock_qname,
            xValue='Q3'
        )
        mock_factsbyqname = {mock_concept.qname: [mock_fact]}
        self.mock_model = Mock(
            factsByQname=mock_factsbyqname,
            facts=[mock_fact],
            nameConcepts=mock_nameconcepts
        )

    def test_lea_facts_and_update(self):
        """
        Test _dict_list_update
        """
        mem_qname = Mock(localName='Company1')
        member = Mock(qname=mem_qname)
        dim_qname = Mock(localName='LegalEntityAxis')
        dim = Mock(qname=dim_qname)
        dim_lea = Mock(isExplicit=True, member=member, dimension=dim)
        seg_dims1 = {'dim1': dim_lea}
        context1 = Mock(segDimValues=seg_dims1)
        context2 = Mock(segDimValues={})
        fact1 = Mock(context=context1)
        fact2 = Mock(context=context2)
        fact3 = Mock(context=context2)
        res1 = facts.legal_entity_axis_facts_by_member([fact1, fact2])
        res2 = facts.legal_entity_axis_facts_by_member([fact3])
        res3 = dqc_us_0006._dict_list_update(res1, res2)

        expected = defaultdict(list)
        expected.update({'': [fact2, fact3], 'Company1': [fact1]})
        self.assertEqual(res3, expected)


class TestDateBoundsCSV(unittest.TestCase):
    def test_date_bounds_csv_keys_equal(self):
        """
        Test to make sure that the dictionary read in from the csv shares
        equals the original date_bounds_dict
        """
        date_bounds_dict = {
            'FY': {'min': 340, 'max': 390},
            'Q1': {'min': 65, 'max': 115},
            'Q3': {'min': 245, 'max': 295},
            'Q2': {'min': 155, 'max': 205}
        }

        date_bounds_dict_from_csv = dqc_us_0006._date_bounds_from_csv()

        self.assertDictEqual(date_bounds_dict, date_bounds_dict_from_csv)

    def test_date_bounds_csv_keys_unequal(self):
        """
        Test to make sure that the dictionary read is doesn't equal something
        other than the original DATE_BOUNDS_DICT
        """
        random_date_bounds_dict = {
            'FY': {'min': 374, 'max': 489},
            'Q1': {'min': 234, 'max': 394},
            'Q3': {'min': 890, 'max': 891},
            'Q2': {'min': 300, 'max': 790}
        }

        date_bounds_dict_from_csv = dqc_us_0006._date_bounds_from_csv()
        self.assertEqual(sorted(list(random_date_bounds_dict.keys())),
                         sorted(list(date_bounds_dict_from_csv.keys())))

        for key in random_date_bounds_dict.keys():
            for subkey in random_date_bounds_dict[key].keys():
                self.assertNotEqual(
                    random_date_bounds_dict[key][subkey],
                    date_bounds_dict_from_csv[key][subkey]
                )
