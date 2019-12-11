FROM ubuntu:18.04

RUN apt update && apt install -y netcat wget python3 python3-pip
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

RUN pip3 install paho-mqtt confluent-kafka configparser colorlog python-schema-registry-client fastavro

COPY FanIn.py entrypoint.sh version.py FanIn.cfg KrakenMareLogger.py /fanin/

WORKDIR /fanin
ENV PYTHONUNBUFFERED=1

CMD ["/fanin/entrypoint.sh"]