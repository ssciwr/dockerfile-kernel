# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Dockerfile Kernel'
copyright = '2023, Dominic Kempf, Marco Lorenz, Shuangshuang Li, Marvin Weitz'
author = 'Dominic Kempf, Marco Lorenz, Shuangshuang Li, Marvin Weitz'

# -- Docstring configuration --------------------------------------------------
import os
import sys
import commonmark

sys.path.insert(0, os.path.abspath('..'))

def docstring(app, what, name, obj, options, lines):
    # https://stackoverflow.com/a/56428123/11785440
    md  = '\n'.join(lines)
    ast = commonmark.Parser().parse(md)
    rst = commonmark.ReStructuredTextRenderer().render(ast)
    lines.clear()
    lines += rst.splitlines()

def setup(app):
    app.connect('autodoc-process-docstring', docstring)

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']
