FROM openjdk:8-jdk

# requirement for wait-for
RUN apt update && apt install -y netcat

RUN wget https://static.imply.io/release/imply-3.1.4.tar.gz \
    && tar -xzf imply-3.1.4.tar.gz \
    && mv imply-3.1.4 /opt/druid/

# Change to zookeeper already existing outside this container
COPY quickstart-no-zk.conf /opt/druid/quickstart/tutorial/conf/quickstart-no-zk.conf
RUN sed -i "s/druid.zk.service.host=localhost/druid.zk.service.host=zookeeper/" /opt/druid/conf-quickstart/druid/_common/common.runtime.properties
# Add Avro extension to loadList
RUN sed -i 's/"imply-utility-belt"/"imply-utility-belt", "druid-avro-extensions"/' /opt/druid/conf-quickstart/druid/_common/common.runtime.properties

RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -

RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

COPY entrypoint.sh /tmp/

WORKDIR /opt/druid/
ENTRYPOINT /tmp/entrypoint.sh
