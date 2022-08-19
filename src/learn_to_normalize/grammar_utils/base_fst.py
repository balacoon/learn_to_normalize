"""
Copyright 2022 Balacoon

base class for all the grammars
"""

import pynini
from pynini.lib import pynutil


class BaseFst:
    """
    Base class for text normalization rules. Wrapper around
    pynini FST, implements some common functions used in
    tokenization / verbalization
    """

    def __init__(self, name: str):
        self._name = name
        self._fst = None

    @property
    def fst(self) -> pynini.FstLike:
        return self._fst

    @fst.setter
    def fst(self, fst):
        self._fst = fst

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
