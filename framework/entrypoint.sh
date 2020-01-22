#!/bin/bash

/tmp/wait-for --timeout=240 redis:6379 \
    && /tmp/wait-for --timeout=240 broker-1:9092 \
    && /tmp/wait-for --timeout=240 broker-2:9093 \
    && /tmp/wait-for --timeout=240 broker-3:9094 \
    && /tmp/wait-for --timeout=240 mosquitto:8883 \
    && /tmp/wait-for --timeout=240 schemaregistry:8081 -- java -cp target/framework-0.0.1-SNAPSHOT-jar-with-dependencies.jar com.hpe.krakenmare.Main 


