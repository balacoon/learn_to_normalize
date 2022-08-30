"""
As part of text-normalization challenge, Google released an automatically generated dataset
of unnormalized/normalized pairs. It is obtained by running Google rule-based frontend (Kestrel)
over Wikipedia. More info can be found in the `paper`_: "RNN Approaches to Text Normalization: A Challenge".

Download and unpack the data from Kaggle: `dataset page`_. You will need to login, but gmail account
can be used.

This data can be used to

- evaluate performance of Balacoon text normalization
- enhance existing text normalization rules by going through mismatches

Text normalization performance
------------------------------
For english, original paper reports 0.998 token-level accuracy for seq2seq model with attention and FST filter.
Accuracy is measured on first 100002 lines of output-00099-of-00100.

Balacoon performance is measured on sentence-level, since we have slightly different set of semiotic classes.
Google data is glued back together into utterances using `ParsedUtterance` and fed to `balacoon_text_normalization` package.
We achieve 0.89 sentence-level accuracy.

Vast majority of errors come from discrepancy in handling abbreviations and non-determinism in expanding numbers:

::

    Expected: fujitsu primergy RX two five four o m one
    Obtained: fujitsu primergy RX two thousand five hundred forty M one
    Original: "Fujitsu Primergy RX 2540 M1".

Nonetheless, some discrepancies indicate flaws of Balacoon normalization rules:

::

    Expected: promo CD CDRDJ six seven two one seven inches R six seven two one what ya gonna do now
    Obtained: promo CD CDRDJ six thousand seven hundred twenty one seven R six thousand seven hundred twenty one what ya gonna do now
    Original: Promo CD CDRDJ 6721, 7" R 6721 "What Ya Gonna Do Now?"

Despite occasional inaccuracies, Balacoon rules can be used as a solid starting point to develop text-normalization
fine-tuned for particular usecase.

Interfaces
----------

Adapters that help to work with google data:

.. autosummary::
    :toctree: generated/
    :nosignatures:
    :template: class.rst

    GoogleDataIterator
    ParsedUtterance

.. _paper: https://arxiv.org/abs/1611.00068
.. _dataset page: https://www.kaggle.com/datasets/richardwilliamsproat/text-normalization-for-english-russian-and-polish
"""

from learn_to_normalize.evaluation.google_data.google_data_iterator import GoogleDataIterator
from learn_to_normalize.evaluation.google_data.parsed_utterance import ParsedUtterance