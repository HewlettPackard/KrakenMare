#!/bin/bash

/tmp/wait-for --timeout=240 mosquitto:8883 || exit 1
/tmp/wait-for --timeout=240 broker-1:9092  || exit 1
/tmp/wait-for --timeout=240 broker-2:9093  || exit 1
/tmp/wait-for --timeout=240 broker-3:9094  || exit 1 
/tmp/wait-for --timeout=240 grafana:3000   || exit 1

python3 webserver.py &
python3 mqttlistener.py &
python3 kafkalistener.py &

sleep infinity
