import unittest
from unittest.mock import MagicMock, patch
from arelle.ModelManager import ModelManager
from arelle.ModelXbrl import ModelXbrl
from arelle.ModelRelationshipSet import ModelRelationshipSet
import arelle.ValidateXbrl, arelle.ModelDtsObject, arelle.ModelRelationshipSet
from dqc_us_rules import dqc_us_0046


class TestDQC0046(unittest.TestCase):
    def setUp(self):
        self.concept_1 = MagicMock(
            spec=arelle.ModelDtsObject.ModelConcept,
            qname=MagicMock(
            namespaceURI='http://fasb.org/us-gaap/2015-01-31',
            localName='Assets'
            )
        )
        self.concept_2 = MagicMock(
            spec=arelle.ModelDtsObject.ModelConcept,
            qname=MagicMock(
            namespaceURI='http://fasb.org/us-gaap/2015-01-31',
            localName='NoncurrentAssets'
            )
        )
        #modelRelationship
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
            spec=arelle.ModelXbrl.ModelRelationshipSet
        )

        self.mock_manager = MagicMock(
            spec=ModelManager,
            cntrl=MagicMock()
        )
        self.mock_modelxbrl = MagicMock(
            modelManager=self.mock_manager,
            spec=ModelXbrl
            )
        self.mock_modelxbrl.relationshipSet.return_value = self.rel_set_1
        self.mock_value = MagicMock(
            spec=arelle.ValidateXbrl.ValidateXbrl,
            modelXbrl=self.mock_modelxbrl
        )
        pass

    def tearDown(self):
        pass

    @patch('arelle.ModelXbrl.ModelRelationshipSet')
    def test_find_errors(self, relationship):
        """
        Tests the check itself
        """
        result = dqc_us_0046._find_errors(self.mock_value)
        from_mo = result[0].fromModelObject.qname.localName
        to_mo = result[0].toModelObject.qname.localName
        self.assertEqual(from_mo, 'Assets')
        self.assertEqual(
            to_mo, 'NoncurrentAssets'
        )