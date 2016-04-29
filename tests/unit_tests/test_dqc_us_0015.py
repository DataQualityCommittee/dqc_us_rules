# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import io
import unittest
from unittest import mock
from dqc_us_rules.util import neg_num

import dqc_us_rules.dqc_us_0015 as dqc_us_0015


class TestDQC0015(unittest.TestCase):
    def test_contains(self):
        """
        Test contains with value that is in list and value that isn't in list
        """
        element_one = 'foo:Credit'
        element_two = 'foo:Accreditation'
        check_list = 'Credit'
        self.assertTrue(neg_num.contains(element_one, check_list))
        self.assertFalse(neg_num.contains(element_two, check_list))

    def test_contains_ignore_case(self):
        """
        Test contains_ignore_case with item that contain the same letters but
        not the same casing
        """
        element_one = 'foo:cRediT'
        element_two = 'foo:aCcRedItAtiON'
        check_list = 'CreDIt'
        self.assertTrue(
            neg_num.contains_insensitive(element_one, check_list)
        )
        self.assertTrue(
            neg_num.contains_insensitive(element_two, check_list)
        )

    def test_equals(self):
        """
        Test equals with values that should be equal and values that aren't
        equal
        """
        element_one = 'foo:Credit'
        element_two = 'foo:Accreditation'
        element_three = 'foo:CreditMaximum'
        check_list = 'foo:Credit'
        self.assertTrue(neg_num.equals(element_one, check_list))
        self.assertFalse(neg_num.equals(element_two, check_list))
        self.assertFalse(neg_num.equals(element_three, check_list))
        self.assertTrue(neg_num.equals(1.0, '1.0'))
        self.assertTrue(neg_num.equals(1, '1.0'))
        self.assertTrue(neg_num.equals(1.00, '1'))
        self.assertTrue(neg_num.equals(1.00, '1.00'))
        self.assertTrue(neg_num.equals('NaN', 'NaN'))
        self.assertFalse(neg_num.equals("NaN", '1'))
        self.assertFalse(neg_num.equals(0, 'zero'))

    def test_parse_row(self):
        """
        Test _parse_row against expected result
        """
        test_row = [
            'ConceptName', 'Not', 'Contains', 'Reserves', 'ConceptName',
            None, 'Contains', 'Recoveries', 'Period', None, 'Equals',
            'Duration'
        ]
        expected_rule = {
            'artifact': 'ConceptName',
            'item_check': 'Reserves',
            'negation': 'Not',
            'relation': 'Contains',
            'additional_conditions': {
                'artifact': 'ConceptName',
                'item_check': 'Recoveries',
                'negation': None,
                'relation': 'Contains',
                'additional_conditions': {
                    'artifact': 'Period',
                    'item_check': 'Duration',
                    'negation': None,
                    'relation': 'Equals',
                    'additional_conditions': None
                }
            }
        }
        rule = neg_num._parse_row(test_row)
        self.assertDictEqual(rule, expected_rule)

    def test_actual_rule_config(self):
        """
        Verifies the actual exclusion rule config can be parsed with no
        exceptions and has only expected values
        """
        with open(dqc_us_0015._DEFAULT_EXCLUSIONS_FILE, 'rt') as f:
            rule_line_count = len(f.readlines()) - 1  # remember the header
        blacklist_exclusion_rules = neg_num.get_rules_from_csv(
            dqc_us_0015._DEFAULT_EXCLUSIONS_FILE
        )
        # If any values are not BLE , they will not get returned and this
        # count will be less than # of lines.
        total_rule_count = len(blacklist_exclusion_rules)
        self.assertEqual(
            rule_line_count, total_rule_count,
            "{} lines resulted in {} rules".format(
                rule_line_count, total_rule_count
            )
        )


class TestBuildDict(unittest.TestCase):
    def setUp(self):
        """
        Sets up the following test cases
        """
        self.csv_lines = [
            'LIST,ARTIFACT,NEGATION,RELATION,ITEM',
            'BLE,Member,,Contains,Something',
            'BLE,Member,,Contains,PartA,Member,Not,Contains,PartB'
        ]
        self.csv_str = '\n'.join(self.csv_lines)
        # Mock the context managed open statement to return the test CSV
        # mock open specifically in the target module
        open_name = '{0}.open'.format(neg_num.__name__)
        with mock.patch(open_name, create=True) as m:
            m.return_value = io.StringIO(self.csv_str)
            self.blacklist_exclusion_rules = neg_num.get_rules_from_csv(
                dqc_us_0015._DEFAULT_EXCLUSIONS_FILE
            )
        self.rule_one = neg_num._parse_row(
            self.csv_lines[0].split(',')[1:]
        )
        self.rule_two = neg_num._parse_row(
            self.csv_lines[1].split(',')[1:]
        )
        self.rule_three = neg_num._parse_row(
            self.csv_lines[2].split(',')[1:]
        )

    def test_blacklist(self):
        """
        Tests blacklist to see if it contains the right items and is the right
        length
        """
        # Test blacklist
        list_color = 'black'
        exp_incl = []  # only concept includes
        exp_excl = [self.rule_two, self.rule_three]
        self.list_helper(
            exp_incl, exp_excl, [], self.blacklist_exclusion_rules, list_color
        )

    def list_helper(self, exp_incl, exp_excl, recv_incl, recv_excl,
                    list_color):
        self.assertEqual(
            len(recv_incl), len(exp_incl),
            'Unexpected number of conditions seen in '
            '{0}list inclusions.'.format(list_color)
        )
        for cond in exp_incl:
            self.assertIn(
                cond, recv_incl,
                'Expected node missing from '
                '{0}list inclusions.'.format(list_color)
            )
        self.assertEqual(
            len(recv_excl), len(exp_excl),
            'Unexpected number of conditions seen in '
            '{0}list inclusions.'.format(list_color)
        )
        for cond in exp_excl:
            self.assertIn(
                cond, recv_excl,
                'Expected node missing from '
                '{0}list exclusions.'.format(list_color)
            )
