# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import unittest
from unittest.mock import Mock, patch
from arelle.ModelDtsObject import ModelConcept

from dqc_us_rules import dqc_us_0001

class TestIsConcept(unittest.TestCase):

    def test_is_concept(self):
        concept = Mock(spec=ModelConcept, qname='Page')
        self.assertTrue(dqc_us_0001._is_concept(concept))
        concept = None
        self.assertFalse(dqc_us_0001._is_concept(concept))
        concept = Mock(spec=ModelConcept, qname=None)
        self.assertFalse(dqc_us_0001._is_concept(concept))

class TestIsDomain(unittest.TestCase):

    def test_is_domain(self):
        concept = Mock()
        concept.label.return_value = 'page [Domain]'
        self.assertTrue(dqc_us_0001._is_domain(concept))

        concept.label.return_value = 'page [Axis]'
        concept.qname = Mock(localName='Trey')
        self.assertFalse(dqc_us_0001._is_domain(concept))

        concept.qname = Mock(localName='MikeDomain')
        self.assertTrue(dqc_us_0001._is_domain(concept))
