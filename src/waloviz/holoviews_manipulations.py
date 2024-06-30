from typing import Any, List, Optional, Tuple, Union

import holoviews as hv
import numpy as np
import torch
import torchaudio.transforms as T

from .tensor_utils import OverCurve, skip_to_size


class ThemeHook:
    def __init__(self, theme_obj):
        self.theme_attrs = theme_obj["attrs"]

    def hook(self, plot, element):
        if "Plot" in self.theme_attrs:
            plot.state.update(**self.theme_attrs["Plot"])
        if "xaxis" in plot.handles and "Axis" in self.theme_attrs:
            plot.handles["xaxis"].update(**self.theme_attrs["Axis"])
            plot.handles["yaxis"].update(**self.theme_attrs["Axis"])
        if "colorbar" in plot.handles and "BaseColorBar" in self.theme_attrs:
            plot.handles["colorbar"].update(**self.theme_attrs["BaseColorBar"])


def get_waloviz_hv(
    wav: torch.Tensor,
    sr: int,
    total_seconds: float,
    over_curve: Optional[OverCurve],
    over_curve_names: Optional[List[str]],
    n_fft: int,
    hop_length: int,
    sync_legends: bool,
    height: int,
    width: Union[int, str],
    audio_height: int,
    pbar_height: int,
    theme_hook: Any,
    max_size: int,
    cmap: str,
    over_curve_colors: Optional[List[str]],
    stay_color: str,
    follow_color: str,
    colorbar: bool,
    title: str,
    embed_title: bool,
    freq_label: str
):
    responsive = width == "responsive"

    spec = T.Spectrogram(n_fft=n_fft, hop_length=hop_length)(wav)

    spec = [skip_to_size(sub_spec, max_size) for sub_spec in spec]
    if over_curve is not None:
        over_curve = [skip_to_size(sub_curve, max_size) for sub_curve in over_curve]

    hz_min = (-1 / n_fft) * sr / 2
    hv_max = (1 + 1 / n_fft) * sr / 2

    spec_height = (height - audio_height - pbar_height) // len(spec)

    plots = []
    for channel, spec_channel in enumerate(spec):
        spec_image = hv.Image(
            spec_channel.numpy()[::-1, :] + 1e-5,
            bounds=(0, hz_min, total_seconds, hv_max),
            kdims=["x", freq_label],
        ).opts(
            xaxis=None,
            cmap=cmap,
            cnorm="log",
            height=spec_height,
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
                    channel_sub_curve = sub_x[channel], sub_y[channel]
                else:
                    channel_sub_curve = (
                        np.linspace(0, total_seconds, sub_curve[channel].shape[-1]),
                        sub_curve[channel],
                    )

                curve = hv.Curve(
                    channel_sub_curve,
                    kdims=["x"],
                    label=f"{over_curve_names[curve_index]}",
                ).opts(
                    height=spec_height, ylabel="", xaxis=None, alpha=0.9, **color_kwargs
                )
                curves.append(curve)
            spec_image = spec_image * hv.Overlay(curves)

        glyph = hv.Points([(0, 0.5)], kdims=["x", "dump"]).opts(
            marker="^", color="white", size=10, yaxis=None, ylim=(0, 1)
        )
        if embed_title:
            channel_title = f"{title} [{channel}]"
        else:
            channel_title = ""
        plot = (spec_image * vline * vspan * glyph).opts(
            multi_y=True,
            legend_position="right",
            hooks=[theme_hook],
            title=channel_title,
        )
        plots.append(plot)

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
    plots.append(pbar)

    base_tools = ["reset", "pan", "wheel_zoom", "save"]
    tools_kwargs = dict(
        tools=base_tools,
        default_tools=["xbox_zoom", *base_tools],
        active_tools=base_tools,
    )

    width_kwargs = {}
    if width != "responsive":
        width_kwargs["width"] = width

    waloviz_hv = (
        hv.Layout(plots)
        .cols(1)
        .opts(toolbar="left", sync_legends=sync_legends)
        .opts(
            hv.opts.Image(
                responsive=responsive,
                hooks=[theme_hook],
                **width_kwargs,
                **tools_kwargs,
            )
        )
        .opts(
            hv.opts.Curve(
                responsive=responsive,
                hooks=[theme_hook],
                **width_kwargs,
                **tools_kwargs,
            )
        )
        .opts(hv.opts.VSpan(line_color=stay_color, line_alpha=0.0, **tools_kwargs))
        .opts(hv.opts.VLine(**tools_kwargs))
    )
    return waloviz_hv
