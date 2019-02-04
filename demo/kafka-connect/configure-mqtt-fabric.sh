#!/bin/bash

echo "removing MQTT Source Connector"

curl -X "DELETE" "connect:8083/connectors/mqtt-source"

echo ""
echo "creating MQTT Source Connector"

curl -X "POST" "connect:8083/connectors" \
     -H "Content-Type: application/json" \
     -d $'{
  "name": "mqtt-source",
  "config": {
    "connector.class": "com.datamountaineer.streamreactor.connect.mqtt.source.MqttSourceConnector",
    "tasks.max": "1",
    "connect.mqtt.connection.clean": "true",
    "connect.mqtt.connection.timeout": "1000",
    "connect.mqtt.kcql": "INSERT INTO fabric SELECT * FROM ibswitch WITHCONVERTER=`com.datamountaineer.streamreactor.connect.converters.source.JsonSimpleConverter`",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "connect.mqtt.connection.keep.alive": "1000",
    "connect.mqtt.client.id": "mqtt-connect-01",
    "connect.mqtt.converter.throw.on.error": "true",
    "connect.mqtt.hosts": "tcp://mosquitto:1883",
    "connect.mqtt.service.quality": "0"
  }
  }'

echo ""
echo "creating Kafka topic"

kafka-topics --zookeeper zookeeper:2181 --topic fabric --partitions 3 --replication-factor 3 --create