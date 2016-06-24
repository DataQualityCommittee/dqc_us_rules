# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import unittest
from unittest.mock import Mock, patch
from arelle.ModelDtsObject import ModelConcept
from collections import defaultdict

from dqc_us_rules import dqc_us_0001


class TestRunChecks(unittest.TestCase):

    @patch('dqc_us_rules.dqc_us_0001._run_axis_checks')
    @patch('dqc_us_rules.dqc_us_0001._load_config')
    @patch('dqc_us_rules.dqc_us_0001._is_concept', return_value=True)
    def test_filtering(self, _, config, checks):
        """
        Tests that we only check on the axes specified in the config.
        """
        config.return_value = {
            "foo": {
                "rule_index": 66,
                "defined_members": [
                    "DesignatedAsHedgingInstrumentMember",
                    "NondesignatedMember"
                ],
                "additional_axes": {},
                "excluded_axes": {},
                "additional_members": [],
                "extensions": []
            }
        }
        expected_config = {
            'excluded_axes': {},
            'additional_members': [],
            'extensions': [],
            'defined_members': [
                'DesignatedAsHedgingInstrumentMember', 'NondesignatedMember'
            ],
            'additional_axes': {},
            'rule_index': 66
        }
        mock_qname = Mock(localName='foo')
        mock_qname2 = Mock(localName='mike')
        mock_qname3 = Mock(localName='fish')
        mock_obj1 = Mock(qname=mock_qname)
        mock_obj2 = Mock(qname=mock_qname2)
        mock_obj3 = Mock(qname=mock_qname3)
        mock_frommodelobj = Mock(
            return_value=(mock_obj1, mock_obj2, mock_obj3)
        )
        mock_relset_obj = Mock(fromModelObjects=mock_frommodelobj)
        mock_relationship_set_func = Mock(return_value=mock_relset_obj)
        mock_model_xbrl = Mock(
            roleTypes=['trey', 'page'],
            relationshipSet=mock_relationship_set_func
        )
        val = Mock(modelXbrl=mock_model_xbrl)

        dqc_us_0001.run_checks(val)
        self.assertTrue(checks.called)
        checks.assert_called_with(
            mock_obj1,
            'foo',
            expected_config,
            mock_relset_obj,
            val,
            'page',
            defaultdict(list)
        )


class TestMemberChecks(unittest.TestCase):

    @patch(
        'dqc_us_rules.dqc_us_0001.facts.axis_member_fact',
        return_value=[]
    )
    @patch('dqc_us_rules.dqc_us_0001._is_extension', return_value=False)
    @patch('dqc_us_rules.dqc_us_0001._all_members_under')
    def test_excluded_list_no_fact(self, members, _, __):
        """
        Tests excluded axes without a fact.
        """
        mock_error_func = Mock()
        mock_model_xbrl = Mock(error=mock_error_func)
        mock_val = Mock(modelXbrl=mock_model_xbrl)
        mock_config = {
            'excluded_axes': {
                'foo': ['trey', 'page', 'mike', 'fish']
            },
            'rule_index': 100
        }
        mock_qname = Mock(localName='trey')
        mock_child = Mock(qname=mock_qname)
        members.return_value = [mock_child]

        mock_axis = Mock()
        mock_role = 'RoDriftBoats'
        dqc_us_0001._run_member_checks(
            mock_axis,
            Mock(),
            mock_config,
            Mock(),
            mock_val,
            mock_role,
            defaultdict(list)
        )

        self.assertTrue(mock_error_func.called)
        mock_error_func.assert_called_with(
            '{base}.{index}'.format(base=dqc_us_0001._CODE_NAME, index=100),
            dqc_us_0001.messages.get_message(
                dqc_us_0001._CODE_NAME,
                dqc_us_0001._NO_FACT_KEY
            ),
            axis=mock_axis.label(),
            group='RoDriftBoats',
            member=mock_child.label(),
            ruleVersion=dqc_us_0001._RULE_VERSION
        )

    @patch(
        'dqc_us_rules.dqc_us_0001.facts.axis_member_fact',
        return_value=None
    )
    @patch('dqc_us_rules.dqc_us_0001._is_extension', return_value=True)
    @patch('dqc_us_rules.dqc_us_0001._all_members_under')
    def test_extensions_no_fire(self, members, _, __):
        """
        Tests that we won't fire for extensions.
        """
        mock_error_func = Mock()
        mock_model_xbrl = Mock(error=mock_error_func)
        mock_val = Mock(modelXbrl=mock_model_xbrl)
        mock_config = {
            'excluded_axes': {
                'foo': ['trey', 'page', 'mike', 'fish']
            },
            'rule_index': 100
        }
        mock_qname = Mock(localName='trey')
        mock_child = Mock(qname=mock_qname)
        members.return_value = [mock_child]

        mock_axis = Mock()
        mock_role = 'RoDriftBoats'
        dqc_us_0001._run_member_checks(
            mock_axis,
            Mock(),
            mock_config,
            Mock(),
            mock_val,
            mock_role,
            defaultdict(list)
        )

        self.assertFalse(mock_error_func.called)

    @patch('dqc_us_rules.dqc_us_0001.facts.axis_member_fact')
    @patch('dqc_us_rules.dqc_us_0001._is_extension', return_value=False)
    @patch('dqc_us_rules.dqc_us_0001._all_members_under')
    def test_excluded_list_with_fact(self, members, _, fact):
        """
        Tests the excluded list with an associated fact.
        """
        mock_fact = Mock()
        fact.return_value = [mock_fact]
        mock_error_func = Mock()
        mock_model_xbrl = Mock(error=mock_error_func)
        mock_val = Mock(modelXbrl=mock_model_xbrl)
        mock_config = {
            'excluded_axes': {
                'foo': ['trey', 'page', 'mike', 'fish']
            },
            'rule_index': 100
        }
        mock_qname = Mock(localName='trey')
        mock_child = Mock(qname=mock_qname)
        members.return_value = [mock_child]

        mock_axis = Mock()
        mock_role = 'RoDriftBoats'
        dqc_us_0001._run_member_checks(
            mock_axis,
            Mock(),
            mock_config,
            Mock(),
            mock_val,
            mock_role,
            defaultdict(list)
        )

        self.assertTrue(mock_error_func.called)
        mock_error_func.assert_called_with(
            '{base}.{index}'.format(base=dqc_us_0001._CODE_NAME, index=100),
            dqc_us_0001.messages.get_message(
                dqc_us_0001._CODE_NAME,
                dqc_us_0001._UGT_FACT_KEY
            ),
            axis=mock_axis.label(),
            member=mock_child.label(),
            modelObject=mock_fact,
            ruleVersion=dqc_us_0001._RULE_VERSION
        )

    @patch('dqc_us_rules.dqc_us_0001.facts.axis_member_fact')
    @patch('dqc_us_rules.dqc_us_0001._is_extension', return_value=False)
    @patch('dqc_us_rules.dqc_us_0001._all_members_under')
    def test_included_axes_list_with_fact(self, members, _, fact):
        """
        Tests the additional axis inclusions with a fact.
        """
        mock_fact = Mock()
        fact.return_value = [mock_fact]
        mock_error_func = Mock()
        mock_model_xbrl = Mock(error=mock_error_func)
        mock_val = Mock(modelXbrl=mock_model_xbrl)
        mock_config = {
            'additional_axes': {
                'foo': ['trey', 'page', 'mike', 'fish']
            },
            'rule_index': 100
        }
        mock_qname = Mock(localName='jerry')
        mock_child = Mock(qname=mock_qname)
        members.return_value = [mock_child]

        mock_axis = Mock()
        mock_role = 'RoDriftBoats'
        dqc_us_0001._run_member_checks(
            mock_axis,
            Mock(),
            mock_config,
            Mock(),
            mock_val,
            mock_role,
            defaultdict(list)
        )

        self.assertTrue(mock_error_func.called)
        mock_error_func.assert_called_with(
            '{base}.{index}'.format(base=dqc_us_0001._CODE_NAME, index=100),
            dqc_us_0001.messages.get_message(
                dqc_us_0001._CODE_NAME,
                dqc_us_0001._UGT_FACT_KEY
            ),
            axis=mock_axis.label(),
            member=mock_child.label(),
            modelObject=mock_fact,
            ruleVersion=dqc_us_0001._RULE_VERSION
        )

    @patch(
        'dqc_us_rules.dqc_us_0001.facts.axis_member_fact',
        return_value=[]
    )
    @patch('dqc_us_rules.dqc_us_0001._is_extension', return_value=False)
    @patch('dqc_us_rules.dqc_us_0001._all_members_under')
    def test_included_axes_list_no_fact(self, members, _, __):
        """
        Tests the additional axis inclusions without a fact.
        """
        mock_error_func = Mock()
        mock_model_xbrl = Mock(error=mock_error_func)
        mock_val = Mock(modelXbrl=mock_model_xbrl)
        mock_config = {
            'additional_axes': {
                'foo': ['trey', 'page', 'mike', 'fish']
            },
            'rule_index': 100
        }
        mock_qname = Mock(localName='jerry')
        mock_child = Mock(qname=mock_qname)
        members.return_value = [mock_child]

        mock_axis = Mock()
        mock_role = 'RoDriftBoats'
        dqc_us_0001._run_member_checks(
            mock_axis,
            Mock(),
            mock_config,
            Mock(),
            mock_val,
            mock_role,
            defaultdict(list)
        )

        self.assertTrue(mock_error_func.called)
        mock_error_func.assert_called_with(
            '{base}.{index}'.format(base=dqc_us_0001._CODE_NAME, index=100),
            dqc_us_0001.messages.get_message(
                dqc_us_0001._CODE_NAME,
                dqc_us_0001._NO_FACT_KEY
            ),
            axis=mock_axis.label(),
            group='RoDriftBoats',
            member=mock_child.label(),
            ruleVersion=dqc_us_0001._RULE_VERSION
        )


class TestExtensionChecks(unittest.TestCase):

    def test_allow_all(self):
        """
        Tests the extension checks with all allowed.
        """
        mock_error_func = Mock()
        mock_model_xbrl = Mock(error=mock_error_func)
        mock_val = Mock(modelXbrl=mock_model_xbrl)
        mock_config = {
            "extensions": ["*"],
            'rule_index': 100
        }

        dqc_us_0001._run_extension_checks(
            Mock(),
            Mock(),
            mock_config,
            Mock(),
            mock_val,
            Mock(),
            Mock()
        )
        self.assertFalse(mock_error_func.called)

    @patch('dqc_us_rules.dqc_us_0001._is_extension', return_value=False)
    @patch(
        'dqc_us_rules.dqc_us_0001._all_members_under',
        return_value=range(10)
    )
    def test_no_ext(self, _, __):
        """
        Tests extension checks for no extensions present.
        """
        mock_error_func = Mock()
        mock_model_xbrl = Mock(error=mock_error_func)
        mock_val = Mock(modelXbrl=mock_model_xbrl)
        mock_config = {
            "extensions": [],
            'rule_index': 100
        }

        dqc_us_0001._run_extension_checks(
            Mock(),
            Mock(),
            mock_config,
            Mock(),
            mock_val,
            Mock(),
            defaultdict(list)
        )
        self.assertFalse(mock_error_func.called)

    @patch(
        'dqc_us_rules.dqc_us_0001.facts.axis_member_fact',
        return_value=[]
    )
    @patch('dqc_us_rules.dqc_us_0001._is_extension', return_value=True)
    @patch('dqc_us_rules.dqc_us_0001._all_members_under')
    def test_has_ext_none_allowed_no_fact(self, members, _, __):
        """
        Test extension blacklisting with no fact.
        """
        mock_error_func = Mock()
        mock_model_xbrl = Mock(error=mock_error_func)
        mock_val = Mock(modelXbrl=mock_model_xbrl)
        mock_qname = Mock(localName='jerry')
        mock_child = Mock(qname=mock_qname)
        members.return_value = [mock_child]
        mock_axis = Mock()
        mock_role = 'RoDriftBoats'
        mock_config = {
            "extensions": [],
            'rule_index': 100
        }

        dqc_us_0001._run_extension_checks(
            mock_axis,
            Mock(),
            mock_config,
            Mock(),
            mock_val,
            mock_role,
            defaultdict(list)
        )
        self.assertTrue(mock_error_func.called)
        mock_error_func.assert_called_with(
            '{base}.{index}'.format(base=dqc_us_0001._CODE_NAME, index=100),
            dqc_us_0001.messages.get_message(
                dqc_us_0001._CODE_NAME,
                dqc_us_0001._NO_FACT_KEY
            ),
            axis=mock_axis.label(),
            group='RoDriftBoats',
            member=mock_child.label(),
            ruleVersion=dqc_us_0001._RULE_VERSION
        )

    @patch('dqc_us_rules.dqc_us_0001.facts.axis_member_fact')
    @patch('dqc_us_rules.dqc_us_0001._is_extension', return_value=True)
    @patch('dqc_us_rules.dqc_us_0001._all_members_under')
    def test_has_ext_none_allowed_has_fact(self, members, _, fact):
        """
        Tests extension blacklisting with a fact.
        """
        mock_fact = Mock()
        fact.return_value = [mock_fact]
        mock_error_func = Mock()
        mock_model_xbrl = Mock(error=mock_error_func)
        mock_val = Mock(modelXbrl=mock_model_xbrl)
        mock_qname = Mock(localName='jerry')
        mock_child = Mock(qname=mock_qname)
        members.return_value = [mock_child]
        mock_axis = Mock()
        mock_role = 'RoDriftBoats'
        mock_config = {
            "extensions": [],
            'rule_index': 100
        }

        dqc_us_0001._run_extension_checks(
            mock_axis,
            Mock(),
            mock_config,
            Mock(),
            mock_val,
            mock_role,
            defaultdict(list)
        )
        self.assertTrue(mock_error_func.called)
        mock_error_func.assert_called_with(
            '{base}.{index}'.format(base=dqc_us_0001._CODE_NAME, index=100),
            dqc_us_0001.messages.get_message(
                dqc_us_0001._CODE_NAME,
                dqc_us_0001._EXT_FACT_KEY
            ),
            axis=mock_axis.label(),
            member=mock_child.label(),
            modelObject=mock_fact,
            ruleVersion=dqc_us_0001._RULE_VERSION
        )


class TestIsConcept(unittest.TestCase):

    def test_is_concept(self):
        """
        Test the _is_concept check.
        """
        concept = Mock(spec=ModelConcept, qname='Page')
        self.assertTrue(dqc_us_0001._is_concept(concept))
        concept = None
        self.assertFalse(dqc_us_0001._is_concept(concept))
        concept = Mock(spec=ModelConcept, qname=None)
        self.assertFalse(dqc_us_0001._is_concept(concept))


class TestIsDomain(unittest.TestCase):

    def test_is_domain(self):
        """
        Test the _is_domain check.
        """
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
            cncpt_a: [
                self._mock_rel(cncpt_a, cncpt_b),
                self._mock_rel(cncpt_a, cncpt_d)
            ],
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
        """
        Build a mock relationshipSet.
        """
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
        concepts = dqc_us_0001._all_members_under(
            self.root_concept,
            self.relset
        )
        # check that we got every concept under the tree
        expected_concepts = set(self.tree_concepts)
        self.assertEqual(set(concepts), expected_concepts)

    @patch('dqc_us_rules.dqc_us_0001._is_domain', return_value=True)
    @patch('dqc_us_rules.dqc_us_0001._is_concept', return_value=True)
    def test_traversal_all_domains(self, _, __):
        """
        Test relationshipSet traversal
        """
        concepts = dqc_us_0001._all_members_under(
            self.root_concept,
            self.relset
        )
        # check that we got every concept under the tree
        expected_concepts = set()
        self.assertEqual(set(concepts), expected_concepts)

    @patch('dqc_us_rules.dqc_us_0001._is_domain', return_value=False)
    @patch('dqc_us_rules.dqc_us_0001._is_concept', return_value=False)
    def test_traversal_no_concepts(self, _, __):
        """
        Test relationshipSet traversal
        """
        concepts = dqc_us_0001._all_members_under(
            self.root_concept,
            self.relset
        )
        # check that we got every concept under the tree
        expected_concepts = set()
        self.assertEqual(set(concepts), expected_concepts)
