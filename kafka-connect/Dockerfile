FROM confluentinc/cp-kafka-connect:5.2.0

# requirement for wait-for
RUN apt update && apt install -y netcat wget

RUN wget https://github.com/Landoop/stream-reactor/releases/download/1.2.0/kafka-connect-mqtt-1.2.0-2.0.0-all.tar.gz \
    && tar zxvpf kafka-connect-mqtt-1.2.0-2.0.0-all.tar.gz && rm kafka-connect-mqtt-1.2.0-2.0.0-all.tar.gz \
    && mkdir /etc/kafka-connect/custom-plugins \
    && mv *.jar /etc/kafka-connect/custom-plugins

COPY configure-mqtt-fabric.sh perfquery-index.json entrypoint.sh collectd-index.json /etc/kafka-connect/

# see https://github.com/confluentinc/cp-docker-images/issues/638
ENV CONNECT_LOG4J_LOGGERS "org.apache.zookeeper=ERROR,org.I0Itec.zkclient=ERROR,org.reflections=ERROR"

RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -                  

RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/


CMD ["/etc/kafka-connect/entrypoint.sh"]
