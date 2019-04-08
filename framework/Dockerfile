FROM maven:3.6.0-jdk-8

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

EXPOSE 8080

CMD ["java", "-cp", "target/framework-0.0.1-SNAPSHOT-jar-with-dependencies.jar", "com.hpe.bluedragon.Main"]
