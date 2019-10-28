#!/bin/bash

wait_for_connect_REST_API(){
  # wait for connect REST API to be up
  until curl connect:8083/connectors; do
    sleep 5
  done

}

/tmp/wait-for --timeout=240 broker-1:9092 || exit 1
/tmp/wait-for --timeout=240 broker-2:9093 || exit 1
/tmp/wait-for --timeout=240 broker-3:9094 || exit 1

wait_for_connect_REST_API &

/etc/confluent/docker/run
