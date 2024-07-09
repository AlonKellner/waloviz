from panel.tests.util import serve_and_wait
from panel.tests.conftest import port  # noqa: F401

import pytest


@pytest.fixture
def serve(page, port):  # noqa: F811
    def serve_and_return_page(obj):
        serve_and_wait(obj, port=port)
        page.goto(f"http://localhost:{port}")
        return page

    return serve_and_return_page


@pytest.fixture
def waloviz():
    import sys

    sys.path.append("/workspaces/waloviz/src")
    sys.path.append("/home/runner/work/waloviz/waloviz/src")
    import waloviz as wv

    return wv
