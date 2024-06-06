FROM mcr.microsoft.com/devcontainers/python:1-3.10-bookworm

RUN apt-get update && apt-get upgrade -y && apt-get install -y ffmpeg sox libavdevice-dev

COPY src/requirements.txt src/requirements.txt
COPY tests/requirements.txt tests/requirements.txt
COPY docs/requirements.txt docs/requirements.txt
RUN --mount=type=cache,target=/root/.cache/ \
    pip install -r src/requirements.txt -r docs/requirements.txt -r tests/requirements.txt
