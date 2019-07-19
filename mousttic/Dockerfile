FROM ubuntu:18.04

# Add the PPA for mousquitto
RUN apt-get update && apt-get -y upgrade && apt-get install software-properties-common -y && add-apt-repository ppa:mosquitto-dev/mosquitto-ppa && apt-get update

#only required for building
RUN apt-get update && apt-get install -y --force-yes gcc make libmosquittopp-dev wget autoconf libtool uuid-dev libuuid1\
&& cd / && wget --no-check-certificate https://github.com/akheron/jansson/archive/v2.12.tar.gz -O - | tar xzf - 

#only required for debugging....
RUN apt-get update && apt-get install -y --force-yes mosquitto-clients gdb valgrind cppcheck

RUN mv /jansson-2.12 /jansson && cd /jansson && autoreconf -fi ; ./configure && make && make install

#just a simple jansson compile test to validate all build env is 'go'
COPY json_simple_write.c /jansson/examples/
RUN cd /jansson/examples && gcc json_simple_write.c -ljansson -o simple_write 

COPY Makefile simul.c registration.c /mousttic/
RUN cd mousttic && make 

WORKDIR /mousttic
ENTRYPOINT export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH ; ./registration -m "Hello World !" -s $MOSQUITTO_IP -t hello_topic -d
