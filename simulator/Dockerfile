FROM ubuntu:18.04

RUN apt-get update && apt-get install -y netcat wget
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

RUN apt update && apt install -y python3 python3-pip
RUN pip3 install paho-mqtt kafka-python configparser

COPY IBswitchSimulator.py version.py IBswitchSimulator.cfg r1i0c-ibswitch r1i1c-ibswitch entrypoint.sh /simulator/
COPY seed/* /tmp/

WORKDIR /simulator
ENV PYTHONUNBUFFERED=1

CMD ["/simulator/entrypoint.sh"]
