# See https://unit.nginx.org/installation/#docker-images

FROM python:3.9.16-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

RUN apt update && apt install -y python3-pip && mkdir build

# Build folder for our app, only stuff that matters copied.
WORKDIR /build

# Update, install requirements and then cleanup.
COPY ./requirements.txt ./pyproject.toml ./pyproject.toml /build/

RUN pip3 install -r requirements.txt                                          \
    && pip3 install psycopg2-binary toml wheel uvicorn                        \
    && apt remove -y python3-pip                                              \
    && apt autoremove --purge -y                                              \
    && rm -rf /var/lib/apt/lists/* /etc/apt/sources.list.d/*.list

# Copy the rest of app
COPY ./app ./app
COPY ./alembic ./alembic
COPY ./alembic.ini .