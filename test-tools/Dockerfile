FROM ubuntu:18.04 as testbuild

# Test env deps
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y bash strace tcpdump mosquitto-clients wget
# Build deps
RUN apt-get update && apt-get install -y gcc make
COPY --from=demo_kafka-embedded-client-1 /usr/local/lib/* /usr/local/lib/
RUN mkdir -p /usr/local/include/librdkafka/
COPY --from=demo_kafka-embedded-client-1 /usr/local/include/librdkafka/* /usr/local/include/librdkafka/
# Build kafkacat
RUN mkdir -p /usr/src
RUN cd /usr/src && wget -q --no-check-certificate https://github.com/edenhill/kafkacat/archive/1.3.1.tar.gz -O - | tar xzf - && cd kafkacat-1.3.1 && ./configure && make && make install && mv kafkacat /usr/local/bin/

FROM ubuntu:18.04
RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y bash strace tcpdump mosquitto-clients wget
COPY --from=demo_kafka-embedded-client-1 /usr/local/lib/* /usr/local/lib/
RUN mkdir -p /usr/local/include/librdkafka/
COPY --from=demo_kafka-embedded-client-1 /usr/local/include/librdkafka/* /usr/local/include/librdkafka/
COPY --from=testbuild /usr/local/bin/* /usr/local/bin/

ENV LD_LIBRARY_PATH /usr/local/lib
CMD /bin/bash
