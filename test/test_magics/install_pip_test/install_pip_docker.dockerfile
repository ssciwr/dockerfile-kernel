# This is the reference dockerfile against which the mymagic_magic.dockerfile is tested

FROM python:3.10-slim-buster

RUN pip install --upgrade pip && pip install pytest && rm -rf /root/.cache/pip