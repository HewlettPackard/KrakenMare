# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

# Create a minimal image for all config containers.  Use ubuntu:18.04 plus wait-for and it's required tools wget and netcat
FROM ubuntu:18.04 as configbase
# Test env deps
RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y wget netcat

# Build wait for tool
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# Create config zookeeper with needed tools from entrypoint.sh (which is a bash script)
# - bash
# - wait-for (netcat) and wait-for from configbase
# - kafka-configs which is in confluent-kafka
#   Installing this deb needs wget to featch the key, gnupg to validate, add-apt-repository (from software-properties-common) to add the repository
#   The deb file that is installed uses apt-utils to post process it
#   Java is required by kafka-configs. Use the same version that the kafka containers have
FROM ubuntu:18.04
RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y bash netcat wget gnupg gnupg2 gnupg1 software-properties-common apt-utils openjdk-11-jre-headless
COPY --from=configbase /tmp/wait-for /tmp/wait-for
RUN wget -qO - https://packages.confluent.io/deb/5.2/archive.key | apt-key add -
RUN add-apt-repository "deb [arch=amd64] https://packages.confluent.io/deb/5.2 stable main"
RUN apt-get update && apt-get install -y confluent-kafka-2.11

COPY entrypoint.sh /tmp/

CMD ["/tmp/entrypoint.sh"]
