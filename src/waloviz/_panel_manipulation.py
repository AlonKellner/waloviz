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
    height: Union[int, str],
    audio_height: int,
    button_height: int,
    pbar_height: int,
    single_min_height: int,
    both_min_height: int,
    download_button: bool,
    native_player: bool,
    aspect_ratio: float,
    sizing_mode: str,
):
    aspect_ratio_kwargs = {}
    if (sizing_mode != "fixed") and (aspect_ratio is not None):
        aspect_ratio_kwargs["aspect_ratio"] = aspect_ratio

    width_kwargs = {}
    if width != "responsive":
        width_kwargs["width"] = width
    height_kwargs = {}
    if height != "responsive":
        plot_height = height - audio_height - button_height
        height_kwargs["height"] = plot_height

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
            sizing_mode="stretch_width",
            height=audio_height,
            visible=native_player,
        )

    plot_0, _, __ = waloviz_bokeh.children[0]
    pause_0 = plot_0.renderers[-1]
    vspan_0 = plot_0.renderers[-2]
    audio.jslink(pause_0, paused="visible", bidirectional=True)
    audio.jslink(vspan_0, time="right", bidirectional=True)
    waloviz_panel_plot = pn.Column(
        waloviz_bokeh, min_height=both_min_height + pbar_height
    )
    rows = [waloviz_panel_plot, audio]

    if download_button:
        buffer = BytesIO()
        buffer: BytesIO = save_waloviz_panel(
            pn.Column(
                *rows,
                **aspect_ratio_kwargs,
                **width_kwargs,
                **height_kwargs,
            ),
            buffer,
            title,
        )
        buffer.seek(0)
        file_download = pn.widgets.FileDownload(
            buffer, filename=f"{title}.html", embed=True
        )
        rows.append(file_download)

    waloviz_panel = pn.Column(
        *rows,
        **aspect_ratio_kwargs,
        **width_kwargs,
        **height_kwargs,
    )

    waloviz_panel.title = title
    return waloviz_panel


def save_waloviz_panel(
    waloviz_panel: pn.viewable.Viewable,
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

    if (
        hasattr(waloviz_panel, "__len__")
        and (len(waloviz_panel) > 2)
        and isinstance(waloviz_panel[2], pn.widgets.misc.FileDownload)
    ):
        waloviz_panel = pn.Column(waloviz_panel[0], waloviz_panel[1])

    pn.panel(waloviz_panel).save(
        file,
        resources=resources,
        embed=embed,
        title=title,
    )

    return file
