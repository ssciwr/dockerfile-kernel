FROM ubuntu:latest

ADD hello.txt /app/

WORKDIR /app

CMD cat hello.txt