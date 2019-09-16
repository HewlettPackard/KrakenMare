FROM ubuntu:18.04

RUN apt update && apt install -y python3 python3-pip
RUN pip3 install paho-mqtt confluent-kafka configparser colorlog

COPY FanIn.py version.py FanIn.cfg KrakenMareLogger.py /fanin/

WORKDIR /fanin
ENV PYTHONUNBUFFERED=1
ENTRYPOINT python3 FanIn.py

#CMD sleep infinity