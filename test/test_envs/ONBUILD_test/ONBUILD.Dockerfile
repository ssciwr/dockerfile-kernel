# Base image
FROM alpine:latest

# ONBUILD instruction: This will be executed when this image is used as a base image
ONBUILD RUN echo "ONBUILD instruction executed: Hello from ONBUILD!"

# This is just a placeholder CMD to show the final image's content
CMD ["echo", "Base image CMD executed"]