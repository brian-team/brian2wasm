# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
import os
import sys

sys.path.insert(0, os.path.abspath("."))


# -- Project information -----------------------------------------------------

project = 'brian2wasm'
copyright = '2025, Palash Chitnavis'
author = 'Palash Chitnavis'
release = '0.1.0'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',   # Pulls docstrings from code
    'sphinx.ext.viewcode',  # Adds "view source" links
    'sphinx_rtd_theme',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Create api docs
def run_apidoc(_):
    try:
        import sphinx.ext.apidoc as apidoc
    except ImportError:
        import sphinx.apidoc as apidoc
    brian2wasm_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                                   '..', 'brian2wasm'))
    docs_sphinx_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
    apidoc.main(argv=['-f', '-e', '-M',
                      '-o', os.path.join(docs_sphinx_dir, 'reference'),
                      brian2wasm_dir, os.path.join(brian2wasm_dir, 'tests')])

def setup(app):
    app.connect('builder-inited', run_apidoc)
