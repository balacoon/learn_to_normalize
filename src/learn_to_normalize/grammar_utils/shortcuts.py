"""
Copyright 2022 Balacoon

some pynini handy shortcuts to be used in grammars
"""

import string

import pynini
from pynini.lib import byte, pynutil, utf8

CHAR = utf8.VALID_UTF8_CHAR

DIGIT = byte.DIGIT
LOWER = pynini.union(*string.ascii_lowercase).optimize()
UPPER = pynini.union(*string.ascii_uppercase).optimize()
ALPHA = pynini.union(LOWER, UPPER).optimize()
ALNUM = pynini.union(DIGIT, ALPHA).optimize()
SPACE = " "
WHITE_SPACE = pynini.union(" ", "\t", "\n", "\r", "\u00A0").optimize()
NOT_SPACE = pynini.difference(CHAR, WHITE_SPACE).optimize()
NOT_QUOTE = pynini.difference(CHAR, r'"').optimize()
NOT_BAR = pynini.difference(CHAR, r"|").optimize()

punct = "!'()-.,:;?{}\"`—"
PUNCT = pynini.union(*map(pynini.escape, punct)).optimize()
NOT_PUNCT = pynini.difference(NOT_SPACE, PUNCT).optimize()
NOT_ALPHA = pynini.difference(NOT_SPACE, ALPHA).optimize()

SIGMA = pynini.closure(CHAR)

delete_space = pynutil.delete(pynini.closure(WHITE_SPACE))
insert_space = pynutil.insert(" ")
delete_extra_space = pynini.cross(pynini.closure(WHITE_SPACE, 1), " ")

TO_LOWER = pynini.union(
    *[
        pynini.cross(x, y)
        for x, y in zip(string.ascii_uppercase, string.ascii_lowercase)
    ]
)
TO_UPPER = pynini.invert(TO_LOWER)


def wrap_token(token: pynini.FstLike) -> pynini.FstLike:
    """
    A helper function that wraps token fst after tokenization and classification into "tokens { ... }"
    This is required by the parser, that each token is distinctly wrapped.

    Parameters
    ----------
    token: pynini.FstLike
        transducer of a token to wrap

    Returns
    -------
    result: pynini.FstLike
        wrapped token, parsable into proto
    """
    return pynutil.insert("tokens { ") + token + pynutil.insert(" }")
