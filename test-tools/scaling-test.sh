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

#
# Adjust recordsize to match test and set num-records to run a reasonable amount of time
# Sticklers for correctness in all things can write their own tests
#
# kafka-producer-perf-test  --topic sasl_ssl --record-size <size> --num-records <number> --throughput -1 --producer.config /run/secrets/client-sasl_ssl.conf

for i in 1 2 4 8 16 32
do
  echo "test with $i kafka-producer-perf-test processes record-size 64"
  mkdir -p /tmp/$i
  for ((j=2; j <= i ; j++))
  do
    kafka-producer-perf-test  --topic sasl_ssl --record-size 64 --num-records 10000000 --throughput -1 --producer.config /run/secrets/client-sasl_ssl.conf >/tmp/$i/$j &
  done
  kafka-producer-perf-test  --topic sasl_ssl --record-size 64 --num-records 10000000 --throughput -1 --producer.config /run/secrets/client-sasl_ssl.conf >/tmp/$i/1
  sleep 10
  tail -n 1 /tmp/$i/* | grep -v "==" | awk 'NF > 0'
  count=0
  total=0
  for ((j=1; j <= i ; j++))
  do 
    rec=$( tail -n 1 /tmp/$i/$j | awk '{ print $4; }' )
    total=$(echo $total+$rec | bc )
    ((count++))
  done
  echo -n "Average records/sec "
  echo "scale=2; $total / $count" | bc
  count=0
  total=0
  for ((j=1; j <= i ; j++))
  do 
    rec=$( tail -n 1 /tmp/$i/$j | awk '{ print $6; }' | cut -c2- )
    total=$(echo $total+$rec | bc )
    ((count++))
  done
  echo -n "Average MB/sec "
  echo "scale=2; $total / $count" | bc
  count=0
  total=0
  for ((j=1; j <= i ; j++))
  do 
    rec=$( tail -n 1 /tmp/$i/$j | awk '{ print $8; }' )
    total=$(echo $total+$rec | bc )
    ((count++))
  done
  echo -n "Average ms avg latency "
  echo "scale=2; $total / $count" | bc
done

