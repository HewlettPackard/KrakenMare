FROM confluentinc/cp-enterprise-kafka:5.2.0

# requirement for wait-for
RUN  apt-get update && apt-get install -y netcat wget
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -                  
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

COPY entrypoint.sh /etc/confluent/docker/

CMD ["/etc/confluent/docker/entrypoint.sh"]
