"""
``waloviz`` , an interactive spectrogram player, for audio experts - by audio experts.

.. code-block:: python

    import waloviz as wv

    wv.extension()
    wv.Audio("local_data/waloviz.wav")

Read our `Documentation <https://waloviz.com/en/latest/>`_ for more information.
You can also try `waloviz` right now with our `Google Colab Demo <https://colab.research.google.com/drive/1euQCxaNlTg0pGvXz6d7RSoDhM3B1k7dy?usp=sharing>`_ :)
"""

from ._user_functions import Audio, extension, save
from ._version import __version__, __version_tuple__, version, version_tuple

__all__ = [
    "Audio",
    "save",
    "extension",
    "__version__",
    "version",
    "__version_tuple__",
    "version_tuple",
]
