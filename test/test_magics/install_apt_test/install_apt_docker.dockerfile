# This is the reference dockerfile against which the mymagic_magic.dockerfile is tested

FROM ubuntu

RUN apt-get update && apt-get install -y rolldice && rm -rf /var/lib/apt/lists/*