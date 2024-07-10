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
**An open source interactive audio player with a spectrogram built-in, primarily based on [Bokeh](https://bokeh.org/) and the [HoloViz](https://holoviz.org/) stack (wav+HoloViz=WaloViz).**

## Installation

```shell
pip install waloviz
apt-get install ffmpeg
```

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

[Our Docs](https://waloviz.com) are generated by [sphinx](https://www.sphinx-doc.org/en/master/) and [`nbsite`](https://nbsite.holoviz.org/) and hosted by [readthedocs](https://docs.readthedocs.io/en/stable/).

## [Contributing](CONTRIBUTING.md)

WaloViz is a beginner friendly open-source project!  
To make a contirbution, please read our [Contributing Guide](CONTRIBUTING.md).

## Our Vision

WaloViz has only two long term goals:

### **Be the Definitive Go-To Visualization Tool for Audio Research Experts**

First by being Simple to Use, and secondly by having Powerful Features.

### **Grow a Healthy Open-Source Community**

By being Responsive to Users, and Welcoming to Beginner Conftributors.

## Roadmap

- [ ] Early Alpha release
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
