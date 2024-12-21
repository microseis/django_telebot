FROM python:3.10-slim-buster as base

# set environment variables
ENV  PYTHONDONTWRITEBYTECODE=1 \
     PIP_NO_CACHE_DIR=off \
     PIP_DISABLE_PIP_VERSION_CHECK=on\
     PYTHONUNBUFFERED=1 \
     UWSGI_PROCESSES=1 \
     UWSGI_THREADS=16 \
     UWSGI_HARAKIRI=240 \
     DJANGO_SETTINGS_MODULE='djbot.settings'

RUN apt-get update

RUN apt-get install -y build-essential

RUN apt-get install libpq-dev python-dev -y

ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME=/opt/poetry \
    POETRY_VENV=/opt/poetry-venv \
    POETRY_CACHE_DIR=/opt/.cache 

# Install poetry separated from system interpreter
RUN python3 -m venv $POETRY_VENV \
    && $POETRY_VENV/bin/pip install -U pip setuptools \
    && $POETRY_VENV/bin/pip install poetry==${POETRY_VERSION}

# Add `poetry` to PATH
ENV PATH="${PATH}:${POETRY_VENV}/bin"

COPY ./poetry.lock /var/www/app/src/
COPY ./pyproject.toml /var/www/app/src/

RUN poetry config virtualenvs.create false

WORKDIR /var/www/app/src/

FROM base as dev

RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && mkdir -p /app/static/ \
     && mkdir -p /app/media/

# Install Dependencies
# to avoid source file changes busting RUN layer cache for the 3rd party dependency.
RUN poetry install --only main --no-root --no-directory

COPY src/ /var/www/app/src/

EXPOSE 8000

RUN poetry install --only main

RUN apt install -y netcat

ENTRYPOINT ["sh", "./scripts/entrypoint.sh"]