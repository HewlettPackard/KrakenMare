FROM confluentinc/cp-kafka-connect:5.0.0

RUN export https_proxy=http://web-proxy.corp.hpecorp.net:8080 \
    && wget https://github.com/Landoop/stream-reactor/releases/download/1.2.0/kafka-connect-mqtt-1.2.0-2.0.0-all.tar.gz \
    && tar zxvpf kafka-connect-mqtt-1.2.0-2.0.0-all.tar.gz && rm kafka-connect-mqtt-1.2.0-2.0.0-all.tar.gz \
    && wget https://github.com/Landoop/stream-reactor/releases/download/1.2.0/kafka-connect-influxdb-1.2.0-2.0.0-all.tar.gz \
    && tar zxvpf kafka-connect-influxdb-1.2.0-2.0.0-all.tar.gz && rm kafka-connect-influxdb-1.2.0-2.0.0-all.tar.gz \
    && mkdir /etc/kafka-connect/custom-plugins \
    && mv *.jar /etc/kafka-connect/custom-plugins \
    && unset https_proxy

COPY configure-mqtt-fabric.sh configure-influxdb.sh entrypoint.sh /etc/kafka-connect/

# see https://github.com/confluentinc/cp-docker-images/issues/638
ENV CONNECT_LOG4J_LOGGERS "org.apache.zookeeper=ERROR,org.I0Itec.zkclient=ERROR,org.reflections=ERROR"

CMD ["/etc/kafka-connect/entrypoint.sh"]