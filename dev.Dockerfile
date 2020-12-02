FROM python:3.8-alpine

COPY ./Vidulum/dev_requirements.txt /var/www/requirements.txt

RUN pip install -U pip
RUN pip install -r /var/www/requirements.txt

