#!/bin/sh
# Assemble the individual schema in framework into standalone ones
cp framework/com.hpe.krakenmare.core-sensor.avsc com.hpe.krakenmare.core-agent.avsc
cat framework/com.hpe.krakenmare.core-device.avsc >> com.hpe.krakenmare.core-agent.avsc
cat framework/com.hpe.krakenmare.core-agent.avsc >> com.hpe.krakenmare.core-agent.avsc

cp framework/com.hpe.krakenmare.core-sensor.avsc com.hpe.krakenmare.core-device.avsc
cat framework/com.hpe.krakenmare.core-device.avsc >> com.hpe.krakenmare.core-device.avsc

cp framework/com.hpe.krakenmare.core-sensor.avsc com.hpe.krakenmare.message.agent-device.list.avsc
cat framework/com.hpe.krakenmare.core-device.avsc >> com.hpe.krakenmare.message.agent-device.list.avsc
cat framework/com.hpe.krakenmare.message.agent-device.list.avsc >> com.hpe.krakenmare.message.agent-device.list.avsc
