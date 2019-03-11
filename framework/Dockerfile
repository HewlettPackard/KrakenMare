FROM maven:3.6.0-jdk-8

COPY mvn-settings.xml /root/.m2/settings.xml

RUN mkdir -p /opt/framework
WORKDIR /opt/framework

COPY pom.xml /opt/framework/
RUN mvn install

COPY src /opt/framework/src
RUN mvn package

EXPOSE 8080

CMD ["mvn", "exec:java"]
