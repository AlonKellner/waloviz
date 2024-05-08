from typing import Any, Dict, List, Optional, Tuple, Union

import numpy as np
import torch

OverCurve = Union[
    List[Any], Dict[str, Any], np.ndarray, torch.Tensor, Tuple[Any, Any], Any
]


def to_tensor(obj: Any) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
    if isinstance(obj, Tuple):
        return tuple([to_tensor(sub) for sub in obj])

    if not torch.is_tensor(obj):
        obj = torch.tensor(obj)
    return obj


def broadcast_to_channels(
    tensor: Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]], channels: int
) -> Union[torch.Tensor, Tuple]:
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
    if isinstance(tensor, Tuple):
        return tuple([skip_to_size(sub, max_size) for sub in tensor])

    if tensor.shape[-1] > max_size:
        tensor = tensor[..., :: (tensor.shape[-1] // max_size) + 1]
    return tensor


def preprocess_over_curve(
    channels: int,
    over_curve: Optional[OverCurve],
    over_curve_names: Optional[Union[str, List[str]]] = None,
    over_curve_colors: Optional[Union[str, List[str]]] = None,
) -> Tuple[List[torch.Tensor], List[str]]:
    if over_curve is None:
        return None, None, None

    if isinstance(over_curve_names, str):
        over_curve_names = [over_curve_names]

    if isinstance(over_curve_colors, str):
        over_curve_colors = [over_curve_colors]

    if not isinstance(over_curve, (List, Dict)):
        if (hasattr(over_curve, "shape") and len(over_curve.shape) == 1) or (
            isinstance(over_curve, Tuple) and len(over_curve) == 2
        ):
            over_curve = [over_curve]
        else:
            over_curve = [sub_curve for sub_curve in over_curve]

    if isinstance(over_curve, List):
        if over_curve_names is None:
            over_curve_names = list(range(len(over_curve)))
        elif len(over_curve_names) != len(over_curve):
            raise ValueError(
                f"Size of `over_curve_names` was different than `over_curve` but should be equal, {len(over_curve_names)} != {len(over_curve)}"
            )

        if over_curve_colors is not None and len(over_curve_colors) != len(over_curve):
            raise ValueError(
                f"Size of `over_curve_colors` was different than `over_curve` but should be equal, {len(over_curve_colors)} != {len(over_curve)}"
            )

    if isinstance(over_curve, Dict):
        if over_curve_names is not None:
            raise ValueError(
                "`over_curve_names` can be set only when `over_curve` is not a dict."
            )
        over_curve = over_curve.items()
        over_curve_names = [name for name, sub_curve in over_curve]
        over_curve = [sub_curve for name, sub_curve in over_curve]

    if isinstance(over_curve_colors, Dict):
        over_curve_colors = [
            (over_curve_colors[name] if name in over_curve_colors else None)
            for name in over_curve_names
        ]

    over_curve = [
        broadcast_to_channels(to_tensor(sub_curve), channels)
        for sub_curve in over_curve
    ]

    for sub_curve in over_curve:
        if isinstance(sub_curve, Tuple):
            if len(sub_curve) != 2:
                raise ValueError(
                    "When `over_curve` contains a tuple it must be of length 2 as such: `(x_coordinates, y_coordinates)`"
                )
            sub_x, sub_y = sub_curve
            if sub_x.shape != sub_y.shape:
                raise ValueError(
                    f"Found a mismatch between `over_curve` x and y coordinates lengths:\t{sub_x.shape[-1]} != {sub_y.shape[-1]}"
                )

    return over_curve, over_curve_names, over_curve_colors
