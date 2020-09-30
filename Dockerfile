FROM python:3

LABEL maintainer="tmunzer@juniper.net"
LABEL one.stag.mrg.version="1.0.0"
LABEL one.stag.mrg.release-date="2020-08-11"


RUN pip install --upgrade pip django whitenoise requests

COPY ./django_app /app/
WORKDIR /app

EXPOSE 8000
CMD ["python","-u","manage.py", "runserver", "0.0.0.0:8000"]