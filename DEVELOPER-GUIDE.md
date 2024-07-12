# Developer Guide

**Finish reading this guide before you start working on a PR.**

## Setup

The recommended setup for developing WaloViz requires to install 2 things:

1. [VSCode](https://code.visualstudio.com/)
2. [Docker Desktop](https://www.docker.com/products/docker-desktop/)

Clone the repository in your favorite manner, and open it with VSCode.  
Now follow these steps:

1. Install the Dev Containers extension
2. Reopen folder in Dev Container (`ctrl+shift+P` -> type "Reopen", this may take a few minutes)
3. `git checkout develop`

## Where is Stuff?

The Repository Structure is like so:

1. `src/` - the `waloviz` package itself, it contains its minimum `src/requirements.txt`
2. `doc/` - the templates for the [Documentation Website](https://waloviz.com), it contains `doc/requirements.txt` which are specific for the docs
3. `tests/` - the manual and UI tests, it contains `tests/requirements.txt` which are specific for the tests
4. `.devcontainer/` - configuration for the VSCode DevContainer extension, it contains `.devcontainer/requirements.txt` which are specific for development
5. `requirements.txt` - points to all of the previously mentioned `*/requirements.txt`
6. `pyproject.toml` - the pypi package configuration
7. `examples/` - notebooks for the docs

## Technologies

In this repo there are many technologies for different usages, here is a list with helpful links:

- [**Github Actions**](https://docs.github.com/en/actions) - A versatile CI\CD solution with a huge community, for automated CI\CD pipelines
- [**Github Pages**](https://pages.github.com/) - A simple static hosting solution, for hosting [the Test Documentation Website](https://alonkellner.com/waloviz/)
- [**Read the Docs**](https://docs.readthedocs.io/en/stable/) - An E2E documentation hosting solution, for hosting [our Released Documentation Websites](https://waloviz.com/)
- [**VSCode Dev Containers**](https://code.visualstudio.com/docs/devcontainers/containers) - A Docker based local development environment, for easy on-boarding and development setup
- [**pre-commit**](https://pre-commit.com/) - a framework for managing pre-commit hooks. In our repo it does mainly static typing, linting and reformatting with [**Pyright**](https://microsoft.github.io/pyright/#/), [**Ruff**](https://docs.astral.sh/ruff/), [**Prettier**](https://prettier.io/docs/en/) and the built-in [**pre-commit-hooks**](https://github.com/pre-commit/pre-commit-hooks).
- [**NBSite**](https://nbsite.holoviz.org/) - a [**Sphinx**](https://www.sphinx-doc.org/en/master/) wrapper for [**HoloViz**](https://holoviz.org/) websites, generates [our Documentation Website](https://waloviz.com/)
- [**Jupyter**](https://jupyter.org/) - a notebook format for interactive python, popular amongst Data-Scientists and researchers in general. Popular IDEs are [**Jupyter Notebook**](https://jupyter.org/), [**JupyterLab**](https://jupyterlab.readthedocs.io/en/latest/), [**VSCode**](https://code.visualstudio.com/) and [**Google Colab**](https://colab.research.google.com/). Almost all users of WaloViz use it in Jupyter notebooks with one of the mentioned IDEs.
- [**Bokeh**](https://bokeh.org/) - A low level interactive plotting framework, it supports Jupyter notebooks. The spectrograms, axes, toolbar and progress bar of the WaloViz player are all native Bokeh components. Bokeh allows advanced JS linking and customizations which WaloViz uses extensively.
- [**HoloViews**](https://holoviews.org/) - Part of the [**HoloViz**](https://holoviz.org/) ecosystem. A high level interactive plotting API, can use [**Bokeh**](https://bokeh.org/), Plotly or Matplotlib as backends, it supports Jupyter notebooks. WaloViz uses HoloViews to create the basic structure of the player, and uses Bokeh for the final customizations.
- [**Panel**](https://github.com/holoviz/panel) - Part of the [**HoloViz**](https://holoviz.org/) ecosystem. A widget based web app framework for creating interactive applications and dashboards, it supports Jupyter notebooks. WaloViz uses Panel for the audio player, the download button, HTML exporting and responsiveness.
- [**PyTorch**](https://pytorch.org/) - An accelerated tensor based framework for Deep-Learning and Data-Science. WaloViz uses PyTorch tensors as the basic format for the audio and spectrogram data.
- [**TorchAudio**](https://pytorch.org/audio/stable/index.html) - Part of the PyTorch ecosystem. TorchAudio has many domains specific features for audio research. WaloViz uses TorchAudio to load audio files into PyTorch tensors and to generate the spectrogram.
- [**PyTest**](https://docs.pytest.org/en/8.2.x/) - A python testing framework
- [**Playwright**](https://playwright.dev/) - A browser simulator, used for testing UI components of WaloViz
- [**hatchling**](https://hatch.pypa.io/latest/) - A modern python package builder, we use it with [**hatch-vcs**](https://github.com/ofek/hatch-vcs) for easy git tag based releases.

## Did you read the entire guide?

### No

[:up: Back to the top with you :up:](#developer-guide)

### YES

You Are READY.  
What a wonder you are, a truly Certified Contributor, **thank you :)**
