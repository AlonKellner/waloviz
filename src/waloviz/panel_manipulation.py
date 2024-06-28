import os
from io import BytesIO, IOBase
from typing import Any, Union, Optional
from unittest.mock import patch

import numpy as np
import panel as pn
import torch
from bokeh.resources import INLINE, Resources
from panel.pane.media import (
    _VALID_NUMPY_DTYPES_FOR_AUDIO,
    _VALID_TORCH_DTYPES_FOR_AUDIO,
    TensorLike,
)


def _is_2dim_int_or_float_ndarray(obj: Any) -> bool:
    return (
        isinstance(obj, np.ndarray)
        and 0 < obj.ndim <= 2
        and obj.dtype in _VALID_NUMPY_DTYPES_FOR_AUDIO
    )


def _is_2dim_int_or_float_tensor(obj: Any) -> bool:
    return (
        isinstance(obj, TensorLike)
        and 0 < obj.dim() <= 2
        and str(obj.dtype) in _VALID_TORCH_DTYPES_FOR_AUDIO
    )


def wrap_with_waloviz_panel(
    waloviz_bokeh,
    wav: torch.Tensor,
    sr: int,
    title: str,
    width: Union[int, str],
    audio_height: int,
    download_button: bool,
):
    sizing_mode = "stretch_width" if width == "responsive" else "fixed"
    width_kwargs = {}
    if width != "responsive":
        width_kwargs["width"] = width

    with patch(
        "panel.pane.media._is_1dim_int_or_float_ndarray",
        new=_is_2dim_int_or_float_ndarray,
    ), patch(
        "panel.pane.media._is_1dim_int_or_float_tensor",
        new=_is_2dim_int_or_float_tensor,
    ):
        audio = pn.pane.Audio(
            wav.T,
            sample_rate=sr,
            sizing_mode=sizing_mode,
            height=audio_height,
            **width_kwargs,
        )

    plot_0, _, __ = waloviz_bokeh.children[0]
    pause_0 = plot_0.renderers[-1]
    vspan_0 = plot_0.renderers[-2]
    audio.jslink(pause_0, paused="visible", bidirectional=True)
    audio.jslink(vspan_0, time="right", bidirectional=True)
    waloviz_panel = pn.Column(waloviz_bokeh, audio)

    if download_button:
        buffer = BytesIO()
        buffer: BytesIO = save_waloviz_panel(waloviz_panel, buffer, title)
        buffer.seek(0)
        file_download = pn.widgets.FileDownload(
            buffer, filename=f"{title}.html", embed=True
        )

        waloviz_panel = pn.Column(waloviz_panel, file_download)

    waloviz_panel.title = title
    return waloviz_panel


def save_waloviz_panel(
    waloviz_panel: pn.pane.PaneBase,
    file: Union[str, os.PathLike, IOBase] = None,
    title: Optional[str] = None,
    resources: Resources = INLINE,
    embed: bool = True,
):
    if title is None:
        try:
            title = waloviz_panel.title
        except Exception:
            title = "waloviz"

    if file is None:
        file = f"{title}.html"

    if isinstance(waloviz_panel[1], pn.widgets.misc.FileDownload):
        waloviz_panel = waloviz_panel[0]

    pn.panel(waloviz_panel).save(
        file,
        resources=resources,
        embed=embed,
        title=title,
    )

    return file
