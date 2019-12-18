# Create container for fanin using ubuntu 18.04 and build librdkafa with full features
FROM ubuntu:18.04 as faninbuild

RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y netcat wget python3 python3-pip
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# Build deps
RUN apt-get update && apt-get install -y gcc g++ make cmake autoconf libtool wget libavro-dev libcurl4-gnutls-dev git gdb valgrind cppcheck zlib1g-dev libssl-dev libsasl2-dev libzstd-dev

# Jansson json library
RUN wget --no-check-certificate https://github.com/akheron/jansson/archive/v2.12.tar.gz -O - | tar xzf -
RUN mv /jansson-2.12 /jansson && cd /jansson && autoreconf -fi ; ./configure && make && make install

# Yajl json library
RUN cd / && wget --no-check-certificate https://github.com/lloyd/yajl/archive/2.1.0.tar.gz -O - | tar xzf - \
&& mv /yajl-2.1.0 /yajl && cd /yajl && ./configure && make && make install

# Confluent serdes library at version to match Kafka components from Confluent
RUN cd / && wget --no-check-certificate https://github.com/confluentinc/libserdes/archive/v5.2.0.tar.gz  -O - | tar xzf - \
&& mv /libserdes-5.2.0 /libserdes && cd /libserdes && ./configure && make && make install

# librdkafa release version 1.1.0
RUN cd / && wget --no-check-certificate https://github.com/edenhill/librdkafka/archive/v1.1.0.tar.gz -O - | tar xzf - \
&& mv /librdkafka-1.1.0 /librdkafka && cd /librdkafka && ./configure && make && make install

# Create container for fanin using ubuntu 18.04 and copy over build features as needed
FROM ubuntu:18.04

RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y python3 python3-pip
# Runtime deps from the build deps above
RUN apt-get update && apt-get install -y libavro23 libcurl3-gnutls zlib1g libssl1.1 libzstd1 netcat libsasl2-2
COPY --from=faninbuild /tmp/wait-for /tmp/wait-for
COPY --from=faninbuild /usr/local /usr/local/

RUN pip3 install paho-mqtt confluent-kafka configparser colorlog python-schema-registry-client fastavro

COPY FanIn.py entrypoint.sh version.py FanIn.cfg KrakenMareLogger.py /fanin/

WORKDIR /fanin
ENV PYTHONUNBUFFERED=1
ENV LD_LIBRARY_PATH=/usr/local/lib

CMD ["/fanin/entrypoint.sh"]
