#!/bin/bash

wait_and_configure(){
  # wait for the REST API to be up
  until curl connect:8083/connectors; do
	sleep 5
  done

  /etc/kafka-connect/configure-mqtt-fabric.sh
}

wait_and_configure &

/etc/confluent/docker/run