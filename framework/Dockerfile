#
# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#

FROM maven:3.6.0-jdk-11

RUN echo "framework"

# Requirement for wait-for
RUN apt-get --allow-unauthenticated install -y sed
RUN sed -i 's/http:\/\/debian\./http:\/\/archive\.debian\./' /etc/apt/sources.list
RUN sed -i 's/http:\/\/\deb\.debian\./http:\/\/archive\.debian\./' /etc/apt/sources.list
RUN sed -i 's/deb http:\/\/security/#deb http:\/\/security/' /etc/apt/sources.list
RUN sed -e '/stretch-updates/ s/^#*/#/' -i /etc/apt/sources.list
RUN sed -i 's/http:\/\/\deb\.debian\./http:\/\/archive\.debian\./' /etc/apt/sources.list.d/stretch-backports.list

# Set up the Azul repository to provide zulu
RUN apt-get -yq install gnupg curl 
RUN curl --insecure -O https://cdn.azul.com/zulu/bin/zulu-repo_1.0.0-2_all.deb

# Annoyingly, the key no longer exists
#RUN apt-key adv \
#    --keyserver hkp://keyserver.ubuntu.com:80 \
#    --recv-keys 0xB1998361219BD9C9

RUN apt-get --allow-unauthenticated install ./zulu-repo_1.0.0-2_all.deb
RUN sed -i 's/https:\/\//http:\/\//' /etc/apt/sources.list.d/zulu-openjdk.list
  
RUN apt-get --allow-unauthenticated update \
    && apt-get --allow-unauthenticated install -y netcat wget zulu-11 && apt-get remove -y zulu-8 
RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -                  
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

RUN mkdir -p /opt/krakenmare/framework
WORKDIR /opt/krakenmare/framework

# this is image MUST be built from the upper directory (docker build -f framework/Dockerfile .) to access avro schema
COPY framework/pom.xml /opt/krakenmare/framework/
COPY config-schemaregistry/*.avdl /opt/krakenmare/config-schemaregistry/

ARG MAVEN_OPTS
RUN echo "Using MAVEN_OPTS: $MAVEN_OPTS"
# run a first assembly to cache maven dependencies in the image
RUN mvn assembly:assembly -DdescriptorId=jar-with-dependencies -DskipTests

COPY framework/src /opt/krakenmare/framework/src
# tests requires a Redis instance: skip them (they are run in the CI)
RUN mvn assembly:assembly -DdescriptorId=jar-with-dependencies -DskipTests

COPY framework/entrypoint.sh /opt/krakenmare/framework/entrypoint.sh
COPY framework/src/main/resources/log.properties /opt/krakenmare/framework/log.properties

EXPOSE 8080

ENTRYPOINT /opt/krakenmare/framework/entrypoint.sh
