#precise, aka Ubuntu12 is the baseline for the SLAPM SDK.
# but we use this build in 18.04 so I'm changing to that
FROM ubuntu:18.04 as kafkabuild

RUN apt-get update && apt-get upgrade -y

#only required for building
RUN apt-get update && apt-get install -y --force-yes gcc g++ make \
&& apt-get install -y autoconf libtool wget libssl-dev \
&& cd / && wget --no-check-certificate https://github.com/akheron/jansson/archive/v2.12.tar.gz -O - | tar xzf - \
&& apt-get install -y --force-yes gdb valgrind cppcheck

RUN mv /jansson-2.12 /jansson && cd /jansson && autoreconf -fi ; ./configure && make && make install

#just a simple jansson compile test to validate all build env is 'go'
COPY json_simple_write.c /jansson/examples/
RUN cd /jansson/examples && gcc -Wall -Werror json_simple_write.c -ljansson -o simple_write 

RUN cd / && wget --no-check-certificate https://github.com/edenhill/librdkafka/archive/v1.1.0.tar.gz -O - | tar xzf - \
&& mv /librdkafka-1.1.0 /librdkafka && cd /librdkafka && ./configure && make && make install
RUN cd /librdkafka/examples && make 

COPY simul.c /librdkafka/examples/simul.c
COPY Makefile /librdkafka/examples/Makefile
RUN cd /librdkafka/examples && make

WORKDIR /

# The demo configuration allows topics to be created. By the act of publishing we create the hello topic
FROM ubuntu:18.04
COPY --from=kafkabuild /usr/local/lib/* /usr/local/lib/
RUN mkdir -p /usr/local/include/librdkafka
COPY --from=kafkabuild /usr/local/include/librdkafka/* /usr/local/include/librdkafka/
COPY --from=kafkabuild /librdkafka/examples/simul /simul
ENV LD_LIBRARY_PATH /usr/local/lib
ENTRYPOINT /simul $KAFKA_BROKER_IP hello Hello_Kafka
