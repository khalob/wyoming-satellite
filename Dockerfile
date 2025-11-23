FROM python:3.11-slim-bookworm

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install --yes --no-install-recommends avahi-utils alsa-utils

WORKDIR /app

COPY sounds/ ./sounds/
COPY script/setup ./script/
COPY pyproject.toml ./
COPY wyoming_satellite/ ./wyoming_satellite/

RUN script/setup

COPY script/run ./script/
COPY docker/run ./

EXPOSE 10700

ENTRYPOINT ["/app/run"]


FROM python:3.11-slim-bookworm

ENV LANG C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && \
    apt-get install --yes --no-install-recommends \
        avahi-utils \
        alsa-utils \
        libsndfile1 \
        libsox-fmt-all \
        git \
        && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY sounds/ ./sounds/
COPY script/setup ./script/
COPY pyproject.toml ./
COPY wyoming_satellite/ ./wyoming_satellite/

# Run the normal setup first
RUN script/setup

# --- Add numpy for Silero VAD padding ---
RUN /app/.venv/bin/pip install --no-cache-dir numpy

# --- NEW: Install Silero VAD and PyTorch ---
# Activate the virtualenv created by script/setup
RUN /app/.venv/bin/pip install --no-cache-dir torch pysilero-vad==2.1.1

COPY script/run ./script/
COPY docker/run ./

EXPOSE 10700

ENTRYPOINT ["/app/run"]
