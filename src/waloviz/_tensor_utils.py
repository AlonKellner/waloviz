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
    | Given a hierarchical tensor object recursively broadcast all leaf tensors to have exactly 2 dimensions and the same amount of channels as the ``wav``.

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
    ``ValueError`` :
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
    | Given a hierarchical tensor object skip equally spaced tensor values along the time dimension (``dim=-1``) to become lower than the ``max_size`` value.

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
) -> Tuple[
    Optional[List[torch.Tensor]], Optional[List[str]], Optional[List[Optional[str]]]
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

    Returns
    -------
    ``over_curve`` : List[torch.Tensor]
        Standardized
    ``over_curve_names`` : List[str]
        Standardized
    ``over_curve_colors`` : List[str]
        Standardized

    Raises
    ------
    ``ValueError`` :
        | When ``over_curve_names`` was provided but of a different size from ``over_curve``
        | **OR**
        | When ``over_curve_colors`` was provided but of a different size from ``over_curve``
        | **OR**
        | When ``over_curve_names`` was provided but ``over_curve`` was a dict
        | **OR**
        | When ``over_curve`` contained an ``(X,Y)`` tuple of size not equal to 2
        | **OR**
        | When ``over_curve`` contained an ``(X,Y)`` tuple where ``X.shape != Y.shape``

    |

    """
    if over_curve is None:
        return None, None, None

    if isinstance(over_curve_names, str):
        over_curve_names = [over_curve_names]

    if isinstance(over_curve_colors, str):
        over_curve_colors = [over_curve_colors]

    if not isinstance(over_curve, (List, Dict)):
        if (hasattr(over_curve, "shape") and len(over_curve.shape) == 1) or (  # pyright: ignore[reportAttributeAccessIssue]
            isinstance(over_curve, Tuple) and len(over_curve) == 2
        ):
            over_curve = [over_curve]
        else:
            over_curve = [sub_curve for sub_curve in over_curve]

    if isinstance(over_curve, List):
        if over_curve_names is None:
            over_curve_names = [str(i) for i in range(len(over_curve))]
        elif len(over_curve_names) != len(over_curve):
            raise ValueError(
                f"Size of ``over_curve_names`` was different than ``over_curve`` but should be equal, {len(over_curve_names)} != {len(over_curve)}"
            )

        if over_curve_colors is not None and len(over_curve_colors) != len(over_curve):
            raise ValueError(
                f"Size of ``over_curve_colors`` was different than ``over_curve`` but should be equal, {len(over_curve_colors)} != {len(over_curve)}"
            )

    if isinstance(over_curve, Dict):
        if over_curve_names is not None:
            raise ValueError(
                "``over_curve_names`` can be set only when ``over_curve`` is not a dict."
            )
        over_curve = over_curve.items()
        over_curve_names = [name for name, _ in over_curve]
        over_curve = [sub_curve for _, sub_curve in over_curve]

    if isinstance(over_curve_colors, Dict):
        if over_curve_names is None:
            raise ValueError(
                "``over_curve_colors`` was a dict but no ``over_curve_names`` were provided"
            )
        over_curve_colors = [
            (over_curve_colors[name] if name in over_curve_colors else None)
            for name in over_curve_names
        ]

    over_curve = [
        (sub_curve(wav, sr) if callable(sub_curve) else sub_curve)
        for sub_curve in over_curve
    ]

    over_curve = [
        broadcast_to_channels(to_tensor(sub_curve), channels)
        for sub_curve in over_curve
    ]

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

    return over_curve, over_curve_names, over_curve_colors
