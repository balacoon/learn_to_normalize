# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os
import sys

project = 'learn_to_normalize'
copyright = '2022, Balacoon'
author = 'Clement Ruhm'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

# add grammars into sys path
cur_file_path = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(cur_file_path, "..", "..", "grammars"))

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.autosummary', "numpydoc", "sphinx.ext.coverage", "sphinx.ext.viewcode"]

templates_path = ['_templates']

autosummary_generate = True
numpydoc_show_class_members = False

autodoc_default_options = {"inherited-members": False}

exclude_patterns = []

autodoc_mock_imports = ["text_normalization", "tqdm", "pynini"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
