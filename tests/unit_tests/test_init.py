# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import unittest
from unittest.mock import patch, MagicMock

import dqc_us_rules


class TestInitFunctions(unittest.TestCase):

    @patch('dqc_us_rules._plugins_to_run')
    def test_run_checks(self, plugins_func):
        """
        Tests to make sure that init.py works correctly
        """
        mock_plugins = [
            MagicMock(
                __pluginInfo__={'Validate.XBRL.Finally': MagicMock()},
                __file__='some_file'
            ),
            MagicMock(
                __pluginInfo__={'Validate.XBRL.Finally': MagicMock()},
                __file__='some_other_file'
            )
        ]
        plugins_func.return_value = mock_plugins
        mock_val = "Something here"
        dqc_us_rules.run_checks(mock_val)
        self.assertTrue(
            mock_plugins[0].__pluginInfo__['Validate.XBRL.Finally'].called
        )
        self.assertTrue(
            mock_plugins[1].__pluginInfo__['Validate.XBRL.Finally'].called
        )
