#!/bin/bash

echo ""
echo "configuring InfluxDB database"

curl -X POST http://influxdb:8086/query --data-urlencode "q=CREATE DATABASE monitoring"

echo "removing InfluxDB Sink Connector"

curl -X DELETE "connect:8083/connectors/influx-sink"

echo ""
echo "creating InfluxDB Sink Connector"

curl -X "POST" "connect:8083/connectors" \
     -H "Content-Type: application/json" \
     -d $'{
  "name": "influx-sink",
  "config": {
    "connector.class": "com.datamountaineer.streamreactor.connect.influx.InfluxSinkConnector",
    "tasks.max": "1",
    "topics": "fabric",
    "connect.influx.url": "http://influxdb:8086",
    "connect.influx.db": "monitoring",
    "connect.influx.username": "influxdb",
    "connect.influx.kcql": "INSERT INTO perfquery SELECT * FROM fabric WITHTIMESTAMP Timestamp",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false"
  }
  }'
