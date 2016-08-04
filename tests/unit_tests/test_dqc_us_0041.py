import unittest
from unittest import mock

from arelle import XbrlConst
from arelle.ModelDtsObject import ModelRelationship
from arelle.ValidateXbrl import ValidateXbrl

from dqc_us_rules import dqc_us_0041


class TestDefaultDimensions(unittest.TestCase):
    def test_default_dimension_mismatch(self):
        """
        Tests to see if _default_dimension_mismatch can determine if two
        dimensions match or not
        """
        bad_relation = mock.MagicMock(spec=ModelRelationship)
        bad_relation.fromModelObject = mock.MagicMock()
        bad_relation.fromModelObject.name = "DebtInstrumentNameDomain"
        bad_relation.toModelObject = mock.MagicMock()
        bad_relation.toModelObject.name = "DebtInstrumentDomain"

        bad_validation = mock.MagicMock(spec=ValidateXbrl)
        bad_validation.usgaapDefaultDimensions = {
            bad_relation.fromModelObject.name: "TEST"
        }
        self.assertTrue(
            dqc_us_0041._default_dimension_mismatch(
                relation=bad_relation, validation=bad_validation
            )
        )

    def test_default_dimensions_missing(self):
        """
        Tests handling of the validation not having a usgaapDefaultDimensions
        """
        bad_relation = mock.MagicMock(spec=ModelRelationship)
        bad_relation.fromModelObject = mock.MagicMock()
        bad_relation.fromModelObject.name = "DebtInstrumentNameDomain"
        bad_relation.toModelObject = mock.MagicMock()
        bad_relation.toModelObject.name = "DebtInstrumentDomain"

        bad_validation = mock.MagicMock(spec=ValidateXbrl)

        self.assertFalse(
            dqc_us_0041._default_dimension_mismatch(
                relation=bad_relation, validation=bad_validation
            )
        )

    def test_default_dimension_mismatch_with_no_mismatch(self):
        """
        Tests to make sure the _default_dimension_mismatch doesn't always throw
        an error
        """
        good_relation = mock.MagicMock(spec=ModelRelationship)
        good_relation.fromModelObject = mock.MagicMock()
        good_relation.fromModelObject.name = "DebtInstrumentNameDomain"
        good_relation.toModelObject = mock.MagicMock()
        good_relation.toModelObject.name = "DebtInstrumentDomain"

        good_validation = mock.MagicMock(spec=ValidateXbrl)
        good_validation.usgaapDefaultDimensions = {
            good_relation.fromModelObject.name: (
                good_relation.toModelObject.name
            )
        }
        self.assertFalse(
            dqc_us_0041._default_dimension_mismatch(
                relation=good_relation, validation=good_validation
            )
        )

    @mock.patch("dqc_us_rules.dqc_us_0041._load_cache", autospec=True)
    @mock.patch(
        "dqc_us_rules.dqc_us_0041._default_dim_rel_is_instance",
        return_value=True
    )
    @mock.patch(
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

    @mock.patch("dqc_us_rules.dqc_us_0041._load_cache", autospec=True)
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
