"""
Grammar utils
=============
Generic utils for grammars.
Recipe interacts with grammar directory through utils


.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template: class.rst

    GrammarLoader
    BaseFst

Some functions and pynini shortcuts that are reused in grammars
throughout the locales are in data_loader.py and shortcuts.py

"""

from learn_to_normalize.grammar_utils.base_fst import BaseFst
from learn_to_normalize.grammar_utils.grammar_loader import GrammarLoader
