FROM python:3.9 as base

ENV PATH="/scripts:${PATH}"


# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV UWSGI_PROCESSES 1
ENV UWSGI_THREADS 16
ENV UWSGI_HARAKIRI 240
ENV DJANGO_SETTINGS_MODULE 'djbot.settings'


RUN apt-get update
RUN pip3 install --upgrade pip

COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt



FROM base as dev

RUN mkdir "app"

RUN  mkdir -p /var/www/static/ \
     && mkdir -p /var/www/media/ \
     && mkdir -p /app/static/ \
     && mkdir -p /app/media/ \


WORKDIR /app

COPY . .


EXPOSE 8000

ENTRYPOINT ["scripts/entrypoint.sh"]
