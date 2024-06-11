# -*- coding: utf-8 -*-
# flake8: noqa (hacky way of sharing config, etc...)

from nbsite.shared_conf import *

###################################################
# edit things below as appropriate for your project

project = "waloviz"
authors = "Alon Kellner"
copyright = "2024 " + authors
description = "An interactive audio player with a spectrogram built-in, as a Jupyter widget or as HTML."
site = "waloviz.com"
version = release = "0.0.0a0"

html_static_path += ["_static"]
html_theme = "pydata_sphinx_theme"
html_logo = "_static/logo_horizontal.png"
html_favicon = "_static/favicon.ico"
html_theme_options = {}  # fill out theme options as desired

extensions += ["nbsite.gallery"]
nbsite_gallery_conf = {
    "backends": ["bokeh"],
    "default_extensions": ["*.ipynb", "*.py"],
    "enable_download": True,
    "examples_dir": os.path.join("..", "examples"),
    "galleries": {"gallery": {"title": "Gallery"}},
    "within_subsection_order": lambda key: key,
}

_NAV = (
    ("Getting Started", "getting_started/index"),
    ("User Guide", "user_guide/index"),
    ("Gallery", "gallery/index"),
    ("API", "Reference_Manual/index"),
    ("FAQ", "FAQ"),
    ("About", "about"),
)

html_context.update(
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
    }
)
