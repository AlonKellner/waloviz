from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch

# A type for the overlaid curves, this comes up multiple times
OverCurve = Union[
    List[Any], Dict[str, Any], np.ndarray, torch.Tensor, Tuple[Any, Any], Any
]


def to_tensor(
    obj: Any,
) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor], Tuple]:
    """
    | Given a hierarchical object recursively converts all leaf nodes into PyTorch tensors.

    Parameters
    ----------
    ``obj`` : Any
        A hierarchical tuple object

    Returns
    -------
    ``obj`` : torch.Tensor
        A hierarchical tuple tensor object

    |
    """
    if isinstance(obj, Tuple):
        return tuple([to_tensor(sub) for sub in obj])

    if not torch.is_tensor(obj):
        obj = torch.tensor(obj)
    return obj


def broadcast_to_channels(
    tensor: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]], channels: int
) -> Union[torch.Tensor, Tuple]:
    """
    | Given a hierarchical tensor object recursively broadcast all leaf tensors to have exactly 2 dimensions and the same amount of channels as the ``wav`` .

    Parameters
    ----------
    ``tensor`` : torch.Tensor | (torch.Tensor, torch.Tensor)
        A hierarchical tensor object with varying amounts of channels

    Returns
    -------
    ``obj`` : torch.Tensor
        A hierarchical tensor object with the same amount of channels

    Raises
    ------
    ``ValueError``
        | When a leaf tensor has 0 non squeezable dimensions
        | **OR**
        | When the initial amount of channels of a leaf tensor was larger than the target amount

    |
    """
    if isinstance(tensor, Tuple):
        return tuple([broadcast_to_channels(sub, channels) for sub in tensor])

    tensor = tensor.squeeze()
    if len(tensor.shape) == 0:
        raise ValueError("tensor must have at least one non squeezable dimension")
    if len(tensor.shape) == 1:
        tensor = tensor[None, ...]
    if tensor.shape[0] > channels:
        raise ValueError("tensor was larger than the amount of channels")

    while tensor.shape[0] < channels:
        tensor = torch.cat([tensor, tensor], dim=0)
    if tensor.shape[0] > channels:
        tensor = tensor[:channels, ...]

    return tensor


def skip_to_size(
    tensor: Union[torch.Tensor, Tuple], max_size: int
) -> Union[torch.Tensor, Tuple]:
    """
    | Given a hierarchical tensor object skip equally spaced tensor values along the time dimension ( ``dim=-1`` ) to become lower than the ``max_size`` value.

    | This helps with the responsiveness of the player and avoids errors at the
    | cost of losing information.
    | This is used for both the overlaid curves and the spectrogram itself.

    Parameters
    ----------
    ``tensor`` : torch.Tensor | (torch.Tensor, torch.Tensor)
        A hierarchical tensor object with an unknown time size
    ``max_size`` : int
        The maximum allowed time dimension size

    Returns
    -------
    ``obj`` : torch.Tensor
        A hierarchical tensor object with a time size lower than ``max_size``

    |
    """
    if isinstance(tensor, Tuple):
        return tuple([skip_to_size(sub, max_size) for sub in tensor])

    if tensor.shape[-1] > max_size:
        tensor = tensor[..., :: (tensor.shape[-1] // max_size) + 1]
    return tensor


def preprocess_over_curve(
    wav: torch.Tensor,
    sr: int,
    channels: int,
    over_curve: Optional[OverCurve],
    over_curve_names: Optional[Union[str, List[str]]] = None,
    over_curve_colors: Optional[Union[str, List[Optional[str]], Dict[str, str]]] = None,
    over_curve_axes: Optional[
        Union[str, List[Optional[str]], List[str], Dict[str, str]]
    ] = None,
) -> Tuple[
    Optional[List[torch.Tensor]],
    Optional[List[str]],
    Optional[List[Optional[str]]],
    Optional[List[str]],
]:
    """
    | Converts user defined overlaid curves related options into a standard format, in terms of object structure and types.

    Parameters
    ----------
    ``wav`` : torch.Tensor
        Loaded audio tensor
    ``sr`` : int
        Resolved sample-rate
    ``channels`` : int
        The amount of channels in ``wav``
    ``over_curve`` : tensorlike | List[tensorlike] | Dict[str, tensorlike] | callable
        User provided
    ``over_curve_names`` : List[str]
        User provided
    ``over_curve_colors`` : List[str]
        User provided
    ``over_curve_axes`` : List[str]
        User provided

    Returns
    -------
    ``over_curve`` : List[torch.Tensor]
        Standardized
    ``over_curve_names`` : List[str]
        Standardized
    ``over_curve_colors`` : List[str]
        Standardized
    ``over_curve_axes`` : List[str]
        User provided

    Raises
    ------
    ``ValueError``
        | When ``over_curve_names`` was provided but of a different size from ``over_curve``
        | **OR**
        | When ``over_curve_colors`` was provided but of a different size from ``over_curve``
        | **OR**
        | When ``over_curve_axes`` was provided but of a different size from ``over_curve``
        | **OR**
        | When ``over_curve_colors`` was a dict but ``over_curve_names`` was not provided
        | **OR**
        | When ``over_curve_axes`` was a dict but ``over_curve_names`` was not provided
        | **OR**
        | When ``over_curve_names`` was provided but ``over_curve`` was a dict
        | **OR**
        | When ``over_curve`` contained an ``(X,Y)`` tuple of size not equal to 2
        | **OR**
        | When ``over_curve`` contained an ``(X,Y)`` tuple where ``X.shape != Y.shape``

    |
    """
    over_curve, over_curve_names, over_curve_colors, over_curve_axes = (
        single_value_to_list(
            over_curve, over_curve_names, over_curve_colors, over_curve_axes
        )
    )

    if over_curve is None:
        return None, None, None, None

    if isinstance(over_curve, List):
        over_curve_names = handle_list_over_curve(
            over_curve, over_curve_names, over_curve_colors, over_curve_axes
        )

    if isinstance(over_curve, Dict):
        over_curve, over_curve_names = handle_dict_over_curve(
            over_curve, over_curve_names
        )

    if isinstance(over_curve_colors, Dict):
        over_curve_colors = handle_dict_colors(over_curve_names, over_curve_colors)

    if isinstance(over_curve_axes, Dict):
        over_curve_axes = handle_dict_axes(over_curve_names, over_curve_axes)

    over_curve_axes_list: Optional[List[str]] = None
    if over_curve_axes is not None:
        over_curve_axes_list = [
            ("y" if axis is None else axis) for axis in over_curve_axes
        ]

    over_curve = [
        (sub_curve(wav, sr) if callable(sub_curve) else sub_curve)
        for sub_curve in over_curve
    ]

    over_curve = [
        broadcast_to_channels(to_tensor(sub_curve), channels)
        for sub_curve in over_curve
    ]

    validate_XY_over_curve(over_curve)

    return over_curve, over_curve_names, over_curve_colors, over_curve_axes_list


def validate_XY_over_curve(over_curve: OverCurve) -> None:
    """
    | If the ``over_curve`` has X and Y tensors, make sure their of the same shape.

    Parameters
    ----------
    ``over_curve`` : List[torch.Tensor | (torch.Tensor, torch.Tensor)]
        Either a list of tensors or ``(X,Y)`` tuples of tensors

    Raises
    ------
    ``ValueError``
        | When ``over_curve`` contained an ``(X,Y)`` tuple of size not equal to 2
        | **OR**
        | When ``over_curve`` contained an ``(X,Y)`` tuple where ``X.shape != Y.shape``

    |
    """
    for sub_curve in over_curve:
        # TODO: The (X, Y) feature of the ``over_curve`` is not well documented, see https://github.com/AlonKellner/waloviz/issues/6
        if isinstance(sub_curve, Tuple):
            if len(sub_curve) != 2:
                raise ValueError(
                    "When ``over_curve`` contains a tuple it must be of length 2 as such: ``(x_coordinates, y_coordinates)``"
                )
            sub_x, sub_y = sub_curve
            if sub_x.shape != sub_y.shape:
                raise ValueError(
                    f"Found a mismatch between ``over_curve`` x and y coordinates lengths:\t{sub_x.shape[-1]} != {sub_y.shape[-1]}"
                )


def handle_dict_colors(
    over_curve_names: Optional[List[str]], over_curve_colors: Dict[str, str]
) -> List[Optional[str]]:
    """
    | Handles the case where ``over_curve_colors`` is a dict and converts it to a list.

    Parameters
    ----------
    ``over_curve_names`` : List[str] | None
        .
    ``over_curve_colors`` : Dict[str, str]
        .

    Returns
    -------
    ``over_curve_colors`` : List[str | None]
        .

    Raises
    ------
    ``ValueError``
        | When ``over_curve_colors`` was a dict but ``over_curve_names`` was not provided

    |
    """
    if over_curve_names is None:
        raise ValueError(
            "``over_curve_colors`` was a dict but ``over_curve_names`` was not provided"
        )
    list_over_curve_colors: List[Optional[str]] = [
        (over_curve_colors[name] if name in over_curve_colors else None)
        for name in over_curve_names
    ]

    return list_over_curve_colors


def handle_dict_axes(
    over_curve_names: Optional[List[str]], over_curve_axes: Dict[str, str]
) -> List[Optional[str]]:
    """
    | Handles the case where ``over_curve_axes`` is a dict and converts it to a list.

    Parameters
    ----------
    ``over_curve_names`` : List[str] | None
        .
    ``over_curve_axes`` : Dict[str, str]
        .

    Returns
    -------
    ``over_curve_axes`` : List[str | None]
        .

    Raises
    ------
    ``ValueError``
        | When ``over_curve_axes`` was a dict but ``over_curve_names`` was not provided

    |
    """
    if over_curve_names is None:
        raise ValueError(
            "``over_curve_axes`` was a dict but ``over_curve_names`` was not provided"
        )
    list_over_curve_axes: List[Optional[str]] = [
        (over_curve_axes[name] if name in over_curve_axes else None)
        for name in over_curve_names
    ]

    return list_over_curve_axes


def handle_dict_over_curve(
    over_curve: Dict[str, Any], over_curve_names: Optional[List[str]]
) -> Tuple[List[Any], List[str]]:
    """
    | Handles the case where ``over_curve`` is a dict and converts it to a list.

    Parameters
    ----------
    ``over_curve`` : Dict[str, Any]
        .
    ``over_curve_names`` : List[str] | None
        .

    Returns
    -------
    ``over_curve`` : List[Any]
        .
    ``over_curve_names`` : List[str]
        .

    Raises
    ------
    ``ValueError``
        | When ``over_curve_names`` was provided but ``over_curve`` was a dict

    |
    """
    if over_curve_names is not None:
        raise ValueError(
            "``over_curve_names`` can be set only when ``over_curve`` is not a dict"
        )
    over_curve_names = [name for name, _ in over_curve.items()]
    list_over_curve: List[Any] = [sub_curve for _, sub_curve in over_curve.items()]
    return list_over_curve, over_curve_names


def handle_list_over_curve(
    over_curve: List[Any],
    over_curve_names: Optional[List[str]],
    over_curve_colors: Optional[Union[List[Optional[str]], Dict[str, str]]],
    over_curve_axes: Optional[Union[List[Optional[str]], List[str], Dict[str, str]]],
) -> Optional[List[str]]:
    """
    | Handles the case where ``over_curve`` is a list, makes a bunch of validations and generates ``over_curve_names`` if None were provided.

    Parameters
    ----------
    ``over_curve`` : Dict[str, Any]
        .
    ``over_curve_names`` : List[str] | None
        .
    ``over_curve_colors`` : List[str] | None
        .
    ``over_curve_axes`` : List[str] | None
        .

    Returns
    -------
    ``over_curve_names`` : List[str]
        .

    Raises
    ------
    ``ValueError``
        | When ``over_curve_names`` was provided but of a different size from ``over_curve``
        | **OR**
        | When ``over_curve_colors`` was provided but of a different size from ``over_curve``
        | **OR**
        | When ``over_curve_axes`` was provided but of a different size from ``over_curve``

    |
    """
    if over_curve_names is None:
        over_curve_names = [str(i) for i in range(len(over_curve))]
    elif len(over_curve_names) != len(over_curve):
        raise ValueError(
            f"Size of ``over_curve_names`` was different than ``over_curve`` but should be equal, {len(over_curve_names)} != {len(over_curve)}"
        )

    if over_curve_colors is not None:
        if len(over_curve_colors) != len(over_curve):
            raise ValueError(
                f"Size of ``over_curve_colors`` was different than ``over_curve`` but should be equal, {len(over_curve_colors)} != {len(over_curve)}"
            )

    if over_curve_axes is not None:
        if len(over_curve_axes) != len(over_curve):
            raise ValueError(
                f"Size of ``over_curve_axes`` was different than ``over_curve`` but should be equal, {len(over_curve_axes)} != {len(over_curve)}"
            )

    return over_curve_names


def single_value_to_list(
    over_curve: Optional[OverCurve],
    over_curve_names: Optional[Union[str, List[str]]] = None,
    over_curve_colors: Optional[Union[str, List[Optional[str]], Dict[str, str]]] = None,
    over_curve_axes: Optional[
        Union[str, List[Optional[str]], List[str], Dict[str, str]]
    ] = None,
) -> Tuple[
    Optional[OverCurve],
    Optional[List[str]],
    Optional[Union[List[Optional[str]], Dict[str, str]]],
    Optional[Union[List[Optional[str]], List[str], Dict[str, str]]],
]:
    """
    | Makes sure that if single values were provided they are wrapped in single element lists.

    Parameters
    ----------
    ``over_curve`` : tensorlike | List[tensorlike] | Dict[str, tensorlike] | callable
        User provided
    ``over_curve_names`` : List[str]
        User provided
    ``over_curve_colors`` : List[str]
        User provided
    ``over_curve_axes`` : List[str]
        User provided

    Returns
    -------
    ``over_curve`` : tensorlike | List[tensorlike] | Dict[str, tensorlike] | callable
        .
    ``over_curve_names`` : List[str]
        .
    ``over_curve_colors`` : List[str]
        .
    ``over_curve_axes`` : List[str]
        .

    |
    """
    if over_curve is None:
        return None, None, None, None

    if isinstance(over_curve_names, str):
        over_curve_names = [over_curve_names]

    if isinstance(over_curve_colors, str):
        over_curve_colors = [over_curve_colors]

    if isinstance(over_curve_axes, str):
        over_curve_axes = [over_curve_axes]

    if not isinstance(over_curve, (List, Dict)):
        if (hasattr(over_curve, "shape") and len(over_curve.shape) == 1) or (  # pyright: ignore[reportAttributeAccessIssue]
            isinstance(over_curve, Tuple)
            and len(over_curve) == 2
            or callable(over_curve)
        ):
            over_curve = [over_curve]
        else:
            over_curve = [sub_curve for sub_curve in over_curve]
    return over_curve, over_curve_names, over_curve_colors, over_curve_axes
