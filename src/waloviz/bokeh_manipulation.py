from typing import Any, Dict

from bokeh.models.callbacks import CustomJS
from bokeh.models.formatters import CustomJSTickFormatter
from bokeh.themes import _caliber, _contrast, _dark_minimal, _light_minimal, _night_sky

themes = dict(
    dark_minimal=_dark_minimal.json,
    light_minimal=_light_minimal.json,
    caliber=_caliber.json,
    contrast=_contrast.json,
    night_sky=_night_sky.json,
)


def apply_theme(plot, theme, theme_elements_mapping):
    for element, attr in theme_elements_mapping.items():
        if hasattr(plot, attr) and element in theme["attrs"]:
            for attr_name, attr_value in theme["attrs"][element].items():
                setattr(getattr(plot, attr), attr_name, attr_value)


def get_audio_xformatter(total_seconds: float) -> CustomJSTickFormatter:
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


def finalize_waloviz_bokeh_gui(
    waloviz_bokeh,
    theme: Dict[str, Any],
    xformatter: CustomJSTickFormatter,
    stay_color: str,
    follow_color: str,
):
    waloviz_bokeh.toolbar.autohide = True

    plots = []
    vlines = []
    vspans = []
    glyphs = []

    children = waloviz_bokeh.children
    for channel, (plot, _, __) in enumerate(children):
        plots.append(plot)

        is_pbar = channel == len(children) - 1
        is_spec = not is_pbar

        vline = plot.renderers[-3]
        vspan = plot.renderers[-2]
        glyph = plot.renderers[-1]

        if is_pbar:
            plot.xaxis.formatter = xformatter

            theme_elements_mapping = dict(Grid="xgrid")
        else:
            plot.min_border_bottom = 0

            theme_elements_mapping = dict(
                Title="title", Grid="grid", BaseColorBar="colorbar"
            )
            if len(plot.legend) != 0:
                theme_elements_mapping["Legend"] = "legend"

            glyph.glyph.angle = -90
            glyph.glyph.angle_units = "deg"

            plot.y_range = plots[0].y_range
            plot.extra_y_ranges = plots[0].extra_y_ranges

        plot.min_border_left = 0
        plot.min_border_right = 0
        plot.min_border_top = 0
        plot.x_range.min_interval = 0.0045
        apply_theme(plot, theme, theme_elements_mapping)

        vlines.append(vline)
        vspans.append(vspan)
        glyphs.append(glyph)

    for channel, (plot, vline, vspan, glyph) in enumerate(
        zip(plots, vlines, vspans, glyphs)
    ):
        is_pbar = channel == len(children) - 1
        is_spec = not is_pbar

        record_ranges_callback = CustomJS(
            args=dict(plot_0=plots[0]),
            code=f"""
plot_0.prev_x_range = {{start: plot_0.x_range.start, end: plot_0.x_range.end}};
plot_0.prev_y_range = {{start: plot_0.y_range.start, end: plot_0.y_range.end}};

plot_0.prev_extra_y_ranges = Object.keys(plot_0.extra_y_ranges).reduce(function(result, key) {{
    result[key] = {{start: plot_0.extra_y_ranges[key].start, end: plot_0.extra_y_ranges[key].end}};
    return result;
}}, {{}});
                """,
        )

        start_follow_callback = CustomJS(
            args=dict(vspan_0=vspans[0], plot_0=plots[0]),
            code=f"""
vspan_0.is_following = true;
vspan_0.line_color = "{follow_color}";
let x = Math.max(Math.min(cb_obj.x, plot_0.x_range.reset_end), plot_0.x_range.reset_start);
vspan_0.ratio = (x-plot_0.x_range.start)/(plot_0.x_range.end-plot_0.x_range.start);
                """,
        )
        stop_follow_callback = CustomJS(
            args=dict(vspan_0=vspans[0]),
            code=f"""
vspan_0.is_following = false;
vspan_0.line_color = "{stay_color}";
                """,
        )
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

        keep_x_range_callback = CustomJS(
            args=dict(plot=plot, plot_0=plots[0]),
            code="""
if (('is_x_fixed' in plot_0) && (plot_0.is_x_fixed)) {
    plot.x_range.start = plot_0.x_fixed_start;
    plot.x_range.end = plot_0.x_fixed_end;
}
            """,
        )

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

        move_time_callback = CustomJS(
            args=dict(vspan_0=vspans[0], plot_0=plots[0]),
            code="""
vspan_0.right = Math.max(Math.min(cb_obj.x, plot_0.x_range.reset_end), plot_0.x_range.reset_start);
            """,
        )
        move_pbar_callback = CustomJS(
            args=dict(vspan_0=vspans[0], plot_0=plots[0]),
            code="""
if (('is_x_fixed' in plot_0) && (plot_0.is_x_fixed)) {
    vspan_0.right = Math.max(Math.min(cb_obj.x, plot_0.x_range.reset_end), plot_0.x_range.reset_start);
}
            """,
        )

        if is_spec:
            glyphs[0].js_link("visible", glyph, "visible")

        vspans[0].js_link("right", glyph.glyph, "x")
        vspans[0].js_link("right", vline, "location")
        vspans[0].js_link("right", vspan, "right")
        vspans[0].js_link("line_color", vline, "line_color")
        vspans[0].js_on_change("right", follow_callback)
        vspans[0].js_on_change("line_color", follow_callback)

        plot.js_on_event("doubletap", start_follow_callback, move_time_callback)
        plot.js_on_event("reset", reset_callback)

        for e in [
            "panstart",
            "panend",
            "wheel",
            "press",
            "pressup",
            "tap",
            "doubletap",
        ]:
            plot.js_on_event(e, set_y_range_callback, set_pbar_x_range_callback)
        for e in [
            "panstart",
            "pan",
            "panend",
            "wheel",
            "press",
            "pressup",
            "rangesupdate",
        ]:
            plot.js_on_event(
                e,
                keep_y_range_callback,
                keep_dump_range_callback,
                keep_x_range_callback,
            )
        for e in ["pan", "rangesupdate", "wheel"]:
            plot.js_on_event(e, stop_follow_callback)

        if is_spec:
            for e in ["tap", "pressup", "doubletap"]:
                plot.js_on_event(e, play_pause_callback)

        if is_pbar:
            for e in [
                "pan",
                "panstart",
                "panend",
                "press",
                "pressup",
                "tap",
            ]:
                plot.js_on_event(e, move_pbar_callback, stop_follow_callback)

        for e in [
            "panstart",
            "pan",
            "panend",
            "wheel",
            "press",
            "pressup",
            "rangesupdate",
        ]:
            plot.js_on_event(e, record_ranges_callback)

    return waloviz_bokeh
