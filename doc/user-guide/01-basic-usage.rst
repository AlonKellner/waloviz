===========
Basic Usage
===========

.. notebook:: holoviews ../../examples/user-guide/01-basic-usage.ipynb
    :offset: 1

The ``extension`` function
--------------------------

| It allows to prepare the visualization libraries and settings for your favorite notebook editor:

.. tabs::

    .. group-tab:: Almost all editors

        .. code-block:: python

            wv.extension()

    .. group-tab:: colab

        .. code-block:: python

            wv.extension("colab")

| Calling ``extension`` lets WaloViz know that you are about to use it in a notebook, you to do it just once.
| Don't think about it too much, that's how many libraries operate (such as ``holoviews`` or ``panel`` ), and it works!
