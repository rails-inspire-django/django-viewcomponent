# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import datetime
import sys
import tomllib
from pathlib import Path

here = Path(__file__).parent.resolve()
sys.path.insert(0, str(here / ".." / ".." / "src"))


# -- Project information -----------------------------------------------------
project = "django-viewcomponent"
copyright = f"{datetime.datetime.now().year}, Michael Yin"  # noqa
author = "Michael Yin"


# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The short X.Y version.


def _get_version() -> str:
    with (here / ".." / ".." / "pyproject.toml").open("rb") as fp:
        data = tomllib.load(fp)
    version: str = data["tool"]["poetry"]["version"]
    return version


version = _get_version()
# The full version, including alpha/beta/rc tags.
release = version

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc", "myst_parser"]

source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "markdown",
    ".md": "markdown",
}

templates_path = ["_templates"]
exclude_patterns = []  # type: ignore


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# html_theme = 'alabaster'
# html_static_path = ['_static']
html_theme = "furo"
pygments_style = "sphinx"

announcement_html = """
<div class="">
  Have questions, feedback, or just want to chat? Reach out to me on
  <a href="https://twitter.com/michaelyinplus" target="_blank">
    <strong>Twitter / X</strong>
  </a>
</div>
"""

html_theme_options = {
    "announcement": announcement_html,
}
