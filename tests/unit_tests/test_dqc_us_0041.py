import unittest
from dqc_us_rules import dqc_us_0041
from unittest import mock
from unittest.mock import patch
from arelle import XbrlConst


class TestDefaultDimensions(unittest.TestCase):
    def test_default_dimension_mismatch(self):
        """
        Tests to see if _default_dimension_mismatch can determine if two
        dimensions match or not
        """
        bad_domain_pair = ["DebtInstrumentNameDomain", "DebtInstrumentDomain"]

        self.assertTrue(
            dqc_us_0041._default_dimension_mismatch(
                bad_domain_pair[0], bad_domain_pair[1]
            )
        )

    def test_default_dimension_mismatch_with_no_mismatch(self):
        """
        Tests to make sure the _default_dimension_mismatch doesn't always throw
        an error
        """
        good_domain_pair = ["DebtInstrumentDomain", "DebtInstrumentDomain"]

        self.assertFalse(
            dqc_us_0041._default_dimension_mismatch(
                good_domain_pair[0], good_domain_pair[1]
            )
        )

    @patch("dqc_us_rules.dqc_us_0041._load_cache", autospec=True)
    @patch(
        "dqc_us_rules.dqc_us_0041._default_dim_rel_is_instance",
        return_value=True
    )
    @patch(
        "dqc_us_rules.dqc_us_0041._check_relationship_exists",
        return_value=True
    )
    def test_catch_dqc_us_0041_errors_with_errors(self, third, second, first):
        """
        Tests to see if dqc_us_0041_errors will be caught
        """
        bad_count = 0
        val = mock.Mock()
        rel = mock.Mock()
        rel.toModelObject.name = "DebtInstrumentNameDomain"
        rel.fromModelObject.name = "DebtInstrumentAxis"
        val.modelXbrl.relationshipSet(
            XbrlConst.dimensionDefault
        ).modelRelationships = [rel]

        usgaap_default_dims = {}
        usgaap_default_dims["DebtInstrumentAxis"] = "DebtInstrumentDomain"
        val.usgaapDefaultDimensions = usgaap_default_dims

        for _ in dqc_us_0041._catch_dqc_us_0041_errors(val):
            bad_count += 1

        self.assertEquals(bad_count, 1)

    @patch("dqc_us_rules.dqc_us_0041._load_cache", autospec=True)
    def test_catch_dqc_us_0041_errors_with_no_errors(self, _):
        """
        Tests to make sure dqc_us_0041 doesn't always throw errors
        """
        good_count = 0

        val = mock.Mock()
        rel = mock.Mock()
        rel.toModelObject.name = "DebtInstrumentNameDomain"
        rel.fromModelObject.name = "DebtInstrumentAxis"
        val.modelXbrl.relationshipSet(
            XbrlConst.dimensionDefault
        ).modelRelationships = [rel]
        usgaap_default_dims = {}
        usgaap_default_dims["DebtInstrumentAxis"] = "DebtInstrumentNameDomain"
        val.usgaapDefaultDimensions = usgaap_default_dims
        for _ in dqc_us_0041._catch_dqc_us_0041_errors(val):
            good_count += 1

        self.assertTrue(good_count == 0)
