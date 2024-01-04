# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Evolvable Hardware'
copyright = '2023-2024, RHIT'
author = 'RHIT'
release = '0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.todo',
              'sphinx.ext.napoleon']

templates_path = ['_templates']
exclude_patterns = []

# -- Adding Modules To sys.path so they can be addressed ---------------------
# may be possible to use __init__.py to get around this and import the project directly, like i think Scipy is doing.
import sys, os
directory_of_source_code = os.path.join(os.getcwd(),"../../../src")
sys.path.append(directory_of_source_code)



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'alabaster'
html_static_path = ['_static']

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html

todo_include_todos=True             # True if want to see todos
todo_emit_warnings=False            # True if want warnings created for each todo item that exists

# -- Options for napoleon extension ------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

napoleon_google_docstring = False           # False to turn off support for google Docstrings
napoleon_numpy_docstring = True             # True to turn on support for numpy Docstrings
napoleon_include_init_with_doc = True       # True to include __init__ as it's own function if it has an a related docstring. If false, just append to class documentation.
napoleon_include_private_with_doc = False   # True to include private members with docstrings, false resorts to Sphinx's defaults
napoleon_include_special_with_doc = True    # True to include special members like __membername__ with docstrings in documentation. If false, Sphinx defaults, defalts to true.
