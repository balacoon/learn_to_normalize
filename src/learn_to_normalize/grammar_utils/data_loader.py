"""
Copyright 2022 Balacoon

Helper functions to load data
that can be used in grammars
"""

import csv
from typing import List, Union

import pynini
from pynini.lib import pynutil

from learn_to_normalize.grammar_utils.shortcuts import LOWER, TO_LOWER


def load_csv(path: str) -> List[Union[str, List[str]]]:
    """
    Loads csv with data to be included into grammars

    Parameters
    ----------
    path: str
        absolute path to the data file

    Returns
    -------
    rows: List[Union[str, List[str]]]
        rows of csv files, where each row is a list of fields. If csv file has just one column,
        i.e. each row has just one field, the structure is flattened and function returns list of strings
        instead of list of lists
    """
    fp = open(path)
    rows = list(csv.reader(fp, delimiter="\t"))
    if all([len(x) == 1 for x in rows]):
        # flatten rows if there is just one column
        rows = [x[0] for x in rows]
    return rows


def load_union(
    path: str, column: int = 0, case_agnostic: bool = False
) -> pynini.FstLike:
    """
    Loads csv, create accep of specified column for each row
    and union those fsts. This is useful when one wants to simply accept
    all the strings from the list without modifying them.

    Parameters
    ----------
    path: str
        path to data file to load union from
    column: int
        column of data table for which to create union.
        if file has just one column, this parameter is ignored
    case_agnostic: bool
        if true, entries are accepted in any case, otherwise
        only the one in data file is allowed

    Returns
    -------
    fst: pynini.FstLike
        union of rows from data file
    """
    data = load_csv(path)
    if not all([isinstance(x, str) for x in data]):
        # this data file contains multiple columns
        data = [x[column] for x in data]
    entries = [pynini.accep(x.strip()) for x in data]
    if case_agnostic:
        lower = pynini.closure(LOWER | TO_LOWER, 1)
        entries = [lower @ x for x in entries]
    return pynini.union(*entries)


def load_mapping(
    path: str,
    key_case_agnostic: bool = False,
    val_case_agnostic: bool = False,
    key_with_dot: bool = False,
) -> pynini.FstLike:
    """
    Loads mapping between keys and values. Usually shortenings of some sort.
    Apart from transducing keys to values, also allows values as is.
    For ex. prof.\tprofessor is a mapping that is read and converted to transducer.

    Paramaters
    ----------
    path: str
        path to data file with mapping
    key_case_agnostic: bool
        If to accept keys from mapping as both upper and lower case or only stick to variant
        specified in the mapping. If true, then mapping of prof.\tprofessor would create
        a transducer for both prof. and PROF.
    val_case_agnostic: bool
        apart from transducing keys to values, the resulting fst also accepts values as is.
        If flag is set to true, it would accept values both in lower and upper cases.
    key_with_dot: bool
        flag that specifies if there is an optional dot after the key. usually shortenings
        have an optional dot. If true - deletes this optional dot, otherwise only transduces
        keys as they appear in the data file - with or without dot.

    Returns
    -------
    fst: pynini.FstLike
        resulting transducer
    """
    rows = load_csv(path)
    assert all(
        [len(x) == 2 for x in rows]
    ), "Mapping file {} should have two columns in each row".format(path)
    keys, values = zip(*rows)

    # transduce lowercase symbols as is, convert uppercase to lowercase
    lower = pynini.closure(LOWER | TO_LOWER, 1)
    # allow multi-word. applicable mostly for values (normalized version)
    lower = lower + pynini.closure(pynini.accep(" ") + lower)

    if key_case_agnostic:
        # accept keys in different cases, transduce uppercase to lower
        keys = [lower @ pynini.accep(x) for x in keys]
    else:
        # accept keys as is
        keys = [pynini.accep(x) for x in keys]

    if key_with_dot:
        # remove optional dot from keys
        optional_dot_delete = pynini.closure(pynutil.delete("."))
        keys = [x + optional_dot_delete for x in keys]

    # transduce keys to values
    expanded_lst = [pynini.cross(x, y) for x, y in zip(keys, values)]
    expanded = pynini.union(*expanded_lst)

    # accept values a is
    if val_case_agnostic:
        values = [lower @ pynini.accep(x) for x in values]
    else:
        values = [pynini.accep(x) for x in values]
    accepted = pynini.union(*values)

    return expanded | accepted
