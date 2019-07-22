# Create container for collect using 18.04 and build both librdkafa in our version and collectd with it.
FROM ubuntu:18.04 as collectdbuild

RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y bash wget diffutils patch
# Build deps
RUN apt-get update && apt-get install -y gcc g++ make \
	&& apt-get install -y autoconf libtool wget \
	&& apt-get install -y --force-yes gdb valgrind cppcheck build-essential flex bison automake pkg-config

RUN cd / && wget --no-check-certificate https://github.com/edenhill/librdkafka/archive/v1.1.0.tar.gz -O - | tar xzf - \
&& mv /librdkafka-1.1.0 /librdkafka && cd /librdkafka && ./configure && make && make install
RUN cd /librdkafka/examples && make 

RUN cd / && wget --no-check-certificate https://api.github.com/repos/collectd/collectd/tarball/e55a6658b22b606595c58a9ce566a253f1aa41da -O - | tar xzf - \
	&& mv /collectd-collectd-* /collectd && cd /collectd && ./build.sh && ./configure --disable-werror && make && make install
COPY collectd.conf.patch /tmp
RUN cd /opt/collectd/etc && patch -p0 < /tmp/collectd.conf.patch
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# Create container for collect using 18.04 and bring in librdkafka and collectd
FROM ubuntu:18.04
#
RUN apt-get update && apt-get upgrade -y
RUN apt update && apt install -y netcat
COPY --from=collectdbuild /usr/local/lib/* /usr/local/lib/
COPY --from=collectdbuild /opt/collectd /opt/collectd
COPY --from=collectdbuild /tmp/wait-for /tmp/wait-for
COPY entrypoint.sh /
#
CMD ["/entrypoint.sh"]
