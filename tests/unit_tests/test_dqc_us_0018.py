import unittest
from unittest import mock
from dqc_us_rules import dqc_us_0018


class TestCompareFacts(unittest.TestCase):
    def test_fact_checkable(self):
        """
        Tests that fact is checkable
        """
        good_fact = mock.Mock()

        bad_fact = mock.Mock()
        bad_fact.concept = None
        bad_fact.context = None

        good_concept = good_fact.concept
        good_context = good_fact.context
        bad_concept = bad_fact.concept
        bad_context = bad_fact.context

        self.assertTrue(
            dqc_us_0018._fact_checkable(good_concept, good_context)
        )

        self.assertFalse(
            dqc_us_0018._fact_checkable(good_concept, bad_context)
        )

        self.assertFalse(
            dqc_us_0018._fact_checkable(bad_concept, good_context)
        )

        self.assertFalse(
            dqc_us_0018._fact_checkable(bad_concept, bad_context)
        )

    # def test_deprecated_concept(self):
    #     """
    #     Tests that fact errors if it contains a deprecated concept
    #     """
    #     val = mock.Mock()
    #     val.usgaapDeprecations = {}
    #     val.usgaapDeprecations['HealthCareOrganizationChangeInWriteOffs'] = (
    #         "Element was deprecated because it was inappropriately modeled. "
    #         "Possible replacement is "
    #         "AllowanceForDoubtfulAccountsReceivableWriteOffs."
    #     )
    #     bad_fact = mock.Mock()
    #     bad_fact.concept = mock.Mock()
    #     bad_fact.concept.name = 'HealthCareOrganizationChangeInWriteOffs'
    #
    #     good_fact = mock.Mock()
    #     good_fact.concept = mock.Mock()
    #     good_fact.concept.name = (
    #         'AllowanceForDoubtfulAccountsReceivableWriteOffs'
    #     )
    #
    #     self.assertTrue(dqc_us_0018._deprecated_concept(val, bad_fact.concept))
    #
    #     self.assertFalse(
    #         dqc_us_0018._deprecated_concept(val, good_fact.concept)
    #     )

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

        mem_qname = mock.Mock(localName='Company1')
        member = mock.Mock(qname=mem_qname)
        dim_qname = mock.Mock(localName='ComponentOfOtherExpenseNonoperatingAxis')
        dim = mock.Mock(qname=dim_qname)
        dim_lea = mock.Mock(isExplicit=True, member=member, dimension=dim)
        bad_seg_dims = {'dim1': dim_lea}
        bad_context = mock.Mock(segDimValues=bad_seg_dims)
        bad_fact = mock.Mock(context=bad_context)


        #good_fact = mock.Mock()
        #good_fact.context = mock.Mock()
        #good_fact.context = mock.Mock(
        #    segDimValues={
        #        'ComponentOfOtherExpenseNonoperatingAxis':
        #        'ComponentOfOtherExpenseNonoperatingAxis'
        #    }
        #)

        self.assertTrue(
            dqc_us_0018._deprecated_dimension(
                val,
                dim_lea
            )
        )

        #self.assertFalse(
        #    dqc_us_0018._deprecated_dimension(
        #        val,
        #        good_fact.context.segDimValues.items()[1]
        #    )
        #)

    # def test_deprecated_member(self):
    #     """
    #     Tests to make sure that fact errors it it contains a deprecated member
    #     """
    #     val = mock.Mock()
    #     val.usggapDeprecations = {}
    #     val.usgaapDeprecations['ComponentOfOtherExpenseNonoperatingAxis'] = (
    #         "Element was deprecated because the financial reporting concept "
    #         "is no longer conveyed dimensionally."
    #     )
    #
    #     bad_fact = mock.Mock()
    #     bad_fact.context = mock.Mock(
    #         segDimValues={
    #             'ComponentOfOtherExpenseNonoperatingAxis',
    #             'ComponentOfOtherExpenseNonoperatingAxis'
    #         }
    #     )
    #
    #     good_fact = mock.Mock()
    #     good_fact.context = mock.Mock(
    #         segDimValues={
    #             'ComponentOfOtherExpenseNonoperatingAxis',
    #             'ComponentOfOtherExpenseNonoperatingAxis'
    #         }
    #     )
    #
    #     self.assertTrue(
    #         dqc_us_0018._deprecated_member(
    #             val,
    #             bad_fact.context.segDimValues.items()[0]
    #         )
    #     )
    #
    #     self.assertFalse(
    #         dqc_us_0018._deprecated_member(
    #             val,
    #             good_fact.context.segDimValues.items()[0]
    #         )
    #     )
