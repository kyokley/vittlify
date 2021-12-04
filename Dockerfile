ARG BASE_IMAGE=python:3.9-slim-bullseye
ARG NODE_IMAGE=node:latest

FROM ${BASE_IMAGE} AS base
ENV VIRTUAL_ENV=/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && \
        apt-get upgrade -y && \
        apt-get install -y --no-install-recommends \
            postgresql-common \
            libffi-dev \
            libpq-dev \
            g++ \
            && \
        rm -rf /var/cache/apt/* /var/lib/apt/lists/*

WORKDIR /code
COPY pyproject.toml poetry.lock ./

RUN pip install --upgrade --no-cache-dir pip poetry wheel && \
        poetry install --no-dev


FROM base AS dev
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

RUN apt-get update && \
        apt-get install -y ripgrep

WORKDIR /code

COPY pyproject.toml poetry.lock ./
RUN poetry install


FROM base AS prod
ENV VIRTUAL_ENV=/venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

COPY . /code
WORKDIR /code

CMD ["gunicorn", "-b", "0.0.0.0:8000", "--access-logfile", "-", "--log-file", "-", "--error-logfile", "-", "config.wsgi:application"]
