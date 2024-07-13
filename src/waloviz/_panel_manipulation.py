import os
from io import BytesIO
from typing import IO, Any, Optional, Union
from unittest.mock import patch

import bokeh
import bokeh.model
import numpy as np
import panel as pn
import torch
from bokeh.resources import INLINE, Resources
from panel.pane.media import (
    _VALID_NUMPY_DTYPES_FOR_AUDIO,
    _VALID_TORCH_DTYPES_FOR_AUDIO,
    TensorLike,
)

IOLike = Union[str, os.PathLike, IO]


def _is_2dim_int_or_float_ndarray(obj: Any) -> bool:
    """
    | A 2d variant of ``_is_1dim_int_or_float_ndarray`` , since scipy actually supports 2d ndarrays.

    | TODO: Create an issue at the `Panel Repository <https://github.com/holoviz/panel>`_ about this.

    Parameters
    ----------
    ``obj`` : Any
        The audio ndarray

    Returns
    -------
    ``is_valid`` : bool


    |
    """
    return (
        isinstance(obj, np.ndarray)
        and 0 < obj.ndim <= 2
        and obj.dtype in _VALID_NUMPY_DTYPES_FOR_AUDIO
    )


def _is_2dim_int_or_float_tensor(obj: Any) -> bool:
    """
    | A 2d variant of ``_is_1dim_int_or_float_tensor`` , since scipy actually supports 2d tensors.

    | TODO: Create an issue at the `Panel Repository <https://github.com/holoviz/panel>`_ about this.

    Parameters
    ----------
    ``obj`` : Any
        The audio tensor

    Returns
    -------
    ``is_valid`` : bool


    |
    """
    return (
        isinstance(obj, TensorLike)
        and 0 < obj.dim() <= 2  # pyright: ignore[reportAttributeAccessIssue]
        and str(obj.dtype) in _VALID_TORCH_DTYPES_FOR_AUDIO  # pyright: ignore[reportAttributeAccessIssue]
    )


def wrap_player_with_panel(
    player_bokeh: bokeh.model.Model,
    wav: torch.Tensor,
    sr: int,
    title: Optional[str],
    width: Union[int, str],
    height: Union[int, str],
    audio_height: int,
    button_height: int,
    pbar_height: int,
    both_min_height: int,
    download_button: bool,
    native_player: bool,
    aspect_ratio: Optional[float],
    sizing_mode: Optional[str],
) -> pn.viewable.Viewable:
    """
    | Wraps the bokeh player with panel, adds the audio and optionally a download button.

    Parameters
    ----------
    ``player_bokeh`` : bokeh.model.Model
        The generated bokeh player with the custom jslink interactivity, without the audio
    ``wav`` : torch.Tensor
        The audio tensor
    ``sr`` : int
        The sample rate
    ``title`` : str
        A title to be used when saving the plot
    ``height`` : int | str
        The total height of the plot
    ``width`` : int | str
        The total width of the plot
    ``audio_height`` : bool
        The expected height of the audio widget
    ``button_height`` : bool
        The expected height of the download button
    ``download_button`` : bool
        Whether to show the html download button
    ``native_player`` : bool
        Whether the underlying native audio player should be visible
    ``aspect_ratio`` : float
        The ratio between the width and height, relevant only when either
        width, height or both are "responsive"
    ``sizing_mode`` : str
        The panel ``sizing_mode`` , can be one of seven values:
        "stretch_width", "stretch_height", "stretch_both",
        "scale_width", "scale_height", "scale_both", or "fixed".

    Returns
    -------
    ``player_panel`` : pn.viewable.Viewable
        A panel pane with a fully featured interactive player

    |
    """
    aspect_ratio_kwargs = {}
    if (sizing_mode != "fixed") and (aspect_ratio is not None):
        aspect_ratio_kwargs["aspect_ratio"] = aspect_ratio

    width_kwargs = {}
    if width != "responsive":
        width_kwargs["width"] = width
    height_kwargs = {}
    if height != "responsive" and isinstance(height, int):
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
        buffer = save_player_panel(
            pn.Column(
                *rows,
                **aspect_ratio_kwargs,
                **width_kwargs,
                **height_kwargs,
            ),
            buffer,
            title,
        )
        if not isinstance(buffer, BytesIO):
            raise NotImplementedError()
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

    player_panel.title = title  # pyright: ignore[reportAttributeAccessIssue]
    return player_panel


def save_player_panel(
    player_panel: pn.viewable.Viewable,
    out_file: Optional[IOLike] = None,
    title: Optional[str] = None,
    resources: Resources = INLINE,
    embed: bool = True,
) -> IOLike:
    """
    | Saves a panel player to an HTML file.

    | Does not save the download button.

    Parameters
    ----------
    ``source`` : pn.viewable.Viewable
        The player created by ``wv.Audio``
    ``out_file`` : str | os.PathLike | IO
        The output file path for the generated html, default is "{title}.html"
    ``title`` : str
        The title to be used in the generated file name and the html title,
        if ``wv.Audio(title="...")`` was specified, then that value is
        used, otherwise, the default is "waloviz".
    ``resources`` : bokeh.resources.Resources
        The resources for the ``panel`` save method, default is INLINE
    ``embed`` : bool
        The embed value for the ``panel`` save method, default is True

    Returns
    -------
    ``out_file`` : str | os.PathLike | IO
        The file that the HTML player content was written into

    |
    """
    if title is None:
        try:
            title = player_panel.title  # pyright: ignore[reportAttributeAccessIssue]
        except Exception:
            title = "waloviz"

    if out_file is None:
        out_file = f"{title}.html"

    if (
        hasattr(player_panel, "__len__")
        and (len(player_panel) > 2)  # pyright: ignore[reportArgumentType]
        and isinstance(player_panel[2], pn.widgets.misc.FileDownload)  # pyright: ignore[reportIndexIssue]
    ):
        player_panel = pn.Column(player_panel[0], player_panel[1])  # pyright: ignore[reportIndexIssue]

    pn.panel(player_panel).save(
        out_file,
        resources=resources,
        embed=embed,
        title=title,
    )

    return out_file
