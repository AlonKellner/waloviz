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

extensions += ["nbsite.gallery", "sphinx_favicon", "sphinxext.opengraph"]
nbsite_gallery_conf = {
    "backends": ["bokeh"],
    "default_extensions": ["*.ipynb", "*.py"],
    "enable_download": True,
    "examples_dir": os.path.join("..", "examples"),
    "galleries": {"gallery": {"title": "Gallery"}},
}

favicons = [
    {"href": "/favicon.ico", "sizes": "32x32"},
    {"rel": "apple-touch-icon", "href": "/apple-touch-icon.png", "sizes": "180x180"},
    {"href": "/favicon-32x32.png", "sizes": "32x32", "type": "image/png"},
    {"href": "/favicon-16x16.png", "sizes": "16x16", "type": "image/png"},
    {"rel": "manifest", "href": "/site.webmanifest"},
    {"rel": "mask-icon", "href": "/safari-pinned-tab.png", "color": "#5bbad5"},
]

ogp_site_url = "http://waloviz.com/"
ogp_image = "https://github.com/AlonKellner/waloviz/raw/main/doc/site_root/android-chrome-512x512.png"
ogp_enable_meta_description = True

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
