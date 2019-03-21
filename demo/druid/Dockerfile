FROM openjdk:8-jdk

RUN export http_proxy=http://web-proxy.bbn.hpecorp.net:8080 \
    && export https_proxy=http://web-proxy.bbn.hpecorp.net:8080 \
    && wget https://static.imply.io/release/imply-2.8.16.tar.gz \
    && tar -xzf imply-2.8.16.tar.gz \
    && mv imply-2.8.16 /opt/druid/

# Change to zookeeper already existing outside this container
COPY quickstart-no-zk.conf /opt/druid/quickstart/tutorial/conf/quickstart-no-zk.conf
RUN sed -i "s/druid.zk.service.host=localhost/druid.zk.service.host=zookeeper/" /opt/druid/conf-quickstart/druid/_common/common.runtime.properties

WORKDIR /opt/druid/
CMD bin/supervise -c quickstart/tutorial/conf/quickstart-no-zk.conf
