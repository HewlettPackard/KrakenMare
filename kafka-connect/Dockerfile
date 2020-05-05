FROM confluentinc/cp-kafka-connect:5.4.0

# requirement for wait-for
RUN  apt-get update && apt-get install -y netcat wget sed zulu-11 unzip && apt-get remove -y zulu-8 
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# get 6.0 beta with fix for https://github.com/confluentinc/kafka-connect-elasticsearch/issues/381 and https://github.com/confluentinc/kafka-connect-elasticsearch/issues/390
RUN cd /tmp/ && wget --no-check-certificate https://github.com/wucheong/kafka-connect-elasticsearch/releases/download/6.0.0-SNAPSHOT/kafka-connect-elasticsearch-6.0.0-SNAPSHOT.zip
RUN cd /tmp/ && unzip kafka-connect-elasticsearch-6.0.0-SNAPSHOT.zip kafka-connect-elasticsearch-6.0.0-SNAPSHOT-package/share/java/kafka-connect-elasticsearch/kafka-connect-elasticsearch-6.0.0-SNAPSHOT.jar && \
    rm kafka-connect-elasticsearch-6.0.0-SNAPSHOT.zip && \
    cp kafka-connect-elasticsearch-6.0.0-SNAPSHOT-package/share/java/kafka-connect-elasticsearch/kafka-connect-elasticsearch-6.0.0-SNAPSHOT.jar /tmp && \
    unzip kafka-connect-elasticsearch-6.0.0-SNAPSHOT.jar && \
    if ! grep -q MAX_CONNECTION_IDLE_TIME_MS_CONFIG io/confluent/connect/elasticsearch/ElasticsearchSinkConnectorConfig.class ; then echo "Connection idle time config not found" ; exit 1; fi && \
    mv kafka-connect-elasticsearch-6.0.0-SNAPSHOT-package/share/java/kafka-connect-elasticsearch/kafka-connect-elasticsearch-6.0.0-SNAPSHOT.jar /usr/share/java/kafka-connect-elasticsearch/kafka-connect-elasticsearch-5.4.0.jar && \
    rm kafka-connect-elasticsearch-6.0.0-SNAPSHOT.jar kafka-connect-elasticsearch-version.properties && \
    rm -r META-INF io kafka-connect-elasticsearch-6.0.0-SNAPSHOT-package

COPY entrypoint.sh /etc/confluent/docker/

CMD ["/etc/confluent/docker/entrypoint.sh"]
