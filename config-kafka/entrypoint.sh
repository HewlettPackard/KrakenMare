#!/bin/bash

/tmp/wait-for --timeout=240 zookeeper:2181 || exit 1
/tmp/wait-for --timeout=240 broker-1:9092 || exit 1
/tmp/wait-for --timeout=240 broker-2:9093 || exit 1
/tmp/wait-for --timeout=240 broker-3:9094 || exit 1

# Create fabric topic
export  KAFKA_OPTS="-Djava.security.auth.login.config=/run/secrets/broker_jaas.conf -Djavax.net.ssl.trustStore=/run/secrets/kafka.client.truststore.pfx -Djavax.net.ssl.trustStorePassword=krakenmare -Djavax.net.ssl.keyStore=/run/secrets/kafka.client.keystore.pfx -Djavax.net.ssl.keyStorePassword=krakenmare"
kafka-topics --bootstrap-server broker-1:29092 --delete --topic fabric  --command-config /run/secrets/client-sasl_ssl.conf
kafka-topics --bootstrap-server broker-1:29092 --create --topic fabric --partitions 10 --replication-factor 2 --command-config /run/secrets/client-sasl_ssl.conf || exit 1
kafka-topics --bootstrap-server broker-1:29092 --topic fabric --describe --command-config /run/secrets/client-sasl_ssl.conf || exit 1
