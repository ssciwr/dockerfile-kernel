FROM alpine:latest

STOPSIGNAL SIGTERM

CMD ["tail", "-f", "/dev/null"]
