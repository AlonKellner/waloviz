# pyright: reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportOperatorIssue=false

from typing import Any, Dict, List, Optional, Tuple, Union

import holoviews as hv
import numpy as np
import torch
import torchaudio.transforms as T

from ._tensor_utils import skip_to_size


class ThemeHook:
    def __init__(self, theme_obj: Dict[str, Any]):
        """=============
        ``ThemeHook``
        =============

        | A class with a HoloViews hook for applying a Bokeh theme.
        | This is due to a problem when using the built-in theme support of
        | HoloViews in integration with Panel, for some reason themes are only
        | partially applied in those situations.
        | TODO: Open an Issue in the `HoloViews <https://github.com/holoviz/holoviews>`_\\`Panel <https://github.com/holoviz/panel>`_ repository about this

        Parameters
        ----------

        ``theme_obj`` : Dict[str, Any]
            A Bokeh theme object

        |"""
        self.theme_attrs = theme_obj["attrs"]

    def hook(self, plot, element):
        """
        | A HoloViews hook for applying a Bokeh theme

        Parameters
        ----------

        ``plot`` : Dict[str, Any]
            A Bokeh theme object

        ``element`` : Any
            Irrelevant

        |"""
        if "Plot" in self.theme_attrs:
            plot.state.update(**self.theme_attrs["Plot"])
        if "xaxis" in plot.handles and "Axis" in self.theme_attrs:
            plot.handles["xaxis"].update(**self.theme_attrs["Axis"])
            plot.handles["yaxis"].update(**self.theme_attrs["Axis"])
        if "colorbar" in plot.handles and "BaseColorBar" in self.theme_attrs:
            plot.handles["colorbar"].update(**self.theme_attrs["BaseColorBar"])


def get_player_hv(
    wav: torch.Tensor,
    sr: int,
    total_seconds: float,
    over_curve: Optional[List[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]]],
    over_curve_names: Optional[List[str]],
    n_fft: int,
    hop_length: int,
    sync_legends: bool,
    pbar_height: int,
    theme_hook: Any,
    max_size: int,
    cmap: str,
    over_curve_colors: Optional[List[Optional[str]]],
    stay_color: str,
    follow_color: str,
    colorbar: bool,
    title: Optional[str],
    embed_title: bool,
    freq_label: Optional[str],
):
    """
    | A HoloViews hook for applying a Bokeh theme

    Parameters
    ----------

    ``wav`` : torch.Tensor
        Loaded audio tensor
    ``sr`` : int
        Resolved sample-rate
    ``total_seconds`` : float
        The total amount of seconds in the ``wav`` as calculated according to the ``sr``
    ``over_curve`` : List[torch.Tensor]
        A list of curves to be displayed over the spectrogram
    ``over_curve_names`` : List[str]
        A list of display names corresponding to the list given in ``over_curve``
    ``n_fft`` : int
        Sets the ``n_fft`` of the torchaudio spectrogram
    ``hop_length`` : int
        Sets the ``hop_length`` of the torchaudio spectrogram
    ``sync_legends`` : bool
        Whether the legends of both audio channels ``over_curve``s should be
        synchronized
    ``pbar_height`` : int
        The total height of both the pbar itself and its axis
    ``theme_hook`` : ThemeHook
        The HoloViews hook for applying a Bokeh theme, see :ref:`ThemeHook <waloviz._holoviews_manipulations.ThemeHook>`.
    ``max_size`` : int
        The maximum amount of values allowed in the time axis, for both
        spectrograms and overlaid curves.
    ``cmap`` : str
        The colormap used to display the spectrogram
    ``over_curve_colors`` : List[str]
        A list of display colors corresponding to the list given in ``over_curve``
    ``stay_color`` : str
        The color for the current time cursor **when not following** it
    ``follow_color`` : str
        The color for the current time cursor **only when following** it
    ``colorbar`` : bool
        Whether to display a colorbar for the spectrograms
    ``title`` : str
        Sets the title of the chart, which is displayed when ``embed_title=True``
    ``freq_label`` : str
        The label of the frequency axis (vertical), hides the label when set
        to None which saves space.

    Returns
    -------

    ``player_hv`` : hv.Layout
        The basic player plot elements in HoloViews format, without any custom
        interactivity

    |"""
    responsive = True

    spec = T.Spectrogram(n_fft=n_fft, hop_length=hop_length)(wav)

    spec = [skip_to_size(sub_spec, max_size) for sub_spec in spec]
    if over_curve is not None:
        over_curve = [skip_to_size(sub_curve, max_size) for sub_curve in over_curve]

    hz_min, hv_max = calculate_frequency_range_of_torhcaudio_spectrogram(sr, n_fft)

    plots = []
    for channel_index, spec_channel in enumerate(spec):
        plot = create_channel_spectrogram_plot(
            channel_index,
            spec_channel,
            total_seconds,
            over_curve,
            over_curve_names,
            theme_hook,
            cmap,
            over_curve_colors,
            stay_color,
            colorbar,
            title,
            embed_title,
            freq_label,
            hz_min,
            hv_max,
        )
        plots.append(plot)

    pbar = create_progress_bar_plot(total_seconds, pbar_height)
    plots.append(pbar)

    player_hv = combine_player_plots(
        plots, sync_legends, theme_hook, stay_color, responsive
    )
    return player_hv


def calculate_frequency_range_of_torhcaudio_spectrogram(sr, n_fft):
    hz_min = (-1 / n_fft) * sr / 2
    hv_max = (1 + 1 / n_fft) * sr / 2
    return hz_min, hv_max


def combine_player_plots(plots, sync_legends, theme_hook, stay_color, responsive):
    base_tools = ["reset", "pan", "wheel_zoom", "save"]
    tools_kwargs = dict(
        tools=base_tools,
        default_tools=["xbox_zoom", *base_tools],
        active_tools=base_tools,
    )

    player_hv = (
        hv.Layout(plots)
        .cols(1)
        .opts(toolbar="left", sync_legends=sync_legends)
        .opts(
            hv.opts.Image(
                responsive=responsive,
                hooks=[theme_hook.hook],
                **tools_kwargs,
            )
        )
        .opts(
            hv.opts.Curve(
                responsive=responsive,
                hooks=[theme_hook.hook],
                **tools_kwargs,
            )
        )
        .opts(hv.opts.VSpan(line_color=stay_color, line_alpha=0.0, **tools_kwargs))
        .opts(hv.opts.VLine(**tools_kwargs))
    )

    return player_hv


def create_progress_bar_plot(total_seconds, pbar_height):
    image = hv.Image(
        np.ones((1, 1)), bounds=(0, 0, total_seconds, 1), kdims=["x", "dump"]
    ).opts(
        xlabel="",
        yaxis=None,
        height=pbar_height,
        cmap=["#444444", "#444444"],
        alpha=0.5,
    )
    vline = hv.VLine(0).opts(line_color="white")
    vspan = hv.VSpan(0, 0).opts(fill_color="white")
    glyph = hv.Points([(0, 0.5)], kdims=["x", "dump"]).opts(
        color="white", size=pbar_height - 30, yaxis=None, ylim=(0, 1)
    )
    pbar = image * vline * vspan * glyph
    return pbar


def create_channel_spectrogram_plot(
    channel_index,
    spec_channel,
    total_seconds,
    over_curve,
    over_curve_names,
    theme_hook,
    cmap,
    over_curve_colors,
    stay_color,
    colorbar,
    title,
    embed_title,
    freq_label,
    hz_min,
    hv_max,
):
    spec_image = hv.Image(
        spec_channel.numpy()[::-1, :] + 1e-5,
        bounds=(0, hz_min, total_seconds, hv_max),
        kdims=["x", "Hz"],
    ).opts(
        xaxis=None,
        ylabel=freq_label,
        cmap=cmap,
        cnorm="log",
        colorbar=colorbar,
    )
    vspan = hv.VSpan(0, 0).opts(fill_color="#ffffff33", yaxis=None)
    vline = hv.VLine(0).opts(line_width=2, line_color=stay_color, yaxis=None)

    has_over_curve = over_curve is not None
    if has_over_curve:
        curves = []
        for curve_index, sub_curve in enumerate(over_curve):
            color_kwargs = {}
            if (
                over_curve_colors is not None
                and len(over_curve_colors) > curve_index
                and over_curve_colors[curve_index] is not None
            ):
                color_kwargs["color"] = over_curve_colors[curve_index]

            if isinstance(sub_curve, Tuple):
                sub_x, sub_y = sub_curve
                channel_sub_curve = sub_x[channel_index], sub_y[channel_index]
            else:
                channel_sub_curve = (
                    np.linspace(0, total_seconds, sub_curve[channel_index].shape[-1]),
                    sub_curve[channel_index],
                )

            curve = hv.Curve(
                channel_sub_curve,
                kdims=["x"],
                label=f"{over_curve_names[curve_index]}",
            ).opts(ylabel="", xaxis=None, alpha=0.9, **color_kwargs)
            curves.append(curve)
        spec_image = spec_image * hv.Overlay(curves)

    glyph = hv.Points([(0, 0.5)], kdims=["x", "dump"]).opts(
        marker="^", color="white", size=10, yaxis=None, ylim=(0, 1)
    )
    if embed_title:
        channel_title = f"{title} [{channel_index}]"
    else:
        channel_title = ""
    plot = (spec_image * vline * vspan * glyph).opts(
        multi_y=True,
        legend_position="right",
        hooks=[theme_hook.hook],
        title=channel_title,
    )

    return plot
