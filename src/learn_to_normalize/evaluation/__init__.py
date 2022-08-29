"""
Text normalization is a complex non-determinstic task
with long tail of errors. Therefore, evaluating
text normalization is challenging and not always descriptive.
Having an evaluation corpus is still highly beneficial, since
it helps to find problematic utterances and adjust normalization
rules.

`evaluate` tool loads pairs of unnormalized/normalized utterances,
applies `test_normalization` to unnormalized one and compairs
it to normalized one. This generic logic relies on data iterator
interface.

Text-normalization datasets supported:

.. autosummary::
    :toctree: generated

    learn_to_normalize.evaluation.google_data

In order to run evaluation and generate report with mismatches:

.. code-block::

    # from within docker
    # see google data docs on how to obtain the data
    # see usage docs on how to build the addon
    evaluate --addon work_dir/normalization.addon --dataset google_en
        --datadir src/learn_to_normalize/evaluation/google_data/en_with_types/
        --subset test --log report.txt

"""