"""
Copyright 2022 Balacoon

base class data iterator.
shows interface that data interator should implement
"""

from typing import Tuple
from abc import ABC, abstractmethod


class DataIterator(ABC):
    def __init__(self, location: str, subset: str = "test", n_utterances: int = -1):
        """
        creates data iterator

        Parameters
        ----------
        location: str
            directory with downloaded and unpacked dataset.
            when passed to appropriate data iterator, it should know
            how to deal with it.
        subset: str
            name of subset to iterate through.
            check actual implementation to learn what is supported
            for particular dataset.
        n_utterances: int
            number of utterances to read from subset. if -1 - reads all.
        """
        pass

    @abstractmethod
    def __iter__(self):
        """
        initializes data iterator
        """
        pass

    @abstractmethod
    def __next__(self) -> Tuple[str, str]:
        """
        Iterates over text normalization data

        Returns
        -------
        pair: Tuple[str, str]
            pair of strings: original and normalized utterances.
        """
        pass
