#!/bin/bash

/tmp/wait-for --timeout=240 zookeeper:2181 || exit 1

/etc/confluent/docker/run
