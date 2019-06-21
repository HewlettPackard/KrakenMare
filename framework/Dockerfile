FROM maven:3.6.0-jdk-8

# requirement for wait-for
RUN apt update && apt install -y netcat

RUN mkdir -p /opt/bluedragon
WORKDIR /opt/bluedragon

COPY pom.xml /opt/bluedragon/
ARG MAVEN_OPTS
RUN echo "Using MAVEN_OPTS: $MAVEN_OPTS"
# run a first assembly to cache maven dependencies in the image
RUN mvn assembly:assembly -DdescriptorId=jar-with-dependencies -DskipTests

COPY src /opt/bluedragon/src
# tests requires a Redis instance: skip them (they are run in the CI)
RUN mvn assembly:assembly -DdescriptorId=jar-with-dependencies -DskipTests

RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -

RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

COPY entrypoint.sh /tmp/

EXPOSE 8080

ENTRYPOINT /tmp/entrypoint.sh
