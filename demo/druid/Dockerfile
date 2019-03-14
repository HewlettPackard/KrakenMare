FROM openjdk:8-jdk

RUN export http_proxy=http://web-proxy.bbn.hpecorp.net:8080 \
    && export https_proxy=http://web-proxy.bbn.hpecorp.net:8080 \
    && wget https://www-us.apache.org/dist/incubator/druid/0.13.0-incubating/apache-druid-0.13.0-incubating-bin.tar.gz \
    && tar -xzf apache-druid-0.13.0-incubating-bin.tar.gz \
    && mv apache-druid-0.13.0-incubating /opt/druid/

# Change to zookeeper already existing outside this container
COPY quickstart-no-zk.conf /opt/druid/quickstart/tutorial/conf/quickstart-no-zk.conf
RUN sed -i "s/druid.zk.service.host=localhost/druid.zk.service.host=zookeeper/" /opt/druid/quickstart/tutorial/conf/druid/_common/common.runtime.properties

WORKDIR /opt/druid/
CMD bin/supervise -c quickstart/tutorial/conf/quickstart-no-zk.conf
