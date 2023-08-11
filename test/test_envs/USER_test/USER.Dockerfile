FROM ubuntu:latest
RUN apt-get -y update
RUN groupadd -r user && useradd -r -g user user
USER user
