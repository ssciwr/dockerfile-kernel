# Use a base image
FROM ubuntu:latest

# Set environment variable
ENV MY_VARIABLE="Hello, Docker!"

# Run a command using the environment variable
CMD echo $MY_VARIABLE
