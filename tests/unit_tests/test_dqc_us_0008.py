import unittest
from unittest.mock import Mock, MagicMock, patch
from arelle.ModelInstanceObject import ModelFact, ModelDimensionValue
import os
from dqc_us_rules import util

from dqc_us_rules import dqc_us_0008
from arelle import ModelRelationshipSet, ModelXbrl, Cntlr, ModelManager, WebCache, ModelValue

from arelle.ModelDtsObject import ModelRoleType, ModelRelationship, ModelConcept



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

    @patch('dqc_us_rules.dqc_us_0008.ModelXbrl', autospec=True)
    def test_create_config(self, mock_modelXbrl_1):
        """
        Tests config file creation
        """
        mock_modelXbrl_1.load.return_value = mock_modelXbrl_1
        model_document_doc = Mock(uri='http://www.documenturi.com/dir1/dir2')

        # modelRoleTypes
        role1 = MagicMock(
            spec=ModelRoleType,
            definition='1004000 - Statement - Statement of Shareholders Equity',
            roleURI='http://www.foo.com/role/StatementOfCashFlows',
            modelDocument=model_document_doc
        )
        role2 = MagicMock(
            spec=ModelRoleType,
            definition='1001000 - Statement - Statement of Financial Position',
            roleURI='http://www.foo.com/role/StatementOfCashFlows',
            modelDocument=model_document_doc
        )


        concept_1 = MagicMock(
            spec=ModelConcept,
            qname=Mock(
                localName='StockRepurchasedDuringPeriodValue',
                namespaceURI='http://xbrl.sec.gov/'
            )
        )
        concept_2 = MagicMock(
            spec=ModelConcept,
            qname=Mock(
                localName='ShareBasedCompensation',
                namespaceURI='http://xbrl.sec.gov/'
            )
        )
        concept_3 = MagicMock(
            spec=ModelConcept,
            qname=Mock(
                localName='SponsorFees',
                namespaceURI='http://xbrl.sec.gov/'
            )
        )
        concept_4 = MagicMock(
            spec=ModelConcept,
            qname=Mock(
                localName='StockRepurchasedDuringPeriodValue',
                namespaceURI='http://xbrl.sec.gov/'
            )
        )

        # modelRelationship
        rel_1 = Mock(
            spec=ModelRelationship,
            arcrole = 'summation-item',
            fromModelObject=concept_1,
            toModelObject=concept_2,
            toLocator='rel_2:locator'
        )
        rel_2 = Mock(
            spec=ModelRelationship,
            arcrole='summation-item',
            fromModelObject=concept_1,
            toModelObject=concept_3,
            toLocator='rel_3:locator'
        )
        rel_3 = Mock(
            spec=ModelRelationship,
            arcrole='summation-item',
            fromModelObject=concept_2,
            toModelObject=concept_4,
            toLocator='rel_4:locator'
        )
        rel_4 = Mock(
            spec=ModelRelationship,
            arcrole='summation-item',
            fromModelObject=concept_3,
            toModelObject=concept_4,
            toLocator='rel_4:locator'
        )

        model_rel_set = MagicMock(
            spec=ModelRelationshipSet,
            modelRelationships=[rel_1, rel_2, rel_3, rel_4]
        )
        #Dimensions
        dim_1 = Mock(
            spec=ModelDimensionValue,
            member=Mock(
                qname=Mock(
                    namespaceURI='http://fasb.org/us-gaap/2015-01-31',
                    localName='NoncontrollingInterestMember'
                )
            ),
            isExplicit=True
        )

        #qnames
        qname_1 = ModelValue.QName(
            'us-gaap',
            'http://fasb.org/us-gaap/2015-01-31',
            'ProfitLoss'
        )
        qname_2 = ModelValue.QName(
            'us-gaap',
            'http://fasb.org/us-gaap/2015-01-31',
            'NetIncomeLossAttributableToNoncontrollingInterest'
        )
        #segDimValues
        dim_values_1 = {'dim_1': dim_1}
        dim_values_2 = {}

        #facts
        fact_1 = Mock(
            spec=ModelFact,
            context=Mock(segDimValues=dim_values_1, startDatetime='01/01/15', endDatetime='12/31/15'),
            xValue=1000
        )
        fact_2 = Mock(
            spec=ModelFact,
            context=Mock(segDimValues=dim_values_2, startDatetime='01/01/15', endDatetime='12/31/15'),
            xValue=2000
        )
        fact_3 = Mock(
            spec=ModelFact,
            context=Mock(segDimValues=dim_values_1, startDatetime='01/01/14', endDatetime='12/31/14'),
            xValue=1000
        )
        fact_4 = Mock(
            spec=ModelFact,
            context=Mock(segDimValues=dim_values_2, startDatetime='01/01/14', endDatetime='12/31/14'),
            xValue=1000
        )
        fact_5 = Mock(
            spec=ModelFact,
            context=Mock(segDimValues=dim_values_1, startDatetime='01/01/13', endDatetime='12/31/13'),
            xValue=1000
        )
        fact_6 = Mock(
            spec=ModelFact,
            context=Mock(segDimValues=dim_values_1, startDatetime='01/01/13', endDatetime='12/31/13'),
            xValue=2000
        )
        fact_7 = Mock(
            spec=ModelFact,
            context=Mock(segDimValues=dim_values_2, startDatetime='01/01/12', endDatetime='12/31/12'),
            xValue=1000
        )
        fact_8 = Mock(
            spec=ModelFact,
            context=Mock(segDimValues=dim_values_2, startDatetime='01/01/12', endDatetime='12/31/12'),
            xValue=2000
        )

        facts_by_qname = {
            qname_1: [fact_1, fact_3, fact_5, fact_7],
            qname_2: [fact_2, fact_4, fact_6, fact_8]
        }
        mock_getfilename=Mock()
        mock_webCache=Mock(spec=WebCache, getfilename=mock_getfilename)
        mock_cntrl=MagicMock(spec=Cntlr, webCache=mock_webCache)
        mock_manager=Mock(spec= ModelManager, cntlr=mock_cntrl, validateDisclosureSystem='false')
        mock_modelXbrl_2=Mock(spec= ModelXbrl, modelManager=mock_manager)
        val=Mock(modelXbrl=mock_modelXbrl_2, RelationshipSet=model_rel_set)

        mock_modelXbrl_1.modelDocument=model_document_doc
        mock_modelXbrl_1.factsByQname=facts_by_qname
        mock_modelXbrl_1.modelManager=mock_manager

        # mock_modelXbrl_3=return.value




        self.assertTrue(
            dqc_us_0008._create_config(val)
        )

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
