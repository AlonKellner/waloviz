===============
Getting Started
===============

TL;DR
-----


.. code-block:: shell

    pip install waloviz
    ffmpeg --version

|

    If the ``ffmpeg --version`` command fails, try following the installation instructions in the `Explanation section <#explanation>`_

.. notebook:: holoviews ../examples/getting-started.ipynb
    :offset: 1

Try clicking the spectrogram above, it will start playing :)

Explanation
-----------

``waloviz`` was built to be as accessible as possible, whether you're using jupyter, colab, VSCode, JupyterLab or just pure HTML - you'll only need three lines of code.

| First we need to install ``waloviz`` :

.. code-block:: shell

    pip install waloviz

| We also need to make sure that ``ffmpeg`` is installed as a backend for ``torchaudio`` :

.. code-block:: shell

    ffmpeg --version

| If this command fails, try installing ``ffmpeg`` in one of the following ways:

.. tabs::

    .. group-tab:: conda (all platforms)

        .. code-block:: shell

            conda install -c conda-forge 'ffmpeg<7'

    .. group-tab:: brew (macos)

        .. code-block:: shell

            brew install 'ffmpeg<7'

    .. group-tab:: apt-get (linux-debian)

        .. code-block:: shell

            apt-get install 'ffmpeg<7'

|

    If none of the ``ffmpeg`` installation options worked for you, follow `this Hostinger Tutorial <https://www.hostinger.com/tutorials/how-to-install-ffmpeg`_, make sure to install a version lower than 7.

| After ``ffmpeg`` is verified to be installed properly, we move on to python!
| All we need to do is import ``waloviz`` and activate the extension:

.. tabs::

    .. group-tab:: jupyter

        .. code-block:: python

            import waloviz as wv
            wv.extension()

    .. group-tab:: colab

        .. code-block:: python

            import waloviz as wv
            wv.extension("colab")

    .. group-tab:: VSCode

        .. code-block:: python

            import waloviz as wv
            wv.extension()

    .. group-tab:: JupyterLab

        .. code-block:: python

            import waloviz as wv
            wv.extension()

    .. group-tab:: Pure HTML

        .. code-block:: python

            import waloviz as wv
            # no need for the extension with pure HTML


| Then we need to call ``wv.Audio`` with our URL or file-path:

.. tabs::

    .. group-tab:: jupyter

        .. code-block:: python

            wv.Audio('https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav')

    .. group-tab:: colab

        .. code-block:: python

            wv.Audio('https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav')

    .. group-tab:: VSCode

        .. code-block:: python

            wv.Audio('https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav')

    .. group-tab:: JupyterLab

        .. code-block:: python

            wv.Audio('https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav')

    .. group-tab:: Pure HTML

        .. code-block:: python

            wv.save('https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav') # saves to ``waloviz.html`` by default

| And... that's it, you're done.
| You can use the player to interact with your audio.

Using the player
----------------

| The controls are pretty intuitive, but here are the most important controls you should to know:

1. A single click on the spectrogram - toggles play\\pause
2. Clicking on the bottom progress - moves the current time
3. Scrolling with the mouse wheel - zooms in\\out
4. Dragging the mouse while pressing down - moves forwards\\backwards
5. The small ↺ icon on the top left toolbar - resets to the initial view
6. Clicking on the ``Download waloviz.html`` - downloads an HTML version of the player

What's up with that ``wv.extension()``?
---------------------------------------

| The ``panel`` and ``holoviews`` libraries are used extensively in WaloViz.
| Those among you which use either of them know that the ``wv.extension()`` is actually an imitation of the ``pn.extension()`` and ``hv.extension()`` functions, and by no coincidence.
|
| But what exactly happens in ``wv.extension()`` in terms of ``panel`` and ``holoviews``?
| Well, ``wv.extension()`` contains just these two lines of code:

.. code-block:: python

        hv.extension("bokeh")
        pn.extension(comms="default")

| So it's more of an easy shorthand than an actual thing of its own.
| Be aware that this is the only setup in which WaloViz currently works, if you call ``hv.extension("plotly")`` just before a ``wv.Audio(...)`` call is made - WaloViz won't work.

| To learn more, read our `User Guide <./user-guide/index.html>`_.
