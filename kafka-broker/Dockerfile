FROM confluentinc/cp-enterprise-kafka:5.2.0

# requirement for wait-for
RUN  apt-get update && apt-get install -y netcat wget sed zulu-11 && apt-get remove -y zulu-8 
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -                  
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# JMX Prometheus exporter
RUN mkdir /opt/prometheus &&\
    wget https://repo1.maven.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.12.0/jmx_prometheus_javaagent-0.12.0.jar -P /opt/prometheus &&\
    wget https://github.com/prometheus/jmx_exporter/raw/master/example_configs/kafka-2_0_0.yml -P /opt/prometheus

COPY entrypoint.sh /etc/confluent/docker/

CMD ["/etc/confluent/docker/entrypoint.sh"]
