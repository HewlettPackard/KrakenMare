#!/bin/bash - 

# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# -- license --

#===============================================================================
#
#          FILE: mqtt-bench.sh
# 
#         USAGE: ./mqtt-bench.sh 
# 
#   DESCRIPTION: 
# 
#       OPTIONS: ---
#  REQUIREMENTS: ---
#          BUGS: ---
#         NOTES: ---
#        AUTHOR: Jeff Hanson (), jeff.hanson@hpe.com
#  ORGANIZATION: ATG
#       CREATED: 12/06/2019 09:23:47 AM
#      REVISION:  ---
#===============================================================================

set -o nounset                              # Treat unset variables as an error
# Methods to use mqtt-bench to test
# Default setup of 10 clients

#echo "mqtt-bench: Standard options"
#/tmp/mqtt-bench -action=pub -broker="ssl://mosquitto:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquitto.certificate.pem,/run/secrets/mosquitto.key"
#echo "mqtt-bench: 1 client, qos 0, 10000 messages, 1M size"
#/tmp/mqtt-bench -action=pub -broker="ssl://mosquitto:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquitto.certificate.pem,/run/secrets/mosquitto.key"  -clients=1 -qos=0 -count=10000 -size=131072
echo "mqtt-bench: 1 client, qos 0, 10000 messages, 2217 byte size"
/tmp/mqtt-bench -action=pub -broker="ssl://mosquitto:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquitto.certificate.pem,/run/secrets/mosquitto.key"  -clients=1 -qos=0 -count=10000 -size=2217
echo "mqtt-bench: 2 client, qos 0, 10000 messages, 2217 byte size"
/tmp/mqtt-bench -action=pub -broker="ssl://mosquitto:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquitto.certificate.pem,/run/secrets/mosquitto.key"  -clients=2 -qos=0 -count=10000 -size=2217
echo "mqtt-bench: 4 client, qos 0, 10000 messages, 2217 byte size"
/tmp/mqtt-bench -action=pub -broker="ssl://mosquitto:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquitto.certificate.pem,/run/secrets/mosquitto.key"  -clients=4 -qos=0 -count=10000 -size=2217
echo "mqtt-bench: 8 client, qos 0, 10000 messages, 2217 byte size"
/tmp/mqtt-bench -action=pub -broker="ssl://mosquitto:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquitto.certificate.pem,/run/secrets/mosquitto.key"  -clients=8 -qos=0 -count=10000 -size=2217
echo "mqtt-bench: 16 client, qos 0, 10000 messages, 2217 byte size"
/tmp/mqtt-bench -action=pub -broker="ssl://mosquitto:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquitto.certificate.pem,/run/secrets/mosquitto.key"  -clients=16 -qos=0 -count=10000 -size=2217
echo "mqtt-bench: 24 client, qos 0, 10000 messages, 2217 byte size"
/tmp/mqtt-bench -action=pub -broker="ssl://mosquitto:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquitto.certificate.pem,/run/secrets/mosquitto.key"  -clients=24 -qos=0 -count=10000 -size=2217

# Method to use mqtt-benchmark
#mqtt-benchmark --broker=mqtts://mosquitto:8883 --ca /run/secrets/km-ca-1.crt --cert /run/secrets/mosquitto.certificate.pem --key /run/secrets/mosquitto.key   --clients 1 --count 5000 --size 131072
