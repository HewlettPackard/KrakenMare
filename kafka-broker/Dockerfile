FROM confluentinc/cp-enterprise-kafka:5.2.0

# requirement for wait-for
RUN  apt-get update && apt-get install -y netcat wget
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -                  
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# jprofiler 8.1
RUN wget https://download-gcdn.ej-technologies.com/jprofiler/jprofiler_linux_8_1_4.tar.gz -P /tmp/ && \
  tar -xzf /tmp/jprofiler_linux_8_1_4.tar.gz -C /opt/ && \
  rm /tmp/jprofiler_linux_8_1_4.tar.gz

COPY entrypoint.sh /etc/confluent/docker/

CMD ["/etc/confluent/docker/entrypoint.sh"]
