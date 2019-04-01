FROM maven:3.6.0-jdk-8-alpine

RUN mkdir -p /opt/bluedragon
WORKDIR /opt/bluedragon

COPY pom.xml /opt/bluedragon/
ARG MAVEN_OPTS
RUN echo "Using MAVEN_OPTS: $MAVEN_OPTS"
RUN mvn dependency:go-offline

COPY src /opt/bluedragon/src
# tests requires a Redis instance: skip them (they are run in the CI)
RUN mvn assembly:assembly -DdescriptorId=jar-with-dependencies -DskipTests
COPY target/framework-0.0.1-SNAPSHOT-jar-with-dependencies.jar framework.jar

EXPOSE 8080

CMD ["java", "-cp", "framework.jar", "com.hpe.bluedragon.Main"]
