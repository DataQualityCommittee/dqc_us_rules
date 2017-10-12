# (c) Copyright 2015 - 2017, XBRL US Inc. All rights reserved.
# See https://xbrl.us/dqc-license for license information.
# See https://xbrl.us/dqc-patent for patent infringement notice.
import os
import csv
from .util import messages
from arelle.PythonUtil import attrdict
from arelle.ValidateXbrlCalcs import roundFact


_CODE_NAME = 'DQC.US.0011'
_RULE_VERSION = '4.0.0'
_DQC_11_ITEMS_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0011',
    'dqc_0011.csv'
)
_NO_FACT_KEY = 'no_fact'


def run_checks(val):
    """
    Entrypoint for the rule.  Load the config, search for instances of
    reversed calculation relationships.

    :param val: val from which to gather end dates
    :type val: :class:'~arelle.ModelXbrl.ModelXbrl'
    :return: No direct return
    :rtype: None
    """
    model_xbrl = val.modelXbrl
    for check in _load_checks(model_xbrl):
        rule_index_key = check.rule_num

        n_facts = [
            fact for fact in
            model_xbrl.factsByQname.get(check.nondim_concept, tuple()) if
            check.axis not in fact.context.qnameDims
        ]
        d_facts = [
            fact for fact in
            model_xbrl.factsByQname.get(check.dim_concept, tuple())
            if fact.context.dimMemberQname(check.axis) == check.member
        ]
        for n_fact in n_facts:
            # here want dimensionless line items only
            # find fact expressed with dimensions
            for d_fact in d_facts:
                n_context = n_fact.context
                n_round_fact = roundFact(n_fact, True)
                d_round_fact = roundFact(d_fact, True)
                if (n_context.isPeriodEqualTo(d_fact.context) and
                    n_context.isEntityIdentifierEqualTo(d_fact.context) and
                    n_fact.unit.isEqualTo(d_fact.unit) and
                    _dim_match(n_fact, d_fact, check.axis) and
                        n_round_fact != d_round_fact * check.weight):
                        val.modelXbrl.error(
                            '{base_key}.{extension_key}'.format(
                                base_key=_CODE_NAME,
                                extension_key=rule_index_key
                            ),
                            messages.get_message(_CODE_NAME, _NO_FACT_KEY),
                            modelObject=(n_fact, d_fact),
                            weight=check.weight,
                            ruleVersion=_RULE_VERSION
                        )


def _dim_match(n_fact, d_fact, check_axis):
    n_dims = {k: (v.member.qname if v.isExplicit else v.typedMember.xValue)
              for k, v in n_fact.context.qnameDims.items()}
    d_dims = {k: (v.member.qname if v.isExplicit else v.typedMember.xValue)
              for k, v in d_fact.context.qnameDims.items()
              if k != check_axis}
    return n_dims == d_dims


def _load_checks(model_xbrl):
    """
    Returns a map of line items and dim items to test

    :rtype: dict by line item name of dim, line item, axis, member and weight
    """
    def _qname(local_name):
        # just get qname of concept, or None if no such local name is a concept
        try:
            return model_xbrl.nameConcepts[local_name][0].qname
        except (KeyError, IndexError):
            return None
    try:
        with open(_DQC_11_ITEMS_FILE, 'rt') as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            return [attrdict(
                rule_num=int(row[0]),
                nondim_concept=_qname(row[1]),
                dim_concept=_qname(row[2]),
                axis=_qname(row[3]),
                member=_qname(row[4]),
                weight=int(row[5])
            )
                    for row in reader]
    except (FileNotFoundError, ValueError):
        return ()


def _check_for_exclusions(fact):
    """
    Checks facts to determine whether the facts contains members or axes we
    do not want to check

    :param fact: fact to check
    :type fact: :class:'~arelle.InstanceModelObject.ModelFact'
    :return: False (so we don't continue) if the fact contains exclusion
        criteria.
        True (so we do continue) otherwise.
    :rtype: bool
    """
    if fact.context:
        for fact_axis, fact_dim_value in fact.context.segDimValues.items():
            mem_name = fact_dim_value.memberQname.localName
            axis_name = fact_axis.qname.localName
            if not fact_dim_value.isTyped and \
                    ('LegalEntityAxis' == axis_name and
                     'ScenarioPreviouslyReportedMember' == mem_name or
                     'StatementScenarioAxis' == axis_name and
                     'RestatementAdjustmentMember' == mem_name or
                     'StatementScenarioAxis' == axis_name and
                     'ScenarioPreviouslyReportedMember' == mem_name):
                return False
        return True


__pluginInfo__ = {
    'name': _CODE_NAME,
    'version': _RULE_VERSION,
    'description': 'Calcs reversed checks.',
    # Mount points
    'Validate.XBRL.Finally': run_checks,
}
