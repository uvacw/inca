FROM python:3.8.0-buster

ADD . inca

RUN pip install /inca

