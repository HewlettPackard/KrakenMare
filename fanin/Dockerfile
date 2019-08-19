FROM ubuntu:18.04

RUN apt update && apt install -y python3 python3-pip
RUN pip3 install paho-mqtt kafka-python configparser colorlog

COPY FanIn.py version.py FanIn.cfg /fanin/

WORKDIR /fanin
ENV PYTHONUNBUFFERED=1
ENTRYPOINT python3 FanIn.py

#CMD sleep infinity