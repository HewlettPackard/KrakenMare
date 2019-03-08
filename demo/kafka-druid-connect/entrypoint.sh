#!/bin/bash

wait_and_configure_kafka(){
  # wait for connect REST API to be up
  until curl connect:8083/connectors; do
    sleep 5
  done

  /etc/kafka-connect/configure-mqtt-fabric.sh

}

wait_and_configure_druid(){
  # wait for supervisor rest API to be up
  until curl druid:8090/druid/indexer/v1/supervisor; do
     sleep 5
  done

  # Load the indexer for simulator data
  curl -XPOST -H'Content-Type: application/json' -d @/etc/kafka-connect/perfquery-index.json http://druid:8090/druid/indexer/v1/supervisor

}

wait_and_configure_kafka &
wait_and_configure_druid &

/etc/confluent/docker/run
