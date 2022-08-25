"""
Google text normalization data
==============================
As part of text-normalization challenge, Google released an automatically generated dataset
of unnormalized/normalized pairs. It is obtained by running Google rule-based frontend (Kestrel)
over Wikipedia. More info can be found in the paper: `"RNN Approaches to Text Normalization: A Challenge"`_.

Download and unpack the data from Kaggle: `dataset page`_. You will need to login, but gmail account
can be used.

This data can be used to

- evaluate performance of Balacoon text normalization
- enhance existing text normalization rules by going through mismatches

Text normalization performance
------------------------------
For english, original paper reports 0.998 accuracy for seq2seq model with attention and FST filter.
Accuracy is measured on first 100002 lines of output-00099-of-00100

Improve existing rules
----------------------

.. _"RNN Approaches to Text Normalization: A Challenge": https://arxiv.org/abs/1611.00068
.. _dataset page: https://www.kaggle.com/datasets/richardwilliamsproat/text-normalization-for-english-russian-and-polish
"""