#!/bin/bash

# Wait for required services to be up
/tmp/wait-for --timeout=240 mosquitto:8883 || exit 1
/tmp/wait-for --timeout=240 framework:8080 || exit 1
/tmp/wait-for --timeout=240 schemaregistry:8081 || exit 1
/simulator/check_schemas.sh || exit 1

cd /simulator

python3 IBswitchSimulator.py --encrypt --batching --numberOfTopic=2 
#--debug
sleep infinity

