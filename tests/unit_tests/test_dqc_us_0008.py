import unittest
from arelle import ValidateXbrl, ModelRelationshipSet
from unittest.mock import MagicMock, patch
from arelle.ModelManager import ModelManager
from arelle.ModelXbrl import ModelXbrl
from arelle.ModelRelationshipSet import ModelRelationshipSet
from arelle.ModelDtsObject import ModelConcept

from dqc_us_rules import dqc_us_0008


class TestDQC0008(unittest.TestCase):
    def setUp(self):
        self.concept_1 = MagicMock(
            spec=ModelConcept,
            qname=MagicMock(
                namespaceURI='http://fasb.org/us-gaap/2015-01-31',
                localName='IncomeTaxExpenseBenefit'
            )
        )
        self.concept_2 = MagicMock(
            spec=ModelConcept,
            qname=MagicMock(
                namespaceURI='http://fasb.org/us-gaap/2015-01-31',
                localName='IncomeTaxExpenseBenefitIntraperiodTaxAllocation'
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
            spec=ModelRelationshipSet
        )
        self.namespace_docs = {
            'http://www.xbrl.org/2003/linkbase': "val1",
            'http://xbrl.sec.gov/currency/2016-01-31': "val2",
            'http://fasb.org/us-gaap/2016-01-31': "val3",
            'http://xbrl.sec.gov/country/2016-01-31': "val4"
        }
        self.mock_namespace = self.namespace_docs
        self.mock_manager = MagicMock(
            spec=ModelManager
        )
        self.mock_modelxbrl = MagicMock(
            modelManager=self.mock_manager,
            spec=ModelXbrl,
            namespaceDocs = self.mock_namespace
            )
        self.mock_modelxbrl.relationshipSet.return_value = self.rel_set_1
        self.mock_value = MagicMock(
            spec=ValidateXbrl.ValidateXbrl,
            modelXbrl=self.mock_modelxbrl
        )

    def tearDown(self):
        pass

    def test_determine_namespace(self):
        """
        Tests the function that detects the namespace of the filing
        """
        cmp_result = 'dqc_0008_2016.json'
        self.assertEqual(
            dqc_us_0008._determine_namespace(self.mock_value)[-18:],
            # Only checking [-18:] because function returns the whole
            # constructed path for the document
            cmp_result,
            'Namespace mismatch'
        )


    @patch('arelle.ModelXbrl.ModelRelationshipSet', autospec=True)
    def test_find_errors(self, relationship):
        """
        Tests the check itself
        """
        result = dqc_us_0008._find_errors(self.mock_value)
        from_mo = result[0].fromModelObject.qname.localName
        to_mo = result[0].toModelObject.qname.localName
        self.assertEqual(
            from_mo,
            'IncomeTaxExpenseBenefit',
            'From concept mismatch.'
        )
        self.assertEqual(
            to_mo,
            'IncomeTaxExpenseBenefitIntraperiodTaxAllocation',
            'To concept mismatch.'
        )
