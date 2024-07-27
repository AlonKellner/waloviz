# pyright: reportAttributeAccessIssue=false, reportOptionalMemberAccess=false, reportOperatorIssue=false

from typing import Any, Dict, List, Optional, Tuple, Union

import bokeh
import bokeh.model
import holoviews as hv
import numpy as np
import torch
import torchaudio.transforms as T

from ._tensor_utils import skip_to_size


class ThemeHook:
    r"""
    | A class with a HoloViews hook for applying a Bokeh theme.

    | This is due to a problem when using the built-in theme support of
      HoloViews in integration with Panel, for some reason themes are only
      partially applied in those situations.
    | TODO: Open an Issue in the `HoloViews <https://github.com/holoviz/holoviews>`_ \\ `Panel <https://github.com/holoviz/panel>`_ repository about this

    Parameters
    ----------
    ``theme_obj`` : Dict[str, Any]
        A Bokeh theme object

    |

    """

    def __init__(self, theme_obj: Dict[str, Any]) -> None:
        self.theme_attrs = theme_obj["attrs"]

    def hook(self, plot: bokeh.model.Model, element: Any) -> None:  # noqa: ARG002
        """
        | A HoloViews hook for applying a Bokeh theme.

        Parameters
        ----------
        ``plot`` : Dict[str, Any]
            A Bokeh theme object
        ``element`` : Any
            Irrelevant

        |

        """
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
    theme_hook: ThemeHook,
    max_size: int,
    cmap: str,
    over_curve_colors: Optional[List[Optional[str]]],
    stay_color: str,
    colorbar: bool,
    title: Optional[str],
    embed_title: bool,
    freq_label: Optional[str],
    over_curve_axes: Optional[List[str]],
    axes_limits: Optional[
        Dict[str, Tuple[Optional[Union[float, int]], Optional[Union[float, int]]]]
    ],
) -> hv.Layout:
    """
    | Uses HoloViews to create the plots elements of the player, without any custom interactivity.

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
        Whether the legends of both audio channels ``over_curve`` s should be
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
    ``embed_title`` : bool
        Displayed the ``title`` as part of the plot when ``True``
    ``freq_label`` : str
        The label of the frequency axis (vertical), hides the label when set
        to None which saves space.
    ``over_curve_axes`` : List[str]
        A list of axes names corresponding to the list given in ``over_curve``
    ``axes_limits`` : Dict[str, Tuple[float, float]]
        Default limits for any of the axes

    Returns
    -------
    ``player_hv`` : hv.Layout
        The basic player plot elements in HoloViews format, without any custom
        interactivity

    |

    """
    responsive = True

    spec = T.Spectrogram(n_fft=n_fft, hop_length=hop_length)(wav)

    # type not inferred to recursive function
    spec: List[torch.Tensor] = [  # pyright: ignore[reportAssignmentType]
        skip_to_size(sub_spec, max_size) for sub_spec in spec
    ]
    if over_curve is not None:
        over_curve = [skip_to_size(sub_curve, max_size) for sub_curve in over_curve]

    hz_min, hv_max = calculate_frequency_range_of_torchaudio_spectrogram(sr, n_fft)

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
            over_curve_axes,
            axes_limits,
        )
        plots.append(plot)

    pbar = create_progress_bar_plot(total_seconds, pbar_height)
    plots.append(pbar)

    player_hv = combine_player_plots(
        plots, sync_legends, theme_hook, stay_color, responsive
    )
    return player_hv


def calculate_frequency_range_of_torchaudio_spectrogram(
    sr: int, n_fft: int
) -> Tuple[float, float]:
    """
    | Calculates the maximum and minimum frequency as in the torchaudio spectrogram.

    Parameters
    ----------
    ``sr`` : int
        Resolved sample-rate
    ``n_fft`` : int
        Sets the ``n_fft`` of the torchaudio spectrogram

    Returns
    -------
    ``hz_min`` : int
        Minimum frequency in the torchaudio spectrogram
    ``hz_max`` : int
        Maximum frequency in the torchaudio spectrogram

    |
    """
    hz_min = (-1 / n_fft) * sr / 2
    hv_max = (1 + 1 / n_fft) * sr / 2
    return hz_min, hv_max


def combine_player_plots(
    plots: List[hv.Layout],
    sync_legends: bool,
    theme_hook: ThemeHook,
    stay_color: str,
    responsive: bool,
) -> hv.Layout:
    """
    | Combines the spectrograms and progress bar plots into one layout.

    Parameters
    ----------
    ``plots`` : List[hv.Layout]
        A list of the plots of the spectrograms and the progress bar
    ``sync_legends`` : bool
        Whether the legends of both audio channels ``over_curve`` s should be
        synchronized
    ``theme_hook`` : ThemeHook
        The HoloViews hook for applying a Bokeh theme, see :ref:`ThemeHook <waloviz._holoviews_manipulations.ThemeHook>`.
    ``stay_color`` : str
        The color for the current time cursor **when not following** it
    ``responsive`` : bool
        Whether the plot width and height should be responsive

    Returns
    -------
    ``player_hv`` : hv.Layout
        A HoloViews Layout with the spectrograms and progress bar stacked together.

    |
    """
    base_tools = ["reset", "pan", "wheel_zoom", "save"]
    tools_kwargs = dict(
        tools=base_tools,
        default_tools=["xbox_zoom", *base_tools],
        active_tools=base_tools,
    )

    player_hv: hv.Layout = (  # pyright: ignore[reportAssignmentType]
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


def create_progress_bar_plot(total_seconds: float, pbar_height: int) -> hv.Layout:
    """
    | Creates a HoloViews plot of the progress bar.

    Parameters
    ----------
    ``total_seconds`` : float
        The total amount of seconds in the ``wav`` as calculated according to the ``sr``
    ``pbar_height`` : int
        The total height of both the pbar itself and its axis

    Returns
    -------
    ``pbar`` : hv.Layout
        A HoloViews plot of the progress bar

    |
    """
    image = hv.Image(
        np.ones((1, 1)), bounds=(0, 0, total_seconds, 1), kdims=["x", "_dump"]
    ).opts(
        xlabel="",
        yaxis=None,
        height=pbar_height,
        cmap=["#444444", "#444444"],
        alpha=0.5,
    )
    vline = hv.VLine(0).opts(line_color="white")
    vspan = hv.VSpan(0, 0).opts(fill_color="white")
    glyph = hv.Points([(0, 0.5)], kdims=["x", "_dump"]).opts(
        color="white", size=pbar_height - 30, yaxis=None, ylim=(0, 1)
    )
    pbar: hv.Layout = image * vline * vspan * glyph
    return pbar


def create_channel_spectrogram_plot(
    channel_index: int,
    spec_channel: torch.Tensor,
    total_seconds: float,
    over_curve: Optional[List[Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]]],
    over_curve_names: Optional[List[str]],
    theme_hook: ThemeHook,
    cmap: str,
    over_curve_colors: Optional[List[Optional[str]]],
    stay_color: str,
    colorbar: bool,
    title: Optional[str],
    embed_title: bool,
    freq_label: Optional[str],
    hz_min: float,
    hv_max: float,
    over_curve_axes: Optional[List[str]],
    axes_limits: Optional[
        Dict[str, Tuple[Optional[Union[float, int]], Optional[Union[float, int]]]]
    ],
) -> hv.Layout:
    """
    | Creates a HoloViews plot of the progress bar.

    Parameters
    ----------
    ``channel_index`` : int
        The current channel to generate spectrogram for
    ``spec_channel`` : torch.Tensor
        The spectrogram of the current channel
    ``total_seconds`` : float
        The total amount of seconds in the ``wav`` as calculated according to the ``sr``
    ``over_curve`` : List[torch.Tensor]
        A list of curves to be displayed over the spectrogram
    ``over_curve_names`` : List[str]
        A list of display names corresponding to the list given in ``over_curve``
    ``theme_hook`` : ThemeHook
        The HoloViews hook for applying a Bokeh theme, see :ref:`ThemeHook <waloviz._holoviews_manipulations.ThemeHook>`.
    ``cmap`` : str
        The colormap used to display the spectrogram
    ``over_curve_colors`` : List[str]
        A list of display colors corresponding to the list given in ``over_curve``
    ``stay_color`` : str
        The color for the current time cursor **when not following** it
    ``colorbar`` : bool
        Whether to display a colorbar for the spectrograms
    ``title`` : str
        Sets the title of the chart, which is displayed when ``embed_title=True``
    ``embed_title`` : bool
        Displayed the ``title as part of the plot when ``True``
    ``freq_label`` : str
        The label of the frequency axis (vertical), hides the label when set
        to None which saves space.
    ``hz_min`` : int
        Minimum frequency in the torchaudio spectrogram
    ``hz_max`` : int
        Maximum frequency in the torchaudio spectrogram
    ``over_curve_axes`` : List[str]
        A list of axes names corresponding to the list given in ``over_curve``
    ``axes_limits`` : Dict[str, Tuple[float, float]]
        Default limits for any of the axes

    Returns
    -------
    ``channel_spectrogram_plot`` : hv.Layout
        A HoloViews plot of the current channel spectrogram

    |
    """
    lim_kwargs = create_lim_kwargs(over_curve_axes, axes_limits)

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
        **lim_kwargs["x"],
        **lim_kwargs["Hz"],
    )
    vspan = hv.VSpan(0, 0).opts(fill_color="#ffffff33", yaxis=None)
    vline = hv.VLine(0).opts(line_width=2, line_color=stay_color, yaxis=None)

    if (over_curve is not None) and (over_curve_names is not None):
        curves = []
        for curve_index, sub_curve in enumerate(over_curve):
            color_kwargs = {}
            if (
                over_curve_colors is not None
                and len(over_curve_colors) > curve_index
                and over_curve_colors[curve_index] is not None
            ):
                color_kwargs["color"] = over_curve_colors[curve_index]

            axes_kwargs = {}
            axes_opts_kwargs = {}
            if (
                over_curve_axes is not None
                and len(over_curve_axes) > curve_index
                and over_curve_axes[curve_index] is not None
            ):
                axis = over_curve_axes[curve_index]
                axes_kwargs["vdims"] = [axis]
                axes_opts_kwargs = lim_kwargs[axis]
            elif "y" in lim_kwargs:
                axis = "y"
                axes_opts_kwargs = lim_kwargs[axis]

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
                **axes_kwargs,
            ).opts(
                ylabel="",
                xaxis=None,
                alpha=0.9,
                **color_kwargs,
                **axes_opts_kwargs,
                **lim_kwargs["x"],
            )
            curves.append(curve)
        spec_image = spec_image * hv.Overlay(curves)

    glyph = hv.Points([(0, 0.5)], kdims=["x", "_dump"]).opts(
        marker="^", color="white", size=10, yaxis=None, ylim=(0, 1)
    )
    if embed_title:
        channel_title = f"{title} [{channel_index}]"
    else:
        channel_title = ""
    plot: hv.Layout = (spec_image * vline * vspan * glyph).opts(  # pyright: ignore[reportAssignmentType]
        multi_y=True,
        legend_position="right",
        hooks=[theme_hook.hook],
        title=channel_title,
    )

    return plot


def create_lim_kwargs(
    over_curve_axes: Optional[List[str]],
    axes_limits: Optional[
        Dict[str, Tuple[Optional[Union[float, int]], Optional[Union[float, int]]]]
    ],
) -> Dict[
    str, Dict[str, Tuple[Optional[Union[float, int]], Optional[Union[float, int]]]]
]:
    """
    | Creates a dict with kwargs for axis limiting, in the required HoloViews axis limits format.

    Parameters
    ----------
    ``over_curve_axes`` : List[str]
        .
    ``axes_limits`` : Dict[str, Tuple[float, float]]
        .

    Returns
    -------
    ``lim_kwargs`` : Dict[str, Dict[str, Tuple[float, float]]]
        The limit kwargs for each axis as required by HoloViews

    |
    """
    lim_kwargs = {"x": {}, "Hz": {}}
    if over_curve_axes is not None:
        for axis in set(over_curve_axes):
            lim_kwargs[axis] = {}

    if axes_limits is not None:
        for axis, limits in axes_limits.items():
            if axis == "x":
                lim_kwargs["x"] = dict(xlim=limits)
            else:
                lim_kwargs[axis] = dict(ylim=limits)
    return lim_kwargs
