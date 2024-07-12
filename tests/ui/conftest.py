"""Pytest conftest with Playwright fixtures."""

from typing import Any, Callable

import panel as pn
import pytest
from panel.tests.conftest import port, server_cleanup  # noqa: F401  # pyright: ignore
from panel.tests.util import serve_and_wait
from pytest_playwright.pytest_playwright import Page


@pytest.fixture
def serve(page: Page, port: int) -> Callable[[pn.viewable.Viewable], Page]:  # noqa: F811
    """Get a callback to serve a playwright page with a panel object locally."""

    def serve_and_return_page(obj: pn.viewable.Viewable) -> Page:
        serve_and_wait(obj, port=port)
        page.goto(f"http://localhost:{port}")
        return page

    return serve_and_return_page


@pytest.fixture
def waloviz() -> Any:
    """Import waloviz by injecting the ``src`` folder into the sys path."""
    import sys

    sys.path.append("/workspaces/waloviz/src")
    sys.path.append("/home/runner/work/waloviz/waloviz/src")
    import waloviz as wv

    return wv
