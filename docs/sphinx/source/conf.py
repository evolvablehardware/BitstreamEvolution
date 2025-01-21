# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import os, sys
import toml
from enum import Enum

######################### Define Available Tags ######################
class sTag(Enum):
    dev = "dev"
    release = "release"
    html = "html"
    tests_failed = "tests_failed"

# Tags are a method of 
def tag_is_applied(tag:sTag)->bool:
    return tag.value in tags

def any_tag_is_applied(tag_list:list[sTag])->bool:
    return any([tag_is_applied(tag) for tag in tag_list])

def apply_tag(tag:sTag)->None:
    tags.add(tag.value)

######################### Apply all automatic Tags ##################
if not tag_is_applied(sTag.dev):
    apply_tag(sTag.release)

apply_tag(sTag.html)

########################### Print all Tags Used #####################
print("List of all Tags Applied:")
print("\t-> All Defined Tags")
for tag in sTag:
    if tag_is_applied(tag):
        print("\t\t|-> "+tag.name)
unknown_tags=set(tags).difference(sTag._member_names_)
print("\t-> All Undefined Tags")
for tag in unknown_tags:
    print("\t\t|-> "+tag)
########################## All Tags are Set ###########################


############################### Project Information ###################
py_project_toml = os.path.join(os.getcwd(),"../../../pyproject.toml")
py_project_data = toml.load(py_project_toml)

#Load general data for website from pyproject.toml file
project = py_project_data["config"]["sphinx"]["name"] + (" Develop Branch" if tag_is_applied(sTag.dev) else "")
copyright = py_project_data["config"]["sphinx"]["copyright_message"]
author = py_project_data["config"]["sphinx"]["author"]
release = py_project_data["tool"]["poetry"]["version"]
########################### End of Project Information ################


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ['sphinx.ext.autodoc',
              'sphinx.ext.todo',
              'sphinx.ext.napoleon',
              'sphinx.ext.viewcode',
              'sphinx.ext.autosectionlabel',
              'sphinx.ext.intersphinx',
              'sphinx.ext.graphviz',
              'sphinx.ext.inheritance_diagram',
              'sphinx_design', # This allows for greater user interfaces. https://sphinx-design.readthedocs.io/en/latest/get_started.html#usage
              ]

templates_path = ['_templates']
exclude_patterns = []

# -- Adding Modules To sys.path so they can be addressed ---------------------
# may be possible to use __init__.py to get around this and import the project directly, like i think Scipy is doing.
directory_of_source_code = os.path.join(os.getcwd(),"../../../src")
sys.path.append(directory_of_source_code)

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_theme = py_project_data["config"]["sphinx"]["dev_theme"] if tag_is_applied(sTag.dev) \
    else py_project_data["config"]["sphinx"]["theme"]
#html_theme = 'sphinx_book_theme'
#html_theme = 'sphinx_wagtail_theme'
#html_theme = 'sphinx_nefertiti'
#html_theme = 'pydata_sphinx_theme'


#html_static_path = ['_static']
# -- Change What Page Automatically Renders -----------------------------------
nitpicky = True # Warnings will be emitted for all references with targets that can't be found
show_authors = True


if tag_is_applied(sTag.tests_failed):
    logo_img = py_project_data["config"]["sphinx"]["test_fail_logo"]
elif tag_is_applied(sTag.dev):
    logo_img = py_project_data["config"]["sphinx"]["dev_logo"]
else:
    logo_img = py_project_data["config"]["sphinx"]["logo"]

html_logo =  logo_img #or a URL that points an image file for the logo. It is placed at the top of the sidebar; its width should therefore not exceed 200 pixels
html_favicon = logo_img #it should be a 16-by-16 pixel icon in the PNG, SVG, GIF, or ICO file formats
latex_logo = logo_img
del logo_img

#keep_warnings = True
#any_tag_is_applied(
#    [sTag.dev]
#)

# -- Options for todo extension ----------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/todo.html

todo_include_todos=any_tag_is_applied( # True if want to see todos
    [sTag.dev]
)             
todo_emit_warnings=False            # True if want warnings created for each todo item that exists

# -- viewcode extension configuration -----------------------------------------
viewcode_line_numbers = True
viewcode_enable_epub  = False

# -- Graphviz Configuration --------------------------------------------------
graphviz_dot = "dot" # specify "neato" layout when there is an issue, see https://graphviz.org/docs/layouts/
graphviz_output_format = "png" # Alternatively, you could use "png" if don't need zoom, "svg" for detail, but can't download.

# -- Autosection Label -------------------------------------------------------
autosectionlabel_prefix_document = True # Can link to 'Section Title' titles using :ref:'document:Section Title'

# -- Intersphinx Configuration -----------------------------------------------

intersphinx_mapping = {'python': ('https://docs.python.org/3', None),
                       'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
                      }


# -- Options for napoleon extension ------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html

napoleon_google_docstring = False           # False to turn off support for google Docstrings
napoleon_numpy_docstring = True             # True to turn on support for numpy Docstrings
napoleon_include_init_with_doc = True       # True to include __init__ as it's own function if it has an a related docstring. If false, just append to class documentation.
napoleon_include_private_with_doc = True    # True to include private members with docstrings, false resorts to Sphinx's defaults
napoleon_include_special_with_doc = True    # True to include special members like __membername__ with docstrings in documentation. If false, Sphinx defaults, defalts to true.

############################# Substitutions #####################################

develop_grid_card = "\n".join([ "grid-item-card: See Development Documentation",
                                '       :link: code/old_test_verify',
                                '       :link-type: doc',
                                '       :link-alt: Link to code/old_test_verify',
                                '       Follow this link to go to the documentation used to develop this software, including information about how to contribute.'])

testing_grid_card = "\n".join([
    'grig-item-card: Testing Results',
    '   :link: code/old_test_verify',
    '   :link-type: doc',
    '   :link-alt: Link to code/old_test_verify',
    '   This brings you to the test results of the previous commit completed.'

])


rst_prolog = f"""
.. |doc_version| replace:: {"Release" if tag_is_applied(sTag.release) else "Develop"}
"""
# .. |dev_test_card| {testing_grid_card if tag_is_applied(sTag.dev) else develop_grid_card}

rst_epilog = f"""

"""