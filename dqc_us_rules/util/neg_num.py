import csv


def concept_map_from_csv(neg_num_file):
    """
    Returns a map of {qname: id} of the concepts to test for the blacklist

    :return: A map of {qname: id}.
    :rtype: dict
    """
    with open(neg_num_file, 'rt') as f:
        reader = csv.reader(f)
        return {row[1]: row[0] for row in reader}