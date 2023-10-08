FROM ubuntu:latest

ENV MY_VARIABLE="Hello, Docker!"

CMD echo $MY_VARIABLE
