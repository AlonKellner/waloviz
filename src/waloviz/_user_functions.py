import os
from io import IOBase
from typing import Any, Dict, List, Optional, Tuple, Union

import holoviews as hv
import numpy as np
import panel as pn
import torch
import torchaudio
import torchaudio.transforms as T
from bokeh.resources import INLINE, Resources

from ._bokeh_manipulation import finalize_waloviz_bokeh_gui, themes
from ._holoviews_manipulations import ThemeHook, get_waloviz_hv
from ._panel_manipulation import wrap_with_waloviz_panel, save_waloviz_panel
from ._tensor_utils import OverCurve, preprocess_over_curve, to_tensor


_mode = "default"


def extension(mode="default"):
    """=================
``waloviz.extension``
=================

Initializes the notebook extensions for the current IDE.

Examples
--------

.. code-block:: python

        import wavloviz as wv
        wv.extension()
        wv.Audio('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3')

|"""
    global _mode
    _mode = mode
    hv.extension("bokeh")
    pn.extension(comms="default")


def Audio(
    source: Union[
        str, os.PathLike, IOBase, Tuple[Union[np.ndarray, torch.Tensor, Any], int]
    ],
    over_curve: Optional[OverCurve] = None,
    *args,
    over_curve_names: Optional[Union[str, List[str]]] = None,
    sr: Optional[int] = None,
    frame_ms: Optional[int] = None,
    n_fft: Optional[int] = None,
    hop_length: Optional[int] = None,
    title: Optional[str] = "waloviz",
    embed_title: bool = False,
    height: int = 500,
    width: Union[int, str] = "responsive",
    sync_legends: bool = False,
    colorbar: bool = False,
    cmap: str = "Inferno",
    over_curve_colors: Optional[Union[str, List[str]]] = None,
    theme: Union[str, Dict[str, Any]] = "dark_minimal",
    max_size: int = 10000,
    download_button: bool = True,
    freq_label: str = "Hz",
    native_player: bool = False,
    minimal: bool = False,
    extended: bool = False,
):
    """=============
``waloviz.Audio``
=============

Creates an interactive audio player with a spectrogram

Examples
--------

.. code-block:: python

        import wavloviz as wv

.. code-block:: python
        
        wv.Audio('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3')

.. code-block:: python

        wav, sr = np.random.randn(8000), 8000
        wv.Audio((wav, sr))

.. code-block:: python
        
        wav, sr = torchaudio.load('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3')
        wv.Audio(wav, sr=sr, over_curve=dict(squared=wav**2, cubed=wav**3))

Parameters
----------

source : str | os.PathLike | IOBase | (tensorlike, int) | tensorlike
    Either an audio file, or an audio tensor\\ndarray with a sample rate
over_curve : tensorlike | List[tensorlike] | Dict[str, tensorlike]
    A single or multiple curves to be displayed over the spectrogram
over_curve_names : str | List[str]
    A list of display names corresponding to the list given in ``over_curve``
sr : int
    The sample rate, when the source does not contain a sample rate,
    the given ``sr`` value is assumed to be the source sample rate, when
    this value is different than the source sample rate, the source
    audio is resampled to the specified ``sr`` value.
frame_ms : int
    Sets the spectrogram frame length to the given amount of milliseconds,
    default is 100.
n_fft : int
    Sets the ``n_fft`` of the spectrogram, overrides the ``frame_ms`` value,
    default is ``(sr/1000 * frame_ms)``.
hop_length : int
    Sets the `hop_length` of the spectrogram, default is ``n_fft/8``
title : str
    A title to be used when saving the plot. If ``embed_title`` is True,
    the ``title`` value will be displayed as part of the plot itself.
    Default is "waloviz".
embed_title : bool
    When True, the ``title`` value will be displayed as part of the plot
    itself, default is False.
height : int
    The total height of the plot
width : int
    The total width of the plot, default is "responsive", which means
    the plot will stretch in width to fit the screen.
sync_legends : bool
    Whether the legends of both audio channels over curves should be
    synchronized, default is False
colorbar : bool
    Whether to display a colorbar for the spectrograms, default is False
cmap : str
    The colormap used to display the spectrogram, default is "Inferno"
over_curve_colors : str | List[str] | Dict[str, str]
    Sets the colors to display for each given ``over_curve``, should match
    the size and structure of the given ``over_curve`` value.
theme : str | Dict[str, Any]
    Sets the visual look and feel of the plot, the value provided must
    be a ``bokeh`` theme, default is "dark_minimal".
max_size : int
    When the spectrogram or one of the over curves contain many values,
    the plot's performance suffers. For that reason ``max_size`` limits the
    amount of displayed values, when the spectrogram or an over curve has
    more values than the ``max_size``, it is reduced in size by skipping
    intermediate values, until the size is less than the ``max_size``.
    Default is 10000.
download_button : bool
    Whether to show the html download button. Defaults to True.
freq_label : str
    The label of the frequency axis (vertical), hides the label when set
    to None which saves space.
native_player : bool
    Whether the underlying native audio player should be visible. Default
    is False
minimal: bool
    Does nothing when False, when True it overrides some settings to make
    the player more compact and simple.
extended: bool
    Does nothing when False, when True it overrides some settings to make
    the player more descriptive and functional.

Returns
-------

panel : pn.pane.PaneBase
    An interactive waloviz panel, can be saved to html with ``waloviz.save(panel)``

|"""

    pbar_height: int = 40
    stay_color: str = "#ffffff88"
    follow_color: str = "#ff0000dd"

    if minimal and extended:
        raise ValueError(
            "`Audio` cannot be both `minimal` and `extended`, choose one to keep"
        )

    if minimal:
        title = "wv"
        embed_title = False
        download_button = False
        freq_label = None
        native_player = False

    if extended:
        embed_title = True
        colorbar = True
        download_button = True
        native_player = True

    if download_button:
        button_height: int = 30
    else:
        button_height: int = 0

    if native_player:
        audio_height: int = 30
    else:
        audio_height: int = 0

    if isinstance(over_curve, int):
        raise ValueError(
            """`over_curve` cannot be an integer! make sure you did not call `waloviz.Audio` like this:
    waloviz.Audio(wav, sr)
    
call `waloviz.Audio` in one of the following ways:
    waloviz.Audio((wav, sr))
    waloviz.Audio(wav, sr=sr)
    waloviz.Audio(file_name_or_obj)"""
        )

    if len(args) > 0:
        raise ValueError(
            """`waloviz.Audio` should be called with at most 2 positional arguments like one of the following ways:
    waloviz.Audio(source)
    waloviz.Audio(source, over_curve)"""
        )

    if isinstance(theme, str):
        if theme.lower() in themes:
            theme = themes[theme.lower()]
        else:
            ValueError(
                f"`theme` was a string, but did not match any of the available options: {sorted(themes.keys())}"
            )
    theme_hook = ThemeHook(theme).hook

    if torch.is_tensor(source) or isinstance(source, np.ndarray):
        source = source, sr
    elif not isinstance(source, tuple):
        source = torchaudio.load(source)

    wav, source_sr = source
    if sr is None:
        target_sr = source_sr
    else:
        target_sr = sr

    if target_sr is None or source_sr is None:
        raise ValueError(
            """A sample rate must be specified but none was provided!
Specify the sample rate in one of the following ways:
    waloviz.Audio(wav, sr=sample_rate)
    waloviz.Audio((wav, sample_rate))"""
        )

    wav = to_tensor(wav).squeeze()
    if len(wav.shape) == 1:
        wav = wav[None, ...]
    elif len(wav.shape) > 2:
        raise ValueError(
            f"The given `wav` value has more than 2 dimensions: {len(wav.shape)}!=2"
        )

    global _mode
    if _mode == "colab":
        extension(_mode)

    if source_sr != target_sr:
        wav = T.Resample(source_sr, target_sr)(wav)
    sr = target_sr

    if (n_fft is None) and (frame_ms is None):
        frame_ms = 100

    if n_fft is None:
        n_fft = (sr * frame_ms) // 1000

    if hop_length is None:
        hop_length = n_fft // 8

    channels = len(wav)
    total_seconds = wav.shape[-1] // sr

    over_curve, over_curve_names, over_curve_colors = preprocess_over_curve(
        channels, over_curve, over_curve_names, over_curve_colors
    )

    waloviz_hv = get_waloviz_hv(
        wav=wav,
        sr=sr,
        total_seconds=total_seconds,
        over_curve=over_curve,
        over_curve_names=over_curve_names,
        n_fft=n_fft,
        hop_length=hop_length,
        sync_legends=sync_legends,
        height=height,
        width=width,
        audio_height=audio_height,
        button_height=button_height,
        pbar_height=pbar_height,
        theme_hook=theme_hook,
        max_size=max_size,
        cmap=cmap,
        over_curve_colors=over_curve_colors,
        stay_color=stay_color,
        follow_color=follow_color,
        title=title,
        embed_title=embed_title,
        colorbar=colorbar,
        freq_label=freq_label,
    )
    waloviz_bokeh = hv.render(waloviz_hv)

    waloviz_bokeh = finalize_waloviz_bokeh_gui(
        waloviz_bokeh,
        theme=theme,
        total_seconds=total_seconds,
        stay_color=stay_color,
        follow_color=follow_color,
    )
    waloviz_panel = wrap_with_waloviz_panel(
        waloviz_bokeh,
        wav=wav,
        sr=sr,
        title=title,
        width=width,
        audio_height=audio_height,
        download_button=download_button,
        native_player=native_player,
    )

    return waloviz_panel


def save(
    source: pn.pane.PaneBase,
    *args,
    out_file: Union[str, os.PathLike, IOBase] = None,
    title: Optional[str] = None,
    resources: Resources = INLINE,
    embed: bool = True,
    **kwargs,
):
    """============
``waloviz.save``
============

Saves a waloviz player to an html file

Example
-------

.. code-block:: python

        import wavloviz as wv
        wv.save('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3')

Parameters
----------

source : pn.pane.PaneBase | str | os.PathLike | IOBase | (tensorlike, int) | tensorlike
    The waloviz player created by ``waloviz.Audio``, or a source for
    ``waloviz.Audio`` to create a player with.
out_file : str | os.PathLike | IOBase
    The output file path for the generated html, default is "{title}.html"
title : str
    The title to be used in the generated file name and the html title,
    if ``waloviz.Audio(title="...")`` was specified, then that value is
    used, otherwise, the default is "waloviz".
resources : bokeh.resources.Resources
    The resources for the ``panel`` save method, default is INLINE
embed : bool
    The embed value for the ``panel`` save method, default is True

Returns
-------

out_file : str | os.PathLike | IOBase
    The file that the waloviz html content was written into

|"""

    if isinstance(source, pn.pane.PaneBase):
        if len(kwargs) > 0:
            raise TypeError(
                f"save() got an unexpected keyword argument '{kwargs.keys()[0]}'"
            )
        if len(args) == 1:
            if isinstance(args[0], (str, os.PathLike, IOBase)):
                out_file = args[0]
                args = []
        elif len(args) > 1:
            raise ValueError(
                """`waloviz.save` should be called with at most 2 positional arguments like one of the following ways:
    waloviz.save(source)
    waloviz.save(source, out_file)
    waloviz.save(source, over_curve)"""
            )
    else:
        source = Audio(source, *args, **kwargs)
    return save_waloviz_panel(source, out_file, title, resources, embed)
