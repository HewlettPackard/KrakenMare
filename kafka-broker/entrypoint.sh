#!/bin/bash

/tmp/wait-for --timeout=240 zookeeper:2181 || exit 1
sed -i -e s[/etc/kafka/secrets[/run/secrets[ /etc/confluent/docker/configure

/etc/confluent/docker/run
