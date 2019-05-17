# Create container for collect using 18.04 and build both librdkafa in our version and collectd with it.
FROM ubuntu:18.04 as collectdbuild

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y bash wget diffutils patch
# Build deps
RUN apt-get update && apt-get install -y gcc g++ make \
&& apt-get install -y autoconf libtool wget \
&& apt-get install -y --force-yes gdb valgrind cppcheck build-essential flex bison automake pkg-config
RUN cd / && wget --no-check-certificate https://api.github.com/repos/edenhill/librdkafka/tarball/f460729fda3916485508e63f491bba4bcae3a80d -O - | tar xzf - \
&& mv /edenhill-librdkafka* /librdkafka && cd /librdkafka && ./configure && make && make install

#RUN cd / && wget --no-check-certificate https://api.github.com/repos/collectd/collectd/tarball/e55a6658b22b606595c58a9ce566a253f1aa41da -O - | tar xzf - \ 
RUN cd / && wget --no-check-certificate https://api.github.com/repos/jhansonhpe/collectd/tarball/ffd2c31220b36197aad83e9f818e88c24fea6718 -O - | tar xzf - \ 
&& mv /jhansonhpe-collectd-* /collectd && cd /collectd && ./build.sh && ./configure --disable-werror && make && make install
COPY collectd.conf.patch /tmp
RUN cd /opt/collectd/etc && patch -p0 < /tmp/collectd.conf.patch

# Create container for collect using 18.04 and bring in librdkafka and collectd
FROM ubuntu:18.04
#
RUN apt-get update && apt-get upgrade -y
COPY --from=collectdbuild /usr/local/lib/* /usr/local/lib/
COPY --from=collectdbuild /opt/collectd /opt/collectd
#
ENV LD_LIBRARY_PATH /usr/local/lib
ENTRYPOINT ["/opt/collectd/sbin/collectd", "-f"]
