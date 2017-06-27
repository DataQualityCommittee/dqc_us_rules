import unittest
from unittest.mock import MagicMock, patch
from arelle.ModelManager import ModelManager
from arelle.ModelXbrl import ModelXbrl
from arelle.ModelRelationshipSet import ModelRelationshipSet
from arelle import ValidateXbrl, ModelDtsObject
from dqc_us_rules import dqc_us_0046


class TestDQC0046(unittest.TestCase):
    def setUp(self):
        self.concept_1 = MagicMock(
            spec=ModelDtsObject.ModelConcept,
            qname=MagicMock(
                namespaceURI='http://fasb.org/us-gaap/2015-01-31',
                localName='Assets'
            )
        )
        self.concept_2 = MagicMock(
            spec=ModelDtsObject.ModelConcept,
            qname=MagicMock(
                namespaceURI='http://fasb.org/us-gaap/2015-01-31',
                localName='NoncurrentAssets'
            )
        )
        self.rel_1 = MagicMock(
            spec=ModelRelationshipSet,
            fromModelObject=self.concept_1,
            toModelObject=self.concept_2,
            arcrole='summation-item'
        )
        self.rel_set_1 = MagicMock(
            spec=ModelRelationshipSet,
            modelRelationships=[self.rel_1]
        )

        self.mock_ModelXbrlrelationshipSet = MagicMock(
            spec=ModelRelationshipSet
        )

        self.mock_manager = MagicMock(
            spec=ModelManager
        )
        self.mock_modelxbrl = MagicMock(
            modelManager=self.mock_manager,
            spec=ModelXbrl
            )
        self.mock_modelxbrl.relationshipSet.return_value = self.rel_set_1
        self.mock_value = MagicMock(
            spec=ValidateXbrl,
            modelXbrl=self.mock_modelxbrl
        )

    def tearDown(self):
        del self.concept_1
        del self.concept_2
        del self.rel_1
        del self.rel_set_1
        del self.mock_ModelXbrlrelationshipSet
        del self.mock_manager
        del self.mock_modelxbrl
        del self.mock_value
        pass

    @patch('arelle.ModelXbrl.ModelRelationshipSet')
    def test_find_errors(self, relationship):
        """
        Tests the check itself
        """
        result = dqc_us_0046._find_errors(self.mock_value)
        from_mo = result[0].fromModelObject.qname.localName
        to_mo = result[0].toModelObject.qname.localName
        self.assertEqual(
            from_mo,
            'Assets',
            'From concept mismatch.'
        )
        self.assertEqual(
            to_mo,
            'NoncurrentAssets',
            'To concept mismatch.'
        )
