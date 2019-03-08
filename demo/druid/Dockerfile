FROM ubuntu:16.04

# Prepare OS
COPY setup-os.sh /root
RUN /root/setup-os.sh

# Copy package from build directory
ARG implyversion
RUN cd /opt && wget https://static.imply.io/release/imply-${implyversion}.tar.gz && tar xf imply-${implyversion}.tar.gz && rm imply-${implyversion}.tar.gz
RUN mkdir -p /mnt/imply/var && ln -snf /mnt/imply/var /opt/imply-${implyversion}/var
RUN ln -snf /opt/imply-${implyversion} /opt/imply
COPY quickstart-no-zk.conf /opt/imply/conf/supervise/quickstart-no-zk.conf
COPY perfquery-index.json /tmp/perfquery-index.json
COPY entrypoint.sh /root


# Change to zookeeper already existing outside this container
RUN sed -i "s/druid.zk.service.host=localhost/druid.zk.service.host=zookeeper/" /opt/imply/conf-quickstart/druid/_common/common.runtime.properties

# Change ports in 808X to 818X to avoid conflict with kafka connect ports

RUN sed -i "s/8081/8181/" /opt/imply/conf-quickstart/druid/coordinator/runtime.properties
RUN sed -i "s/8082/8182/" /opt/imply/conf-quickstart/druid/broker/runtime.properties
RUN sed -i "s/8083/8183/" /opt/imply/conf-quickstart/druid/historical/runtime.properties

EXPOSE 1527 8181 8182 8183 8090 8091 8100 8101 8102 8103 8104 8105 8106 8107 8108 8109 8110 8200 9095

WORKDIR /opt/imply-$implyversion

CMD ["/root/entrypoint.sh"]
