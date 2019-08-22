FROM maven:3.6.0-jdk-11

# requirement for wait-for
RUN apt update && apt install -y netcat

RUN cd /tmp/ && wget --no-check-certificate https://api.github.com/repos/eficode/wait-for/tarball/828386460d138e418c31a1ebf87d9a40f5cedc32 -O - | tar xzf -
RUN mv /tmp/eficode-wait-for-*/wait-for /tmp/

# jprofiler 8.1
RUN wget https://download-gcdn.ej-technologies.com/jprofiler/jprofiler_linux_8_1_4.tar.gz -P /tmp/ && \
  tar -xzf /tmp/jprofiler_linux_8_1_4.tar.gz -C /opt/ && \
  rm /tmp/jprofiler_linux_8_1_4.tar.gz

RUN mkdir -p /opt/krakenmare
WORKDIR /opt/krakenmare

COPY pom.xml /opt/krakenmare/
ARG MAVEN_OPTS
RUN echo "Using MAVEN_OPTS: $MAVEN_OPTS"
# run a first assembly to cache maven dependencies in the image
RUN mvn assembly:assembly -DdescriptorId=jar-with-dependencies -DskipTests

COPY src /opt/krakenmare/src
# tests requires a Redis instance: skip them (they are run in the CI)
RUN mvn assembly:assembly -DdescriptorId=jar-with-dependencies -DskipTests

COPY entrypoint.sh /opt/krakenmare/entrypoint.sh

EXPOSE 8080

ENTRYPOINT /opt/krakenmare/entrypoint.sh
