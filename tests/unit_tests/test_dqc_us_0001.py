# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import unittest

from dqc_us_rules import dqc_us_0001


class TestDQCOne(unittest.TestCase):

    def test(self):
        """
        Tests to make sure that _get_default_dped on an empty dict returns None
        """
        self.assertEqual(dqc_us_0001.find_facts_with_inappropriate_members(), 'Foo')
