FROM maven:3.6.0-jdk-11

# requirement for wait-for
RUN apt update && apt install -y netcat

RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

RUN mkdir -p /opt/krakenmare/framework
WORKDIR /opt/krakenmare/framework

# this is image MUST be built from the upper directory (docker build -f framework/Dockerfile .) to access avro schema
COPY framework/pom.xml /opt/krakenmare/framework/
COPY config-schemaregistry/protocol.avdl /opt/krakenmare/config-schemaregistry/

ARG MAVEN_OPTS
RUN echo "Using MAVEN_OPTS: $MAVEN_OPTS"
# run a first assembly to cache maven dependencies in the image
# src/main/resources/velocity-templates/record.vm shall exist or avro-maven-plugin will fail
COPY framework/src/main/resources/velocity-templates/ /opt/krakenmare/framework/src/main/resources/velocity-templates/
RUN mvn assembly:assembly -DdescriptorId=jar-with-dependencies -DskipTests

COPY framework/src /opt/krakenmare/framework/src
# tests requires a Redis instance: skip them (they are run in the CI)
RUN mvn assembly:assembly -DdescriptorId=jar-with-dependencies -DskipTests

COPY framework/entrypoint.sh /opt/krakenmare/framework/entrypoint.sh

EXPOSE 8080

ENTRYPOINT /opt/krakenmare/framework/entrypoint.sh
