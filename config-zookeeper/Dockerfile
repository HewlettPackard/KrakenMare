# Create a minimal image for all config containers.  Use ubuntu:18.04 plus curl
FROM ubuntu:18.04 as configbase
# Test env deps
RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y bash wget curl netcat

# Build wait for tool
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# Create config zookeeper with needs confluent tools
FROM ubuntu:18.04
RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y bash wget curl gnupg gnupg2 gnupg1 software-properties-common apt-utils netcat openjdk-11-jre-headless
COPY --from=configbase /tmp/wait-for /tmp/wait-for
RUN wget -qO - https://packages.confluent.io/deb/5.2/archive.key | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://packages.confluent.io/deb/5.2 stable main"
RUN apt-get update && apt-get install -y confluent-kafka-2.11

COPY entrypoint.sh /tmp/

CMD ["/tmp/entrypoint.sh"]
