FROM ubuntu

RUN apt-get update && apt-get install -y rolldice && rm -rf /var/lib/apt/lists/*