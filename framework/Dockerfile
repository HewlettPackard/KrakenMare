FROM maven:3.6.0-jdk-8-alpine

RUN mkdir -p /opt/bluedragon
WORKDIR /opt/bluedragon

COPY pom.xml /opt/bluedragon/
ARG MAVEN_OPTS
RUN echo "Using MAVEN_OPTS: $MAVEN_OPTS"
RUN mvn install

COPY src /opt/bluedragon/src
# tests requires a Redis instance: skip them (they are run in the CI)
RUN /mvn.sh package -DskipTests

EXPOSE 8080

CMD ["mvn", "exec:java"]
