#!/bin/bash
echo "removing Elastic Sink Connector for agent registration"
curl -X DELETE "https://connect:8083/connectors/elastic-sink-agent-registration" --cert /run/secrets/connect.certificate.pem --key /run/secrets/connect.key  --cacert /run/secrets/km-ca-1.crt

echo ""
echo "creating Elastic Sink Connector for agent registration"

curl -X POST "https://connect:8083/connectors" \
     -H "Content-Type: application/json" \
     -d '{
  "name": "elastic-sink-agent-registration",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "connection.url": "http://elastic:9200",
    "type.name": "_doc",
    "tasks.max": "1",
    "topics": "agent-registration",
    "key.ignore": "true",
    "schema.ignore": "false",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://schemaregistry:8085",
    "value.converter.schema.enable": "true",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "key.converter.schema.registry.url": "http://schemaregistry:8085",
    "key.converter.schema.enable": "false"
  }
  }' --cert /run/secrets/connect.certificate.pem --key /run/secrets/connect.key  --cacert /run/secrets/km-ca-1.crt

echo ""
echo "removing Elastic Sink Connector for device registration"
curl -X DELETE "https://connect:8083/connectors/elastic-sink-device-registration" --cert /run/secrets/connect.certificate.pem --key /run/secrets/connect.key  --cacert /run/secrets/km-ca-1.crt

echo ""
echo "creating Elastic Sink Connector for device registration"

curl -X POST "https://connect:8083/connectors" \
     -H "Content-Type: application/json" \
     -d '{
  "name": "elastic-sink-device-registration",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "connection.url": "http://elastic:9200",
    "type.name": "_doc",
    "tasks.max": "1",
    "topics": "device-registration",
    "key.ignore": "false",
    "schema.ignore": "false",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://schemaregistry:8085",
    "value.converter.schema.enable": "true",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "key.converter.schema.registry.url": "http://schemaregistry:8085",
    "key.converter.schema.enable": "false"
  }
  }' --cert /run/secrets/connect.certificate.pem --key /run/secrets/connect.key  --cacert /run/secrets/km-ca-1.crt

echo ""
echo "removing Elastic Sink Connector for agent deregistration"
curl -X DELETE "https://connect:8083/connectors/elastic-sink-agent-deregistration" --cert /run/secrets/connect.certificate.pem --key /run/secrets/connect.key  --cacert /run/secrets/km-ca-1.crt

echo ""
echo "creating Elastic Sink Connector for agent deregistration"

curl -X POST "https://connect:8083/connectors" \
     -H "Content-Type: application/json" \
     -d '{
  "name": "elastic-sink-agent-deregistration",
  "config": {
    "connector.class": "io.confluent.connect.elasticsearch.ElasticsearchSinkConnector",
    "connection.url": "http://elastic:9200",
    "type.name": "_doc",
    "tasks.max": "1",
    "topics": "agent-deregistration",
    "key.ignore": "true",
    "schema.ignore": "false",
    "value.converter": "io.confluent.connect.avro.AvroConverter",
    "value.converter.schema.registry.url": "http://schemaregistry:8085",
    "value.converter.schema.enable": "true",
    "key.converter": "org.apache.kafka.connect.storage.StringConverter",
    "key.converter.schema.registry.url": "http://schemaregistry:8085",
    "key.converter.schema.enable": "false"
  }
  }' --cert /run/secrets/connect.certificate.pem --key /run/secrets/connect.key  --cacert /run/secrets/km-ca-1.crt
  
