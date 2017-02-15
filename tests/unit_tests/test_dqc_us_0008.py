import unittest
from unittest.mock import Mock, MagicMock
from dqc_us_rules import util

from dqc_us_rules import dqc_us_0008
from arelle import ModelRelationshipSet, ModelXbrl, Cntlr, ModelManager


from arelle.ModelDtsObject import ModelRoleType, ModelRelationship, ModelConcept



class TestDQC0008(unittest.TestCase):
    def test_create_config(self):
        """
        Tests that fact errors if it contains a deprecated concept
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
        mock_cntrl = MagicMock(spec=Cntlr)
        mock_manager = Mock(spec= ModelManager, cntrl = mock_cntrl)
        mock_modelXbrl = Mock(spec= ModelXbrl, modelManager = mock_manager)
        validateDisclosureSystem = 'False'
        val=Mock()
        val.modelXbrl=mock_modelXbrl
        val.RelationshipSet=model_rel_set
        val.modelXbrl.modelManager.cntlr = mock_cntrl
        val.ModelXbrl.modelManager.validateDisclosureSystem=validateDisclosureSystem


        self.assertNotNone(
            dqc_us_0008._create_config(val)
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

        self.assertNotNone(
            dqc_us_0008._determine_namespace(val)
        )