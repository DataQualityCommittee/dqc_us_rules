# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import unittest
from unittest.mock import patch, MagicMock, Mock

from dqc_us_rules import dqc_us_0009


class TestCompareFacts(unittest.TestCase):

    @patch('dqc_us_rules.dqc_us_0009.facts')
    def test_empty_compare(self, fact_patch):
        """
        Tests _compare_facts with empty facts
        """
        lesser = Mock()
        greater = Mock()
        val = MagicMock(xbrlModel='false model')
        fact_patch.lookup_gaap_facts = MagicMock(return_value=[])
        fact_patch.prepare_facts_for_calculation = MagicMock(return_value=[])
        results = dqc_us_0009._compare_facts(lesser, greater, val)
        self.assertEqual(0, len(results))

    @patch('dqc_us_rules.dqc_us_0009.facts.lookup_gaap_facts')
    @patch('dqc_us_rules.dqc_us_0009.facts.prepare_facts_for_calculation')
    def test_extant_compare(self, fact_patch, lookup_patch):
        """
        Tests compare facts with different values and one value that is the
        same
        """
        lesser = Mock()
        greater = Mock()
        val = MagicMock(xbrlModel='false model')
        lookup_patch.return_value = []
        fact_list = [
            {
                lesser: MagicMock(xValue=100, decimals=1),
                greater: MagicMock(xValue=99, decimals=1)
            },
            {
                lesser: MagicMock(xValue=100, decimals=1),
                greater: MagicMock(xValue=101, decimals=1)
            },
            {
                lesser: MagicMock(xValue=100, decimals=1),
                greater: MagicMock(xValue=100, decimals=1)
            }
        ]
        fact_patch.return_value = fact_list
        results = dqc_us_0009._compare_facts(lesser, greater, val)
        self.assertEqual(1, len(results))
        self.assertEqual([fact_list[0]], results)
