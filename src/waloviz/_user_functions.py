import os
from io import IOBase
from typing import IO, Any, BinaryIO, Dict, List, Optional, Tuple, Union

import holoviews as hv
import numpy as np
import panel as pn
import torch
import torchaudio
import torchaudio.transforms as T
from bokeh.resources import INLINE, Resources

from ._bokeh_manipulation import finalize_player_bokeh_gui, themes
from ._holoviews_manipulations import ThemeHook, get_player_hv
from ._panel_manipulation import IOLike, save_player_panel, wrap_player_with_panel
from ._tensor_utils import OverCurve, preprocess_over_curve, to_tensor

FileLike = Union[str, os.PathLike, BinaryIO]
AudioSource = Union[
    FileLike,
    Union[np.ndarray, torch.Tensor, Any],
    Tuple[Union[np.ndarray, torch.Tensor, Any], int],
]

# The mode is set with the ``extension`` function, the mode can be either "default" or "colab".
# If the mode is "colab" the ``extension`` will be loaded in every cell, see https://github.com/holoviz/holoviews/issues/3551
# Otherwise the mode does nothing.
_mode = "default"


def extension(mode: str = "default") -> None:
    """
    | Initializes the notebook extensions for the current IDE.

    Examples
    --------

    .. code-block:: python

            import wavloviz as wv
            wv.extension()
            wv.Audio('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3')

    Parameters
    ----------
    ``mode`` : str
        Sets the mode of WaloViz, currently the only active mode is "colab".
        Default is "default"

    |
    """
    global _mode  # noqa: PLW0603  # ``_mode`` specifically needs to be global because it is the only stateful feature for the whole package
    _mode = mode

    # WaloViz is built exclusively with bokeh, this will not likely to change in the foreseeable future.
    hv.extension("bokeh")  # pyright: ignore[reportCallIssue]

    # When the ``comms`` are auto-detected (in colab for example) it doesn't work, ``comms="default"`` works on all platforms, not sure why
    pn.extension(comms="default")


def Audio(
    source: AudioSource,
    over_curve: Optional[OverCurve] = None,
    *args: Tuple,
    over_curve_names: Optional[Union[str, List[str]]] = None,
    sr: Optional[int] = None,
    frame_ms: Optional[int] = None,
    n_fft: Optional[int] = None,
    hop_ms: Optional[int] = None,
    hop_length: Optional[int] = None,
    title: Optional[str] = "waloviz",
    embed_title: bool = False,
    height: Union[int, str] = "responsive",
    width: Union[int, str] = "responsive",
    aspect_ratio: Optional[float] = None,
    sizing_mode: Optional[str] = None,
    sync_legends: bool = False,
    colorbar: bool = False,
    cmap: str = "Inferno",
    over_curve_colors: Optional[Union[str, List[Optional[str]], Dict[str, str]]] = None,
    theme: Union[str, Dict[str, Any]] = "dark_minimal",
    max_size: int = 10000,
    download_button: bool = True,
    freq_label: Optional[str] = "Hz",
    native_player: bool = False,
    minimal: bool = False,
    extended: bool = False,
) -> pn.viewable.Viewable:
    r"""
    | Create an interactive audio player with a spectrogram.

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
    ``source`` : str | os.PathLike | IO | (tensorlike, int) | tensorlike
        Either an audio file, or an audio tensor\\ndarray with a sample rate
    ``over_curve`` : tensorlike | List[tensorlike] | Dict[str, tensorlike] | callable
        A single or multiple curves to be displayed over the spectrogram
    ``over_curve_names`` : str | List[str]
        A list of display names corresponding to the list given in ``over_curve``
    ``sr`` : int
        The sample rate, when the source does not contain a sample rate,
        the given ``sr`` value is assumed to be the source sample rate, when
        this value is different than the source sample rate, the source
        audio is resampled to the specified ``sr`` value.
    ``frame_ms`` : float
        Sets the spectrogram frame length to the given amount of milliseconds,
        default is 100.0.
    ``n_fft`` : int
        Sets the ``n_fft`` of the spectrogram, overrides the ``frame_ms`` value,
        default is ``(sr/1000 * frame_ms)`` .
    ``hop_ms`` : float
        Sets the ``hop_length`` of the spectrogram, in milliseconds.
    ``hop_length`` : int
        Sets the ``hop_length`` of the spectrogram, default is ``n_fft/8``
    ``title`` : str
        A title to be used when saving the plot. If ``embed_title`` is True,
        the ``title`` value will be displayed as part of the plot itself.
        Default is "waloviz".
    ``embed_title`` : bool
        When True, the ``title`` value will be displayed as part of the plot
        itself, default is False.
    ``height`` : int | str
        The total height of the plot, default is "responsive", which means
        the plot will stretch in height to fit.
    ``width`` : int | str
        The total width of the plot, default is "responsive", which means
        the plot will stretch in width to fit.
    ``aspect_ratio`` : float
        The ratio between the width and height, relevant only when either
        width, height or both are "responsive", default is 3.5.
    ``sizing_mode`` : str
        The panel ``sizing_mode`` , can be one of seven values:
        "stretch_width", "stretch_height", "stretch_both",
        "scale_width", "scale_height", "scale_both", or "fixed".
        Default is "scale_both".
    ``sync_legends`` : bool
        Whether the legends of both audio channels over curves should be
        synchronized, default is False
    ``colorbar`` : bool
        Whether to display a colorbar for the spectrograms, default is False
    ``cmap`` : str
        The colormap used to display the spectrogram, default is "Inferno"
    ``over_curve_colors`` : str | List[str] | Dict[str, str]
        Sets the colors to display for each given ``over_curve`` , should match
        the size and structure of the given ``over_curve`` value.
    ``theme`` : str | Dict[str, Any]
        Sets the visual look and feel of the plot, the value provided must
        be a ``bokeh`` theme, default is "dark_minimal".
    ``max_size`` : int
        When the spectrogram or one of the over curves contain many values,
        the plot's performance suffers. For that reason ``max_size`` limits the
        amount of displayed values, when the spectrogram or an over curve has
        more values than the ``max_size`` , it is reduced in size by skipping
        intermediate values, until the size is less than the ``max_size`` .
        Default is 10000.
    ``download_button`` : bool
        Whether to show the html download button. Defaults to True.
    ``freq_label`` : str
        The label of the frequency axis (vertical), hides the label when set
        to None which saves space.
    ``native_player`` : bool
        Whether the underlying native audio player should be visible. Default
        is False
    ``minimal`` : bool
        Does nothing when False, when True it overrides some settings to make
        the player more compact and simple. Default is False.
    ``extended`` : bool
        Does nothing when False, when True it overrides some settings to make
        the player more descriptive and functional. Default is False.

    Returns
    -------
    ``player`` : pn.viewable.Viewable
        An interactive player, can be saved to html with ``wv.save(player)``

    Raises
    ------
    ``ValueError``
        | When both ``minimal=True`` and ``extended=True``
        | **OR**
        | When no sample-rate was provided
        | **OR**
        | When the ``wav`` tensor had more than 2 non squeezable dimensions
        | **OR**
        | When the ``theme`` string value was not found in Bokeh
        | **OR**
        | When there are more than 2 positional ``args``
        | **OR**
        | When the provided ``over_curve`` was an integer

    |
    """
    # These are configurable values which are not useful for users, but for developers
    single_min_height: int = 80  # The minimum height of a single spectrogram, value is 80 based on manual testing, below it the ticks text starts to overlap
    both_min_height: int = 150  # The minimum height of all spectrogram channels together, regardless of amount, value is 150, below it the Bokeh toolbar starts to hide tools
    pbar_height: int = 40  # The total height of the progress bar including the axis itself, value is 40 = 10 for the bar itself + 30 for the axis
    stay_color: str = "#ffffff88"  # A half transparent white when playing normally
    follow_color: str = "#ff0000dd"  # A slightly transparent bright red when following

    sizing_mode, width, height, aspect_ratio = _resolve_sizing_args(
        sizing_mode, width, height, aspect_ratio
    )
    title, embed_title, colorbar, download_button, freq_label, native_player = (
        _resolve_presets(
            minimal,
            extended,
            title,
            embed_title,
            colorbar,
            download_button,
            freq_label,
            native_player,
        )
    )

    button_height: int = _resolve_button_height(download_button)
    audio_height: int = _resolve_audio_height(native_player)

    _validate_over_curve(over_curve)
    _validate_max_args(args)

    theme, theme_hook = _create_theme_hook(theme)

    wav, sr = _load_audio(source, sr)
    channels = len(wav)
    total_seconds = wav.shape[-1] / sr

    if _mode == "colab":
        extension(_mode)

    n_fft, hop_length = _resolve_spectrogram_resolution(
        sr, frame_ms, n_fft, hop_ms, hop_length
    )

    single_min_height, both_min_height = _resolve_min_spectrogram_heights(
        single_min_height, both_min_height, channels
    )

    over_curve, over_curve_names, over_curve_colors = preprocess_over_curve(
        wav, sr, channels, over_curve, over_curve_names, over_curve_colors
    )

    player_hv = get_player_hv(
        wav=wav,
        sr=sr,
        total_seconds=total_seconds,
        over_curve=over_curve,
        over_curve_names=over_curve_names,
        n_fft=n_fft,
        hop_length=hop_length,
        sync_legends=sync_legends,
        pbar_height=pbar_height,
        theme_hook=theme_hook,
        max_size=max_size,
        cmap=cmap,
        over_curve_colors=over_curve_colors,
        stay_color=stay_color,
        title=title,
        embed_title=embed_title,
        colorbar=colorbar,
        freq_label=freq_label,
    )
    player_bokeh = hv.render(player_hv)

    player_bokeh = finalize_player_bokeh_gui(
        player_bokeh,
        theme=theme,
        total_seconds=total_seconds,
        stay_color=stay_color,
        follow_color=follow_color,
        aspect_ratio=aspect_ratio,
        sizing_mode=sizing_mode,
        single_min_height=single_min_height,
    )
    player_panel = wrap_player_with_panel(
        player_bokeh,
        wav=wav,
        sr=sr,
        title=title,
        width=width,
        height=height,
        audio_height=audio_height,
        button_height=button_height,
        pbar_height=pbar_height,
        both_min_height=both_min_height,
        download_button=download_button,
        native_player=native_player,
        aspect_ratio=aspect_ratio,
        sizing_mode=sizing_mode,
    )

    return player_panel


def _resolve_presets(
    minimal: bool,
    extended: bool,
    title: Optional[str],
    embed_title: bool,
    colorbar: bool,
    download_button: bool,
    freq_label: Optional[str],
    native_player: bool,
) -> Tuple[Optional[str], bool, bool, bool, Optional[str], bool]:
    """
    | Handles the ``minimal`` and ``extended`` presets.

    Parameters
    ----------
    ``minimal`` : bool
        Whether to use the minimal preset
    ``extended`` : bool
        Whether to use the extended preset
    ``title`` : str
        User provided
    ``embed_title`` : bool
        User provided
    ``colorbar`` : bool
        User provided
    ``download_button`` : bool
        User provided
    ``freq_label`` : str
        User provided
    ``native_player`` : bool
        User provided

    Returns
    -------
    ``title`` : str
        Resolved by presets
    ``embed_title`` : bool
        Resolved by presets
    ``colorbar`` : bool
        Resolved by presets
    ``download_button`` : bool
        Resolved by presets
    ``freq_label`` : str
        Resolved by presets
    ``native_player`` : bool
        Resolved by presets

    Raises
    ------
    ``ValueError``
        When both ``minimal=True`` and ``extended=True``

    |
    """
    if minimal and extended:
        raise ValueError(
            "``Audio`` cannot be both ``minimal`` and ``extended`` , choose one to keep"
        )

    # TODO: The current logic does not allow the user to override the preset values,
    # see https://github.com/AlonKellner/waloviz/issues/5
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

    return title, embed_title, colorbar, download_button, freq_label, native_player


def _resolve_min_spectrogram_heights(
    single_min_height: int, both_min_height: int, channels: int
) -> Tuple[int, int]:
    """
    | Makes sure that `single_min_height * channels == both_min_height`.

    Parameters
    ----------
    ``single_min_height`` : int
        As configured
    ``both_min_height`` : int
        As configured
    ``channels`` : str
        Calculated from the wav

    Returns
    -------
    ``single_min_height`` : int
        Calculated
    ``both_min_height`` : int
        Calculated

    |
    """
    if both_min_height < single_min_height * channels:
        both_min_height = single_min_height * channels

    if single_min_height < both_min_height // channels:
        single_min_height = both_min_height // channels
    return single_min_height, both_min_height


def _resolve_spectrogram_resolution(
    sr: int,
    frame_ms: Optional[float],
    n_fft: Optional[int],
    hop_ms: Optional[float],
    hop_length: Optional[int],
) -> Tuple[int, int]:
    """
    | Calculates ``n_fft`` and ``hop_length`` while considering ``frame_ms`` and ``hop_ms`` .

    Parameters
    ----------
    ``sr`` : int
        Resolved from ``_load_audio``
    ``frame_ms`` : float
        User provided
    ``n_fft`` : int
        User provided
    ``hop_ms`` : float
        User provided
    ``hop_length`` : int
        User provided

    Returns
    -------
    ``n_fft`` : int
        Calculated
    ``hop_length`` : int
        Calculated

    |
    """
    if (n_fft is None) and (frame_ms is None):
        frame_ms = 100.0

    if n_fft is None:
        if frame_ms is None:
            raise ValueError("``frame_ms`` was set to None without setting ``n_fft``")
        n_fft = int((sr * frame_ms) / 1000)

    if hop_ms is not None:
        hop_length = int((sr * hop_ms) / 1000)

    if hop_length is None:
        hop_length = n_fft // 8
    return n_fft, hop_length


def _load_audio(
    source: AudioSource,
    sr: Optional[int],
) -> Tuple[torch.Tensor, int]:
    """
    | Resolves the ``source`` into a ``wav`` tensor and ``sr`` , loads and resamples using ``torchaudio`` if needed.

    Parameters
    ----------
    ``source`` : str | os.PathLike | IO | (tensorlike, int) | tensorlike
        User provided
    ``sr`` : int
        User provided

    Returns
    -------
    ``wav`` : torch.Tensor
        Loaded and resampled
    ``sr`` : int
        Calculated

    Raises
    ------
    ``ValueError``
        | When no sample-rate was provided
        | **OR**
        | When the ``wav`` tensor had more than 2 non squeezable dimensions

    |
    """
    if torch.is_tensor(source) or isinstance(source, np.ndarray):
        source = source, sr
    if isinstance(source, IOLike):
        source = torchaudio.load(source)

    if not isinstance(source, tuple):
        raise ValueError("The given ``source`` type is not supported")

    source_sr: int
    wav, source_sr = source
    if sr is None:
        target_sr = source_sr
    else:
        target_sr = sr

    if target_sr is None or source_sr is None:
        raise ValueError(
            """A sample rate must be specified but none was provided!
Specify the sample rate in one of the following ways:
    wv.Audio(wav, sr=sample_rate)
    wv.Audio((wav, sample_rate))"""
        )

    wav = to_tensor(wav).squeeze()  # pyright: ignore[reportAttributeAccessIssue]
    if len(wav.shape) == 1:
        wav = wav[None, ...]
    elif len(wav.shape) > 2:
        raise ValueError(
            f"The given ``wav`` value has more than 2 dimensions: {len(wav.shape)}!=2"
        )

    if source_sr != target_sr:
        wav = T.Resample(source_sr, target_sr)(wav)
    sr = target_sr
    return wav, sr


def _create_theme_hook(
    theme: Union[str, Dict[str, Any]],
) -> Tuple[Dict[str, Any], ThemeHook]:
    """
    | Resolves and validates the ``theme`` and creates a ``ThemeHook`` from it.

    Parameters
    ----------
    ``theme`` : str | Dict[str, Any]
        User provided

    Returns
    -------
    ``theme`` : str | Dict[str, Any]
        Resolved and validated
    ``theme_hook`` : ThemeHook
        Created from the ``theme``

    Raises
    ------
    ``ValueError``
        When the ``theme`` string value was not found in Bokeh

    |
    """
    if isinstance(theme, str):
        if theme.lower() not in themes:
            raise ValueError(
                f"``theme`` was a string, but did not match any of the available options: {sorted(themes.keys())}"
            )
        theme = themes[theme.lower()]
    theme_hook = ThemeHook(theme)
    return theme, theme_hook


def _validate_max_args(args: Tuple) -> None:
    """
    | Validates the positional ``args`` , max of 2.

    Parameters
    ----------
    ``args`` : List[Any]
        User provided

    Raises
    ------
    ``ValueError``
        When there are more than 2 positional ``args``

    |
    """
    if len(args) > 0:
        raise ValueError(
            """``wv.Audio`` should be called with at most 2 positional arguments like one of the following ways:
    wv.Audio(source)
    wv.Audio(source, over_curve)"""
        )


def _validate_over_curve(over_curve: Optional[OverCurve]) -> None:
    """
    | Validates that the ``over_curve`` was not mixed up with the ``sr` value.

    Parameters
    ----------
    ``over_curve`` : tensorlike | List[tensorlike] | Dict[str, tensorlike] | callable
        User provided

    Raises
    ------
    ``ValueError``
        When the provided ``over_curve`` was an integer

    |
    """
    if isinstance(over_curve, int):
        raise ValueError(
            """``over_curve`` cannot be an integer! make sure you did not call ``wv.Audio`` like this:
    wv.Audio(wav, sr)
call ``wv.Audio`` in one of the following ways:
    wv.Audio((wav, sr))
    wv.Audio(wav, sr=sr)
    wv.Audio(file_name_or_obj)"""
        )


def _resolve_sizing_args(
    sizing_mode: Optional[str],
    width: Union[int, str],
    height: Union[int, str],
    aspect_ratio: Optional[float],
) -> Tuple[Optional[str], Union[int, str], Union[int, str], Optional[float]]:
    """
    | Resolves the sizing options to behave as expected, mainly with respect to responsiveness.

    Parameters
    ----------
    ``sizing_mode`` : str
        User provided
    ``height`` : int | str
        User provided
    ``width`` : int | str
        User provided
    ``aspect_ratio`` : float
        User provided

    Returns
    -------
    ``sizing_mode`` : str
        Resolved
    ``height`` : int | str
        Resolved
    ``width`` : int | str
        Resolved
    ``aspect_ratio`` : float
        Resolved

    |
    """
    if sizing_mode is None:
        if (width != "responsive") and (height != "responsive"):
            sizing_mode = "fixed"
        elif (width == "responsive") and (height == "responsive"):
            if aspect_ratio is None:
                aspect_ratio = 3.5
            sizing_mode = "scale_both"
        elif (width == "responsive") and (height != "responsive"):
            sizing_mode = "stretch_width"
        elif (width != "responsive") and (height == "responsive"):
            sizing_mode = "stretch_height"
    return sizing_mode, width, height, aspect_ratio


def _resolve_button_height(download_button: bool) -> int:
    """
    | Infers the height that the button will take, whether it will be visible or not, 30 is the default ``panel`` button height.

    Parameters
    ----------
    ``download_button`` : bool
        User provided

    Returns
    -------
    ``button_height`` : int
        Inferred

    |
    """
    return 30 if download_button else 0


def _resolve_audio_height(native_player: bool) -> int:
    """
    | Infers the height that the audio will take, whether it will be visible or not.

    Parameters
    ----------
    ``native_player`` : bool
        User provided

    Returns
    -------
    ``audio_height`` : int
        Inferred

    |
    """
    return 30 if native_player else 0


def save(
    source: Union[pn.viewable.Viewable, AudioSource],
    second_arg: Optional[Union[OverCurve, IOLike]] = None,
    *args: Tuple,
    out_file: Optional[IOLike] = None,
    title: Optional[str] = None,
    resources: Resources = INLINE,
    embed: bool = True,
    **kwargs: Dict[str, Any],
) -> IOLike:
    """
    | Saves a player to an html file.

    Example
    -------

    .. code-block:: python

            import wavloviz as wv
            wv.save('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3')

    Parameters
    ----------
    ``source`` : pn.viewable.Viewable | str | os.PathLike | IO | (tensorlike, int) | tensorlike
        The player created by ``wv.Audio`` , or a source for ``wv.Audio`` to
        create a player with.
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

    Raises
    ------
    ``ValueError``
        When called with more than 2 positional ``args``

    |
    """
    out_file = _resolve_out_file(out_file, second_arg, args, kwargs)

    if not issubclass(type(source), pn.viewable.Viewable):
        if not isinstance(
            source, (IOLike, Union[np.ndarray, torch.Tensor, Any], tuple, int)
        ):
            raise ValueError("The provided ``source`` type is not supported")
        source = Audio(source, *args, **kwargs)  # pyright: ignore[reportArgumentType]
        # TODO: this being a "reportArgumentType" actually looks like a pyright bug, it
        #       assumes that the Dict[str, Any] is assigned when the Any is assigned.
        #       Should open an Issue in their repo, see https://github.com/microsoft/pyright

    return save_player_panel(source, out_file, title, resources, embed)  # pyright: ignore[reportArgumentType]


def _resolve_out_file(
    out_file: Optional[IOLike],
    second_arg: Optional[Union[OverCurve, IOLike]],
    args: Tuple,
    kwargs: Dict[str, Any],
) -> Optional[IOLike]:
    """
    | Resolves the ``out_file``  whether it was given positionally or as a keyword.

    | This is needed to support both ``out_file`` and ``over_curve`` as values for
    | the second positional argument.

    Parameters
    ----------
    ``out_file`` : str | os.PathLike | IO
        User provided
    ``args`` : List[Any]
        User provided
    ``kwargs`` : Dict[str, Any]
        user provided

    Returns
    -------
    ``out_file`` : str | os.PathLike | IO
        Resolved

    Raises
    ------
    ``ValueError``
        When called with more than 2 positional ``args``

    |
    """
    if len(kwargs) > 0:
        raise TypeError(
            f"save() got an unexpected keyword argument '{list(kwargs.keys())[0]}'"
        )
    if (len(args) == 0) and (second_arg is not None):
        if isinstance(second_arg, (str, os.PathLike, IO)) or issubclass(
            type(second_arg), IOBase
        ):
            out_file = second_arg  # pyright: ignore[reportAssignmentType]
    elif len(args) > 0:
        raise ValueError(
            """``wv.save`` should be called with at most 2 positional arguments like one of the following ways:
    wv.save(source)
    wv.save(source, out_file)
    wv.save(source, over_curve)"""
        )

    return out_file
