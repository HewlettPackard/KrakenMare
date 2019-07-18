ARG kafka_prefix
FROM ${kafka_prefix}kafka-embedded-client-1 as kafka-client

FROM ubuntu:18.04 as testbuild
# Test env deps
RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y bash strace tcpdump mosquitto-clients wget libssl-dev
# Build deps
RUN apt-get update && apt-get install -y gcc make cmake
COPY --from=kafka-client /usr/local/lib/* /usr/local/lib/
RUN mkdir -p /usr/local/include/librdkafka/
COPY --from=kafka-client /usr/local/include/librdkafka/* /usr/local/include/librdkafka/
RUN cd / && wget --no-check-certificate https://github.com/lloyd/yajl/archive/2.1.0.tar.gz -O - | tar xzf - \
&& mv /yajl-2.1.0 /yajl && cd /yajl && ./configure && make && make install

# Build kafkacat
RUN mkdir -p /usr/src
RUN cd /usr/src && wget -q --no-check-certificate https://github.com/edenhill/kafkacat/archive/1.4.0.tar.gz -O - | tar xzf - && cd kafkacat-1.4.0 && ./configure  && make && make install && mv kafkacat /usr/local/bin/
# Build wait for tool
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

FROM ubuntu:18.04
RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y bash strace tcpdump mosquitto-clients wget curl nmap netcat iputils-ping jq redis-server openssl libssl-dev
COPY --from=kafka-client /usr/local/lib/* /usr/local/lib/
RUN mkdir -p /usr/local/include/librdkafka/
COPY --from=kafka-client /usr/local/include/librdkafka/* /usr/local/include/librdkafka/
COPY --from=testbuild /usr/local/bin/* /usr/local/bin/
COPY --from=testbuild /tmp/wait-for /tmp/wait-for
RUN mkdir -p /usr/local/include/yajl
COPY --from=testbuild /usr/local/include/yajl/* /usr/local/include/yajl/
COPY --from=testbuild /usr/local/lib/* /usr/local/lib/

COPY ./check-pipeline.sh /tmp/

ENV LD_LIBRARY_PATH /usr/local/lib

CMD sleep infinity
