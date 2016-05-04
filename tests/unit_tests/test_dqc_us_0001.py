# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import unittest
from unittest.mock import Mock, patch
from arelle.ModelDtsObject import ModelConcept

from dqc_us_rules import dqc_us_0001

class TestRunChecks(unittest.TestCase):

    @patch('dqc_us_rules.dqc_us_0001._run_axis_checks')
    @patch('dqc_us_rules.dqc_us_0001._load_config')
    @patch('dqc_us_rules.dqc_us_0001._is_concept', return_value=True)
    def test_filtering(self, _, config, checks):
        config.return_value = {
            "foo":{
                "rule_index":66,
                "defined_members":[
                    "DesignatedAsHedgingInstrumentMember",
                    "NondesignatedMember"
                ],
                "additional_axes":{},
                "excluded_axes":{},
                "additional_members":[],
                "extensions":[]
            }
        }
        expected_config = {
            'excluded_axes': {},
            'additional_members': [],
            'extensions': [],
            'defined_members': ['DesignatedAsHedgingInstrumentMember', 'NondesignatedMember'],
            'additional_axes': {},
            'rule_index': 66
        }
        mock_qname = Mock(localName='foo')
        mock_qname2 = Mock(localName='mike')
        mock_qname3 = Mock(localName='fish')
        mock_obj1 = Mock(qname=mock_qname)
        mock_obj2 = Mock(qname=mock_qname2)
        mock_obj3 = Mock(qname=mock_qname3)
        mock_frommodelobj = Mock(return_value=(mock_obj1, mock_obj2, mock_obj3))
        mock_relset_obj = Mock(fromModelObjects=mock_frommodelobj)
        mock_relationship_set_func = Mock(return_value=mock_relset_obj)
        mock_model_xbrl = Mock(roleTypes=['trey', 'page'], relationshipSet=mock_relationship_set_func)
        val = Mock(modelXbrl=mock_model_xbrl)

        dqc_us_0001.run_checks(val)
        self.assertTrue(checks.called)
        checks.assert_called_with(mock_obj1, expected_config, mock_relset_obj, val, 'page')


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

class TestAllConceptsUnder(unittest.TestCase):
    root_concept = None
    relset = []
    tree_concepts = []

    def setUp(self):
        """
        Initialize a relset with this tree:
            A
            |-- B
            |    +-- C
            |         +-- A
            |              +-- (...)  # cycle
            +-- D
        """
        # make some concepts
        cncpt_a = Mock()  # root
        cncpt_b = Mock()
        cncpt_c = Mock()
        cncpt_d = Mock()
        self.tree_concepts = [cncpt_a, cncpt_b, cncpt_c, cncpt_d]
        # initialize relset
        mock_relset = Mock()
        fromModelObject_rels = {
            cncpt_a: [self._mock_rel(cncpt_a, cncpt_b), self._mock_rel(cncpt_a, cncpt_d)],
            cncpt_b: [self._mock_rel(cncpt_b, cncpt_c)],
            cncpt_c: [self._mock_rel(cncpt_c, cncpt_a)],  # cycle
            cncpt_d: []
        }
        toModelObject_rels = {
            cncpt_a: [self._mock_rel(cncpt_c, cncpt_a)],
            cncpt_b: [self._mock_rel(cncpt_a, cncpt_b)],
            cncpt_c: [self._mock_rel(cncpt_b, cncpt_c)],
            cncpt_d: [self._mock_rel(cncpt_a, cncpt_d)]
        }
        mock_relset.fromModelObject = lambda c: fromModelObject_rels[c]
        mock_relset.toModelObject = lambda c: toModelObject_rels[c]
        self.root_concept = cncpt_a
        self.relset = mock_relset

    @staticmethod
    def _mock_rel(fr, to):
        rel = Mock()
        rel.fromModelObject = fr
        rel.toModelObject = to
        rel.toLocator = id(to)
        return rel

    @patch('dqc_us_rules.dqc_us_0001._is_domain', return_value=False)
    @patch('dqc_us_rules.dqc_us_0001._is_concept', return_value=True)
    def test_traversal(self, _, __):
        """
        Test relationshipSet traversal
        """
        concepts = dqc_us_0001._all_members_under(self.root_concept, self.relset)
        # check that we got every concept under the tree
        expected_concepts = set(self.tree_concepts)
        self.assertEqual(set(concepts), expected_concepts)

    @patch('dqc_us_rules.dqc_us_0001._is_domain', return_value=True)
    @patch('dqc_us_rules.dqc_us_0001._is_concept', return_value=True)
    def test_traversal_all_domains(self, _, __):
        """
        Test relationshipSet traversal
        """
        concepts = dqc_us_0001._all_members_under(self.root_concept, self.relset)
        # check that we got every concept under the tree
        expected_concepts = set()
        self.assertEqual(set(concepts), expected_concepts)

    @patch('dqc_us_rules.dqc_us_0001._is_domain', return_value=False)
    @patch('dqc_us_rules.dqc_us_0001._is_concept', return_value=False)
    def test_traversal_no_concepts(self, _, __):
        """
        Test relationshipSet traversal
        """
        concepts = dqc_us_0001._all_members_under(self.root_concept, self.relset)
        # check that we got every concept under the tree
        expected_concepts = set()
        self.assertEqual(set(concepts), expected_concepts)
