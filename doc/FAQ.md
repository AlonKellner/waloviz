# FAQ
* **Q:** I got an error: `RuntimeError: Couldn't find appropriate backend to handle uri my.wav and format None.` Why?<details>
  <summary><b>A:</b></summary>

    WaloViz uses `torchaudio` to load audio files, and `torchaudio` itself uses a beckend to load them, the recommended backend is `ffmpeg`, so just make sure you've installed it:
    ```shell
    apt-get install ffmpeg
    ```
</details>

* **Q:** How can I help WaloViz?<details>
  <summary><b>A:</b></summary>

    Consider giving us a star on [our github repository](https://github.com/AlonKellner/waloviz)!  
    If you've had any issue open a [Github Issue](https://github.com/AlonKellner/waloviz/issues/new) and tell us about it, we'll do our best to help :)  
    Also, you can contribute! Read our [Contributing Guide](https://github.com/AlonKellner/waloviz/blob/main/CONTRIBUTING.md) and take a shot at one of our [good first issues](https://github.com/AlonKellner/waloviz/issues?q=is%3Aissue+is%3Aopen+%3Agood-first-issue)!
</details>