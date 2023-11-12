#!/bin/sh
python manage.py makemigrations
python manage.py makemigrations base
python manage.py migrate
python manage.py migrate base
python manage.py initadmin