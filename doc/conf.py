"""The Sphinx configuration file, for the Documentation Website, see https://waloviz.com."""
# -*- coding: utf-8 -*-
# (hacky way of sharing config, etc...)

###################################################
# edit things below as appropriate for your project
import sys

from nbsite.shared_conf import *  # noqa: F403 # type: ignore
from nbsite.shared_conf import (
    extensions,
    html_context,
    html_css_files,
    html_static_path,
)

sys.path.append("/workspaces/waloviz/src")
sys.path.append("/home/runner/work/waloviz/waloviz/src")

import waloviz as wv

project = "WaloViz"
authors = "Alon Kellner"
copyright = "2024 " + authors
description = "An interactive audio player with a spectrogram built-in, as a Jupyter widget or as HTML."
site = "waloviz.com"
version = release = wv.version

html_static_path += ["_static"]  # noqa: F405
html_theme = "pydata_sphinx_theme"
html_css_files += ["css/custom.css"]  # noqa: F405
html_logo = "_static/logo_horizontal.png"
html_favicon = "_static/favicon.ico"
html_title = f"{project} v{version}"
html_theme_options = {
    "github_url": "https://github.com/AlonKellner/waloviz",
    "icon_links": [
        {
            "name": "Twitter",
            "url": "https://x.com/waloviz",
            "icon": "fa-brands fa-square-x-twitter",
        },
    ],
    "footer_start": [
        "copyright",
        "last-updated",
    ],
}
html_last_updated_fmt = "%Y-%m-%d"

extensions += [  # noqa: F405
    "sphinx_favicon",
    "sphinxext.opengraph",
    "sphinx_tabs.tabs",
    "sphinx_copybutton",
    "sphinxemoji.sphinxemoji",
    "sphinx_toolbox.collapse",
]

myst_enable_extensions = ["colon_fence", "deflist"]

sphinx_tabs_disable_tab_closing = True

favicons = [
    {"href": "/en/latest/favicon.ico", "sizes": "32x32"},
    {"href": "/en/latest/favicon.svg", "sizes": "any", "type": "image/svg+xml"},
    {
        "rel": "apple-touch-icon",
        "href": "/en/latest/apple-touch-icon.png",
        "sizes": "180x180",
    },
    {"href": "/en/latest/favicon-32x32.png", "sizes": "32x32", "type": "image/png"},
    {"href": "/en/latest/favicon-16x16.png", "sizes": "16x16", "type": "image/png"},
    {"rel": "manifest", "href": "/en/latest/site.webmanifest"},
    {
        "rel": "mask-icon",
        "href": "/en/latest/safari-pinned-tab.svg",
        "color": "#5bbad5",
    },
]

ogp_site_url = "http://waloviz.com/"
ogp_image = "https://waloviz.com/en/latest/_static/logo_vertical.png"
ogp_enable_meta_description = True

_NAV = (
    ("Getting Started", "getting-started/index"),
    ("User Guide", "user-guide/index"),
    ("API", "reference-manual/index"),
    ("Releases", "releases"),
    ("FAQ", "FAQ"),
    ("About", "about"),
)

html_context.update(  # noqa: F405
    {
        "PROJECT": project,
        "DESCRIPTION": description,
        "AUTHOR": authors,
        # will work without this - for canonical (so can ignore when building locally or test deploying)
        "WEBSITE_SERVER": site,
        "VERSION": version,
        "NAV": _NAV,
        # by default, footer links are same as those in header
        "LINKS": _NAV,
        "SOCIAL": (
            ("Twitter", "https://x.com/waloviz"),
            ("Github", "https://github.com/AlonKellner/waloviz"),
        ),
        "github_user": "AlonKellner",
        "github_repo": "waloviz",
    }
)
