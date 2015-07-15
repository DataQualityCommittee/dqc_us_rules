# Copyright (c) 2015, Workiva Inc.  All rights reserved
# Copyright (c) 2015, XBRL US Inc.  All rights reserved
from nose.tools import assert_equal, assert_true, assert_false, assert_in, assert_dict_equal, raises
import src.dqc_us_0015 as dqc_us_0015
import mock
import io
import unittest
import os


def test_contains():
    element_one = 'foo:Credit'
    element_two = 'foo:Accreditation'
    check_list = 'Credit'
    assert_true(dqc_us_0015.contains(element_one, check_list))
    assert_false(dqc_us_0015.contains(element_two, check_list))


def test_contains_insensitive():
    element_one = 'foo:cRediT'
    element_two = 'foo:aCcRedItAtiON'
    check_list = 'CreDIt'
    assert_true(dqc_us_0015.contains_insensitive(element_one, check_list))
    assert_true(dqc_us_0015.contains_insensitive(element_two, check_list))


def test_equals():
    element_one = 'foo:Credit'
    element_two = 'foo:Accreditation'
    element_three = 'foo:CreditMaximum'
    check_list = 'foo:Credit'
    assert_true(dqc_us_0015.equals(element_one, check_list))
    assert_false(dqc_us_0015.equals(element_two, check_list))
    assert_false(dqc_us_0015.equals(element_three, check_list))
    assert_true(dqc_us_0015.equals(1.0, '1.0'))
    assert_true(dqc_us_0015.equals(1, '1.0'))
    assert_true(dqc_us_0015.equals(1.00, '1'))
    assert_true(dqc_us_0015.equals(1.00, '1.00'))
    assert_true(dqc_us_0015.equals('NaN', 'NaN'))
    assert_false(dqc_us_0015.equals("NaN", '1'))
    assert_false(dqc_us_0015.equals(0, 'zero'))


def test_parse_row():
    test_row = ['ConceptName', 'Not', 'Contains', 'Reserves', 'ConceptName',
                None, 'Contains', 'Recoveries', 'Period', None, 'Equals', 'Duration']
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
    rule = dqc_us_0015._parse_row(test_row)
    assert_dict_equal(rule, expected_rule)


class TestBuildDict(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.csv_lines = [
            'LIST,ARTIFACT,NEGATION,RELATION,ITEM',
            'BLE,Member,,Contains,Something',
            'BLE,Member,,Contains,PartA,Member,Not,Contains,PartB'
        ]
        cls.csv_str = '\n'.join(cls.csv_lines)
        # Mock the context managed open statement to return the test CSV
        # mock open specifically in the target module
        open_name = '{0}.open'.format(dqc_us_0015.__name__)
        with mock.patch(open_name, create=True) as m:
            m.return_value = io.StringIO(cls.csv_str)
            cls.blacklist_exclusion_rules = dqc_us_0015.get_rules_from_csv()
        cls.rule_one = dqc_us_0015._parse_row(cls.csv_lines[0].split(',')[1:])
        cls.rule_two = dqc_us_0015._parse_row(cls.csv_lines[1].split(',')[1:])
        cls.rule_three = dqc_us_0015._parse_row(cls.csv_lines[2].split(',')[1:])

    def test_blacklist(self):
        # Test blacklist
        list_color = 'black'
        exp_incl = []  # only concept includes
        exp_excl = [self.rule_two, self.rule_three]
        self.list_helper(exp_incl, exp_excl, [], self.blacklist_exclusion_rules, "black")

    def list_helper(self, exp_incl, exp_excl, recv_incl, recv_excl, list_color):
        assert_equal(len(recv_incl), len(exp_incl), msg='Unexpected number of conditions seen in {0}list inclusions.'.format(list_color))
        for cond in exp_incl:
            assert_in(cond, recv_incl, msg='Expected node missing from {0}list inclusions.'.format(list_color))
        assert_equal(len(recv_excl), len(exp_excl), msg='Unexpected number of conditions seen in {0}list inclusions.'.format(list_color))
        for cond in exp_excl:
            assert_in(cond, recv_excl, msg='Expected node missing from {0}list exclusions.'.format(list_color))


def test_actual_rule_config():
    """verifies the actual exclusion rule config can be parsed with no exceptions and has only expected values"""
    with open(dqc_us_0015._DEFAULT_EXCLUSIONS_FILE, 'rt') as f:
        rule_line_count = len(f.readlines()) - 1  # remember the header
    blacklist_exclusion_rules = dqc_us_0015.get_rules_from_csv()
    # if any values are not BLE , they will not get returned and this count will be less than # of lines.
    total_rule_count = len(blacklist_exclusion_rules)
    assert_equal(rule_line_count, total_rule_count, msg="{} lines resulted in {} rules".format(rule_line_count, total_rule_count))
