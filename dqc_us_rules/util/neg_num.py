import csv


def concept_map_from_csv(neg_num_file):
    """
    Returns a map of {qname: id} of the concepts to test for the blacklist

    :param neg_num_file: The .csv file containing the list of concepts for
        this rule.
    :type neg_num_file: file
    :return: A map of {qname: id}.
    :rtype: dict
    """
    with open(neg_num_file, 'rt') as f:
        reader = csv.reader(f)
        return {row[1]: row[0] for row in reader}
