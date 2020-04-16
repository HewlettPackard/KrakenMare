FROM openjdk:8-jdk

# requirement for wait-for
RUN apt update && apt install -y netcat

RUN wget https://downloads.apache.org/druid/0.17.1/apache-druid-0.17.1-bin.tar.gz \
    && tar -xzf apache-druid-0.17.1-bin.tar.gz \
    && mv apache-druid-0.17.1 /opt/druid/

# Swap hdfs for avro as we are only using local storage in all the common properties. These are all the same in this version but are not links
RUN sed -i 's/druid-hdfs-storage/druid-avro-extensions/' /opt/druid/conf/druid/single-server/nano-quickstart/_common/common.runtime.properties
RUN sed -i 's/druid-hdfs-storage/druid-avro-extensions/' /opt/druid/conf/druid/single-server/micro-quickstart/_common/common.runtime.properties
RUN sed -i 's/druid-hdfs-storage/druid-avro-extensions/' /opt/druid/conf/druid/single-server/small/_common/common.runtime.properties
RUN sed -i 's/druid-hdfs-storage/druid-avro-extensions/' /opt/druid/conf/druid/single-server/medium/_common/common.runtime.properties
RUN sed -i 's/druid-hdfs-storage/druid-avro-extensions/' /opt/druid/conf/druid/single-server/large/_common/common.runtime.properties
RUN sed -i 's/druid-hdfs-storage/druid-avro-extensions/' /opt/druid/conf/druid/single-server/xlarge/_common/common.runtime.properties

RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -

RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

COPY entrypoint.sh /tmp/

WORKDIR /opt/druid/
ENTRYPOINT /tmp/entrypoint.sh
