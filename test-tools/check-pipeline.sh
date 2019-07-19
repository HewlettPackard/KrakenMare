#!/bin/bash

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


run_me kafka-connect  curl -s http://connect:8083/connectors      || exit 1
run_me broker-1       kafkacat -b broker-1 -L                     || exit 1
run_me broker-2       kafkacat -b broker-2:9093 -L                || exit 1
run_me broker-3       kafkacat -b broker-3:9094 -L                || exit 1
run_me redis          redis-cli -h redis ping                     || exit 1
run_me framework      curl -s framework:8080/agents               || exit 1
run_me mosquitto      timeout 10 mosquitto_sub -h mosquitto -t '\$'SYS/broker/version -C 1 || exit 1
run_me influx         curl -s influxdb:8086/ping                  || exit 1
run_me druid_coord    curl -s http://druid:8081/status/health     || exit 1
run_me druid_broker   curl -s http://druid:8082/status/health     || exit 1
run_me druid_histo    curl -s http://druid:8083/status/health     || exit 1
run_me druid_overlord curl -s http://druid:8090/status/health     || exit 1
run_me druid_middle   curl -s http://druid:8091/status/health     || exit 1
run_me druid_perfquery  'curl -s -X 'POST' -H 'Content-Type:application/json' -d @/tmp/druid_perfquery.json http://druid:8082/druid/v2?pretty | grep timestamp' || exit 1
run_me druid_collectd   'curl -s -X 'POST' -H 'Content-Type:application/json' -d @/tmp/druid_collectd.json   http://druid:8082/druid/v2?pretty | grep timestamp' || exit 1
run_me influxdb       timeout 10 'curl -G "http://influxdb:8086/query?pretty=true" --data-urlencode "db=datapipes" --data-urlencode "q=show diagnostics"' || exit 1
run_me ssl-broker-1   kafkacat -L -X ssl.ca.location=/run/secrets/bd-ca-1.crt -X ssl.certificate.location=/run/secrets/client.certificate.pem -X ssl.key.location=/run/secrets/client.key -X ssl.key.password=bluedragon -X security.protocol=ssl -b broker-1:19092 || exit 1
run_me ssl-broker-2   kafkacat -L -X ssl.ca.location=/run/secrets/bd-ca-1.crt -X ssl.certificate.location=/run/secrets/client.certificate.pem -X ssl.key.location=/run/secrets/client.key -X ssl.key.password=bluedragon -X security.protocol=ssl -b broker-2:19093 || exit 1
run_me ssl-broker-3   kafkacat -L -X ssl.ca.location=/run/secrets/bd-ca-1.crt -X ssl.certificate.location=/run/secrets/client.certificate.pem -X ssl.key.location=/run/secrets/client.key -X ssl.key.password=bluedragon -X security.protocol=ssl -b broker-3:19094 || exit 1

echo ""
echo "all tests succeeded..."
echo ""

exit 0
