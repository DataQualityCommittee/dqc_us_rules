import unittest
from unittest.mock import Mock, MagicMock, patch

from dqc_us_rules import dqc_us_0008

class TestDQC0008(unittest.TestCase):
    def setUp(self):
        self.mock_relationships = MagicMock(
            spec='arelle.ModelXbrl.ModelRelationshipSet',
            return_value=[
                '55569, linkrole: statement-note-14-income-taxes-provision-for-income-taxes-details, arcrole: summation-item, from: us-gaap:IncomeTaxExpenseBenefit, to: us-gaap:IncomeTaxExpenseBenefitIntraperiodTaxAllocation, cznc-20161231_cal.xml, line 39']
        )
        self.mock_value=MagicMock(spec='arelle.ValidateXbrl.ValidateXbrl')
        self.mock_ModelXbrlrelationshipSet = MagicMock(
            spec='arelle.ModelXbrl.ModelRelationshipSet'
        )
        self.namespace_docs = {'http://www.xbrl.org/2003/linkbase': "val1",
            'http://xbrl.sec.gov/currency/2016-01-31': "val2",
            'http://fasb.org/us-gaap/2016-01-31': "val3",
            'http://xbrl.sec.gov/country/2016-01-31': "val4"
        }
        self.mock_namespace = self.namespace_docs
        self.mock_manager = Mock(spec='arelle.ModelManager', cntrl=Mock())
        self.mock_modelxbrl = Mock(spec='arelle.modelXbrl',
            modelManager=self.mock_manager
        )
        pass

    def tearDown(self):
        pass

    def test_determine_namespace(self):
        """
        Tests the function that detects the namespace of the filing
        """
        comp_result='dqc_0008_2016.json'
        val = self.mock_value
        val.modelXbrl = self.mock_modelxbrl
        val.modelXbrl.namespaceDocs = self.mock_namespace


        self.assertEqual(
            dqc_us_0008._determine_namespace(val)[-18:], comp_result
        )

    @patch('arelle.ModelXbrl.ModelRelationshipSet')
    def test_run_checks(self, mock_relationships):
        """

        :param self:
        :type self:
        :return:
        :rtype:
        """
        val = self.mock_value
        val.modelXbrl = self.mock_modelxbrl
        val.modelXbrl.relationshipSet = self.mock_ModelXbrlrelationshipSet
        val.modelXbrl.relationshipSet.modelRelationships = self.mock_relationships
        val.modelXbrl.namespaceDocs = self.mock_namespace

        self.assertEqual(
            dqc_us_0008._run_checks(val), None
        )
