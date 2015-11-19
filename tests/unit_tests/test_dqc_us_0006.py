# (c) Copyright 2015, XBRL US Inc, All rights reserved   
# See license.md for license information.  
# See PatentNotice.md for patent infringement notice.
import unittest
import src.dqc_us_0006 as dqc_us_0006
from mock import Mock
from collections import defaultdict
import src.util.facts


class TestContextDates(unittest.TestCase):
    def setUp(self):
        mock_type = Mock()
        mock_type.name = 'textBlockItemType'
        mock_qname = Mock(return_value='{http://xbrl.sec.gov/dei/2014-01-31}DocumentFiscalPeriodFocus',
                          namespaceURI='http://xbrl.sec.gov/dei/2014-01-31',
                          localName='DocumentFiscalPeriodFocus')
        mock_concept = Mock(qname=mock_qname,
                            type=mock_type)
        mock_nameConcepts = {'DocumentFiscalPeriodFocus': [mock_concept]}
        mock_context = Mock()
        mock_fact = Mock(context=mock_context,
                         concept=mock_concept,
                         qname=mock_qname,
                         xValue='Q3')
        mock_factsByQname = {mock_concept.qname: [mock_fact]}
        self.mock_model = Mock(factsByQname=mock_factsByQname,
                               facts=[mock_fact],
                               nameConcepts=mock_nameConcepts)

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
        res1 = src.util.facts.LegalEntityAxis_facts_by_member([fact1, fact2])
        res2 = src.util.facts.LegalEntityAxis_facts_by_member([fact3])
        res3 = dqc_us_0006._dict_list_update(res1, res2)

        expected = defaultdict(list)
        expected.update({'': [fact2, fact3], 'Company1': [fact1]})
        self.assertEqual(res3, expected)
