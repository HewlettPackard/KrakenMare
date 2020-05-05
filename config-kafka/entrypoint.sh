#!/bin/bash

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# -- license --

/tmp/wait-for --timeout=240 zookeeper:2181 || exit 1
/tmp/wait-for --timeout=240 broker-1:29092 || exit 1
/tmp/wait-for --timeout=240 broker-2:29093 || exit 1
/tmp/wait-for --timeout=240 broker-3:29094 || exit 1

# Create fabric topic
export  KAFKA_OPTS="-Djava.security.auth.login.config=/run/secrets/broker_jaas.conf -Djavax.net.ssl.trustStore=/run/secrets/kafka.client.truststore.pfx -Djavax.net.ssl.trustStorePassword=krakenmare -Djavax.net.ssl.keyStore=/run/secrets/kafka.client.keystore.pfx -Djavax.net.ssl.keyStorePassword=krakenmare"
kafka-topics --bootstrap-server broker-1:29092 --delete --topic fabric  --command-config /run/secrets/client-sasl_ssl.conf
kafka-topics --bootstrap-server broker-1:29092 --create --topic fabric --partitions 10 --replication-factor 2 --command-config /run/secrets/client-sasl_ssl.conf || exit 1
kafka-topics --bootstrap-server broker-1:29092 --topic fabric --describe --command-config /run/secrets/client-sasl_ssl.conf || exit 1

# Create registration topics
kafka-topics --bootstrap-server broker-1:29092 --delete --topic agent-registration  --command-config /run/secrets/client-sasl_ssl.conf
kafka-topics --bootstrap-server broker-1:29092 --create --topic agent-registration --config retention.ms=-1 --partitions 1 --replication-factor 3 --command-config /run/secrets/client-sasl_ssl.conf || exit 1
kafka-topics --bootstrap-server broker-1:29092 --topic agent-registration --describe --command-config /run/secrets/client-sasl_ssl.conf || exit 1
kafka-topics --bootstrap-server broker-1:29092 --delete --topic device-registration  --command-config /run/secrets/client-sasl_ssl.conf
kafka-topics --bootstrap-server broker-1:29092 --create --topic device-registration --config retention.ms=-1  --partitions 1 --replication-factor 3 --command-config /run/secrets/client-sasl_ssl.conf || exit 1
kafka-topics --bootstrap-server broker-1:29092 --topic device-registration --describe --command-config /run/secrets/client-sasl_ssl.conf || exit 1
kafka-topics --bootstrap-server broker-1:29092 --delete --topic agent-deregistration  --command-config /run/secrets/client-sasl_ssl.conf
kafka-topics --bootstrap-server broker-1:29092 --create --topic agent-deregistration --config retention.ms=-1 --partitions 1 --replication-factor 3 --command-config /run/secrets/client-sasl_ssl.conf || exit 1
kafka-topics --bootstrap-server broker-1:29092 --topic agent-deregistration --describe --command-config /run/secrets/client-sasl_ssl.conf || exit 1
