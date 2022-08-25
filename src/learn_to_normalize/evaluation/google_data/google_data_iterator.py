"""
Copyright 2022 Balacoon

Iterates over google dataset.
Format is token per line, so some logic to merge utterances is required.
"""

import os
import re
import glob
import logging
from typing import Tuple

from learn_to_normalize.evaluation.data_iterator import DataIterator
from learn_to_normalize.evaluation.google_data.parsed_utterance import ParsedUtterance


class GoogleDataIterator(DataIterator):
    """
    Data iterator over Google text normalization data
    (https://www.kaggle.com/datasets/richardwilliamsproat/text-normalization-for-english-russian-and-polish).
    Unpacked data contains multiple text files with one token per line, that looks like that:

    ::

        PLAIN	Brillantaisia	<self>
        PLAIN	is	<self>
        PLAIN	a	<self>
        PLAIN	genus	<self>
        PLAIN	of	<self>
        PLAIN	plant	<self>
        PLAIN	in	<self>
        PLAIN	family	<self>
        PLAIN	Acanthaceae	<self>
        PUNCT	.	sil
        <eos>	<eos>

    Data iterator parses those data files and composes pairs of unnomralized/normalized utterances.
    It needs to tackle punctuation marks and spelling.
    """

    GOOGLE_SEMIOTIC_CLASSES = ["ADDRESS", "CARDINAL", "DATE", "DECIMAL", "DIGIT", "ELECTRONIC", "FRACTION",
                               "LETTERS", "MEASURE", "MONEY", "ORDINAL", "TELEPHONE", "TIME", "VERBATIM"]

    def __init__(self, location: str, subset: str = "test", n_utterances: int = -1):
        """
        constructor of google data iterator

        Parameters
        ----------
        location: str
            directory with the data, for ex. downloaded and unpacked
            https://storage.googleapis.com/kaggle-data-sets/869240/1481083/compressed/en_with_types.tgz.zip
        subset: str
            subset of the data to iterate over. supported values:

            - `test` - conventional test set of google dataset.
               For english its first 100002 tokens of output-00099-of-00100
            - `all` - iterate over all the data
            - `ADDRESS`, `CARDINAL`, ... - selects utterances with specific semiotic class present

        n_utterances: int
            number of utterances to read from subset
        """
        # find data files to read
        self._data_files = []  # list of data files to read
        self._data_file_idx = 0  # which data file is currently parsed
        self._n_tokens = -1  # max number of tokens to read
        self._n_utterances = n_utterances  # max number of utterances to read
        self._expected_semiotic = ""  # which semiotic class to pick
        if subset == "test":
            test_file = os.path.join(location, "output-00099-of-00100")
            assert os.path.isfile(test_file), "{} is not in {}".format(test_file, location)
            self._data_files = [test_file]
            self._n_tokens = 100002
            self._n_utterances = -1
            logging.info("For `test` subset processing first {} tokens from {}".format(self._n_tokens, test_file))
        elif subset == "all" or subset in self.GOOGLE_SEMIOTIC_CLASSES:
            self._data_files = glob.glob(os.path.join(location, "*"))
            if subset != "all":
                # subset specifies which semiotic class to preselect
                self._expected_semiotic = subset
        else:
            raise RuntimeError("{} subset is not supported by google data iterator. "
                               "Use test/toy/all or any from {}".format(subset, str(self.GOOGLE_SEMIOTIC_CLASSES)))

        # set up class members that track current state of reading data
        self._current_data_file = None  # data file from which we currently read
        self._processed_tokens = 0  # how many tokens we already processed
        self._processed_utterances = 0  # how many utterances we already processed

    def __iter__(self):
        """
        Reset iterating through data.
        """
        self._data_file_idx = 0
        self._processed_tokens = 0
        self._processed_utterances = 0
        return self

    def _raise_stop_iteration(self):
        """
        Helper function that prints some stats and raises
        StopIteration to exit __next__
        """
        logging.info("Processed {} utterances with {} tokens".format(
            self._processed_utterances, self._processed_tokens))
        raise StopIteration

    def _get_utterance(self) -> Tuple[str, str]:
        """
        helper function that attempts to read a single utterance from a data file.
        it reads lines before it finds "<eos>".
        it also manages the end of file, switching to read next file.
        """
        if self._current_data_file is None:
            # need to open file to read
            if self._data_file_idx >= len(self._data_files):
                # reached the end, no more data files to iterate over
                self._raise_stop_iteration()
            data_file_path = self._data_files[self._data_file_idx]
            logging.info("Opening {} for parsing".format(data_file_path))
            self._current_data_file = open(data_file_path, "r")
        utterance = ParsedUtterance()
        while True:
            line = self._current_data_file.readline().strip()
            if line.startswith("<eos>"):
                # found end of utterance, process what was read before
                break
            if not line:
                # reached end of file
                self._data_file_idx += 1
                self._current_data_file = None
                break
            parts = line.split("\t")
            if len(parts) != 3:
                raise RuntimeError("Can't parse [{}] from {}".format(line, self._data_files[self._data_file_idx]))
            utterance.add_token(*parts)

        if utterance.is_empty():
            # nothing was read from this file, attempt again recursively
            return self._get_utterance()
        else:
            if self._expected_semiotic and utterance.has_semiotic_class(self._expected_semiotic):
                # current line doesn't have a semiotic class of interest, skip
                return self._get_utterance()
            else:
                # get what was accumulated
                unnorm, norm = utterance.get_unnormalized(), utterance.get_normalized()
                # quick sanity check to confirm that utterance parsed properly
                if re.match("^[A-Za-z-' ]+$", norm):
                    self._processed_tokens += utterance.get_tokens_num()
                    self._processed_utterances += 1
                    return unnorm, norm
                else:
                    # probably failed to parse
                    logging.warning("Failed to parse utterance from {}. "
                                    "Normalized utterance [{}] contains unusual characters. "
                                    "Original utterance: [{}]".format(
                        self._data_files[self._data_file_idx], norm, unnorm))
                    return self._get_utterance()

    def __next__(self) -> Tuple[str, str]:
        """
        Iterate over the google text normalization data

        Returns
        -------
        utterance: Tuple[str, str]
            pair of strings which represent single utterance.
            specifically it is unnormalized and normalized versions
            of the utterance.
        """
        enough_tokens = 0 < self._n_tokens <= self._processed_tokens
        enough_utterances = 0 < self._n_utterances <= self._processed_utterances
        if enough_tokens or enough_utterances:
            self._raise_stop_iteration()
        return self._get_utterance()
