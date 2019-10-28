#!/bin/bash

/tmp/wait-for --timeout=240 zookeeper:2181 || exit 1
/tmp/wait-for --timeout=240 broker-1:9092 || exit 1
/tmp/wait-for --timeout=240 broker-2:9093 || exit 1
/tmp/wait-for --timeout=240 broker-3:9094 || exit 1

kafka-topics --zookeeper zookeeper:2181 --topic fabric --create --partitions 10 --replication-factor 2
kafka-topics --zookeeper zookeeper:2181 --topic fabric --describe
