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

export  KAFKA_OPTS="-Djava.security.auth.login.config=/run/secrets/broker_jaas.conf"
kafka-configs --zookeeper zookeeper:2181 --alter --add-config 'SCRAM-SHA-256=[password=schemaregistry-secret],SCRAM-SHA-512=[password=schemaregistry-secret]' --entity-type users --entity-name schemaregistry
kafka-configs --zookeeper zookeeper:2181 --alter --add-config 'SCRAM-SHA-256=[password=client-secret],SCRAM-SHA-512=[password=client-secret]' --entity-type users --entity-name client
kafka-configs --zookeeper zookeeper:2181 --alter --add-config 'SCRAM-SHA-256=[password=broker-secret],SCRAM-SHA-512=[password=broker-secret]' --entity-type users --entity-name broker
kafka-configs --zookeeper zookeeper:2181 --alter --add-config 'SCRAM-SHA-256=[password=kakfasecret],SCRAM-SHA-512=[password=kafkasecret]' --entity-type users --entity-name kafka
