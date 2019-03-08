FROM openjdk:8-jre

RUN export http_proxy=http://web-proxy.corp.hpecorp.net:8080 \
    && apt-get update \
    && apt-get install sqlite3

ARG CMU_BRANCH=master

RUN curl -f -o cmu-jars.zip -H "PRIVATE-TOKEN: znW21MkX4QA2Ez5j2xGP" \
    "http://16.16.184.24/api/v4/projects/60/jobs/artifacts/$CMU_BRANCH/download?job=maven-package" \
    && unzip cmu-jars.zip \
    && cp Java/build/cmu-server-impl-0.0.1-SNAPSHOT-standalone.jar cmuserver.jar \
    && rm -rf Java

# use "mvn assembly:assembly -DdescriptorId=jar-with-dependencies" to build
COPY target/framework-0.0.1-SNAPSHOT-jar-with-dependencies.jar framework.jar

RUN  mkdir -p /opt/clmgr/etc \
    && mkdir -p /opt/clmgr/log \
    && mkdir -p /opt/clmgr/database/db \
    && mkdir -p /opt/clmgr/history/db \
    && mkdir -p /opt/clmgr/history/snapshots

RUN echo "CREATE TABLE userGroup ( \
	id INTEGER PRIMARY KEY AUTOINCREMENT, \
	name TEXT NOT NULL, \
	stateFile TEXT, \
	creationTime INTEGER NOT NULL, \
	deletionTime INTEGER DEFAULT NULL \
);" | sqlite3 /opt/clmgr/history/db/history.sqlite3


ENTRYPOINT java \
    -Dcmu.dev=true \
    -Dcmu.http.authentication.anonymousReadAccess=true \
    -Dcmu.http.authentication.method=token \
    -Dcmu.http.https=true \
    -Dcmu.http.port=8080 \
    -Dcmu.http.additionalHosts=0.0.0.0 \
    -Dcmu.rmi=false \
    -Dcmu.http.static=false \
    -Dcmu.generateLegacyConf=false \
    -Dcmu.writeEtcHosts=false \
    -Dcmu.monitoring.runArchiver=false \
    -cp cmuserver.jar:framework.jar \
    com.hpe.cmu.server.Main
