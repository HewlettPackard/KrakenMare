FROM ubuntu:18.04
# Test env deps
RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y bash strace tcpdump mosquitto-clients wget libssl-dev

# Build deps
RUN apt-get update && apt-get install -y gcc g++ make cmake autoconf libtool wget libssl-dev libavro-dev libcurl4-gnutls-dev git gdb valgrind cppcheck

# Jansson json library
RUN wget --no-check-certificate https://github.com/akheron/jansson/archive/v2.12.tar.gz -O - | tar xzf - 
RUN mv /jansson-2.12 /jansson && cd /jansson && autoreconf -fi ; ./configure && make && make install

# Yajl json library
RUN cd / && wget --no-check-certificate https://github.com/lloyd/yajl/archive/2.1.0.tar.gz -O - | tar xzf - \
&& mv /yajl-2.1.0 /yajl && cd /yajl && ./configure && make && make install

# Confluent serdes library at top of tree
# Will be replaced by a version once we settle on that
RUN cd / && git clone https://github.com/confluentinc/libserdes.git && cd libserdes && ./configure && make && make install

# librdkafa release version 1.1.0
RUN cd / && wget --no-check-certificate https://github.com/edenhill/librdkafka/archive/v1.1.0.tar.gz -O - | tar xzf - \
&& mv /librdkafka-1.1.0 /librdkafka && cd /librdkafka && ./configure && make && make install
RUN cd /librdkafka/examples && make 

# Build kafkacat at release 1.5.0
RUN mkdir -p /usr/src
RUN cd /usr/src && wget -q --no-check-certificate https://github.com/edenhill/kafkacat/archive/1.5.0.tar.gz -O - | tar xzf - && cd kafkacat-1.5.0 && ./configure  && make && make install && mv kafkacat /usr/local/bin/
# Build wait for tool
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# Add other tools not needed for build
RUN apt-get update && apt-get install -y nmap netcat iputils-ping jq redis-server openssl libssl-dev gnupg software-properties-common openjdk-11-jre-headless vim emacs less bc iperf

# Confluent kafka tools
RUN wget -qO - https://packages.confluent.io/deb/5.2/archive.key | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://packages.confluent.io/deb/5.2 stable main"
RUN apt-get update && apt-get install -y confluent-community-2.12

# Add avrocat to work at commandline with avro files
RUN apt update && apt install -y python3 python3-pip git libavro-dev
RUN pip3 install colorama
RUN cd /usr/src && git clone https://github.com/simonwahlgren/avrocat.git && cd avrocat && pip3 install -e .

# Bring in the environment of the simulator so we can play with it
RUN pip3 install avro-python3==1.8.2
RUN pip3 install paho-mqtt configparser python-schema-registry-client fastavro confluent-kafka

COPY ./check-pipeline.sh ./client-sasl_ssl.conf ./client-plain.conf ./scaling-test.sh ./scaling-test-setup.sh ./print-schemaregistry.sh /tmp/

ENV LD_LIBRARY_PATH /usr/local/lib

CMD sleep infinity
