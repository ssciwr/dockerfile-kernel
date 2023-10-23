# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Dockerfile Kernel"
copyright = "2023, Dominic Kempf, Marco Lorenz, Shuangshuang Li, Marvin Weitz"
author = "Dominic Kempf, Marco Lorenz, Shuangshuang Li, Marvin Weitz"

# -- Docstring configuration --------------------------------------------------
import os
import sys
import commonmark

sys.path.insert(0, os.path.abspath(".."))


def docstring(app, what, name, obj, options, lines):
    # https://stackoverflow.com/a/70174158
    wrapped = []
    literal = False
    for line in lines:
        if line.strip().startswith(r"```"):
            literal = not literal
        if not literal:
            line = " ".join(x.rstrip() for x in line.split("\n"))
            indent = len(line) - len(line.lstrip())
        if indent and not literal:
            wrapped.append(" " + line.lstrip())
        else:
            wrapped.append("\n" + line.strip())
    ast = commonmark.Parser().parse("".join(wrapped))
    rst = commonmark.ReStructuredTextRenderer().render(ast)
    lines.clear()
    lines += rst.splitlines()


def setup(app):
    app.connect("autodoc-process-docstring", docstring)


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "sphinx.ext.autosummary"]
autodoc_mock_imports = ["dockerfile_kernel.__main__"]  # Otherwise Kernel would start
autosummary_generate = True


templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store", "_template"]


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
