FROM confluentinc/cp-kafka-connect:5.2.0

# requirement for wait-for
RUN apt update && apt install -y netcat wget zulu-11 && apt remove -y zulu-8

COPY entrypoint.sh /etc/kafka-connect/

# see https://github.com/confluentinc/cp-docker-images/issues/638
ENV CONNECT_LOG4J_LOGGERS "org.apache.zookeeper=ERROR,org.I0Itec.zkclient=ERROR,org.reflections=ERROR"

RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -                  

RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

CMD ["/etc/kafka-connect/entrypoint.sh"]
