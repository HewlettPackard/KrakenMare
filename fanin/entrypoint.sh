#!/bin/bash

# Wait for all three brokers to be up
/tmp/wait-for --timeout=240 mosquitto:8883 || exit 1
/tmp/wait-for --timeout=240 framework:8080 || exit 1
/tmp/wait-for --timeout=240 broker-1:9092 || exit 1
/tmp/wait-for --timeout=240 broker-2:9093 || exit 1
/tmp/wait-for --timeout=240 broker-3:9094 || exit 1
/tmp/wait-for --timeout=240 schemaregistry:8081 || exit 1

cd /fanin
python3 FanIn.py --encrypt
sleep infinity
