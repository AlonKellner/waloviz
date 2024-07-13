===
FAQ
===

* **Q:** I got an error: ``RuntimeError: Couldn't find appropriate backend to handle uri my.wav and format None.`` Why?

  .. collapse:: A:

      | WaloViz uses ``torchaudio`` to load audio files, and ``torchaudio`` itself uses a backend to load them, the recommended backend is ``ffmpeg`` , so just make sure you've installed it:

      .. code-block:: shell

        apt-get install ffmpeg

* **Q:** How can I help WaloViz?

  .. collapse:: A:

    | Consider giving us a star on `our github repository <https://github.com/AlonKellner/waloviz>`_ :star2:
    | If you've had any issue open a `Github Issue <https://github.com/AlonKellner/waloviz/issues/new>`_ and tell us about it, we'll do our best to help :)
    | Also, you can contribute! Read our `Contributing Guide <https://github.com/AlonKellner/waloviz/blob/main/CONTRIBUTING.md>`_ and take a shot at one of our `Good First Issues <https://github.com/AlonKellner/waloviz/issues?q=is%3Aissue+is%3Aopen+%3Agood-first-issue>`_!
