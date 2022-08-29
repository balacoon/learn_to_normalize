Usage
=====

In order to build text normalization addon:

1. get the repo

.. code-block::

   git clone git@github.com:balacoon/learn_to_normalize.git

2. build docker that manages all the dependencies

.. code-block::

    # if "build-tn" is specified, text_normalization
    # is built from sources. You need special access for it
    # which you likely dont have.
    bash docker/build.sh [--build-tn]

3. get text normalization rules. Adjust those if needed, but don't
   forget to share changes as a contribution.

.. code-block::

    # text normalization rules are stored as submodules, pick one you need
    # from grammars dir
    git submodule update --init grammars/en_us_normalization/

4. launch docker and execute addon creation. This will just compile
   text normalization rules and pack them.

.. code-block::

    # script is really simple shortcut to start container. Adjust it
    # if needed
    bash docker/run.sh
    # create addon
    learn_to_normalize --locale en_us --work-dir work_dir \
        --resources grammars/en_us_normalization/production/ \
        --out en_us_normalization.addon

5. learn_to_normalize contains interactive demos for debugging
   and to showcase how to use obtained artifacts.

.. code-block::

    # executing single grammar to debug it
    demo_grammar --grammars grammars/en_us_normalization/production/ --module classify.time --name TimeFst
    # using packed addon
    demo_normalize --addon work_dir/normalization.addon

6. finding flaws in rules, checking stability and evaluating performance of built rule-set is essential next
   step:

.. autosummary::
    :toctree: generated

    learn_to_normalize.evaluation

