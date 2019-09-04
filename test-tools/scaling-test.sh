#!/bin/bash
#
# Scale from 4 to 64 threads in power of 2 running
#
# kafka-producer-perf-test  --topic sasl_ssl --record-size 128 --num-records 1000000 --throughput -1 --producer.config /tmp/client-sasl_ssl.conf

for i in 4 8 16 32 64
do
  echo "test number $i"
  mkdir -p /tmp/$i
  for ((j=2; j <= i ; j++))
  do
    kafka-producer-perf-test  --topic sasl_ssl --record-size 128 --num-records 1000000 --throughput -1 --producer.config /tmp/client-sasl_ssl.conf >/tmp/$i/$j &
  done
  kafka-producer-perf-test  --topic sasl_ssl --record-size 128 --num-records 1000000 --throughput -1 --producer.config /tmp/client-sasl_ssl.conf >/tmp/$i/1
  grep "1000000 records sent" /tmp/$i/*
done

