#!/bin/bash

# Wait for all three brokers to be up
/tmp/wait-for --timeout=240 mosquitto:1883 || exit 1
/tmp/wait-for --timeout=240 mosquittosecu:8883 || exit 1
/tmp/wait-for --timeout=240 framework:8080 || exit 1
/tmp/wait-for --timeout=240 schemaregistry:8081 || exit 1

cd /simulator

python3 IBswitchSimulator.py --encrypt
sleep infinity

