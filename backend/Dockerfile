FROM python:3.11-slim

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

ARG DJANGO_SECRET
ARG DEBUG
ARG POSTGRES_DB
ARG POSTGRES_USER
ARG POSTGRES_PASSWORD
ARG POSTGRES_HOST

RUN mkdir /source
COPY . /source
WORKDIR /source

RUN apt-get update
RUN apt-get install -y libpq-dev gcc

RUN chmod +x entrypoint.sh

RUN pip install -r requirements.txt
RUN pip install psycopg2-binary
RUN pip install psycopg2

RUN python manage.py collectstatic

CMD ["python", "/source/manage.py", "runserver", "0.0.0.0:8000"]
