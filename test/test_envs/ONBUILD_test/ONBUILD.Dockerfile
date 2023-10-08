FROM alpine:latest

ONBUILD RUN echo "ONBUILD instruction executed: Hello from ONBUILD!"

CMD ["echo", "Base image CMD executed"]