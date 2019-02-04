#!/bin/bash

wait_and_configure(){
  # wait for connect REST API to be up
  until curl connect:8083/connectors; do
    sleep 5
  done

  /etc/kafka-connect/configure-mqtt-fabric.sh

  # now wait for influxdb REST API to be up
  until curl influxdb:8086/query; do
    sleep 5
  done

  /etc/kafka-connect/configure-influxdb.sh
}

wait_and_configure &

/etc/confluent/docker/run