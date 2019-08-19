FROM ubuntu:18.04

RUN apt update && apt install -y python3 python3-pip
RUN pip3 install paho-mqtt kafka-python configparser

COPY IBswitchSimulator.py version.py IBswitchSimulator.cfg r1i0c-ibswitch r1i1c-ibswitch /simulator/
COPY seed/* /tmp/

WORKDIR /simulator
ENV PYTHONUNBUFFERED=1

ENTRYPOINT python3 IBswitchSimulator.py --mode=kafka

#CMD sleep infinity