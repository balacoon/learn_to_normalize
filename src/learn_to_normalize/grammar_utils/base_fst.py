"""
Copyright 2022 Balacoon

base class for all the grammars
"""

from typing import Union, List

import pynini
from pynini.lib import pynutil

from learn_to_normalize.grammar_utils.shortcuts import wrap_token, delete_space, insert_space


class BaseFst:
    """
    Base class for text normalization rules. Wrapper around
    pynini FST, implements some common functions used in
    tokenization / verbalization

    BaseFST implements a logic of connecting transducer to itself, for ex. when it is allowed
    to connect a semiotic class to itself. It is expected that implementations of BaseFst
    would first define self._single_fst and then can call :func:`.connect_to_self` multiple times.
    At usage (when merging all transducers together), one just refers to fst which returns
    multi or single fst depending on what's available.

    When reusing fst in other semiotic classes you probably want to access single_fst though.
    """

    def __init__(self, name: str):
        self._name = name
        self._single_fst = None
        self._multi_fst = None

    @property
    def fst(self) -> pynini.FstLike:
        if self._multi_fst is not None:
            return self._multi_fst
        assert self._single_fst is not None, "both single- and multi-token fsts are None for {}".format(self.name)
        return self._single_fst

    @property
    def single_fst(self) -> pynini.FstLike:
        return self._single_fst

    def add_tokens(self, fst: pynini.FstLike) -> pynini.FstLike:
        """
        Wraps fst into curly brackets and prepends with name of grammar.
        Used in tokenization/classification

        Parameters
        ----------
        fst: pynini.FstLike
            fst to wrap

        Returns
        -------
        fst: pynini.FstLike
            fst wrapped with grammar names
        """
        return pynutil.insert("{} {{ ".format(self._name)) + fst + pynutil.insert(" }")

    def delete_tokens(self, fst: pynini.FstLike) -> pynini.FstLike:
        """
        Removes name grammar name from string passed for verbalization

        Parameters
        ----------
        fst: pynini.FstLike
            fst to remove grammar name from

        Returns
        -------
        fst: pynini.FstLike
            fst without grammar name and trailing straight slash
        """
        return pynutil.delete("{}|".format(self._name)) + fst

    def connect_to_self(self, connector_in: Union[str, List[str]], connector_out: Union[str, List[str]],
                        connector_spaces: str = "any", weight: float = 1.0, to_closure: bool = False,
                        to_closure_connector: bool = False):
        """
        Helper function which connects self.fst to itself through intermediate connector.
        Should be applied at final stage of creating classification transducer
        For example, allows to connect cardinals with a dash, i.e. "28 - 40" which means range.
        It changes `self.fst` to `self.fst | (self.fst + connector + self.fst)`

        Parameters
        ----------
        connector_in: Union[str, List[str]]
            which connector tokens to look for. either single connector or multiple
        connector_out: Union[str, List[str]]
            what is the expansion of a connector. For example "-" in case of range is expanded to "to".
            If its none, transducer just deletes strings from `connector_in`
        connector_spaces: str
            defines which spaces are allowed around connector

            `any` - means can be no or any number of spaces both form left and right from connector
            `none_or_one` - means there is no spaces around connector or one from each side, for ex. 1:2 or 1 : 2.
            `none` - there shouldn't be any spaces around connector

        weight: float
            weight to add to multi-token branch
        to_closure: bool
            if True, allows multiple repetitions of (connector + fst)
        to_closure_connector: bool
            if True, also closure connector, so multiple occurrences of same connector between tokens are allowed
        """
        if isinstance(connector_in, str):
            connector_in = [connector_in]
        if connector_out is not None:
            if isinstance(connector_out, str):
                connector_out = [connector_out]
            assert len(connector_in) == len(connector_out), "Number of in/out connectors should be the same!"

        all_connectors = []
        if connector_out:
            for c_in, c_out in zip(connector_in, connector_out):
                connector = pynini.cross(c_in, c_out)
                connector = pynutil.insert('name: "') + connector + pynutil.insert('"')
                connector = wrap_token(connector)
                all_connectors.append(connector)
        else:
            all_connectors = [pynutil.delete(x) for x in connector_in]

        final_connector = pynini.union(*all_connectors)
        if to_closure_connector:
            closured_connector = final_connector
            if connector_out:
                closured_connector = insert_space + final_connector
            final_connector += pynini.closure(closured_connector)

        # define spaces and surround connector with spaces
        if connector_spaces == "any":
            # remove all spaces (no matter how many including 0) and insert just one.
            space = delete_space + insert_space
        elif connector_spaces == "none_or_one":
            # either accept just one space or expect no spaces and insert one
            space = pynini.accep(" ") | insert_space
        elif connector_spaces == "none":
            # no spaces around connector expected
            space = insert_space
        else:
            raise RuntimeError("Unexpected configuration of spaces around connector: {}".format(connector_spaces))
        if connector_out:
            final_connector = space + final_connector + space
        else:
            final_connector = space + final_connector + delete_space

        extra_fst = pynutil.insert(' }') + final_connector + pynutil.insert('tokens { ') + self.single_fst
        if to_closure:
            extra_fst = pynini.closure(extra_fst, 1)
        multi_fst = self.single_fst + extra_fst
        if weight != 1.0:
            multi_fst = pynutil.add_weight(multi_fst, weight)
        if self._multi_fst is not None:
            self._multi_fst |= multi_fst
        else:
            self._multi_fst = self._single_fst | multi_fst
        self._multi_fst.optimize()

    def apply(self, text: str) -> str:
        """
        helper method to apply the grammar to input text

        Parameters
        ----------
        text: str
            input string to apply transducer to

        Returns
        -------
        res: str
            transduced string. In case of tokenize/classify - returns
            string parsable into protobuf. In case of verbalization,
            converts the text into spoken form
        """
        lattice = text @ self.fst
        res = pynini.shortestpath(lattice, nshortest=1, unique=True).string()
        return res
