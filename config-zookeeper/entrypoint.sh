#!/bin/bash

/tmp/wait-for --timeout=240 zookeeper:2181 || exit 1

export  KAFKA_OPTS="-Djava.security.auth.login.config=/run/secrets/broker_jaas.conf"
kafka-configs --zookeeper zookeeper:2181 --alter --add-config 'SCRAM-SHA-256=[password=schemaregistry-secret],SCRAM-SHA-512=[password=schemaregistry-secret]' --entity-type users --entity-name schemaregistry
kafka-configs --zookeeper zookeeper:2181 --alter --add-config 'SCRAM-SHA-256=[password=client-secret],SCRAM-SHA-512=[password=client-secret]' --entity-type users --entity-name client
kafka-configs --zookeeper zookeeper:2181 --alter --add-config 'SCRAM-SHA-256=[password=broker-secret],SCRAM-SHA-512=[password=broker-secret]' --entity-type users --entity-name broker
kafka-configs --zookeeper zookeeper:2181 --alter --add-config 'SCRAM-SHA-256=[password=kakfasecret],SCRAM-SHA-512=[password=kafkasecret]' --entity-type users --entity-name kafka
