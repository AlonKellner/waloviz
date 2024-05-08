FROM python

RUN apt-get update && apt-get upgrade -y && apt-get install -y ffmpeg sox libavdevice-dev

COPY src/requirements.txt src/requirements.txt
RUN --mount=type=cache,target=/root/.cache/ \
    pip install -r src/requirements.txt
