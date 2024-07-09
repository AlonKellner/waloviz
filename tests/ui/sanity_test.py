import numpy as np

from playwright.sync_api import expect


def test_sanity_bokeh_logo(serve, waloviz):
    wv = waloviz
    wv.extension()
    player = wv.Audio((np.random.randn(8000), 8000))
    page = serve(player)
    bokeh_logo = page.locator(".bk-logo")
    expect(bokeh_logo).to_have_count(1)
