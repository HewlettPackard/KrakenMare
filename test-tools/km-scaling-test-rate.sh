#!/bin/bash

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
# Start this when the test has started to get a running 5 second sample of rate into Kafka
# Script must be killed by hand

while true; do 
  t0=$(( `date +%s` ))
  m0=$(( `kafka-run-class kafka.tools.GetOffsetShell --broker-list  broker-1:9092  --topic fabric --time -1 | cut -f3 -d":" | paste -s -d+ - | bc` ))
  sleep 5
  t1=$(( `date +%s` ))
  m1=$(( `kafka-run-class kafka.tools.GetOffsetShell --broker-list  broker-1:9092  --topic fabric --time -1 | cut -f3 -d":" | paste -s -d+ - | bc` ))
  sample_rate=$(( ($m1 - $m0) / ($t1 - $t0) ))
  echo "$m1 samples: sample rate number of messages in KAFKA on the fabric topic: $sample_rate "
done
