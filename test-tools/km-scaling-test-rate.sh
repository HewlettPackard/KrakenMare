#!/bin/bash
# (C) Copyright 2020 Hewlett Packard Enterprise Development LP.
# Start this when the test has started to get a running 5 second sample of rate into Kafka
# Script must be killed by hand

while true; do 
  t0=$(( `date +%s` ))
  m0=$(( `kafka-run-class kafka.tools.GetOffsetShell --broker-list  broker-1:9092  --topic fabric --time -1 | cut -f3 -d":" | paste -s -d+ - | bc` ))
  sleep 5
  t1=$(( `date +%s` ))
  m1=$(( `kafka-run-class kafka.tools.GetOffsetShell --broker-list  broker-1:9092  --topic fabric --time -1 | cut -f3 -d":" | paste -s -d+ - | bc` ))
  sample_rate=$(( ($m1 - $m0) / ($t1 - $t0) ))
  echo "sample rate number of messages in KAFKA on the fabric topic: $sample_rate "
done
