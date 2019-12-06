#!/bin/bash - 
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
/tmp/mqtt-bench -action=pub -broker="tcp://mosquitto:1883" 
/tmp/mqtt-bench -action=pub -broker="tcp://mosquitto:1883" -clients=1 -qos=0 -count=100000 -size=131072
 
# Same for secured mqtt
/tmp/mqtt-bench -action=pub -broker="ssl://mosquittosecu:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquittosecu.certificate.pem,/run/secrets/mosquittosecu.key"
/tmp/mqtt-bench -action=pub -broker="ssl://mosquittosecu:8883" -tls="client:/run/secrets/km-ca-1.crt,/run/secrets/mosquittosecu.certificate.pem,/run/secrets/mosquittosecu.key"  -clients=1 -qos=0 -count=100000 -size=131072

# Method to use mqtt-benchmark
mqtt-benchmark --broker=mqtt://mosquitto:1883 --clients 1 --count 5000 --size 131072
mqtt-benchmark --broker=mqtts://mosquittosecu:8883 --ca /run/secrets/km-ca-1.crt --cert /run/secrets/mosquittosecu.certificate.pem --key /run/secrets/mosquittosecu.key   --clients 1 --count 5000 --size 131072
