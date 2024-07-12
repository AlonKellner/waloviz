"""Test for sanity that something works, not features."""

from typing import Any, Callable

import numpy as np
import panel as pn
from playwright.sync_api import expect
from pytest_playwright.pytest_playwright import Page


def test_sanity_bokeh_logo(
    serve: Callable[[pn.viewable.Viewable], Page], waloviz: Any
) -> None:
    """A sanity test which uses playwright to find whether the bokeh logo is visible within the player."""
    wv = waloviz
    wv.extension()
    player = wv.Audio((np.random.randn(8000), 8000))
    page = serve(player)
    bokeh_logo = page.locator(".bk-logo")
    expect(bokeh_logo).to_have_count(1)
