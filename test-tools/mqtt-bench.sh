#!/bin/bash - 
# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.

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

/tmp/mqtt-bench -action=pub -broker="ssl://mosquitto:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquitto.certificate.pem,/run/secrets/mosquitto.key"
/tmp/mqtt-bench -action=pub -broker="ssl://mosquitto:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquitto.certificate.pem,/run/secrets/mosquitto.key"  -clients=1 -qos=0 -count=100000 -size=131072

# Method to use mqtt-benchmark
mqtt-benchmark --broker=mqtts://mosquitto:8883 --ca /run/secrets/km-ca-1.crt --cert /run/secrets/mosquitto.certificate.pem --key /run/secrets/mosquitto.key   --clients 1 --count 5000 --size 131072
