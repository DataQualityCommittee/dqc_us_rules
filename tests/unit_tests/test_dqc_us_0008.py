import unittest
from unittest.mock import Mock, MagicMock, patch
from arelle.ModelInstanceObject import ModelFact, ModelDimensionValue
from dqc_us_rules import util

from dqc_us_rules import dqc_us_0008
from arelle import ModelRelationshipSet, ModelXbrl, Cntlr, ModelManager, WebCache, ModelValue

from arelle.ModelDtsObject import ModelRoleType, ModelRelationship, ModelConcept



class TestDQC0008(unittest.TestCase):
    @patch('arelle.ModelXbrl.load')
    def test_create_config(self, mock_modelXbrl_1):
        """
        Tests config file creation
        """
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

        mock_modelXbrl_1= Mock(
            spec=ModelXbrl,
            modelDocument=model_document_doc,
            factsByQname=facts_by_qname,
            modelManager=mock_manager
        )
        mock_modelXbrl_3=return.value




        self.assertTrue(
            dqc_us_0008._create_config(self)
        )

    def test_determine_namespace(self):
        """
        Tests the
        :return:
        :rtype:
        """
        # val.modelXbrl.namespaceDocs
        namespace_docs = {
        'http://www.xbrl.org/2003/linkbase': '[ModelDocument[__19]())]',
        'http://xbrl.sec.gov/currency/2016-01-31': '[ModelDocument[__19401]())]',
        'http://fasb.org/us-gaap/2016-01-31': '[ModelDocument[__7]())]',
        'http://xbrl.sec.gov/country/2016-01-31': '[ModelDocument[__19122]())]'
        }
        mock_manager = Mock(spec= modelManager, cntrl = Mock())
        mock_modelXbrl = Mock(spec= ModelXbrl, modelManager = mock_manager)
        namespaceDocs = Mock(spec=ModelXbrl.namespaceDocs, cntrl=Mock(), namespaceDocs=namespace_docs)
        val = Mock()
        val.ModelXbrl=mock_modelXbrl
        val.ModelXbrl.namespaceDocs=namespaceDocs

        self.assertTrue(
            dqc_us_0008._determine_namespace(val)
        )

        # def test_run_checks(self):
        #     """
        #     Tests validation check is running
        #     :param self:
        #     :type self:
        #     :return:
        #     :rtype:
        #     """