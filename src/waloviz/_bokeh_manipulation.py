"""
Here there are all sorts of Bokeh related manipulations, but most dominantly custom jslink.

| There are multiple functions in here that set some JS properties of Bokeh JS elements
| in order to "communicate" between those jslinks, for example the color of the current
| time cursor is communicated through the bright "played" region.
| At times these are confusing, this is a work in progress and will get better as we
| learn :)
"""

from typing import Any, Dict, List, Optional

import bokeh
import bokeh.model
from bokeh.models.callbacks import CustomJS
from bokeh.models.formatters import CustomJSTickFormatter
from bokeh.themes import built_in_themes

themes: Dict[str, Dict[str, Any]] = {k: v._json for k, v in built_in_themes.items()}


def apply_theme(
    plot: bokeh.model.Model,
    theme: Dict[str, Any],
    theme_elements_mapping: Dict[str, str],
) -> None:
    """
    | Manually sets theme values of a plot.

    Parameters
    ----------
    ``plot`` : bokeh.model.Model

    ``theme`` : Dict[str, Any]

    ``theme_elements_mapping`` : Dict[str, str]
        A mapping between theme keys and plot attributes

    |
    """
    for element, attr in theme_elements_mapping.items():
        if hasattr(plot, attr) and element in theme["attrs"]:
            for attr_name, attr_value in theme["attrs"][element].items():
                setattr(getattr(plot, attr), attr_name, attr_value)


def finalize_player_bokeh_gui(
    player_bokeh: bokeh.model.Model,
    theme: Dict[str, Any],
    total_seconds: float,
    stay_color: str,
    follow_color: str,
    aspect_ratio: Optional[float],
    sizing_mode: Optional[str],
    single_min_height: int,
) -> bokeh.model.Model:
    """
    | Modify bokeh settings and adds custom jslink interactivity.

    Parameters
    ----------
    ``player_bokeh`` : bokeh.model.Model
        As rendered by HoloViews
    ``theme`` : Dict[str, Any]

    ``total_seconds`` : float

    ``stay_color`` : str

    ``follow_color`` : str

    ``aspect_ratio`` : float | None

    ``single_min_height`` : int


    Returns
    -------
    ``player_bokeh`` : bokeh.model.Model
        With modifications and custom jslink interactivity

    |
    """
    player_bokeh.toolbar.autohide = True

    plots = []
    vlines = []
    vspans = []
    glyphs = []

    player_bokeh = modify_bokeh_elements(
        player_bokeh,
        theme,
        total_seconds,
        aspect_ratio,
        sizing_mode,
        single_min_height,
        plots,
        vlines,
        vspans,
        glyphs,
    )

    player_bokeh = add_interactivity_with_jslinks(
        player_bokeh, stay_color, follow_color, plots, vlines, vspans, glyphs
    )

    return player_bokeh


def add_interactivity_with_jslinks(
    player_bokeh: bokeh.model.Model,
    stay_color: str,
    follow_color: str,
    plots: List[bokeh.model.Model],
    vlines: List[bokeh.model.Model],
    vspans: List[bokeh.model.Model],
    glyphs: List[bokeh.model.Model],
) -> bokeh.model.Model:
    """
    | Adds custom jslink interactivity.

    Parameters
    ----------
    ``player_bokeh`` : bokeh.model.Model
        .
    ``stay_color`` : str
        .
    ``follow_color`` : str
        .
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar
    ``vlines`` : List[bokeh.model.Model]
        Bokeh elements for current time cursors
    ``vspans`` : List[bokeh.model.Model]
        Bokeh elements that brighten the section played so far
    ``glyphs`` : List[bokeh.model.Model]
        Bokeh elements for play icons and the progress bar circular handle

    Returns
    -------
    ``player_bokeh`` : bokeh.model.Model
        With custom jslink interactivity

    |
    """
    children = player_bokeh.children

    for channel, (plot, vline, vspan, glyph) in enumerate(
        zip(plots, vlines, vspans, glyphs)
    ):
        is_pbar = channel == len(children) - 1
        is_spec = not is_pbar

        if is_spec:
            glyphs[0].js_link("visible", glyph, "visible")

        vspans[0].js_link("right", glyph.glyph, "x")
        vspans[0].js_link("right", vline, "location")
        vspans[0].js_link("right", vspan, "right")
        vspans[0].js_link("line_color", vline, "line_color")
        vspans[0].js_on_change("right", get_follow_callback(plot, vspan))
        vspans[0].js_on_change("line_color", get_follow_callback(plot, vspan))

        plot.js_on_event(
            "doubletap",
            get_start_follow_callback(follow_color, vspans, plots),
            get_move_time_callback(vspans, plots),
        )
        plot.js_on_event("reset", get_reset_callback(plot, plots))

        for e in [
            "panstart",
            "panend",
            "pinchstart",
            "pinchend",
            "wheel",
            "press",
            "pressup",
            "tap",
            "doubletap",
        ]:
            plot.js_on_event(
                e,
                get_set_y_range_callback(plot, plots),
                get_set_pbar_x_range_callback(plot, plots),
            )
        for e in [
            "panstart",
            "pan",
            "pinchstart",
            "pinch",
            "panend",
            "wheel",
            "press",
            "pressup",
            "rangesupdate",
        ]:
            plot.js_on_event(
                e,
                get_keep_y_range_callback(plot, plots),
                get_keep_dump_range_callback(plot),
                get_keep_x_range_callback(plot, plots),
            )
        for e in ["pan", "pinch", "rangesupdate", "wheel"]:
            plot.js_on_event(e, get_stop_follow_callback(stay_color, vspans))

        if is_spec:
            for e in ["tap", "pressup", "doubletap"]:
                plot.js_on_event(e, get_play_pause_callback(plots, glyphs))

        if is_pbar:
            for e in [
                "pinch",
                "pinchstart",
                "pinchend",
                "pan",
                "panstart",
                "panend",
                "press",
                "pressup",
                "tap",
            ]:
                plot.js_on_event(
                    e,
                    get_move_pbar_callback(vspans, plots),
                    get_stop_follow_callback(stay_color, vspans),
                )

        for e in [
            "pinch",
            "pinchstart",
            "pinchend",
            "panstart",
            "pan",
            "panend",
            "wheel",
            "press",
            "pressup",
            "rangesupdate",
        ]:
            plot.js_on_event(e, get_record_ranges_callback(plots))
    return player_bokeh


def modify_bokeh_elements(
    player_bokeh: bokeh.model.Model,
    theme: Dict[str, Any],
    total_seconds: float,
    aspect_ratio: Optional[float],
    sizing_mode: Optional[str],
    single_min_height: int,
    plots: List[bokeh.model.Model],
    vlines: List[bokeh.model.Model],
    vspans: List[bokeh.model.Model],
    glyphs: List[bokeh.model.Model],
) -> bokeh.model.Model:
    """
    | Adds custom jslink interactivity.

    Parameters
    ----------
    ``player_bokeh`` : bokeh.model.Model
        .
    ``theme`` : Dict[str, Any]
        .
    ``total_seconds`` : float
        .
    ``aspect_ratio`` : float | None
        .
    ``sizing_mode`` : str | None
        .
    ``single_min_height`` : int
        .
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar
    ``vlines`` : List[bokeh.model.Model]
        Bokeh elements for current time cursors
    ``vspans`` : List[bokeh.model.Model]
        Bokeh elements that brighten the section played so far
    ``glyphs`` : List[bokeh.model.Model]
        Bokeh elements for play icons and the progress bar circular handle

    Returns
    -------
    ``player_bokeh`` : bokeh.model.Model
        With manual modifications

    |
    """
    children = player_bokeh.children

    for channel, (plot, _, __) in enumerate(children):
        plots.append(plot)

        is_pbar = channel == len(children) - 1

        vline = plot.renderers[-3]
        vspan = plot.renderers[-2]
        glyph = plot.renderers[-1]

        if is_pbar:
            plot.xaxis.formatter = get_audio_xformatter(total_seconds)

            theme_elements_mapping = dict(Grid="xgrid")
        else:
            plot.min_border_bottom = 0
            plot.min_height = single_min_height

            theme_elements_mapping = dict(
                Title="title", Grid="grid", BaseColorBar="colorbar"
            )
            if len(plot.legend) != 0:
                theme_elements_mapping["Legend"] = "legend"

            glyph.glyph.angle = -90
            glyph.glyph.angle_units = "deg"

            plot.y_range = plots[0].y_range
            plot.extra_y_ranges = plots[0].extra_y_ranges
            if (sizing_mode != "fixed") and (aspect_ratio is not None):
                plot.aspect_ratio = aspect_ratio / (len(children) - 1)

        plot.min_border_left = 0
        plot.min_border_right = 0
        plot.min_border_top = 0
        plot.x_range.min_interval = 0.0045
        apply_theme(plot, theme, theme_elements_mapping)

        vlines.append(vline)
        vspans.append(vspan)
        glyphs.append(glyph)

    return player_bokeh


def get_audio_xformatter(total_seconds: float) -> CustomJSTickFormatter:
    """
    | Create a relative time tick formatter, with dynamic resolution from days up to milliseconds.

    Parameters
    ----------
    ``total_seconds`` : float


    Returns
    -------
    ``xformatter`` : CustomJSTickFormatter
        Relative time tick formatter.

    |
    """
    xformatter = CustomJSTickFormatter(
        code=f"""
if ((tick < 0) || tick > {total_seconds}) {{
    return ""
}}

var d = new Date(0);
d.setMilliseconds(tick*1000);
var days = Math.floor(d.getTime() / (1000*60*60*24));
var hours = `${{d.getUTCHours()}}`.padStart(2, "0");
var minutes = `${{d.getUTCMinutes()}}`.padStart(2, "0");
var seconds = `${{d.getUTCSeconds()}}`.padStart(2, "0");
var milli = `${{d.getUTCMilliseconds()}}`.padStart(3, "0").replace(/0+$/, '');
var range = ticks[ticks.length-1] - ticks[0];

var result;
if ((range > 3600) || ((milli == 0) && (seconds == 0) && (minutes == 0))) {{
    result = `${{hours}}:${{minutes}}:${{seconds}}`;
}}
else if (range > 4) {{
    result = `${{minutes}}:${{seconds}}`;
}}
else {{
    if (milli.length > 0) {{
        result = `${{minutes}}:${{seconds}}.${{milli}}`;
    }} else {{
        result = `${{minutes}}:${{seconds}}`;
    }}
}}
if (days > 0) {{
    result = `${{days}}d ${{result}}`;
}}
return result;
"""
    )
    return xformatter


def get_record_ranges_callback(plots: List[bokeh.model.Model]) -> CustomJS:
    """
    | Create a jslink callback which records the previous ranges, important for following and zooming on x axis only.

    | Saves ``prev_x_range`` and ``prev_y_range`` in the zeroth plot (first spectrogram).

    Parameters
    ----------
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar

    Returns
    -------
    ``record_ranges_callback`` : CustomJS
        A jslink callback.

    |
    """
    record_ranges_callback = CustomJS(
        args=dict(plot_0=plots[0]),
        code="""
plot_0.prev_x_range = {start: plot_0.x_range.start, end: plot_0.x_range.end};
plot_0.prev_y_range = {start: plot_0.y_range.start, end: plot_0.y_range.end};

plot_0.prev_extra_y_ranges = Object.keys(plot_0.extra_y_ranges).reduce(function(result, key) {
    result[key] = {start: plot_0.extra_y_ranges[key].start, end: plot_0.extra_y_ranges[key].end};
    return result;
}, {});
                """,
    )
    return record_ranges_callback


def get_start_follow_callback(
    follow_color: str, vspans: List[bokeh.model.Model], plots: List[bokeh.model.Model]
) -> CustomJS:
    """
    | Create a jslink callback which activates "follow" mode.

    | Saves ``is_following`` to the zeroth vspan (first spectrogram bright section).
    | Also used to synchronize the vline follow color with the vspan ``line_color`` .

    Parameters
    ----------
    ``follow_color`` : List[bokeh.model.Model]
        The color of the vlines when in "follow" mode
    ``vspans`` : List[bokeh.model.Model]
        Bokeh elements that brighten the section played so far
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar

    Returns
    -------
    ``start_follow_callback`` : CustomJS
        A jslink callback.

    |
    """
    start_follow_callback = CustomJS(
        args=dict(vspan_0=vspans[0], plot_0=plots[0]),
        code=f"""
vspan_0.is_following = true;
vspan_0.line_color = "{follow_color}";
let x = Math.max(Math.min(cb_obj.x, plot_0.x_range.reset_end), plot_0.x_range.reset_start);
vspan_0.ratio = (x-plot_0.x_range.start)/(plot_0.x_range.end-plot_0.x_range.start);
                """,
    )
    return start_follow_callback


def get_stop_follow_callback(
    stay_color: str, vspans: List[bokeh.model.Model]
) -> CustomJS:
    """
    | Create a jslink callback which activates "stay" mode, stops "follow" mode.

    | Sets ``is_following`` of the zeroth vspan (first spectrogram bright section).
    | Also used to synchronize the vline stay color with the vspan ``line_color`` .

    Parameters
    ----------
    ``stay_color`` : List[bokeh.model.Model]
        The color of the vlines when in "stay" mode
    ``vspans`` : List[bokeh.model.Model]
        Bokeh elements that brighten the section played so far

    Returns
    -------
    ``stop_follow_callback`` : CustomJS
        A jslink callback.

    |
    """
    stop_follow_callback = CustomJS(
        args=dict(vspan_0=vspans[0]),
        code=f"""
vspan_0.is_following = false;
vspan_0.line_color = "{stay_color}";
                """,
    )
    return stop_follow_callback


def get_set_y_range_callback(
    plot: bokeh.model.Model, plots: List[bokeh.model.Model]
) -> CustomJS:
    """
    | Create a jslink callback which stops the y zoom by setting a constant y range when the mouse is over the spectrograms.

    | Sets ``is_y_fixed`` , ``hz_fixed_start`` and ``hz_fixed_end`` of the zeroth plot (first spectrogram).

    Parameters
    ----------
    ``plot`` : bokeh.model.Model
        The current ``plot``
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar

    Returns
    -------
    ``set_y_range_callback`` : CustomJS
        A jslink callback.

    |
    """
    set_y_range_callback = CustomJS(
        args=dict(plot=plot, plot_0=plots[0]),
        code="""
let mouse_in = ('x' in cb_obj) && (cb_obj.x > plot.x_range.start) && (cb_obj.x < plot.x_range.end);
if (('is_y_fixed' in plot_0) && (plot_0.is_y_fixed)) {
    if (mouse_in) {
        if ('dump' in plot.extra_y_ranges) {
            plot.y_range.start = plot_0.hz_fixed_start;
            plot.y_range.end = plot_0.hz_fixed_end;
            if (('y' in plot_0.extra_y_ranges) && ('y_fixed_start' in plot_0)) {
                plot.extra_y_ranges['y'].start = plot_0.y_fixed_start;
                plot.extra_y_ranges['y'].end = plot_0.y_fixed_end;
            }
        }
    } else {
        plot_0.is_y_fixed = false;
    }
} else {
    if (mouse_in) {
        plot_0.is_y_fixed = true;
        if ('prev_y_range' in plot_0) {
            plot_0.hz_fixed_start = plot_0.prev_y_range.start;
            plot_0.hz_fixed_end = plot_0.prev_y_range.end;
            if ('y' in plot_0.prev_extra_y_ranges) {
                plot_0.y_fixed_start = plot_0.prev_extra_y_ranges['y'].start;
                plot_0.y_fixed_end = plot_0.prev_extra_y_ranges['y'].end;
            }
        } else {
            plot_0.hz_fixed_start = plot_0.y_range.reset_start;
            plot_0.hz_fixed_end = plot_0.y_range.reset_end;
            if (('y' in plot.extra_y_ranges) && (plot.extra_y_ranges['y'].reset_start != null)) {
                plot_0.y_fixed_start = plot_0.extra_y_ranges['y'].reset_start;
                plot_0.y_fixed_end = plot_0.extra_y_ranges['y'].reset_end;
            }
        }
    }
}
                """,
    )
    return set_y_range_callback


def get_keep_y_range_callback(
    plot: bokeh.model.Model, plots: List[bokeh.model.Model]
) -> CustomJS:
    """
    | Create a jslink callback which keeps the constant y range when the mouse is over the spectrograms.

    | Uses ``is_y_fixed`` , ``hz_fixed_start`` and ``hz_fixed_end`` of the zeroth plot (first spectrogram).

    Parameters
    ----------
    ``plot`` : bokeh.model.Model
        The current ``plot``
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar

    Returns
    -------
    ``keep_y_range_callback`` : CustomJS
        A jslink callback.

    |
    """
    keep_y_range_callback = CustomJS(
        args=dict(plot=plot, plot_0=plots[0]),
        code="""
if (('is_y_fixed' in plot_0) && (plot_0.is_y_fixed)) {
    if ('dump' in plot.extra_y_ranges) {
        plot.y_range.start = plot_0.hz_fixed_start;
        plot.y_range.end = plot_0.hz_fixed_end;
        if (('y' in plot.extra_y_ranges) && ('y_fixed_start' in plot_0)) {
            plot.extra_y_ranges['y'].start = plot_0.y_fixed_start;
            plot.extra_y_ranges['y'].end = plot_0.y_fixed_end;
        }
    }
}
                """,
    )
    return keep_y_range_callback


def get_set_pbar_x_range_callback(
    plot: bokeh.model.Model, plots: List[bokeh.model.Model]
) -> CustomJS:
    """
    | Create a jslink callback which stops the x zoom by setting a constant x range when the mouse is over the progress bar.

    | Sets ``is_x_fixed`` , ``x_fixed_start`` and ``x_fixed_end`` of the zeroth plot (first spectrogram).

    Parameters
    ----------
    ``plot`` : bokeh.model.Model
        The current ``plot``
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar

    Returns
    -------
    ``set_pbar_x_range_callback`` : CustomJS
        A jslink callback.

    |
    """
    set_pbar_x_range_callback = CustomJS(
        args=dict(plot=plot, pbar=plots[-1], plot_0=plots[0]),
        code="""
let mouse_in = ('y' in cb_obj) && (cb_obj.y > pbar.y_range.start) && (cb_obj.y < pbar.y_range.end);
if (('is_x_fixed' in plot_0) && (plot_0.is_x_fixed)) {
    if (mouse_in) {
        plot.x_range.start = plot_0.x_fixed_start;
        plot.x_range.end = plot_0.x_fixed_end;
    } else {
        plot_0.is_x_fixed = false;
    }
} else {
    if (mouse_in) {
        plot_0.is_x_fixed = true;
        if ('prev_x_range' in plot_0) {
            plot_0.x_fixed_start = plot_0.prev_x_range.start;
            plot_0.x_fixed_end = plot_0.prev_x_range.end;
        } else {
            plot_0.x_fixed_start = plot_0.x_range.reset_start;
            plot_0.x_fixed_end = plot_0.x_range.reset_end;
        }
    }
}
                        """,
    )
    return set_pbar_x_range_callback


def get_keep_x_range_callback(
    plot: bokeh.model.Model, plots: List[bokeh.model.Model]
) -> CustomJS:
    """
    | Create a jslink callback which keeps the constant x range when the mouse is over the progress bar.

    | Uses ``is_x_fixed`` , ``x_fixed_start`` and ``x_fixed_end`` of the zeroth plot (first spectrogram).

    Parameters
    ----------
    ``plot`` : bokeh.model.Model
        The current ``plot``
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar

    Returns
    -------
    ``keep_x_range_callback`` : CustomJS
        A jslink callback.

    |
    """
    keep_x_range_callback = CustomJS(
        args=dict(plot=plot, plot_0=plots[0]),
        code="""
if (('is_x_fixed' in plot_0) && (plot_0.is_x_fixed)) {
    plot.x_range.start = plot_0.x_fixed_start;
    plot.x_range.end = plot_0.x_fixed_end;
}
            """,
    )
    return keep_x_range_callback


def get_keep_dump_range_callback(plot: bokeh.model.Model) -> CustomJS:
    """
    | Create a jslink callback which keeps the "dump" y axis between 0 and 1.

    | The "dump" axis is used for the play and stop icons as well as the progress bar handle.

    Parameters
    ----------
    ``plot`` : bokeh.model.Model
        The current ``plot``

    Returns
    -------
    ``keep_dump_range_callback`` : CustomJS
        A jslink callback.

    |
    """
    keep_dump_range_callback = CustomJS(
        args=dict(plot=plot),
        code="""
if ('dump' in plot.extra_y_ranges) {
    plot.extra_y_ranges['dump'].start = 0;
    plot.extra_y_ranges['dump'].end = 1;
} else {
    plot.y_range.start = 0;
    plot.y_range.end = 1;
}
                """,
    )
    return keep_dump_range_callback


def get_play_pause_callback(
    plots: List[bokeh.model.Model], glyphs: List[bokeh.model.Model]
) -> CustomJS:
    r"""
    | Create a jslink callback which toggles play\\pause when the mouse is over the spectrograms.

    | Makes the zeroth glyph (first spectrogram play icon) visible.

    Parameters
    ----------
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar
    ``glyphs`` : List[bokeh.model.Model]
        Bokeh elements for play icons and the progress bar circular handle

    Returns
    -------
    ``play_pause_callback`` : CustomJS
        A jslink callback.

    |
    """
    play_pause_callback = CustomJS(
        args=dict(plot_0=plots[0], pause_0=glyphs[0]),
        code="""
let x = cb_obj.x;
let y = cb_obj.y;
let sx = cb_obj.sx;
let sy = cb_obj.sy;
let mouse_on_xrange = (x > plot_0.x_range.start) && (x < plot_0.x_range.end);
if (mouse_on_xrange) {
    pause_0.visible = !pause_0.visible;
}
                """,
    )
    return play_pause_callback


def get_reset_callback(
    plot: bokeh.model.Model, plots: List[bokeh.model.Model]
) -> CustomJS:
    """
    | Create a jslink callback which updates saved values to their presets.

    Parameters
    ----------
    ``plot`` : bokeh.model.Model
        The current ``plot``
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar

    Returns
    -------
    ``reset_callback`` : CustomJS
        A jslink callback.

    |
    """
    reset_callback = CustomJS(
        args=dict(plot=plot, plot_0=plots[0]),
        code="""
if (('is_y_fixed' in plot_0) && (plot_0.is_y_fixed)) {
    plot_0.is_y_fixed = false;
    plot.y_range.start = plot.y_range.reset_start;
    plot.y_range.end = plot.y_range.reset_end;
    if (('y' in plot.extra_y_ranges) && (plot.extra_y_ranges['y'].reset_start != null)) {
        plot.extra_y_ranges['y'].start = plot.extra_y_ranges['y'].reset_start;
        plot.extra_y_ranges['y'].end = plot.extra_y_ranges['y'].reset_end;
    }
}
if (('is_x_fixed' in plot_0) && (plot_0.is_x_fixed)) {
    plot_0.is_x_fixed = false;
    plot.x_range.start = plot.x_range.reset_start;
    plot.x_range.end = plot.x_range.reset_end;
}
            """,
    )
    return reset_callback


def get_follow_callback(plot: bokeh.model.Model, vspan: bokeh.model.Model) -> CustomJS:
    """
    | Create a jslink callback which updates the x range when in "follow" mode.

    Parameters
    ----------
    ``plot`` : bokeh.model.Model
        The current ``plot``
    ``vspans`` : List[bokeh.model.Model]
        Bokeh elements that brighten the section played so far

    Returns
    -------
    ``follow_callback`` : CustomJS
        A jslink callback.

    |
    """
    follow_callback = CustomJS(
        args=dict(plot=plot, vspan=vspan),
        code="""
if (('is_following' in cb_obj) && (cb_obj.is_following)) {
    let current_size = plot.x_range.end - plot.x_range.start;
    plot.x_range.start = cb_obj.right - current_size * cb_obj.ratio;
    plot.x_range.end = cb_obj.right + current_size * (1-cb_obj.ratio);
}
        """,
    )
    return follow_callback


def get_move_time_callback(
    vspans: List[bokeh.model.Model], plots: List[bokeh.model.Model]
) -> CustomJS:
    """
    | Create a jslink callback which moves the current time to the mouse position.

    | Used when double clicking.

    Parameters
    ----------
    ``vspans`` : List[bokeh.model.Model]
        Bokeh elements that brighten the section played so far
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar

    Returns
    -------
    ``move_time_callback`` : CustomJS
        A jslink callback.

    |
    """
    move_time_callback = CustomJS(
        args=dict(vspan_0=vspans[0], plot_0=plots[0]),
        code="""
vspan_0.right = Math.max(Math.min(cb_obj.x, plot_0.x_range.reset_end), plot_0.x_range.reset_start);
            """,
    )
    return move_time_callback


def get_move_pbar_callback(
    vspans: List[bokeh.model.Model], plots: List[bokeh.model.Model]
) -> CustomJS:
    """
    | Create a jslink callback which moves the current time to the mouse position when the mouse is over the progress bar.

    Parameters
    ----------
    ``vspans`` : List[bokeh.model.Model]
        Bokeh elements that brighten the section played so far
    ``plots`` : List[bokeh.model.Model]
        Bokeh plots for the spectrograms and progress bar

    Returns
    -------
    ``move_pbar_callback`` : CustomJS
        A jslink callback.

    |
    """
    move_pbar_callback = CustomJS(
        args=dict(vspan_0=vspans[0], plot_0=plots[0]),
        code="""
if (('is_x_fixed' in plot_0) && (plot_0.is_x_fixed)) {
    vspan_0.right = Math.max(Math.min(cb_obj.x, plot_0.x_range.reset_end), plot_0.x_range.reset_start);
}
            """,
    )
    return move_pbar_callback
