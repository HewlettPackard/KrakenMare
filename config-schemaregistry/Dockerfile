# Create a minimal image for all config containers.  Use ubuntu:18.04 plus wait-for and it's required tools wget and netcat
FROM ubuntu:18.04 as configbase
# Test env deps
RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y wget netcat

# Build wait for tool
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# Create config schemaregistry with needed tools from entrypoint.sh (which is a bash script)
# - bash
# - wait-for (netcat) and wait-for from configbase
# - python for script that pushes to schemaregistry. Plus os, sys and requests modules.
# - curl to get avro-cli
# - apt-utils to process deb conf
# - avro-cli to check the validity of avro schema files
# - Java 8 is required by avro-cli (java 11 causes issues with Springframework)
# - jq to extract schema topic from the avro file
FROM ubuntu:18.04
RUN apt-get update && apt-get upgrade -y
RUN apt-get update && apt-get install -y bash netcat python3 python3-requests openjdk-8-jre-headless curl apt-utils jq
RUN cd /tmp/ && curl -L -O https://github.com/rkluszczynski/avro-cli/releases/download/avro-cli-0.2.7/avro-cli-0.2.7.jar
RUN cd /tmp/ && curl -L -O https://repo1.maven.org/maven2/org/apache/avro/avro-tools/1.9.1/avro-tools-1.9.1.jar
COPY --from=configbase /tmp/wait-for /tmp/wait-for

COPY *.avdl register_schema.py entrypoint.sh /tmp/

CMD ["/tmp/entrypoint.sh"]
