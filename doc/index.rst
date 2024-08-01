===============
Introduction
===============

.. code-block:: shell

    pip install waloviz
    ffmpeg --version


..

    If the ``ffmpeg --version`` command fails, try following the `Installation Instructions in our Getting Started guide <../getting-started.html#explanation>`_.

.. notebook:: holoviews ../examples/introduction.ipynb
    :offset: 1

**An interactive audio player with a spectrogram built-in, as a Jupyter widget or as HTML.**

| Try clicking the spectrogram above, it will start playing :)
| It will sound like aliens arguing with robots, for a more musical demo go to our `Getting Started <./getting-started.html>`_ guide!

|:star:| `GitHub Repo <https://github.com/AlonKellner/waloviz/>`_ |:star:|, |:arrow_forward:| `Google Colab Demo <https://colab.research.google.com/drive/1euQCxaNlTg0pGvXz6d7RSoDhM3B1k7dy>`_ |:arrow_forward:|, |:bust_in_silhouette:| `Portfolio Project Page <https://alonkellner.com/projects/open-source_2024-07-25_waloviz/>`_ |:bust_in_silhouette:|

| Welcome!
| WaloViz is an open source audio player with a spectrogram built-in, it was built by audio experts - for audio experts.
|
| The name comes from ``WaloViz = wav + HoloViz``, since it supports common audio file formats such as ``wav`` and many others thanks to ``torhcaudio`` and ``ffmpeg`` , and it is interactive thanks to the high customizability of the ``HoloViz`` stack, integrated with ``Bokeh``.
| To learn more about ``HoloViz`` - go to `the HoloViz website <https://holoviz.org/>`_, to learn more about ``Bokeh`` - go to `the Bokeh website <https://bokeh.org/>`_, they're great :)
|
| To start using WaloViz right now - read our `Getting Started <./getting-started.html>`_ guide.
| You can also try ``waloviz`` right now with our `Google Colab Demo <https://colab.research.google.com/drive/1euQCxaNlTg0pGvXz6d7RSoDhM3B1k7dy?usp=sharing>`_ :)
|
| To learn what WaloViz is all about, read |:information_source:| `About Us <./about.html>`_ |:information_source:|

.. toctree::
    :titlesonly:
    :hidden:
    :maxdepth: 2

    Introduction <self>
    Getting Started <getting-started>
    User Guide <user-guide/index>
    API <reference-manual/index>
    Releases <releases>
    FAQ <FAQ>
    About <about>
