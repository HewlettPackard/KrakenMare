#!/bin/bash

# Under high load, we have seen resident memory of 512MB so setting to 1GB to be safe. Can be set to 256MB for local testing.

/tmp/wait-for --timeout=240 redis:6379 \
    && /tmp/wait-for --timeout=240 broker-1:9092 \
    && /tmp/wait-for --timeout=240 broker-2:9093 \
    && /tmp/wait-for --timeout=240 broker-3:9094 \
    && /tmp/wait-for --timeout=240 mosquitto:8883 \
    && /tmp/wait-for --timeout=240 schemaregistry:8081 -- java -server -Xms${KM_FM_XMS} -Xmx${KM_FM_XMX} -cp target/framework-0.0.1-SNAPSHOT-jar-with-dependencies.jar -XX:+ExitOnOutOfMemoryError -XX:+HeapDumpOnOutOfMemoryError com.hpe.krakenmare.Main &

sleep infinity
