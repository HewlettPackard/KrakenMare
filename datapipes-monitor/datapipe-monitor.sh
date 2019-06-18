#!/bin/bash
python3 webserver.py &
python3 mqttlistener.py &
python3 kafkalistener.py &
sleep infinity
