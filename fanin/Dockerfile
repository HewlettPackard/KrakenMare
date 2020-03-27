# Create container for fanin using ubuntu 18.04 and build librdkafa with full features
FROM ubuntu:18.04 as faninbuild

RUN apt-get update && apt-get upgrade -y && apt-get -y install software-properties-common
RUN apt-get update && apt-get install -y netcat wget python3.7 python3.7-dev
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN apt-get update && apt-get install -y python3-pip
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# Build deps
RUN apt-get update && apt-get install -y gcc g++ make cmake autoconf libtool wget libavro-dev libcurl4-gnutls-dev git gdb valgrind cppcheck zlib1g-dev libssl-dev libsasl2-dev libzstd-dev

# Create container for fanin using ubuntu 18.04 and copy over build features as needed
FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y && apt-get -y install software-properties-common
RUN apt-get update && apt-get install -y netcat wget python3.7 python3.7-dev curl jq
RUN wget -qO - https://packages.confluent.io/deb/5.4/archive.key | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://packages.confluent.io/deb/5.4 stable main"
RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.7 1
RUN apt-get update && apt-get install -y python3-pip
# Runtime deps from the build deps above
RUN apt-get update && apt-get install -y libavro23 libcurl3-gnutls zlib1g libssl1.1 libzstd1 netcat libsasl2-2 software-properties-common
COPY --from=faninbuild /tmp/wait-for /tmp/wait-for
COPY --from=faninbuild /usr/local /usr/local/

RUN apt-get update && apt-get install -y librdkafka-dev

RUN pip3 install paho-mqtt confluent-kafka configparser colorlog python-schema-registry-client faust

COPY ./fanin/FanIn.py ./fanin/entrypoint.sh fanin/version.py fanin/FanIn.cfg fanin/KrakenMareLogger.py /fanin/
COPY ./agent-python-module/agentcommon.py /fanin
COPY ./test-schemas/check_schemas.sh /fanin

WORKDIR /fanin
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/usr/local/lib

CMD ["/fanin/entrypoint.sh"]
