# Base image
FROM alpine:latest

# Set the custom signal to stop the container gracefully
STOPSIGNAL SIGTERM

# This is just a placeholder CMD to keep the container running
CMD ["tail", "-f", "/dev/null"]
