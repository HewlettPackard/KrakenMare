#precise, aka Ubuntu12 is the baseline for the SLAPM SDK.
FROM ubuntu:precise

RUN echo "deb http://ppa.launchpad.net/mosquitto-dev/mosquitto-ppa/ubuntu precise main" >> /etc/apt/sources.list && apt-get update

#only required for building
RUN apt-get install -y --force-yes gcc make libmosquittopp-dev wget autoconf libtool uuid-dev libuuid1\
&& cd / && wget --no-check-certificate https://api.github.com/repos/akheron/jansson/tarball/f4498d2856fff130366e1dacc74d66d3502e0e5c -O - | tar xzf - 

#only required for debugging....
RUN apt-get install -y --force-yes mosquitto-clients gdb valgrind cppcheck

RUN mv /akheron-jansson* /jansson && cd /jansson && autoreconf -fi ; ./configure && make && make install

#just a simple jansson compile test to validate all build env is 'go'
COPY json_simple_write.c /jansson/examples/
RUN cd /jansson/examples && gcc json_simple_write.c -ljansson -o simple_write 

COPY Makefile simul.c registration.c /mousttic/
RUN cd mousttic && make 


WORKDIR /mousttic

ENTRYPOINT export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH ; ./registration -m "Hello World !" -s $MOSQUITTO_IP -t hello_topic -d
