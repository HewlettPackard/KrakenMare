FROM ubuntu:18.04

RUN apt-get update && apt-get install -y netcat wget
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

RUN apt update && apt install -y python3 python3-pip
RUN pip3 install paho-mqtt configparser python-schema-registry-client faust

# this is image MUST be built from the upper directory (docker build -f simulator/Dockerfile .) to access agentcommon.py

COPY ./simulator/IBswitchSimulator.py ./simulator/version.py ./simulator/IBswitchSimulator.cfg ./simulator/r1i0c-ibswitch ./simulator/r1i1c-ibswitch ./simulator/entrypoint.sh /simulator/
COPY ./agent-python-module/agentcommon.py /simulator/
COPY ./simulator/seed/* /tmp/
COPY ./simulator/SensorDescriptors/*.json /simulator/

WORKDIR /simulator
ENV PYTHONUNBUFFERED=1

CMD ["/simulator/entrypoint.sh"]
