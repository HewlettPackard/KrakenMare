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

#
# Setup for scaling test. Run on ONE instance only and only once.
#

export  KAFKA_OPTS="-Djava.security.auth.login.config=/run/secrets/broker_jaas.conf"
# In the test below we are sending what Kafka by default considers extra large records (the defaults are roughly 1M)
# To do this we adjust topic to have a size of 9 million, the brokers to support 9 million and producer to support 9 million
# producer configuration is in /run/secrets/client-sasl_ssl.conf
kafka-topics --bootstrap-server broker-1:29092 --delete --topic sasl_ssl  --command-config /run/secrets/client-sasl_ssl.conf
kafka-topics --bootstrap-server broker-1:29092 --create --topic sasl_ssl --partitions 10 --replication-factor 2 --command-config /run/secrets/client-sasl_ssl.conf || exit 1
kafka-topics --bootstrap-server broker-1:29092 --topic sasl_ssl --describe --command-config /run/secrets/client-sasl_ssl.conf || exit 1
