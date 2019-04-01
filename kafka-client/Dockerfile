#precise, aka Ubuntu12 is the baseline for the SLAPM SDK.
FROM ubuntu:precise

RUN apt-get update && apt-get upgrade

#only required for building
RUN apt-get install -y --force-yes gcc g++ make \
&& apt-get install -y autoconf libtool wget \
&& cd / && wget --no-check-certificate https://api.github.com/repos/akheron/jansson/tarball/f4498d2856fff130366e1dacc74d66d3502e0e5c -O - | tar xzf - \
&& apt-get install -y --force-yes gdb valgrind cppcheck

RUN mv /akheron-jansson* /jansson && cd /jansson && autoreconf -fi ; ./configure && make && make install

#just a simple jansson compile test to validate all build env is 'go'
COPY json_simple_write.c /jansson/examples/
RUN cd /jansson/examples && gcc -Wall -Werror json_simple_write.c -ljansson -o simple_write 

RUN cd / && wget --no-check-certificate https://api.github.com/repos/edenhill/librdkafka/tarball/f460729fda3916485508e63f491bba4bcae3a80d -O - | tar xzf - \
&& mv /edenhill-librdkafka* /librdkafka && cd /librdkafka && ./configure && make && make install
RUN cd /librdkafka/examples && make 

COPY simul.c /librdkafka/examples/simul.c
COPY Makefile /librdkafka/examples/Makefile
RUN cd /librdkafka/examples && make

WORKDIR /

#the 'fabric' topic is already generated in the demo project by the python simulator, this code will simply publish to this assumed
#already existing topic.
ENTRYPOINT export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib && /librdkafka/examples/simul $KAFKA_BROKER_IP fabric Hello_Kafka
