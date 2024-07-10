FROM mcr.microsoft.com/devcontainers/python:1-3.10-bookworm

RUN apt-get update && apt-get upgrade -y && apt-get install -y ffmpeg sox libavdevice-dev graphviz && dot -c

COPY src/requirements.txt src/requirements.txt
COPY tests/requirements.txt tests/requirements.txt
COPY doc/requirements.txt doc/requirements.txt
COPY .devcontainer/requirements.txt .devcontainer/requirements.txt
COPY requirements.txt requirements.txt
RUN --mount=type=cache,target=/root/.cache/ \
    pip install -r requirements.txt

RUN playwright install chromium && playwright install-deps
