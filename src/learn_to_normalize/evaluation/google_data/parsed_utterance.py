"""
Copyright 2022 Balacoon

a holder for tokens that are getting parsed
from a google data file.
"""

import re
import unidecode


class ParsedUtterance:
    """
    A data structure that contains unnormalized and normalized tokens
    parsed from a Google data file. This class also contains
    knowledge how google data conventions map to Balacoon text_normalization formats.
    """
    def __init__(self):
        self._tags = []
        self._unnormalized = []
        self._normalized = []
        self._next_token_prefix = ""
        self._is_first_qoute = True

    @staticmethod
    def _strip_letter_suffix(normalized: str) -> str:
        """
        ELECTRONIC semiotic class has fields being
        spelled letter by letter, where each character
        gets special "_letter" suffix. This is a helper
        method to collapse that suffix.
        """
        if "_letter" not in normalized:
            return normalized
        parts = normalized.split()
        new_parts = []
        cur_word = []
        for p in parts:
            if p.endswith("_letter"):
                p = p[:-len("_letter")]
                if p:
                    cur_word.append(p.upper())
                elif cur_word:
                    # its just suffix. indicates whitespace
                    new_parts.append("".join(cur_word))
                    cur_word = []
            else:
                if cur_word:
                    new_parts.append("".join(cur_word))
                    cur_word = []
                new_parts.append(p)
        if cur_word:
            new_parts.append("".join(cur_word))
        return " ".join(new_parts)

    def add_token(self, tag: str, unnormalized: str, normalized: str):
        """
        once a line from data file is read, add that info into
        currently parsed utterance
        """
        self._tags.append(tag)
        # most of the work is to handle punctiation marks. need to attach them properly
        if tag == "PUNCT":
            if not self._unnormalized or unnormalized in ["(", "{", "["]:
                # if there is no previous token or its an opening bracket,
                # then its should be attached to the next token
                self._next_token_prefix += unnormalized
            elif unnormalized == "\"":
                # handling a qoute trying to track if its an opening or a closing one
                if self._is_first_qoute:
                    self._is_first_qoute = False
                    self._next_token_prefix += unnormalized
                else:
                    self._unnormalized[-1] = self._unnormalized[-1] + unnormalized
                    self._is_first_qoute = True
            else:
                # other punctuation marks are just attached to the previous token
                if self._next_token_prefix:
                    # there is some prefix but no actual token was found
                    unnormalized = self._next_token_prefix + unnormalized
                    self._next_token_prefix = ""
                self._unnormalized[-1] = self._unnormalized[-1] + unnormalized
        else:
            # this is non punct semiotic class
            if normalized == "<self>":
                normalized = unnormalized.lower()
            if tag == "LETTERS":
                normalized = normalized.replace(" ", "").upper()
            if tag == "VERBATIM" and re.match("[a-z]( [a-z])+", normalized):
                # its an abbreviation
                normalized = normalized.replace(" ", "").upper()
            # replace all non-ascii characters if any
            normalized = unidecode.unidecode(normalized)
            # strip all "_letter" suffixes if any
            normalized = self._strip_letter_suffix(normalized)
            if normalized and normalized != "sil":
                self._normalized.append(normalized)
            if self._next_token_prefix:
                # there is some prefix but no actual token was found
                unnormalized = self._next_token_prefix + unnormalized
                self._next_token_prefix = ""
            self._unnormalized.append(unnormalized)

    def has_semiotic_class(self, tag: str) -> bool:
        """
        checks if this utterance has particular semiotic class

        Parameters
        ----------
        tag: str
            semiotic class to look for

        Returns
        -------
        flag: bool
            True if this utterance has requested semiotic class
        """
        return tag in self._tags

    def get_unnormalized(self) -> str:
        """
        getter to return unnomralized utterance as a single string
        concatenates previously accumulated unnormalized tokens

        Returns
        -------
        unnorm: str
            string with unnormalized utterance
        """
        unnorm = " ".join(self._unnormalized)
        # remove space after slash if any
        unnorm = unnorm.replace("/ ", "/")
        return unnorm

    def get_normalized(self) -> str:
        """
        getter to return normalized utterance as a single string.
        essentially a ground truth for text normalization.
        concatenates previously accumulated normalized tokens

        Returns
        -------
        norm: str
            string with normalized utterance
        """
        return " ".join(self._normalized)

    def get_tokens_num(self):
        """
        getter that returns number of tokens that were added to this utterance

        Returns
        -------
        num: int
            number of tokens added
        """
        return len(self._tags)

    def is_empty(self) -> bool:
        """
        checks if any tokens where added to the utterance

        Returns
        -------
        flag: bool
            True if no tokens where added to this utterance
        """
        return self.get_tokens_num() == 0
