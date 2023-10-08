# This is the reference dockerfile against which the mymagic_magic.dockerfile is tested

FROM ubuntu

RUN RUN pip install --upgrade pip && \
    pip install pytest && \
    -rf /root/.cache/pip