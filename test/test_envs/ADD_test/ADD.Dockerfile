# Use a base image
FROM ubuntu:latest

# Copy a file from the host into the image
ADD hello.txt /app/

# Set the working directory
WORKDIR /app

# Run a command to display the content of the copied file
CMD cat hello.txt