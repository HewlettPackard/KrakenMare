#!/bin/bash

/tmp/wait-for --timeout=240 druid:8090 || exit 1

# wait for supervisor rest API to be up
until curl druid:8090/druid/indexer/v1/supervisor; do
  sleep 5
done

# Load the indexer for simulator data
curl -s -XPOST -H'Content-Type: application/json' -d @/tmp/perfquery-index.json http://druid:8090/druid/indexer/v1/supervisor
curl -s druid:8090/druid/indexer/v1/supervisor | jq .
# Load the indexer for collectd data
curl -s -XPOST -H'Content-Type: application/json' -d @/tmp/collectd-index.json http://druid:8090/druid/indexer/v1/supervisor || exit 1
curl -s druid:8090/druid/indexer/v1/supervisor | jq .
