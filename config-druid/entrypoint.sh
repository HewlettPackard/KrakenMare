#!/bin/bash

wait_and_configure_druid_supervisor(){
  # wait for supervisor rest API to be up
  until curl druid:8090/druid/indexer/v1/supervisor; do
     sleep 5
  done

  # Load the indexer for simulator data
  curl -XPOST -H'Content-Type: application/json' -d @/tmp/perfquery-index.json http://druid:8090/druid/indexer/v1/supervisor
  # Load the indexer for collectd data
  curl -XPOST -H'Content-Type: application/json' -d @/tmp/collectd-index.json http://druid:8090/druid/indexer/v1/supervisor

}

wait_and_configure_druid_supervisor &
