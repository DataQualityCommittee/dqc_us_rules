# (c) Copyright 2015 - 2017, XBRL US Inc. All rights reserved.
# See https://xbrl.us/dqc-license for license information.
# See https://xbrl.us/dqc-patent for patent infringement notice.
import unittest
import arelle.ValidateXbrl
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
        disclosuresystem = 'arelle.ValidateXbrl.ValidateXbrl.disclosureSystem'
        plugins_func.return_value = mock_plugins
        mock_disclosure = MagicMock(
            spec=disclosuresystem,
            validationType='EFM'
        )
        val_spec = arelle.ValidateXbrl.ValidateXbrl
        mock_val = MagicMock(
            spec=val_spec,
            disclosureSystem=mock_disclosure
        )
        dqc_us_rules.run_checks(mock_val)
        self.assertTrue(
            mock_plugins[0].__pluginInfo__['Validate.XBRL.Finally'].called
        )
        self.assertTrue(
            mock_plugins[1].__pluginInfo__['Validate.XBRL.Finally'].called
        )
