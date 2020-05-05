#!/bin/bash

/tmp/wait-for --timeout=240 zookeeper:2181 || exit 1
/tmp/wait-for --timeout=240 broker-1:29092 || exit 1
/tmp/wait-for --timeout=240 broker-2:29093 || exit 1
/tmp/wait-for --timeout=240 broker-3:29094 || exit 1

/etc/confluent/docker/run
