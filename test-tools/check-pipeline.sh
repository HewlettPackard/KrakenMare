#!/bin/bash
# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.


run_me()
{
    tf=/tmp/$1
    shift
    a="$@"
    #echo -n "running: $a"
    printf "running:%-40.40s" "$a"
    r=0
    { eval "$@" &> $tf ; } || { echo -n " ko "; r=1 ; }
    if [ "$r" == 0 ] ; then echo -n " ok " ; fi
    echo "... see logs <$tf>"
    return $r
}

cat > /tmp/druid_collectd.json <<EOF
{
    "queryType" : "timeBoundary",
    "dataSource": "collectd"
}
EOF

cat > /tmp/druid_perfquery.json <<EOF
{
    "queryType" : "timeBoundary",
    "dataSource": "perfquery"
}
EOF

run_me mosquitto  timeout 10 mosquitto_sub -h mosquitto  -p 8883 --cafile /run/secrets/km-ca-1.crt --cert /run/secrets/mosquitto.certificate.pem --key /run/secrets/mosquitto.key --keyform pem -t '\$'SYS/broker/version -C 1 || exit 1
run_me broker-1       kafkacat -b broker-1 -L                     || exit 1
run_me broker-2       kafkacat -b broker-2:9093 -L                || exit 1
run_me broker-3       kafkacat -b broker-3:9094 -L                || exit 1
run_me redis          redis-cli -h redis ping                     || exit 1
run_me framework      curl -s framework:8080/agents               || exit 1
#run_me influx         curl -s influxdb:8086/ping                  || exit 1
#run_me kafka-avro-console kafka-avro-console-consumer --bootstrap-server broker-1:29092 --topic fabric --property schema.registry.url=https://schemaregistry:8081 --consumer.config /run/secrets/client-sasl_ssl.conf --max-messages=1 || exit 1
run_me druid_coord    curl -s http://druid:8081/status/health     || exit 1
run_me druid_broker   curl -s http://druid:8082/status/health     || exit 1
run_me druid_histo    curl -s http://druid:8083/status/health     || exit 1
run_me druid_overlord curl -s http://druid:8090/status/health     || exit 1
run_me druid_middle   curl -s http://druid:8091/status/health     || exit 1
#run_me druid_perfquery  'curl -s -X 'POST' -H 'Content-Type:application/json' -d @/tmp/druid_perfquery.json http://druid:8082/druid/v2?pretty | grep timestamp' || exit 1
#run_me druid_collectd   'curl -s -X 'POST' -H 'Content-Type:application/json' -d @/tmp/druid_collectd.json   http://druid:8082/druid/v2?pretty | grep timestamp' || exit 1
run_me ssl-broker-1   kafkacat -L -X ssl.ca.location=/run/secrets/km-ca-1.crt -X ssl.certificate.location=/run/secrets/client.certificate.pem -X ssl.key.location=/run/secrets/client.key -X ssl.key.password=krakenmare -X security.protocol=ssl -b broker-1:19092 || exit 1
run_me ssl-broker-2   kafkacat -L -X ssl.ca.location=/run/secrets/km-ca-1.crt -X ssl.certificate.location=/run/secrets/client.certificate.pem -X ssl.key.location=/run/secrets/client.key -X ssl.key.password=krakenmare -X security.protocol=ssl -b broker-2:19093 || exit 1
run_me ssl-broker-3   kafkacat -L -X ssl.ca.location=/run/secrets/km-ca-1.crt -X ssl.certificate.location=/run/secrets/client.certificate.pem -X ssl.key.location=/run/secrets/client.key -X ssl.key.password=krakenmare -X security.protocol=ssl -b broker-3:19094 || exit 1
run_me prometheus     curl -s http://prometheus:9090/api/v1/targets    || exit 1
run_me schemaregistry 'curl -s --cacert /run/secrets/km-ca-1.crt --cert /run/secrets/schemaregistry.certificate.pem --key /run/secrets/schemaregistry.key -X GET https://schemaregistry:8081/subjects/ | jq .'   || exit 1
run_me sasl-broker-1  kafkacat -b broker-1:29092 -L -X security.protocol=SASL_SSL -X sasl.mechanisms=SCRAM-SHA-256 -X sasl.username=client -X sasl.password=client-secret -X ssl.ca.location=/run/secrets/km-ca-1.crt -X ssl.certificate.location=/run/secrets/client.certificate.pem -X ssl.key.location=/run/secrets/client.key -X ssl.key.password=krakenmare || exit 1
run_me sasl-broker-2  kafkacat -b broker-2:29093 -L -X security.protocol=SASL_SSL -X sasl.mechanisms=SCRAM-SHA-256 -X sasl.username=client -X sasl.password=client-secret -X ssl.ca.location=/run/secrets/km-ca-1.crt -X ssl.certificate.location=/run/secrets/client.certificate.pem -X ssl.key.location=/run/secrets/client.key -X ssl.key.password=krakenmare || exit 1
run_me sasl-broker-3  kafkacat -b broker-3:29094 -L -X security.protocol=SASL_SSL -X sasl.mechanisms=SCRAM-SHA-256 -X sasl.username=client -X sasl.password=client-secret -X ssl.ca.location=/run/secrets/km-ca-1.crt -X ssl.certificate.location=/run/secrets/client.certificate.pem -X ssl.key.location=/run/secrets/client.key -X ssl.key.password=krakenmare || exit 1
run_me schemaregistry 'curl -s --cacert /run/secrets/km-ca-1.crt --cert /run/secrets/schemaregistry.certificate.pem --key /run/secrets/schemaregistry.key -X GET https://schemaregistry:8081/subjects/ | jq . | grep -c com'   || exit 1

echo -n "number of messages in KAFKA on the fabric topic..."
kafka-run-class kafka.tools.GetOffsetShell --broker-list  broker-1:9092  --topic fabric --time -1 | cut -f3 -d":" | paste -s -d+ - | bc  

echo ""
echo "all tests succeeded..."
echo ""

exit 0
