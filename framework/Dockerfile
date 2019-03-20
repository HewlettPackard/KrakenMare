FROM maven:3.6.0-jdk-8-alpine

# proxy settings
COPY mvn-settings.xml /root/.m2/settings.xml

RUN mkdir -p /opt/bluedragon
WORKDIR /opt/bluedragon

COPY pom.xml /opt/bluedragon/
RUN mvn install

COPY src /opt/bluedragon/src
RUN mvn package

EXPOSE 8080

CMD ["mvn", "exec:java"]
