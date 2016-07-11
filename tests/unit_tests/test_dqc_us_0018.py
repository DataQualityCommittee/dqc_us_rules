import unittest
from unittest import mock

from dqc_us_rules import dqc_us_0018

from arelle.ModelDtsObject import ModelConcept


class TestCompareFacts(unittest.TestCase):
    def test_fact_checkable(self):
        """
        Tests that fact is checkable
        """
        good_fact = mock.Mock()

        bad_fact = mock.Mock()
        bad_fact.concept = None
        bad_fact.context = None

        self.assertTrue(
            dqc_us_0018._fact_checkable(good_fact)
        )

        self.assertFalse(
            dqc_us_0018._fact_checkable(bad_fact)
        )

    def test_deprecated_concept(self):
        """
        Tests that fact errors if it contains a deprecated concept
        """
        val = mock.Mock()
        val.usgaapDeprecations = {}
        val.usgaapDeprecations['HealthCareOrganizationChangeInWriteOffs'] = (
            "Element was deprecated because it was inappropriately modeled. "
            "Possible replacement is "
            "AllowanceForDoubtfulAccountsReceivableWriteOffs."
        )
        bad_concept = mock.Mock(spec=ModelConcept)
        bad_concept.name = 'HealthCareOrganizationChangeInWriteOffs'
        good_concept = mock.Mock(spec=ModelConcept)
        good_concept.name = (
            'AllowanceForDoubtfulAccountsReceivableWriteOffs'
        )
        none_concept = None

        self.assertTrue(
            dqc_us_0018._deprecated_concept(val, bad_concept)
        )

        self.assertFalse(
            dqc_us_0018._deprecated_concept(val, good_concept)
        )

        self.assertFalse(
            dqc_us_0018._deprecated_concept(val, none_concept)
        )

    def test_deprecated_dimension(self):
        """
        Tests that fact errors if it contains a deprecated dimension
        """
        val = mock.Mock()
        gaapDeps = {}
        gaapDeps['ComponentOfOtherExpenseNonoperatingAxis'] = (
            "Element was deprecated because the financial reporting concept "
            "is no longer conveyed dimensionally."
        )
        val.usgaapDeprecations = gaapDeps
        bad_dim = mock.Mock(spec=ModelConcept)
        bad_dim.name = 'ComponentOfOtherExpenseNonoperatingAxis'
        good_dim = mock.Mock(spec=ModelConcept)
        good_dim.name = 'LegalEntityAxis'
        none_dim = None

        self.assertTrue(
            dqc_us_0018._deprecated_dimension(
                val,
                bad_dim
            )
        )

        self.assertFalse(
           dqc_us_0018._deprecated_dimension(
               val,
               good_dim
           )
        )

        self.assertFalse(
           dqc_us_0018._deprecated_dimension(
               val,
               none_dim
           )
        )

    def test_deprecated_member(self):
        """
        Tests to make sure that fact errors it it contains a deprecated member
        """
        val = mock.Mock()
        gaapDeps = {}
        gaapDeps['OtherMember'] = (
             "Element was deprecated. Possible replacement is "
             "OtherCreditDerivativesMember."
        )
        val.usgaapDeprecations = gaapDeps
        bad_mem = mock.Mock(spec=ModelConcept)
        bad_mem.name = 'OtherMember'
        good_mem = mock.Mock(spec=ModelConcept)
        good_mem.name = 'OtherCreditDerivativesMember'

        self.assertTrue(
            dqc_us_0018._deprecated_dimension(
                val,
                bad_mem
            )
        )

        self.assertFalse(
           dqc_us_0018._deprecated_dimension(
               val,
               good_mem
           )
        )

    def test_fact_uses_deprecated_item_concept(self):
        """
        Tests to make sure that fact errors it it contains a deprecated member
        """
        val = mock.Mock()
        gaapDeps = {}
        gaapDeps['old'] = (
             "Element was deprecated. Possible replacement is "
             "new."
        )
        val.usgaapDeprecations = gaapDeps
        dep_concept = mock.Mock(spec=ModelConcept)
        dep_concept.name = 'old'

        context = mock.Mock()
        context.segDimValues = {}

        fact = mock.Mock(concept=dep_concept, context=context)

        fire, item = dqc_us_0018._fact_uses_deprecated_item(
            val,
            fact
        )

        self.assertTrue(fire)
        self.assertEqual(item, 'old')

    def test_fact_uses_deprecated_item_dimconcept(self):
        """
        Tests to make sure that fact errors it it contains a deprecated member
        """
        val = mock.Mock()
        gaapDeps = {}
        gaapDeps['old'] = (
             "Element was deprecated. Possible replacement is "
             "new."
        )
        val.usgaapDeprecations = gaapDeps
        dep_concept = mock.Mock(spec=ModelConcept)
        dep_concept.name = 'old'

        good_concept = mock.Mock(spec=ModelConcept)
        good_concept.name = 'trey'

        context = mock.Mock()
        context.segDimValues = {
            dep_concept: mock.Mock()
        }

        fact = mock.Mock(
            concept=good_concept,
            context=context,
            isItem=True
        )

        fire, item = dqc_us_0018._fact_uses_deprecated_item(
            val,
            fact
        )

        self.assertTrue(fire)
        self.assertEqual(item, 'old')

    def test_fact_uses_deprecated_item_dimvalue(self):
        """
        Tests to make sure that fact errors it it contains a deprecated member
        """
        val = mock.Mock()
        gaapDeps = {}
        gaapDeps['old'] = (
             "Element was deprecated. Possible replacement is "
             "new."
        )
        val.usgaapDeprecations = gaapDeps
        dep_concept = mock.Mock(spec=ModelConcept)
        dep_concept.name = 'old'

        good_concept = mock.Mock(spec=ModelConcept)
        good_concept.name = 'trey'

        dep_dim = mock.Mock(dimension=dep_concept)

        context = mock.Mock()
        context.segDimValues = {
            good_concept: dep_dim
        }

        fact = mock.Mock(
            concept=good_concept,
            context=context,
            isItem=True
        )

        fire, item = dqc_us_0018._fact_uses_deprecated_item(
            val,
            fact
        )

        self.assertTrue(fire)
        self.assertEqual(item, 'old')

    def test_catch_linkbase_deprecated_errors(self):
        """
        Tests for deprecated concepts in relationships
        """
        val = mock.Mock()
        val.modelXbrl.namespaceDocs = {
            "http://fasb.org/us-gaap/2015-01-31": [0]
        }
        deprecated_concept = "PolicyChargesInsurance"
        from_model = mock.Mock(spec=ModelConcept)
        from_model.name = deprecated_concept
        to_model = mock.Mock(spec=ModelConcept)
        to_model.name = deprecated_concept
        val.usgaapDeprecations = [deprecated_concept]
        relationship = mock.Mock(
            fromModelObject=from_model,
            toModelObject=to_model
        )
        relset = mock.Mock(modelRelationships=[relationship])
        val.modelXbrl.relationshipSet.return_value = relset
        deprecated_concepts = {}
        dqc_us_0018._catch_linkbase_deprecated_errors(val, deprecated_concepts)
        self.assertEqual(1, len(deprecated_concepts.keys()))
        self.assertTrue(deprecated_concept in deprecated_concepts.keys())
