********************
API Reference Manual
********************

The API reference manual is generated directly from documentation and declarations in the source code, and is thus often much more verbose than necessary.
Still, it often helps to navigate the code when necessary. Use only when you need a deep-dive into the code.

--------

Module Structure
________________

WaloViz subpackages
---------------------
These subpackages should not be used directly, they contain a LOT of internal logic which is not relevant for the average user.

`waloviz`_
 The parent ``waloviz`` module itself.
`\_user_functions`_
 As the name suggests - all of the top-level functionality which is officially available to the user is here.
`\_tensor_utils`_
 Utilities for manipulating tensors, mostly to do with different tensor input formats support.
`\_holoviews_manipulations`_
 Functions to do with ``holoviews`` , they create the elements of the plots.
`\_bokeh_manipulation`_
 Functions to do with ``bokeh`` , they customize the plots interactivity and appearance.
`\_panel_manipulation`_
 Functions to do with ``panel`` , they add the audio and link it to the plot.

.. toctree::
   :maxdepth: 2
   :hidden:

   waloviz <waloviz.__init__>
   _user_functions <waloviz._user_functions>
   _tensor_utils <waloviz._tensor_utils>
   _holoviews_manipulations <waloviz._holoviews_manipulations>
   _bokeh_manipulation <waloviz._bokeh_manipulation>
   _panel_manipulation <waloviz._panel_manipulation>

.. _Getting Started guide: ../getting-started/index.html
.. _User Guide: ../user-guide/index.html


.. _waloviz: waloviz.__init__.html
.. _\_user_functions: waloviz._user_functions.html
.. _\_tensor_utils: waloviz._tensor_utils.html
.. _\_holoviews_manipulations: waloviz._holoviews_manipulations.html
.. _\_bokeh_manipulation: waloviz._bokeh_manipulation.html
.. _\_panel_manipulation: waloviz._panel_manipulation.html
