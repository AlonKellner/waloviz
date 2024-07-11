import os
from io import BytesIO, IOBase
from typing import Any, Optional, Union
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


def wrap_player_with_panel(
    player_bokeh,
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

    plot_0, _, __ = player_bokeh.children[0]
    pause_0 = plot_0.renderers[-1]
    vspan_0 = plot_0.renderers[-2]
    audio.jslink(pause_0, paused="visible", bidirectional=True)
    audio.jslink(vspan_0, time="right", bidirectional=True)
    player_panel_plot = pn.Column(
        player_bokeh, min_height=both_min_height + pbar_height
    )
    rows = [player_panel_plot, audio]

    if download_button:
        buffer = BytesIO()
        buffer: BytesIO = save_player_panel(
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

    player_panel = pn.Column(
        *rows,
        **aspect_ratio_kwargs,
        **width_kwargs,
        **height_kwargs,
    )

    player_panel.title = title
    return player_panel


def save_player_panel(
    player_panel: pn.viewable.Viewable,
    file: Union[str, os.PathLike, IOBase] = None,
    title: Optional[str] = None,
    resources: Resources = INLINE,
    embed: bool = True,
):
    if title is None:
        try:
            title = player_panel.title
        except Exception:
            title = "waloviz"

    if file is None:
        file = f"{title}.html"

    if (
        hasattr(player_panel, "__len__")
        and (len(player_panel) > 2)
        and isinstance(player_panel[2], pn.widgets.misc.FileDownload)
    ):
        player_panel = pn.Column(player_panel[0], player_panel[1])

    pn.panel(player_panel).save(
        file,
        resources=resources,
        embed=embed,
        title=title,
    )

    return file
