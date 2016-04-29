# (c) Copyright 2015 - 2016, XBRL US Inc. All rights reserved.
# See license.md for license information.
# See PatentNotice.md for patent infringement notice.
import csv
import os
from .util import facts, messages

_CODE_NAME = 'DQC.US.0001'
_RULE_VERSION = '1.1'
_DQC_01_AXIS_FILE = os.path.join(
    os.path.dirname(__file__),
    'resources',
    'DQC_US_0001',
    'dqc_01_axis.csv'
)


def run_axis_with_inappropriate_members(val):
    """

    :return:
    """
    inappropriate_members_dict = axis_map_from_csv(_DQC_01_AXIS_FILE)
    inappropriate_members_facts = find_facts_with_inappropriate_members(val, inappropriate_members_dict)


def find_facts_with_inappropriate_members(val, inappropriate_members):
    """

    :return:
    """
    inappropriate_members_list = []
    facts_list = list(val.modelXbrl.facts)

    # Find the facts that contain an axis in the list of relevant axis
    for fact in facts_list:
        if fact.dim.dimensionQname.localName in inappropriate_members:
            inappropriate_members_list.append(fact)

    for fact in inappropriate_members_list:
        if fact.dim.member is not None:
            if fact.dim.dimensionQname.localName == 'LegalEntityAxis':

            elif fact.dim.dimensionQname.localName == 'ProductOrServiceAxis':

            elif fact.dim.dimensionQname.localName == 'DefinedBenefitPlanByPlanAssetCategoriesAxis':

            else:


    return inappropriate_members_list


def axis_map_from_csv(axis_file):
    """
    Returns a map of {qname: id} of the concepts to test for the blacklist

    :return: A map of {qname: id}.
    :rtype +    """
    with open(axis_file, 'rt') as f:
        reader = csv.reader(f)
        return {row[0] for row in reader}
