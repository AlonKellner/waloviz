<h1><img class="dark-light" src="doc/_static/logo_horizontal.png" style="width: 30%;"></h1>

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Contributor Covenant](https://img.shields.io/badge/Contributor%20Covenant-2.1-4baaaa.svg)](code_of_conduct.md)
[![UI Tests](https://github.com/AlonKellner/waloviz/actions/workflows/ui-tests.yml/badge.svg)](https://github.com/AlonKellner/waloviz/actions/workflows/ui-tests.yml)
[![Docs](https://github.com/AlonKellner/waloviz/actions/workflows/docsite.yml/badge.svg)](https://waloviz.com/en/latest)  
[![PyPi Version](https://img.shields.io/pypi/v/waloviz.svg)](https://pypi.python.org/pypi/waloviz/)
[![All time downloads](https://static.pepy.tech/badge/waloviz)](https://pepy.tech/project/waloviz)
[![Weekly Downloads](https://static.pepy.tech/badge/waloviz/week)](https://pepy.tech/project/waloviz)
[![PyPi Python Versions](https://img.shields.io/pypi/pyversions/waloviz.svg)](https://pypi.python.org/pypi/waloviz/)

[![example snapshot](doc/resources/example_snapshot.png)](https://waloviz.com)
**An open source interactive audio player with a spectrogram built-in, primarily based on [Bokeh](https://bokeh.org/) and the [HoloViz](https://holoviz.org/) stack (`wav+HoloViz=WaloViz`).**

[:globe_with_meridians: WaloViz Website :globe_with_meridians:](https://waloviz.com), [:arrow_forward: Google Colab Demo :arrow_forward:](https://colab.research.google.com/drive/1euQCxaNlTg0pGvXz6d7RSoDhM3B1k7dy), [:bust_in_silhouette: Portfolio Project Page :bust_in_silhouette:](https://alonkellner.com/projects/open-source_2024-07-25_waloviz/)

## Installation

```shell
pip install waloviz
ffmpeg --version
```

> If the `ffmpeg --version` command fails, try following the [Installation Instructions in our Getting Started guide](https://waloviz.com/en/stable/getting-started.html#explanation).

## Quickstart

In a notebook cell:

```python
import waloviz as wv
wv.extension()
wv.Audio('http://ccrma.stanford.edu/~jos/mp3/pno-cs.mp3')
```

![Stereo Example](doc/resources/simple-stereo-example.png)

To learn more read our [Getting Started Guide](https://waloviz.com/en/latest/getting-started.html) :)

## [Documentation](https://waloviz.com)

[Our Docs](https://waloviz.com) are generated by [Sphinx](https://www.sphinx-doc.org/en/master/) and [NBSite](https://nbsite.holoviz.org/) and hosted by [Read the Docs](https://docs.readthedocs.io/en/stable/).  
You can also try `waloviz` right now with our [Google Colab Demo](https://colab.research.google.com/drive/1euQCxaNlTg0pGvXz6d7RSoDhM3B1k7dy?usp=sharing) :)

## [Contributing](CONTRIBUTING.md)

WaloViz is a beginner friendly open-source project!  
To make a contribution, please read our [Contributing Guide](CONTRIBUTING.md).

## Star History

<a href="https://star-history.com/#AlonKellner/waloviz&Date">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/svg?repos=AlonKellner/waloviz&type=Date&theme=dark" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/svg?repos=AlonKellner/waloviz&type=Date" />
   <img alt="Star History Chart" src="https://api.star-history.com/svg?repos=AlonKellner/waloviz&type=Date" />
 </picture>
</a>

What an incredible community response to our launch! Thank you all so much!

## Our Vision

WaloViz has only two long term goals:

### **Be the Definitive Go-To Visualization Tool for Audio Research Experts**

First by being Simple to Use, and secondly by having Powerful Features.

### **Grow a Healthy Open-Source Community**

By being Responsive to Users, and Welcoming to Beginner Contributors.

## Roadmap

- [x] Early Alpha release
- [ ] Create and follow dependencies Issues
- [ ] Create a PR for the [Panel Community Gallery](https://panel.holoviz.org/gallery/index.html#community-gallery)
- [ ] Plan Beta release features
- [ ] Extensive UI Tests (with playwright, see [tests/ui/sanity_test.py](tests/ui/sanity_test.py))
- [ ] Prepare Beta release
- [ ] Write Medium article for Beta launch
- [ ] Beta release
- [ ] Plan 1.0 release features
- [ ] Prepare 1.0 release
- [ ] 1.0 release
