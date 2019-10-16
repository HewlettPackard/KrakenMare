#!/bin/bash
#
# Setup for scaling test. Run on ONE instance only and only once.
#

export  KAFKA_OPTS="-Djava.security.auth.login.config=/run/secrets/broker_jaas.conf"
# In the test below we are sending what Kafka by default considers extra large records (the defaults are roughly 1M)
# To do this we adjust topic to have a size of 9 million, the brokers to support 9 million and producer to support 9 million
# producer configuration is in /run/secrets/client-sasl_ssl.conf
kafka-topics --bootstrap-server broker-1:29092 --delete --topic sasl_ssl  --command-config /run/secrets/client-sasl_ssl.conf
kafka-topics --bootstrap-server broker-1:29092 --create --topic sasl_ssl --partitions 5 --replication-factor 2 --config max.message.bytes=9000000 --command-config /run/secrets/client-sasl_ssl.conf || exit 1
kafka-topics --bootstrap-server broker-1:29092 --topic sasl_ssl --describe --command-config /run/secrets/client-sasl_ssl.conf || exit 1

kafka-configs --bootstrap-server broker-1:29092 --entity-default  --entity-type brokers --alter --add-config message.max.bytes=9000000  --command-config /run/secrets/client-sasl_ssl.conf || exit 1
kafka-configs --bootstrap-server broker-1:29092 --entity-type brokers --describe --entity-default --command-config /run/secrets/client-sasl_ssl.conf || exit 1
