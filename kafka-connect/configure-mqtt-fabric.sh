#!/bin/bash

echo "creating Kafka topics"

kafka-topics --zookeeper zookeeper:2181 --topic fabric --partitions 3 --replication-factor 3 --create
kafka-topics --zookeeper zookeeper:2181 --topic hello --partitions 3 --replication-factor 3 --create

echo ""
echo "removing MQTT Sink Connector"

curl -X DELETE "connect:8083/connectors/mqtt-sink-reg-res"

echo ""
echo "creating MQTT Sink Connector"

curl -X POST "connect:8083/connectors" \
     -H "Content-Type: application/json" \
     -d $'{
  "name": "mqtt-sink-reg-res",
  "config": {
    "connector.class": "com.datamountaineer.streamreactor.connect.mqtt.sink.MqttSinkConnector",
    "tasks.max": "1",
    "topics": "registration-result",
    "connect.mqtt.connection.clean": "true",
    "connect.mqtt.connection.timeout": "1000",
    "connect.mqtt.kcql": "INSERT INTO registration-result SELECT * FROM registration-result WITHCONVERTER=`com.datamountaineer.streamreactor.connect.converters.source.JsonSimpleConverter`",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "connect.mqtt.connection.keep.alive": "1000",
    "connect.mqtt.client.id": "mqtt-connect-sink",
    "connect.mqtt.converter.throw.on.error": "true",
    "connect.mqtt.hosts": "tcp://mosquitto:1883",
    "connect.mqtt.service.quality": "2"
  }
  }'

echo ""
echo "removing MQTT IBswitch and Registration Source Connector"

curl -X DELETE "connect:8083/connectors/mqtt-source-ibswitch"
curl -X DELETE "connect:8083/connectors/mqtt-source-reg-req"

echo ""
echo "creating MQTT IBswitch Source Connector"

curl -X POST "connect:8083/connectors" \
     -H "Content-Type: application/json" \
     -d $'{
  "name": "mqtt-source-ibswitch",
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
echo "creating MQTT Registration Request Source Connector"

curl -X POST "connect:8083/connectors" \
     -H "Content-Type: application/json" \
     -d $'{
  "name": "mqtt-source-reg-req",
  "config": {
    "connector.class": "com.datamountaineer.streamreactor.connect.mqtt.source.MqttSourceConnector",
    "tasks.max": "1",
    "connect.mqtt.connection.clean": "true",
    "connect.mqtt.connection.timeout": "1000",
    "connect.mqtt.kcql": "INSERT INTO registration-request SELECT * FROM registration-request/+ WITHCONVERTER=`com.datamountaineer.streamreactor.connect.converters.source.JsonSimpleConverter`",
    "key.converter": "org.apache.kafka.connect.json.JsonConverter",
    "key.converter.schemas.enable": "false",
    "value.converter": "org.apache.kafka.connect.json.JsonConverter",
    "value.converter.schemas.enable": "false",
    "connect.mqtt.connection.keep.alive": "1000",
    "connect.mqtt.client.id": "mqtt-connect-02",
    "connect.mqtt.converter.throw.on.error": "true",
    "connect.mqtt.hosts": "tcp://mosquitto:1883",
    "connect.mqtt.service.quality": "2"
  }
  }'
