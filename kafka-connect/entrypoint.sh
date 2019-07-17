#!/bin/bash

wait_for_connect_REST_API(){
  # wait for connect REST API to be up
  until curl connect:8083/connectors; do
    sleep 5
  done

  /etc/kafka-connect/configure-mqtt-fabric.sh

}

wait_and_configure_druid_supervisor(){
  # wait for supervisor rest API to be up
  until curl druid:8090/druid/indexer/v1/supervisor; do
     sleep 5
  done

  # Load the indexer for simulator data
  curl -XPOST -H'Content-Type: application/json' -d @/etc/kafka-connect/perfquery-index.json http://druid:8090/druid/indexer/v1/supervisor
  # Load the indexer for collectd data
  curl -XPOST -H'Content-Type: application/json' -d @/etc/kafka-connect/collectd-index.json http://druid:8090/druid/indexer/v1/supervisor

}

/tmp/wait-for --timeout=240 broker-1:9092 || exit 1
/tmp/wait-for --timeout=240 broker-2:9093 || exit 1
/tmp/wait-for --timeout=240 broker-3:9094 || exit 1

wait_for_connect_REST_API &
wait_and_configure_druid_supervisor &

/etc/confluent/docker/run
