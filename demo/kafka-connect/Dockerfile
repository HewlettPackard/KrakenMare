FROM confluentinc/cp-kafka-connect:5.0.0

ENV http_proxy http://web-proxy.corp.hpecorp.net:8080
ENV https_proxy http://web-proxy.corp.hpecorp.net:8080

RUN wget https://github.com/Landoop/stream-reactor/releases/download/1.2.0/kafka-connect-elastic6-1.2.0-2.0.0-all.tar.gz \
    && tar zxvpf kafka-connect-elastic6-1.2.0-2.0.0-all.tar.gz && rm kafka-connect-elastic6-1.2.0-2.0.0-all.tar.gz \
    && wget https://github.com/Landoop/stream-reactor/releases/download/1.2.0/kafka-connect-mqtt-1.2.0-2.0.0-all.tar.gz \
    && tar zxvpf kafka-connect-mqtt-1.2.0-2.0.0-all.tar.gz && rm kafka-connect-mqtt-1.2.0-2.0.0-all.tar.gz \
    && mkdir /etc/kafka-connect/custom-plugins \
    && mv *.jar /etc/kafka-connect/custom-plugins
