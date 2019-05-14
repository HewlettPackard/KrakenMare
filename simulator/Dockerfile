FROM ubuntu:18.04

RUN apt update && apt install -y python python-pip
RUN pip install paho-mqtt kafka-python

COPY fake-ibswitchquery.py r1i0c-ibswitch r1i1c-ibswitch /simulator/
COPY seed/* /tmp/

WORKDIR /simulator
ENV PYTHONUNBUFFERED=1
ENTRYPOINT python fake-ibswitchquery.py
