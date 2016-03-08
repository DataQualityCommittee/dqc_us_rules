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
        mock_nameConcepts = {'DocumentFiscalPeriodFocus': [mock_concept]}
        mock_context = Mock()
        mock_fact = Mock(
            context=mock_context,
            concept=mock_concept,
            qname=mock_qname,
            xValue='Q3'
        )
        mock_factsByQname = {mock_concept.qname: [mock_fact]}
        self.mock_model = Mock(
            factsByQname=mock_factsByQname,
            facts=[mock_fact],
            nameConcepts=mock_nameConcepts
        )

    def test_lea_facts_and_update(self):
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
        res1 = facts.LegalEntityAxis_facts_by_member([fact1, fact2])
        res2 = facts.LegalEntityAxis_facts_by_member([fact3])
        res3 = dqc_us_0006._dict_list_update(res1, res2)

        expected = defaultdict(list)
        expected.update({'': [fact2, fact3], 'Company1': [fact1]})
        self.assertEqual(res3, expected)

class Test_Date_Bounds_CVS(unittest.TestCase):
    def test_date_bounds_cvs_keys(self):
        """
        Test to make sure that dictionary read in from the csv shares equals the original DATE_BOUNDS_DICT
        """
        DATE_BOUNDS_DICT = {
            'FY':{'min':340,'max':390},
            'Q1':{'min':65,'max':115},
            'Q3':{'min':245,'max':295},
            'Q2':{'min':155,'max':205}
        }

        date_bounds_dict_from_csv = dqc_us_0006.date_bounds_from_csv()

        self.assertDictEqual(DATE_BOUNDS_DICT,date_bounds_dict_from_csv)
