#!/bin/bash

/etc/confluent/docker/run

# wait for the REST API to be up
until curl connect:8083/connectors; do
	sleep 5
done

./configure-mqtt-fabric.sh