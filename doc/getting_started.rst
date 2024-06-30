===============
Getting Started
===============

.. notebook:: holoviews ../examples/getting-started.ipynb
    :offset: 1

Explanation
-----------

``waloviz`` was built to be as accessible as possible, whether you're using jupyter, colab, VSCode, JupyterLab or just pure HTML - you'll only need three lines of code.  

First we need to install ``waloviz``:

.. code-block:: shell 
    
    pip install waloviz
    
We also need to install ``ffmpeg`` as a backend for ``torchaudio``:

.. code-block:: shell 
    
    apt-get install ffmpeg

Then we need to import ``waloviz`` and activate the extension:  

.. tab:: jupyter

    .. code-block:: python

        import waloviz as wv
        wv.extension()

.. tab:: colab

    .. code-block:: python

        import waloviz as wv
        wv.extension("colab")

.. tab:: VSCode

    .. code-block:: python

        import waloviz as wv
        wv.extension()

.. tab:: JupyterLab

    .. code-block:: python

        import waloviz as wv
        wv.extension()
        
.. tab:: Pure HTML

    .. code-block:: python

        import waloviz as wv


Then we need to call ``wv.Audio`` with our URL or file-path:

.. tab:: jupyter

    .. code-block:: python

        wv.Audio('https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav')

.. tab:: colab

    .. code-block:: python

        wv.Audio('https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav')

.. tab:: VSCode

    .. code-block:: python

        wv.Audio('https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav')

.. tab:: JupyterLab

    .. code-block:: python

        wv.Audio('https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav')
        
.. tab:: Pure HTML

    .. code-block:: python

        wv.save('https://www2.cs.uic.edu/~i101/SoundFiles/CantinaBand3.wav') # saves to `waloviz.html` by default

And... that's it, you're done.  
You can use the player to interact with your audio.  

Using the player
----------------

The controls are pretty intuitive, but here are the most important controls you should to know:  
1. A single click anywhere - toggles play\\pause.
2. Scrolling with the mouse wheel - zooms in\\out.
3. Dragging the mouse while pressing down - moves forwards\\backwards.
4. The small ↺ icon on the top left - resets to the initial view.
5. Clicking on the ``Download waloviz.html`` - will download an HTML version of the player.

To learn more, read our `User Guide <./user_guide.md>`_.